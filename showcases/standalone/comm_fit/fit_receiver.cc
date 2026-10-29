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

// Standalone C++ consumer for the communication feature integration tests.
//
// Discovers the VehicleInterface service instance offered by fit_sender (or
// fit_sender_cc), subscribes to left_tire, and prints each received sequence
// number as "FIT_RECV seq=<n>". Emits the same FIT_RECV_* markers as the Rust
// fit_receiver so the ITF oracles in comm_helpers.py work unchanged for
// cross-language tests.
//
// Exit code: 0 when it received the requested number of samples, 1 otherwise.
//
// Usage: fit_receiver_cc [-s <manifest>] [-n <cycles>] [-t <interval_ms>]
//                        [--max-polls <n>] [-i <instance_specifier>]

#include "score/mw/com/example/com-api-example/com-api-gen/vehicle_gen.h"
#include "score/mw/com/runtime.h"
#include "score/mw/com/runtime_configuration.h"

#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <optional>
#include <string>
#include <sys/stat.h>
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
    int cycles{10};
    int interval_ms{100};
    int max_polls{100};
    std::string specifier{kDefaultSpecifier};
};

static int parse_int_arg(const char* flag, const char* val)
{
    char* end = nullptr;
    const long n = std::strtol(val, &end, 10);
    if (end == val || *end != '\0') {
        std::fprintf(stderr, "FIT_RECV_ERROR invalid integer for %s: %s\n", flag, val);
        std::exit(1);
    }
    return static_cast<int>(n);
}

Args ParseArgs(int argc, char* argv[])
{
    Args a;
    for (int i = 1; i < argc; ++i) {
        const std::string flag{argv[i]};
        const bool has_next = (i + 1 < argc);
        if ((flag == "-s" || flag == "--service-instance-manifest") && has_next) {
            a.manifest = argv[++i];
        } else if ((flag == "-n" || flag == "--cycles") && has_next) {
            a.cycles = parse_int_arg(flag.c_str(), argv[++i]);
        } else if ((flag == "-t" || flag == "--interval-ms") && has_next) {
            a.interval_ms = parse_int_arg(flag.c_str(), argv[++i]);
        } else if (flag == "--max-polls" && has_next) {
            a.max_polls = parse_int_arg(flag.c_str(), argv[++i]);
        } else if ((flag == "-i" || flag == "--instance-specifier") && has_next) {
            a.specifier = argv[++i];
        } else {
            std::fprintf(stderr, "FIT_RECV_IGNORED_ARG %s\n", argv[i]);
        }
    }
    return a;
}

bool FileExists(const std::string& path)
{
    struct stat st {};
    return stat(path.c_str(), &st) == 0;
}

}  // namespace

int main(int argc, char* argv[])
{
    const auto args = ParseArgs(argc, argv);

    if (!FileExists(args.manifest)) {
        std::fprintf(stderr, "FIT_RECV_CONFIG_MISSING path=%s\n", args.manifest.c_str());
        return 1;
    } else {
        rt::InitializeRuntime(
            rt::RuntimeConfiguration{score::filesystem::Path{args.manifest}});
    }

    auto spec_result = com::InstanceSpecifier::Create(std::string{args.specifier});
    if (!spec_result.has_value()) {
        std::fprintf(stderr, "FIT_RECV_SPEC_ERROR\n");
        return 1;
    }
    const auto& spec = spec_result.value();

    std::optional<com::VehicleProxy> proxy;
    for (int poll = 0; poll < args.max_polls && !proxy.has_value(); ++poll) {
        auto handles = com::VehicleProxy::FindService(spec);
        if (handles.has_value() && !handles.value().empty()) {
            auto proxy_result = com::VehicleProxy::Create(handles.value().front());
            if (proxy_result.has_value()) {
                proxy = std::move(proxy_result.value());
            } else {
                std::fprintf(stderr, "FIT_RECV_PROXY_BUILD_ERROR\n");
            }
        }
        if (!proxy.has_value()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(args.interval_ms));
        }
    }

    if (!proxy.has_value()) {
        std::fprintf(stderr, "FIT_RECV_NO_SERVICE\n");
        return 1;
    }
    std::printf("FIT_FOUND_SERVICE\n");
    std::fflush(stdout);

    if (!proxy->left_tire.Subscribe(static_cast<std::size_t>(args.cycles)).has_value()) {
        std::fprintf(stderr, "FIT_RECV_SUBSCRIBE_ERROR\n");
        return 1;
    }

    int received = 0;
    for (int poll = 0; poll < args.max_polls && received < args.cycles; ++poll) {
        auto result = proxy->left_tire.GetNewSamples(
            [&received](com::SamplePtr<const com::Tire> sample) noexcept {
                std::printf("FIT_RECV seq=%.9g\n", static_cast<double>(sample->pressure));
                std::fflush(stdout);
                ++received;
            },
            static_cast<std::size_t>(args.cycles));

        if (!result.has_value() || result.value() == 0U) {
            std::this_thread::sleep_for(std::chrono::milliseconds(args.interval_ms));
        }
    }

    proxy->left_tire.Unsubscribe();

    if (received >= args.cycles) {
        std::printf("FIT_RECV_DONE count=%d\n", received);
        return 0;
    }
    std::fprintf(stderr, "FIT_RECV_INCOMPLETE count=%d expected=%d\n", received, args.cycles);
    return 1;
}
