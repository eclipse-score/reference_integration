# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
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
"""TCK packaging rules.

Builds the score-tck binary (Rust) and packages it with golden reference data.

Usage:
    bazel build //tck:score-tck
    ./bazel-bin/tck/score-tck --help
"""

load("@rules_rust//rust:defs.bzl", "rust_binary")

# Golden SBOM - copy from root product SBOM (built separately)
# The runner expects the SBOM at tck/reference/sbom.spdx.json
filegroup(
    name = "golden_sbom",
    srcs = ["reference/sbom.spdx.json"],
    visibility = ["//visibility:public"],
)

# Rust TCK runner binary
rust_binary(
    name = "score-tck",
    srcs = glob([
        "runner/src/**/*.rs",
    ]),
    crate_root = "runner/src/main.rs",
    deps = [
        "@score_crates//:anyhow",
        "@score_crates//:clap",
        "@score_crates//:serde",
        "@score_crates//:serde_json",
    ],
    visibility = ["//visibility:public"],
)

# Distribution config example
filegroup(
    name = "config_example",
    srcs = ["tck.config.example.toml"],
    visibility = ["//visibility:public"],
)
