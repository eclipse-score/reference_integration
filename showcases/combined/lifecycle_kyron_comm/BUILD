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
load("@rules_pkg//pkg:mappings.bzl", "pkg_attributes", "pkg_files")
load("@score_lifecycle//:defs.bzl", "launch_manager_config")
load("//bazel_common:bundlers.bzl", "score_pkg_bundle")

# No unique bins: safety_task and com-api-example are provided by lifecycle_kyron_data_pkg_files
# and lifecycle_comm_data_pkg_files respectively when composing showcases_bundle.
pkg_files(
    name = "lifecycle_kyron_comm_data_pkg_files",
    srcs = [
        ":lifecycle_kyron_comm_configs",
        "//showcases/combined/lifecycle_kyron_comm:lifecycle_kyron_comm.score.json",
        "//showcases/combined/lifecycle_kyron_comm/configs:logging.json",
        "@score_communication//score/mw/com/example/com-api-example:etc/mw_com_config.json",
    ],
    attributes = pkg_attributes(mode = "0755"),
    renames = {
        "@score_communication//score/mw/com/example/com-api-example:etc/mw_com_config.json": "data/lifecycle_kyron_comm/etc/mw_com_config.json",
        "//showcases/combined/lifecycle_kyron_comm:lifecycle_kyron_comm.score.json": "configs/lifecycle_kyron_comm.score.json",
        ":lifecycle_kyron_comm_configs": "data/lifecycle_kyron_comm/etc/",
        "//showcases/combined/lifecycle_kyron_comm/configs:logging.json": "data/lifecycle_kyron_comm/etc/logging.json",
    },
    visibility = ["//showcases:__pkg__"],
)

launch_manager_config(
    name = "lifecycle_kyron_comm_configs",
    config = "//showcases/combined/lifecycle_kyron_comm/configs:launch_manager_config.json",
    flatbuffer_out_dir = "etc",
)

score_pkg_bundle(
    name = "lifecycle_kyron_comm",
    bins = [
        "@score_lifecycle//score/launch_manager:launch_manager",
        "@score_lifecycle//examples/control_application:control_daemon",
        "@score_kyron//examples:safety_task",
        "@score_communication//score/mw/com/example/com-api-example:com-api-example",
        "//showcases/simple_lifecycle:lifecycle_signal.sh",
    ],
    config_data = [
        "//showcases/combined/lifecycle_kyron_comm:lifecycle_kyron_comm.score.json",
    ],
    custom_layout = {
        ":lifecycle_kyron_comm_configs": "etc/",
        "//showcases/combined/lifecycle_kyron_comm/configs:logging.json": "etc/logging.json",
        "@score_communication//score/mw/com/example/com-api-example:etc/mw_com_config.json": "etc/mw_com_config.json",
    },
    package_dir = "lifecycle_kyron_comm",
)
