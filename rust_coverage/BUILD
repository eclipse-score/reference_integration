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

# Generated from known_good.json at 2026-08-21T00:00:00+00:00Z
# Do not edit manually - use scripts/known_good/update_module_from_known_good.py --known known_good.json --output-dir-modules bazel_common

load("@score_tooling//:defs.bzl", "rust_coverage_report")

rust_coverage_report(
    name = "rust_coverage_score_communication",
    bazel_configs = [
        "linux-x86_64",
        "ferrocene-coverage",
    ],
    query = 'kind("rust_test", @score_communication//...)',
    visibility = ["//visibility:public"],
)

rust_coverage_report(
    name = "rust_coverage_score_persistency",
    bazel_configs = [
        "linux-x86_64",
        "ferrocene-coverage-per",
    ],
    query = 'kind("rust_test", @score_persistency//src/...) -@score_persistency//src/cpp/tests:bm_kvs_cpp',
    visibility = ["//visibility:public"],
)

rust_coverage_report(
    name = "rust_coverage_score_kyron",
    bazel_configs = [
        "linux-x86_64",
        "ferrocene-coverage",
    ],
    query = 'kind("rust_test", @score_kyron//src/...)',
    visibility = ["//visibility:public"],
)

rust_coverage_report(
    name = "rust_coverage_score_lifecycle_health",
    bazel_configs = [
        "linux-x86_64",
        "ferrocene-coverage",
    ],
    query = 'kind("rust_test", @score_lifecycle_health//score/...) -@score_lifecycle_health//score/health_monitor/src/rust:miri_tests -@score_lifecycle_health//score/launch_manager/src/daemon/src/common/concurrency:mpmc_concurrent_queue_tsan_test',
    visibility = ["//visibility:public"],
)

rust_coverage_report(
    name = "rust_coverage_score_logging",
    bazel_configs = [
        "linux-x86_64",
        "ferrocene-coverage",
    ],
    query = 'kind("rust_test", @score_logging//...)',
    visibility = ["//visibility:public"],
)
