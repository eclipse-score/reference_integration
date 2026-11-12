/********************************************************************************
 * Copyright (c) 2026 Contributors to the Eclipse Foundation
 *
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 ********************************************************************************/

// Forward collision warning: consumes the drive frames via mw::com, computes the time to collision,
// is supervised by the health monitor and keeps its counters in the persistency KVS.
// SIGUSR1 injects a fault: the processing loop hangs and stops sending heartbeats.

#include "showcases/drive_replay/drive_data.h"
#include "showcases/drive_replay/viz_link.h"

#include "score/kvs/kvs_builder.h"
#include "score/mw/com/runtime.h"
#include "score/mw/log/logger.h"
#include "score/string_manipulation/arguments/arguments.h"
#include <score/mw/health/common.h>
#include <score/mw/health/health_monitor.h>
#include <score/mw/lifecycle/report_running.h>

#include <algorithm>
#include <array>
#include <chrono>
#include <csignal>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <optional>
#include <string>
#include <thread>
#include <utility>
#include <variant>

namespace
{

using namespace score::showcases::drive_replay;
using namespace std::chrono_literals;

constexpr auto kCycle{50ms};
constexpr double kWarningTtcS{3.0};
constexpr double kCriticalTtcS{2.0};
constexpr double kMinClosingSpeedMps{0.1};
constexpr double kNoCollisionTtcS{99.0};
constexpr std::uint64_t kSummaryEveryFrames{100U};
constexpr const char* kDefaultKvsDir{"/tmp/drive_replay/kvs/"};

volatile std::sig_atomic_t g_stop_requested{0};
volatile std::sig_atomic_t g_hang_requested{0};

extern "C" void HandleSignal(int signal)
{
    if (signal == SIGUSR1)
    {
        g_hang_requested = 1;
    }
    else
    {
        g_stop_requested = 1;
    }
}

enum class WarningLevel : std::uint8_t
{
    kNone = 0U,
    kWarning = 1U,
    kCritical = 2U,
};

const char* LevelName(const WarningLevel level)
{
    switch (level)
    {
        case WarningLevel::kWarning:
            return "WARNING";
        case WarningLevel::kCritical:
            return "CRITICAL";
        case WarningLevel::kNone:
        default:
            return "OK";
    }
}

std::string Fixed(const double value, const int decimals)
{
    std::array<char, 32U> buffer{};
    static_cast<void>(std::snprintf(buffer.data(), buffer.size(), "%.*f", decimals, value));
    return std::string{buffer.data()};
}

std::int64_t ReadCounter(const score::kvs::Kvs& kvs, const std::string_view key)
{
    const auto value = kvs.GetValue(key);
    if (value.has_value() && (value->GetType() == score::kvs::KvsValue::Type::kI64))
    {
        return std::get<std::int64_t>(value->GetValue());
    }
    return 0;
}

void WriteCounter(score::kvs::Kvs& kvs, const std::string_view key, const std::int64_t counter)
{
    static_cast<void>(kvs.SetValue(key, score::kvs::KvsValue{counter}));
    static_cast<void>(kvs.Flush());
}

std::optional<DriveDataProxy> ConnectToDriveData(score::mw::log::Logger& logger)
{
    auto instance_specifier = score::mw::com::InstanceSpecifier::Create(std::string{kDriveDataInstance});
    if (!instance_specifier.has_value())
    {
        logger.LogError() << "invalid instance specifier";
        return std::nullopt;
    }
    bool waiting_reported{false};
    while (g_stop_requested == 0)
    {
        auto handles = DriveDataProxy::FindService(instance_specifier.value());
        if (handles.has_value() && !handles->empty())
        {
            auto proxy = DriveDataProxy::Create(handles->front());
            if (proxy.has_value())
            {
                return std::move(proxy).value();
            }
        }
        if (!waiting_reported)
        {
            logger.LogInfo() << "waiting for service " + std::string{kDriveDataInstance};
            waiting_reported = true;
        }
        std::this_thread::sleep_for(kCycle);
    }
    return std::nullopt;
}

}  // namespace

int main(int argc, const char* argv[])
{
    std::signal(SIGTERM, HandleSignal);
    std::signal(SIGINT, HandleSignal);
    std::signal(SIGUSR1, HandleSignal);

    score::mw::com::runtime::InitializeRuntime(score::string_manipulation::GetArguments(argc, argv));
    auto& logger = score::mw::log::CreateLogger("FCW", "forward collision warning");
    const VizLink viz{};

    const char* kvs_dir = std::getenv("DRIVE_KVS_DIR");
    auto kvs_result = score::kvs::KvsBuilder(0)
                          .Defaults(score::kvs::KvsDefaults::kOptional)
                          .KvsLoad(score::kvs::KvsLoad::kOptional)
                          .WorkingDir((kvs_dir != nullptr) ? kvs_dir : kDefaultKvsDir)
                          .Build();
    if (!kvs_result.has_value())
    {
        logger.LogError() << "cannot open persistency KVS";
        return 1;
    }
    auto kvs = std::move(kvs_result).value();
    const std::int64_t start_count = ReadCounter(kvs, "start_count") + 1;
    std::int64_t warn_count = ReadCounter(kvs, "warn_count");
    WriteCounter(kvs, "start_count", start_count);
    logger.LogInfo() << "started (start #" + std::to_string(start_count) +
                            "), restored warn_count=" + std::to_string(warn_count) + " from persistency";

    const score::mw::health::MonitorTag monitor_tag{"fcw_cycle"};
    // The heartbeat minimum must exceed half the internal processing cycle.
    auto health_monitor_result =
        score::mw::health::HealthMonitorBuilder()
            .AddHeartbeatMonitor(monitor_tag,
                                 score::mw::health::heartbeat::HeartbeatMonitorBuilder(
                                     score::mw::health::TimeRange(30ms, 300ms)))
            .WithInternalProcessingCycle(kCycle)
            .WithSupervisorApiCycle(kCycle)
            .Build();
    if (!health_monitor_result.has_value())
    {
        logger.LogError() << "cannot build health monitor";
        return 2;
    }
    auto health_monitor = std::move(*health_monitor_result);
    auto heartbeat_result = health_monitor.GetHeartbeatMonitor(monitor_tag);
    if (!heartbeat_result.has_value())
    {
        logger.LogError() << "cannot get heartbeat monitor";
        return 3;
    }
    auto heartbeat = std::move(*heartbeat_result);
    health_monitor.Start();
    score::mw::lifecycle::report_running();
    logger.LogInfo() << "supervised by health monitor: heartbeat every 50 ms, tolerance 300 ms";

    auto proxy = ConnectToDriveData(logger);
    if (!proxy.has_value())
    {
        return (g_stop_requested != 0) ? 0 : 4;
    }
    if (!proxy->frame_.Subscribe(4U).has_value())
    {
        logger.LogError() << "cannot subscribe to drive frames";
        return 5;
    }
    logger.LogInfo() << "connected to " + std::string{kDriveDataInstance} + " via mw::com, subscribed to frames";

    WarningLevel level{WarningLevel::kNone};
    double episode_min_ttc_s{kNoCollisionTtcS};
    std::optional<std::uint64_t> last_sequence{};
    auto next_cycle = std::chrono::steady_clock::now();
    while ((g_stop_requested == 0) && (g_hang_requested == 0))
    {
        heartbeat.Heartbeat();

        std::optional<DriveFrame> frame{};
        static_cast<void>(proxy->frame_.GetNewSamples(
            [&frame](score::mw::com::SamplePtr<DriveFrame> sample) noexcept {
                frame = *sample;
            },
            4U));

        if (frame.has_value())
        {
            const auto sequence = frame->sequence;
            if (!last_sequence.has_value())
            {
                logger.LogInfo() << "first frame #" + std::to_string(sequence) + " received";
            }
            else if (sequence > (*last_sequence + 4U))
            {
                logger.LogWarn() << "frames #" + std::to_string(*last_sequence + 1U) + "..#" +
                                        std::to_string(sequence - 1U) + " missed";
            }
            last_sequence = sequence;

            const double gap_m = frame->lead_position_m - frame->ego_position_m - kVehicleLengthM;
            const double closing_mps = frame->ego_speed_mps - frame->lead_speed_mps;
            const double ttc_s =
                (closing_mps > kMinClosingSpeedMps) ? std::min(gap_m / closing_mps, kNoCollisionTtcS) : kNoCollisionTtcS;
            const WarningLevel new_level = (ttc_s < kCriticalTtcS)  ? WarningLevel::kCritical
                                           : (ttc_s < kWarningTtcS) ? WarningLevel::kWarning
                                                                    : WarningLevel::kNone;
            episode_min_ttc_s = std::min(episode_min_ttc_s, ttc_s);

            if (new_level != level)
            {
                const std::string situation = "TTC " + Fixed(ttc_s, 1) + " s, gap " + Fixed(gap_m, 1) + " m";
                if ((level == WarningLevel::kNone) && (new_level != WarningLevel::kNone))
                {
                    ++warn_count;
                    WriteCounter(kvs, "warn_count", warn_count);
                    logger.LogWarn() << "frame #" + std::to_string(sequence) + ": FORWARD COLLISION WARNING - " +
                                            situation + " (warning #" + std::to_string(warn_count) + ", persisted)";
                }
                if (new_level == WarningLevel::kCritical)
                {
                    logger.LogWarn() << "frame #" + std::to_string(sequence) + ": CRITICAL, brake now! " + situation;
                }
                if (new_level == WarningLevel::kNone)
                {
                    logger.LogInfo() << "frame #" + std::to_string(sequence) + ": situation resolved (min TTC " +
                                            Fixed(episode_min_ttc_s, 2) + " s)";
                    episode_min_ttc_s = kNoCollisionTtcS;
                }
                level = new_level;
            }
            if ((sequence % kSummaryEveryFrames) == 0U)
            {
                logger.LogInfo() << "frame #" + std::to_string(sequence) + " processed: gap " + Fixed(gap_m, 1) +
                                        " m, closing " + Fixed(closing_mps, 1) + " m/s, " + LevelName(level);
            }
            logger.LogDebug() << "frame #" + std::to_string(sequence) + " TTC " + Fixed(ttc_s, 2);

            viz.Send("{\"src\":\"FCW\",\"type\":\"warn\",\"seq\":" + std::to_string(sequence) +
                     ",\"ttc\":" + Fixed(ttc_s, 3) + ",\"gap\":" + Fixed(gap_m, 3) +
                     ",\"closing\":" + Fixed(closing_mps, 3) + ",\"level\":\"" + LevelName(level) +
                     "\",\"level_id\":" + std::to_string(static_cast<int>(level)) +
                     ",\"warn_count\":" + std::to_string(warn_count) +
                     ",\"start_count\":" + std::to_string(start_count) + "}");
        }

        next_cycle += kCycle;
        std::this_thread::sleep_until(next_cycle);
    }

    if (g_hang_requested != 0)
    {
        logger.LogError() << "FAULT INJECTED: processing loop hangs, no more heartbeats to the health monitor";
        while (g_stop_requested == 0)
        {
            std::this_thread::sleep_for(100ms);
        }
    }

    proxy->frame_.Unsubscribe();
    logger.LogInfo() << "stopped by launch manager";
    return 0;
}
