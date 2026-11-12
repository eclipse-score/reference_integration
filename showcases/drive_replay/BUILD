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
load("@score_lifecycle//:defs.bzl", "launch_manager_config")
load("//bazel_common:bundlers.bzl", "score_pkg_bundle")

cc_library(
    name = "drive_data",
    hdrs = ["drive_data.h"],
    deps = ["@score_communication//score/mw/com"],
)

cc_library(
    name = "viz_link",
    srcs = ["viz_link.cpp"],
    hdrs = ["viz_link.h"],
)

cc_binary(
    name = "replay_app",
    srcs = ["replay_app.cpp"],
    deps = [
        ":drive_data",
        ":viz_link",
        "@score_baselibs//score/string_manipulation/arguments",
        "@score_communication//score/mw/com",
        "@score_lifecycle//score/launch_manager:lifecycle_cc",
        "@score_logging//score/mw/log",
    ],
)

cc_binary(
    name = "warn_app",
    srcs = ["warn_app.cpp"],
    deps = [
        ":drive_data",
        ":viz_link",
        "@score_baselibs//score/string_manipulation/arguments",
        "@score_communication//score/mw/com",
        "@score_lifecycle//score/health_monitor:health_monitoring_cc",
        "@score_lifecycle//score/launch_manager:lifecycle_cc",
        "@score_logging//score/mw/log",
        "@score_persistency//score/kvs",
    ],
)

cc_binary(
    name = "drive_state_manager",
    srcs = ["drive_state_manager.cpp"],
    deps = [
        ":viz_link",
        "@score_baselibs//score/string_manipulation/arguments",
        "@score_communication//score/mw/com",
        "@score_lifecycle//score/launch_manager:control_cc",
        "@score_lifecycle//score/launch_manager:lifecycle_cc",
        "@score_logging//score/mw/log",
    ],
)

launch_manager_config(
    name = "lifecycle_configs",
    config = "//showcases/drive_replay/configs:launch_manager_config.json",
    flatbuffer_out_dir = "etc",
)

score_pkg_bundle(
    name = "drive_replay",
    bins = [
        ":drive_state_manager",
        ":replay_app",
        ":warn_app",
    ],
    config_data = [
        "//showcases/drive_replay:drive_replay.score.json",
    ],
    custom_layout = {
        ":lifecycle_configs": "etc/",
        "//showcases/drive_replay/configs:logging.json": "etc/logging.json",
        "//showcases/drive_replay/configs:logging_fcw.json": "etc/logging_fcw.json",
        "//showcases/drive_replay/configs:logging_replay.json": "etc/logging_replay.json",
        "//showcases/drive_replay/configs:logging_sm.json": "etc/logging_sm.json",
        "//showcases/drive_replay/configs:mw_com_config.json": "etc/mw_com_config.json",
    },
)
