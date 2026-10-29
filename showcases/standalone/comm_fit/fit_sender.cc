// *******************************************************************************
// Copyright (c) 2026 Contributors to the Eclipse Foundation
//
// See the NOTICE file(s) distributed with this work for additional
// information regarding copyright ownership.
//
// This program and the accompanying materials are made available under the
// terms of the Apache License Version 2.0 which is available at
// https://www.apache.org/licenses/LICENSE-2.0
//
// SPDX-License-Identifier: Apache-2.0
// *******************************************************************************

// Standalone C++ producer for the communication feature integration tests.
//
// Offers the VehicleInterface service instance and publishes left_tire samples
// whose pressure field carries a monotonically increasing sequence number
// (0, 1, 2, ...). Emits the same FIT_SEND_* markers as the Rust fit_sender so
// the ITF oracles in comm_helpers.py work unchanged for cross-language tests.
//
// Usage: fit_sender_cc [-s <manifest>] [-n <cycles>] [-t <interval_ms>]
//                      [-i <instance_specifier>]

#include "score/mw/com/example/com-api-example/com-api-gen/vehicle_gen.h"
#include "score/mw/com/runtime.h"
#include "score/mw/com/runtime_configuration.h"

#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <thread>

namespace com = score::mw::com;
namespace rt = score::mw::com::runtime;

namespace
{

constexpr const char* kDefaultManifest = "./etc/mw_com_config.json";
constexpr const char* kDefaultSpecifier = "/Vehicle/Service1/Instance";

struct Args
{
    std::string manifest{kDefaultManifest};
    int cycles{50};
    int interval_ms{100};
    std::string specifier{kDefaultSpecifier};
};

Args ParseArgs(int argc, char* argv[])
{
    Args a;
    for (int i = 1; i < argc - 1; ++i) {
        const std::string flag{argv[i]};
        if (flag == "-s" || flag == "--service-instance-manifest") {
            a.manifest = argv[++i];
        } else if (flag == "-n" || flag == "--cycles") {
            a.cycles = std::atoi(argv[++i]);
        } else if (flag == "-t" || flag == "--interval-ms") {
            a.interval_ms = std::atoi(argv[++i]);
        } else if (flag == "-i" || flag == "--instance-specifier") {
            a.specifier = argv[++i];
        } else {
            std::fprintf(stderr, "FIT_SEND_IGNORED_ARG %s\n", argv[i]);
        }
    }
    return a;
}

}  // namespace

int main(int argc, char* argv[])
{
    const auto args = ParseArgs(argc, argv);

    rt::InitializeRuntime(
        rt::RuntimeConfiguration{score::filesystem::Path{args.manifest}});

    auto spec_result = com::InstanceSpecifier::Create(std::string{args.specifier});
    if (!spec_result.has_value()) {
        std::fprintf(stderr, "FIT_SEND_SPEC_ERROR\n");
        return 1;
    }

    auto skel_result = com::VehicleSkeleton::Create(spec_result.value());
    if (!skel_result.has_value()) {
        std::fprintf(stderr, "FIT_SEND_CREATE_ERROR\n");
        return 1;
    }
    auto& skeleton = skel_result.value();

    if (!skeleton.OfferService().has_value()) {
        std::fprintf(stderr, "FIT_SEND_OFFER_ERROR\n");
        return 1;
    }
    std::printf("FIT_SEND_OFFERED\n");
    std::fflush(stdout);

    for (int seq = 0; seq < args.cycles; ++seq) {
        auto alloc = skeleton.left_tire.Allocate();
        if (!alloc.has_value()) {
            std::fprintf(stderr, "FIT_SEND_ERROR allocate failed at seq=%d\n", seq);
            return 1;
        }
        alloc.value()->pressure = static_cast<float>(seq);
        if (!skeleton.left_tire.Send(std::move(alloc.value())).has_value()) {
            std::fprintf(stderr, "FIT_SEND_ERROR send failed at seq=%d\n", seq);
            return 1;
        }
        std::printf("FIT_SEND seq=%d\n", seq);
        std::fflush(stdout);
        std::this_thread::sleep_for(std::chrono::milliseconds(args.interval_ms));
    }

    std::printf("FIT_SEND_DONE count=%d\n", args.cycles);
    return 0;
}
