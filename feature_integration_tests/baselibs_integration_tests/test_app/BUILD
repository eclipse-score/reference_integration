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

# On-target test app exercising one baselibs feature library per subcommand. It
# is bundled into //images/linux_x86_64:image (see that package's BUILD) and
# driven by the baselibs integration tests in the parent package.
cc_binary(
    name = "baselibs_test_app",
    srcs = ["main.cpp"],
    tags = ["manual"],
    visibility = ["//visibility:public"],
    deps = [
        "@score_baselibs//score/bitmanipulation",
        "@score_baselibs//score/containers:dynamic_array",
        "@score_baselibs//score/hash/code/crc:crc_ieee",
        "@score_baselibs//score/json",
        "@score_baselibs//score/language/futurecpp",
        "@score_baselibs//score/result",
        "@score_baselibs//score/utils:base64",
    ],
)
