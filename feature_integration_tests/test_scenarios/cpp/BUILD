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

load("@rules_cc//cc:defs.bzl", "cc_binary", "cc_library")

cc_library(
    name = "kvs_parameters",
    hdrs = ["src/internals/persistency/kvs_parameters.h"],
    srcs = ["src/internals/persistency/kvs_parameters.cpp"],
    deps = [
        "@score_baselibs//score/json",
    ],
)

cc_library(
    name = "kvs_instance",
    hdrs = ["src/internals/persistency/kvs_instance.h"],
    srcs = ["src/internals/persistency/kvs_instance.cpp"],
    deps = [
        ":kvs_parameters",
        "@score_baselibs//score/mw/log:console_only_backend",
        "@score_persistency//:kvs_cpp",
    ],
)

cc_library(
    name = "scenarios_lib",
    srcs = [
        "src/scenarios/mod.cpp",
        "src/scenarios/persistency/multiple_kvs_per_app.cpp",
    ],
    deps = [
        ":kvs_instance",
        "@score_baselibs//score/json",
        "@score_test_scenarios//test_scenarios_cpp",
    ],
)

cc_binary(
    name = "cpp_test_scenarios",
    srcs = ["src/main.cpp"],
    tags = ["manual"],
    visibility = ["//feature_integration_tests/test_cases:__pkg__"],
    deps = [
        ":scenarios_lib",
        "@score_test_scenarios//test_scenarios_cpp",
    ],
)
