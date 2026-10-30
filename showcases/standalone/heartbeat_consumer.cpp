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

// Consumer of the platform heartbeat service (//deploy/communication).
//
// Exits 0 only if it finds the deployed service via mw::com service discovery,
// the platform reports the S-CORE version this consumer was built for, and it
// receives kExpectedHeartbeats heartbeats whose baselibs CRC32 is intact.

#include "deploy/communication/heartbeat.h"

#include "score/mw/com/runtime.h"
#include "score/string_manipulation/arguments/arguments.h"

#include <chrono>
#include <cstddef>
#include <iostream>
#include <optional>
#include <string>
#include <thread>
#include <tuple>
#include <utility>

namespace
{

using namespace std::chrono_literals;
using score::platform::heartbeat::Heartbeat;
using score::platform::heartbeat::HeartbeatProxy;
using score::platform::heartbeat::PlatformInfo;

constexpr auto kDiscoveryTimeout{10s};
constexpr auto kReceiveTimeout{10s};
constexpr auto kPollInterval{50ms};
constexpr std::size_t kMaxSamples{5U};
constexpr std::size_t kExpectedHeartbeats{10U};

int Fail(const std::string& reason)
{
    std::cerr << "heartbeat_consumer: FAILED - " << reason << std::endl;
    return 1;
}

std::optional<PlatformInfo> ReceivePlatformInfo(HeartbeatProxy& proxy)
{
    if (!proxy.platform_info_.Subscribe(1U).has_value())
    {
        return std::nullopt;
    }
    std::optional<PlatformInfo> info{};
    const auto deadline = std::chrono::steady_clock::now() + kReceiveTimeout;
    while (!info.has_value() && (std::chrono::steady_clock::now() < deadline))
    {
        std::ignore = proxy.platform_info_.GetNewSamples(
            [&info](score::mw::com::SamplePtr<PlatformInfo> sample) noexcept {
                info = *sample;
            },
            1U);
        if (!info.has_value())
        {
            std::this_thread::sleep_for(kPollInterval);
        }
    }
    proxy.platform_info_.Unsubscribe();
    return info;
}

}  // namespace

int main(int argc, const char* argv[])
{
    score::mw::com::runtime::InitializeRuntime(score::string_manipulation::GetArguments(argc, argv));

    auto instance_specifier =
        score::mw::com::InstanceSpecifier::Create(std::string{score::platform::heartbeat::kInstanceSpecifier});
    if (!instance_specifier.has_value())
    {
        return Fail("invalid instance specifier");
    }

    score::mw::com::ServiceHandleContainer<HeartbeatProxy::HandleType> handles{};
    const auto discovery_deadline = std::chrono::steady_clock::now() + kDiscoveryTimeout;
    while (handles.empty() && (std::chrono::steady_clock::now() < discovery_deadline))
    {
        auto found = HeartbeatProxy::FindService(instance_specifier.value());
        if (found.has_value())
        {
            handles = std::move(found).value();
        }
        if (handles.empty())
        {
            std::this_thread::sleep_for(kPollInterval);
        }
    }
    if (handles.empty())
    {
        return Fail("the platform offers no heartbeat service (is //deploy/communication deployed and running?)");
    }
    std::cout << "heartbeat_consumer: found the platform heartbeat service" << std::endl;

    auto proxy = HeartbeatProxy::Create(handles.front());
    if (!proxy.has_value())
    {
        return Fail("cannot connect to the heartbeat service");
    }

    const auto platform_info = ReceivePlatformInfo(proxy.value());
    if (!platform_info.has_value())
    {
        return Fail("the platform reports no S-CORE version");
    }
    if (!score::platform::heartbeat::IsValid(platform_info.value()))
    {
        return Fail("the S-CORE version reported by the platform fails the CRC32 check");
    }
    std::cout << "heartbeat_consumer: platform runs S-CORE "
              << score::platform::heartbeat::ToString(platform_info.value()) << std::endl;
    const auto differences =
        score::platform::heartbeat::Compare(score::platform::heartbeat::MakePlatformInfo(), platform_info.value());
    if (!differences.empty())
    {
        return Fail("the platform runs a different S-CORE version than this check was built for:\n" + differences);
    }

    if (!proxy->heartbeat_.Subscribe(kMaxSamples).has_value())
    {
        return Fail("cannot subscribe to heartbeats");
    }

    std::size_t valid{0U};
    std::size_t corrupt{0U};
    std::uint64_t last_sequence{0U};
    const auto receive_deadline = std::chrono::steady_clock::now() + kReceiveTimeout;
    while ((valid < kExpectedHeartbeats) && (corrupt == 0U) &&
           (std::chrono::steady_clock::now() < receive_deadline))
    {
        std::ignore = proxy->heartbeat_.GetNewSamples(
            [&valid, &corrupt, &last_sequence](score::mw::com::SamplePtr<Heartbeat> sample) noexcept {
                if (score::platform::heartbeat::IsValid(*sample))
                {
                    ++valid;
                    last_sequence = sample->sequence;
                }
                else
                {
                    ++corrupt;
                }
            },
            kMaxSamples);
        std::this_thread::sleep_for(kPollInterval);
    }

    if (corrupt != 0U)
    {
        return Fail("received " + std::to_string(corrupt) + " heartbeat(s) failing the CRC32 check");
    }
    if (valid < kExpectedHeartbeats)
    {
        return Fail("received only " + std::to_string(valid) + " of " + std::to_string(kExpectedHeartbeats) +
                    " heartbeats");
    }

    std::cout << "heartbeat_consumer: received " << valid
              << " valid heartbeats from the platform heartbeat service (last sequence " << last_sequence << ")"
              << std::endl;
    return 0;
}
