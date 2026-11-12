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

// Replays a scripted 40 s highway drive (lead vehicle brakes hard, ego driver reacts late)
// and publishes it frame by frame as mw::com event to the vehicle functions.

#include "showcases/drive_replay/drive_data.h"
#include "showcases/drive_replay/viz_link.h"

#include "score/mw/com/runtime.h"
#include "score/mw/log/logger.h"
#include "score/string_manipulation/arguments/arguments.h"
#include <score/mw/lifecycle/report_running.h>

#include <array>
#include <chrono>
#include <csignal>
#include <cstdint>
#include <cstdio>
#include <string>
#include <thread>
#include <utility>

namespace
{

using namespace score::showcases::drive_replay;
using namespace std::chrono_literals;

constexpr auto kFramePeriod{50ms};
constexpr double kFramePeriodS{0.05};
constexpr double kLapDurationS{40.0};
constexpr double kInitialGapM{40.0};
constexpr std::uint64_t kSummaryEveryFrames{100U};

struct Keyframe
{
    double time_s;
    double speed_mps;
};

constexpr std::array<Keyframe, 6U> kLeadSpeed{{{0.0, 22.0}, {10.0, 22.0}, {13.0, 5.0}, {19.0, 5.0}, {25.0, 22.0}, {40.0, 22.0}}};
// The end of the ego ramp is tuned so that the gap returns to kInitialGapM at the end of the lap.
constexpr std::array<Keyframe, 6U> kEgoSpeed{{{0.0, 22.0}, {11.6, 22.0}, {14.8, 4.0}, {20.0, 4.0}, {26.23, 22.0}, {40.0, 22.0}}};

volatile std::sig_atomic_t g_stop_requested{0};

extern "C" void RequestStop(int /*signal*/)
{
    g_stop_requested = 1;
}

template <std::size_t N>
double Interpolate(const std::array<Keyframe, N>& table, const double time_s)
{
    for (std::size_t i = 1U; i < N; ++i)
    {
        if (time_s <= table[i].time_s)
        {
            const auto& from = table[i - 1U];
            const auto& to = table[i];
            return from.speed_mps + ((to.speed_mps - from.speed_mps) * (time_s - from.time_s) / (to.time_s - from.time_s));
        }
    }
    return table[N - 1U].speed_mps;
}

DrivePhase PhaseAt(const double time_s)
{
    if (time_s < 10.0)
    {
        return DrivePhase::kCruise;
    }
    if (time_s < 11.6)
    {
        return DrivePhase::kLeadBraking;
    }
    if (time_s < 19.0)
    {
        return DrivePhase::kEgoBraking;
    }
    if (time_s < 26.23)
    {
        return DrivePhase::kRecovering;
    }
    return DrivePhase::kCruise;
}

const char* PhaseName(const DrivePhase phase)
{
    switch (phase)
    {
        case DrivePhase::kLeadBraking:
            return "lead_braking";
        case DrivePhase::kEgoBraking:
            return "ego_braking";
        case DrivePhase::kRecovering:
            return "recovering";
        case DrivePhase::kCruise:
        default:
            return "cruise";
    }
}

const char* PhaseStory(const DrivePhase phase)
{
    switch (phase)
    {
        case DrivePhase::kLeadBraking:
            return "lead vehicle brakes hard (79 -> 18 km/h)";
        case DrivePhase::kEgoBraking:
            return "ego driver reacts late and brakes";
        case DrivePhase::kRecovering:
            return "traffic clears, both vehicles accelerate";
        case DrivePhase::kCruise:
        default:
            return "both vehicles cruising at 79 km/h";
    }
}

std::string Format(const char* format, const double a, const double b, const double c)
{
    std::array<char, 128U> buffer{};
    static_cast<void>(std::snprintf(buffer.data(), buffer.size(), format, a, b, c));
    return std::string{buffer.data()};
}

std::string VizRecord(const DriveFrame& frame, const std::uint64_t lap)
{
    std::array<char, 384U> buffer{};
    static_cast<void>(std::snprintf(buffer.data(),
                                    buffer.size(),
                                    "{\"src\":\"RPLY\",\"type\":\"drive\",\"seq\":%llu,\"lap\":%llu,\"t\":%.2f,"
                                    "\"ego_x\":%.3f,\"ego_v\":%.3f,\"lead_x\":%.3f,\"lead_v\":%.3f,\"gap\":%.3f,"
                                    "\"phase\":\"%s\"}",
                                    static_cast<unsigned long long>(frame.sequence),
                                    static_cast<unsigned long long>(lap),
                                    frame.sim_time_s,
                                    frame.ego_position_m,
                                    frame.ego_speed_mps,
                                    frame.lead_position_m,
                                    frame.lead_speed_mps,
                                    frame.lead_position_m - frame.ego_position_m - kVehicleLengthM,
                                    PhaseName(frame.phase)));
    return std::string{buffer.data()};
}

}  // namespace

int main(int argc, const char* argv[])
{
    std::signal(SIGTERM, RequestStop);
    std::signal(SIGINT, RequestStop);

    score::mw::com::runtime::InitializeRuntime(score::string_manipulation::GetArguments(argc, argv));
    auto& logger = score::mw::log::CreateLogger("DRV", "drive replay");

    auto instance_specifier = score::mw::com::InstanceSpecifier::Create(std::string{kDriveDataInstance});
    if (!instance_specifier.has_value())
    {
        logger.LogError() << "invalid instance specifier: " << std::string{instance_specifier.error().Message()};
        return 1;
    }
    auto skeleton = DriveDataSkeleton::Create(std::move(instance_specifier).value());
    if (!skeleton.has_value())
    {
        logger.LogError() << "cannot create skeleton: " << std::string{skeleton.error().Message()};
        return 2;
    }
    const auto offered = skeleton->OfferService();
    if (!offered.has_value())
    {
        logger.LogError() << "cannot offer service: " << std::string{offered.error().Message()};
        return 3;
    }

    const score::showcases::drive_replay::VizLink viz{};
    logger.LogInfo() << "offering " + std::string{kDriveDataInstance} + " via mw::com, 20 frames/s, viz -> " +
                            viz.Destination();
    score::mw::lifecycle::report_running();

    DriveFrame frame{};
    frame.lead_position_m = kInitialGapM;
    std::uint64_t lap{1U};
    double lap_time_s{0.0};
    DrivePhase last_phase{DrivePhase::kCruise};
    bool send_error_reported{false};
    logger.LogInfo() << "lap " + std::to_string(lap) + " started: " + PhaseStory(last_phase);

    auto next_tick = std::chrono::steady_clock::now();
    while (g_stop_requested == 0)
    {
        frame.sim_time_s = lap_time_s;
        frame.ego_speed_mps = Interpolate(kEgoSpeed, lap_time_s);
        frame.lead_speed_mps = Interpolate(kLeadSpeed, lap_time_s);
        frame.phase = PhaseAt(lap_time_s);

        const auto sent = skeleton->frame_.Send(frame);
        if (!sent.has_value() && !send_error_reported)
        {
            logger.LogError() << "frame #" + std::to_string(frame.sequence) +
                                     " could not be sent: " + std::string{sent.error().Message()};
            send_error_reported = true;
        }
        viz.Send(VizRecord(frame, lap));

        if (frame.phase != last_phase)
        {
            logger.LogInfo() << "frame #" + std::to_string(frame.sequence) + ": " + PhaseStory(frame.phase);
            last_phase = frame.phase;
        }
        if ((frame.sequence % kSummaryEveryFrames) == 0U)
        {
            logger.LogInfo() << "frame #" + std::to_string(frame.sequence) + " published via mw::com: " +
                                    Format("ego %.0f km/h, lead %.0f km/h, gap %.1f m",
                                           frame.ego_speed_mps * 3.6,
                                           frame.lead_speed_mps * 3.6,
                                           frame.lead_position_m - frame.ego_position_m - kVehicleLengthM);
        }
        logger.LogDebug() << "frame #" + std::to_string(frame.sequence) + " sent";

        frame.ego_position_m += frame.ego_speed_mps * kFramePeriodS;
        frame.lead_position_m += frame.lead_speed_mps * kFramePeriodS;
        ++frame.sequence;
        lap_time_s += kFramePeriodS;
        if (lap_time_s >= kLapDurationS)
        {
            lap_time_s = 0.0;
            ++lap;
            frame.lead_position_m = frame.ego_position_m + kInitialGapM;
            logger.LogInfo() << "lap " + std::to_string(lap) + " started: " + PhaseStory(DrivePhase::kCruise);
        }

        next_tick += kFramePeriod;
        std::this_thread::sleep_until(next_tick);
    }

    skeleton->StopOfferService();
    logger.LogInfo() << "stopped after " + std::to_string(frame.sequence) + " frames";
    return 0;
}
