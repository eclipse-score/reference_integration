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

load("@rules_cc//cc:defs.bzl", "cc_binary")

cc_binary(
    name = "cpp_test_scenarios",
    srcs = glob([
        "src/**/*.cpp",
        "src/**/*.h",
    ]),
    includes = ["src/internals/persistency"],
    tags = ["manual"],
    visibility = ["//visibility:public"],
    deps = [
        "@score_baselibs//score/json",
        "@score_baselibs//score/mw/log:console_only_backend",
        "@score_persistency//:kvs_cpp",
        "@score_test_scenarios//test_scenarios_cpp",
    ],
)
