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
load("@rules_rust//rust:defs.bzl", "rust_binary")
load("//bazel_common:bundlers.bzl", "score_pkg_bundle")

rust_binary(
    name = "kyron_logging",
    srcs = ["src/main.rs"],
    visibility = ["//visibility:public"],
    deps = [
        "@score_kyron//src/kyron:libkyron",
        "@score_kyron//src/kyron-foundation:libkyron_foundation",
        "@score_baselibs//src/log/score_log",
        "@score_baselibs//src/log/stdout_logger",
    ],
    proc_macro_deps = [
        "@score_kyron//src/kyron-macros:runtime_macros",
    ],
)

score_pkg_bundle(
    name = "kyron_logging_showcase",
    bins = [":kyron_logging"],
    config_data = [":kyron_logging.score.json"],
    package_dir = "kyron_logging",
)
