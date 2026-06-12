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

load("//bazel_common:bundlers.bzl", "score_pkg_bundle")

cc_binary(
    name = "logging_example",
    srcs = ["main.cpp"],
    visibility = ["//visibility:public"],
    deps = [
        "@score_logging//score/mw/log:log",
        "@score_logging//score/mw/log/backend:remote",
    ],
)

score_pkg_bundle(
    name = "logging",
    bins = [
        ":logging_example",
    ],
      config_data = [
        "logging.score.json",

    ],

    custom_layout = {
        "//showcases/logging:config/logging.json": "etc/logging.json",
    },
    
)

