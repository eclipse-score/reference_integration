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

# Generated from known_good.json at 2026-02-10T21:12:42+00:00Z
# Do not edit manually - use scripts/known_good/update_module_from_known_good.py

load("@score_tooling//:defs.bzl", "rust_coverage_report")



rust_coverage_report(
    name = "rust_coverage_score_baselibs_rust",
    bazel_configs = [
        "linux-x86_64",
        "ferrocene-coverage",
    ],
    query = 'kind("rust_test", @score_baselibs_rust//src/...) -@score_baselibs_rust//src/log/score_log_fmt_macro:tests',
    visibility = ["//visibility:public"],
)
            

rust_coverage_report(
    name = "rust_coverage_score_communication",
    bazel_configs = [
        "linux-x86_64",
        "ferrocene-coverage",
    ],
    query = 'kind("rust_test", @score_communication//score/mw/com/impl/...) -@score_communication//score/mw/com/impl:unit_test_runtime_single_exec -@score_communication//score/mw/com/impl/configuration:config_parser_test -@score_communication//score/mw/com/impl/configuration:configuration_test -@score_communication//score/mw/com/impl/tracing/configuration:tracing_filter_config_parser_test',
    visibility = ["//visibility:public"],
)
            

rust_coverage_report(
    name = "rust_coverage_score_persistency",
    bazel_configs = [
        "linux-x86_64",
        "ferrocene-coverage",
    ],
    query = 'kind("rust_test", @score_persistency//src/...) -@score_persistency//src/cpp/tests:bm_kvs_cpp',
    visibility = ["//visibility:public"],
)
            

rust_coverage_report(
    name = "rust_coverage_score_orchestrator",
    bazel_configs = [
        "linux-x86_64",
        "ferrocene-coverage",
    ],
    query = 'kind("rust_test", @score_orchestrator//src/...)',
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
    query = 'kind("rust_test", @score_lifecycle_health//src/...)',
    visibility = ["//visibility:public"],
)
            

rust_coverage_report(
    name = "rust_coverage_score_logging",
    bazel_configs = [
        "linux-x86_64",
        "ferrocene-coverage",
    ],
    query = 'kind("rust_test", @score_logging//score/...) -@score_logging//score/datarouter/test/ut/ut_logging:dltprotocolUT -@score_logging//score/datarouter/test/ut/ut_logging:persistentLogConfigUT -@score_logging//score/datarouter/test/ut/ut_logging:socketserverConfigUT -@score_logging//score/datarouter/test/ut/ut_logging:socketserverUT -@score_logging//score/mw/log/legacy_non_verbose_api:unit_test',
    visibility = ["//visibility:public"],
)
            