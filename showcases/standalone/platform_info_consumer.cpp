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

// Consumer of the platform info service (//deploy/platform_info).
//
// Exits 0 only if it finds the deployed service via mw::com service discovery,
// receives platform_info with an intact baselibs CRC32, and the platform reports
// the S-CORE version this consumer was built for.

#include "deploy/platform_info/platform_info.h"

#include "score/mw/com/runtime.h"
#include "score/mw/log/logger.h"
#include "score/string_manipulation/arguments/arguments.h"

#include <chrono>
#include <optional>
#include <string>
#include <thread>
#include <tuple>
#include <utility>

namespace
{

using namespace std::chrono_literals;
using score::platform::info::PlatformInfo;
using score::platform::info::PlatformInfoProxy;

constexpr auto kDiscoveryTimeout{10s};
constexpr auto kReceiveTimeout{10s};
constexpr auto kPollInterval{50ms};

score::mw::log::Logger& Logger()
{
    static auto& logger = score::mw::log::CreateLogger("PINF", "platform info");
    return logger;
}

int Fail(const std::string& reason)
{
    Logger().LogError() << "platform_info_consumer: FAILED - " + reason;
    return 1;
}

std::optional<PlatformInfo> ReceivePlatformInfo(PlatformInfoProxy& proxy)
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
        score::mw::com::InstanceSpecifier::Create(std::string{score::platform::info::kInstanceSpecifier});
    if (!instance_specifier.has_value())
    {
        return Fail("invalid instance specifier");
    }

    score::mw::com::ServiceHandleContainer<PlatformInfoProxy::HandleType> handles{};
    const auto discovery_deadline = std::chrono::steady_clock::now() + kDiscoveryTimeout;
    while (handles.empty() && (std::chrono::steady_clock::now() < discovery_deadline))
    {
        auto found = PlatformInfoProxy::FindService(instance_specifier.value());
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
        return Fail("the platform offers no platform info service (is //deploy/platform_info deployed and running?)");
    }
    Logger().LogInfo() << "platform_info_consumer: found the platform info service";

    auto proxy = PlatformInfoProxy::Create(handles.front());
    if (!proxy.has_value())
    {
        return Fail("cannot connect to the platform info service");
    }

    const auto platform_info = ReceivePlatformInfo(proxy.value());
    if (!platform_info.has_value())
    {
        return Fail("the platform reports no S-CORE version");
    }
    if (!score::platform::info::IsValid(platform_info.value()))
    {
        return Fail("the S-CORE version reported by the platform fails the CRC32 check");
    }
    Logger().LogInfo() << "platform_info_consumer: platform runs S-CORE " +
                              score::platform::info::ToString(platform_info.value());

    const auto differences =
        score::platform::info::Compare(score::platform::info::MakePlatformInfo(), platform_info.value());
    if (!differences.empty())
    {
        return Fail("the platform runs a different S-CORE version than this check was built for:\n" + differences);
    }

    Logger().LogInfo() << "platform_info_consumer: S-CORE version check passed (" +
                              std::to_string(platform_info->module_count) + " modules match)";
    return 0;
}
