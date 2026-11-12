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

// State manager of the drive replay demo: reports every Run Target change and, after the
// launch manager fell back to the degraded Run Target, requests "Drive" again.

#include "showcases/drive_replay/viz_link.h"

#include "score/mw/com/runtime.h"
#include "score/mw/log/logger.h"
#include "score/string_manipulation/arguments/arguments.h"
#include <score/mw/lifecycle/ilm_control.hpp>
#include <score/mw/lifecycle/report_running.h>

#include <chrono>
#include <csignal>
#include <cstdint>
#include <deque>
#include <memory>
#include <mutex>
#include <optional>
#include <string>
#include <thread>
#include <utility>

namespace
{

using namespace std::chrono_literals;
using score::mw::lifecycle::RunTargetActivationSource;
using score::mw::lifecycle::RunTargetName;

constexpr auto kLoopPeriod{100ms};
constexpr auto kStatusPeriod{1s};
constexpr auto kRecoveryDelay{3s};
constexpr const char* kNominalRunTarget{"Drive"};

volatile std::sig_atomic_t g_stop_requested{0};

extern "C" void RequestStop(int /*signal*/)
{
    g_stop_requested = 1;
}

struct Activation
{
    RunTargetActivationSource source;
    std::string run_target;
};

const char* SourceName(const RunTargetActivationSource source)
{
    switch (source)
    {
        case RunTargetActivationSource::kInitialActivation:
            return "initial";
        case RunTargetActivationSource::kStateManagerRequest:
            return "state_manager";
        case RunTargetActivationSource::kRecoveryAction:
            return "recovery_action";
        default:
            return "unknown";
    }
}

}  // namespace

int main(int argc, const char* argv[])
{
    std::signal(SIGTERM, RequestStop);
    std::signal(SIGINT, RequestStop);

    score::mw::com::runtime::InitializeRuntime(score::string_manipulation::GetArguments(argc, argv));
    auto& logger = score::mw::log::CreateLogger("SM", "drive state manager");
    const score::showcases::drive_replay::VizLink viz{};

    score::mw::lifecycle::report_running();

    auto client_result = score::mw::lifecycle::ILmControl::Create("StateManager/LaunchManager/Instance");
    if (!client_result.has_value())
    {
        logger.LogError() << "cannot connect to the launch manager";
        return 1;
    }
    std::unique_ptr<score::mw::lifecycle::ILmControl> client = std::move(client_result).value();

    std::mutex activations_mutex{};
    std::deque<Activation> activations{};
    const auto registered = client->register_run_target_activation_callback(
        [&activations_mutex, &activations](RunTargetActivationSource source, RunTargetName target) {
            const std::lock_guard<std::mutex> lock{activations_mutex};
            activations.push_back(Activation{source, std::string{target.as_string_view()}});
        });
    if (!registered.has_value())
    {
        logger.LogError() << "cannot register for Run Target activations";
        return 2;
    }
    logger.LogInfo() << "connected to the launch manager, watching Run Target changes";

    std::string run_target{"(starting)"};
    std::string source{"initial"};
    std::uint32_t recoveries{0U};
    std::optional<std::chrono::steady_clock::time_point> recover_at{};
    auto next_status = std::chrono::steady_clock::now();

    while (g_stop_requested == 0)
    {
        std::deque<Activation> pending{};
        {
            const std::lock_guard<std::mutex> lock{activations_mutex};
            pending.swap(activations);
        }
        for (const auto& activation : pending)
        {
            run_target = activation.run_target;
            source = SourceName(activation.source);
            if (activation.source == RunTargetActivationSource::kRecoveryAction)
            {
                ++recoveries;
                logger.LogError() << "launch manager recovered a failure: Run Target '" + run_target +
                                         "' active, DEGRADED - collision warning is OFF (recovery #" +
                                         std::to_string(recoveries) + ")";
                recover_at = std::chrono::steady_clock::now() + kRecoveryDelay;
            }
            else
            {
                logger.LogInfo() << "Run Target '" + run_target + "' active (" + source + ")" +
                                        ((run_target == kNominalRunTarget) ? ", all functions running" : "");
            }
        }

        const auto now = std::chrono::steady_clock::now();
        if (!pending.empty())
        {
            next_status = now;
        }
        if (recover_at.has_value() && (now >= *recover_at))
        {
            recover_at.reset();
            logger.LogWarn() << "requesting Run Target '" + std::string{kNominalRunTarget} +
                                    "' to restore the collision warning";
            const auto requested = client->activate_run_target(RunTargetName{"Drive"});
            if (!requested.has_value())
            {
                logger.LogError() << "Run Target request rejected, retrying";
                recover_at = now + kRecoveryDelay;
            }
        }

        if (now >= next_status)
        {
            next_status = now + kStatusPeriod;
            viz.Send("{\"src\":\"SM\",\"type\":\"system\",\"run_target\":\"" + run_target + "\",\"source\":\"" +
                     source + "\",\"degraded\":" + ((run_target == kNominalRunTarget) ? "false" : "true") +
                     ",\"recoveries\":" + std::to_string(recoveries) + "}");
        }
        std::this_thread::sleep_for(kLoopPeriod);
    }

    logger.LogInfo() << "stopped";
    return 0;
}
