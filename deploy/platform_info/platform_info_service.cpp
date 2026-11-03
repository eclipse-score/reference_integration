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

// Platform info service: offers the score/platform/info mw::com service, whose
// platform_info field reports the S-CORE version the platform was built from,
// until SIGTERM or SIGINT.

#include "deploy/platform_info/platform_info.h"

#include "score/mw/com/runtime.h"
#include "score/string_manipulation/arguments/arguments.h"

#include <chrono>
#include <csignal>
#include <iostream>
#include <string>
#include <thread>
#include <utility>

namespace
{

volatile std::sig_atomic_t g_stop_requested{0};

extern "C" void RequestStop(int /*signal*/)
{
    g_stop_requested = 1;
}

}  // namespace

int main(int argc, const char* argv[])
{
    using namespace score::platform::info;

    std::signal(SIGTERM, RequestStop);
    std::signal(SIGINT, RequestStop);

    score::mw::com::runtime::InitializeRuntime(score::string_manipulation::GetArguments(argc, argv));

    auto instance_specifier = score::mw::com::InstanceSpecifier::Create(std::string{kInstanceSpecifier});
    if (!instance_specifier.has_value())
    {
        std::cerr << "platform_info_service: invalid instance specifier: " << std::move(instance_specifier).error()
                  << '\n';
        return 1;
    }

    auto skeleton = PlatformInfoSkeleton::Create(std::move(instance_specifier).value());
    if (!skeleton.has_value())
    {
        std::cerr << "platform_info_service: cannot create skeleton: " << std::move(skeleton).error() << '\n';
        return 2;
    }

    const auto platform_info = MakePlatformInfo();
    const auto published = skeleton->platform_info_.Update(platform_info);
    if (!published.has_value())
    {
        std::cerr << "platform_info_service: cannot publish the platform info: " << published.error() << '\n';
        return 3;
    }

    const auto offered = skeleton->OfferService();
    if (!offered.has_value())
    {
        std::cerr << "platform_info_service: cannot offer service: " << offered.error() << '\n';
        return 4;
    }
    std::cout << "platform_info_service: offering " << kInstanceSpecifier << " for S-CORE "
              << ToString(platform_info) << std::endl;

    while (g_stop_requested == 0)
    {
        std::this_thread::sleep_for(std::chrono::milliseconds{100});
    }

    skeleton->StopOfferService();
    std::cout << "platform_info_service: stopped" << std::endl;
    return 0;
}
