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

rust_binary(
    name = "rust_test_scenarios",
    srcs = glob(["src/**/*.rs"]),
    tags = [
        "manual",
    ],
    visibility = ["//visibility:public"],
    deps = [
        "@score_crates//:serde",
        "@score_crates//:serde_json",
        "@score_crates//:tracing",
        "@score_crates//:tracing_subscriber",
        "@score_kyron//src/kyron:libkyron",
        "@score_kyron//src/kyron-foundation:libkyron_foundation",
        "@score_orchestrator//src/orchestration:liborchestration",
        "@score_persistency//src/rust/rust_kvs",
        "@score_test_scenarios//test_scenarios_rust",
    ],
)

rust_binary(
    name = "rust_lifecycle_test_scenarios",
    srcs = [
        "src/main.rs",
        "src/scenarios/lifecycle/conditional_launching.rs",
        "src/scenarios/lifecycle/mod.rs",
    ],
    crate_root = "src/main.rs",
    # Build the lifecycle-only Rust FIT from the same main.rs entrypoint.
    # This target exists as a workaround: the full Rust FIT graph currently
    # hits unresolved ScoreDebug issues in score_persistency/rust_kvs.
    # Keep this until score_persistency is fixed upstream.
    rustc_flags = ["--cfg=lifecycle_only"],
    tags = [
        "manual",
    ],
    visibility = ["//visibility:public"],
    deps = [
        "@score_crates//:serde_json",
        "@score_crates//:tracing",
        "@score_crates//:tracing_subscriber",
        "@score_test_scenarios//test_scenarios_rust",
    ],
)
