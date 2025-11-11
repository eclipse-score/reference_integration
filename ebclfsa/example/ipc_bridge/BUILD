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
load("@score_baselibs//score/language/safecpp:toolchain_features.bzl", "COMPILER_WARNING_FEATURES")

cc_binary(
    name = "ipc_bridge_cpp",
    srcs = [
        "assert_handler.cpp",
        "assert_handler.h",
        "main.cpp",
    ],
    data = ["etc/mw_com_config.json"],
    features = COMPILER_WARNING_FEATURES,
    deps = [
        ":sample_sender_receiver",
        "@score_communication//score/mw/com",
        "@score_baselibs//score/mw/log",
        "@score_baselibs//score/language/futurecpp",
        "@boost.program_options",
    ],
    visibility = [
        "//visibility:public", # platform_only
    ],
)

cc_library(
    name = "sample_sender_receiver",
    srcs = [
        "sample_sender_receiver.cpp",
    ],
    hdrs = [
        "sample_sender_receiver.h",
    ],
    features = COMPILER_WARNING_FEATURES,
    deps = [
        ":datatype",
        "@score_communication//score/mw/com",
        "@score_baselibs//score/mw/log",
    ],
)

cc_library(
    name = "datatype",
    srcs = [
        "datatype.cpp",
    ],
    hdrs = [
        "datatype.h",
    ],
    features = COMPILER_WARNING_FEATURES,
    deps = [
        "@score_communication//score/mw/com",
        "@score_baselibs//score/language/futurecpp",
    ],
)
