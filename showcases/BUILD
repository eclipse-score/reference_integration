# *******************************************************************************
# Copyright (c) 2025 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************

load("@rules_rust//rust:defs.bzl", "rust_binary")
load("//bazel_common:bundlers.bzl", "score_pkg_bundle")

score_pkg_bundle(
    name = "showcases_all",
    # package_dir = "",
    bins = [":kyron_example", ":orch_per_example", ],
    other_package_files = ["//showcases/standalone:standalone_pkg_files"]
)

rust_binary(
    name = "kyron_example",
    srcs = glob(["kyron/**/*.rs"]),
    deps = [
        "@score_kyron//src/kyron:libkyron",
        "@score_kyron//src/kyron-foundation:libkyron_foundation",
        "@score_crates//:tracing_subscriber",
    ],
    visibility = ["//visibility:public"],
)

rust_binary(
    name = "orch_per_example",
    srcs = glob(["orchestration_persistency/**/*.rs"]),
    deps = [
        "@score_kyron//src/kyron:libkyron",
        "@score_kyron//src/kyron-foundation:libkyron_foundation",
        "@score_orchestrator//src/orchestration:liborchestration",
        "@score_kyron//src/logging_tracing:liblogging_tracing",
        "@score_persistency//src/rust/rust_kvs:rust_kvs",
    ],
    visibility = ["//visibility:public"],
)
