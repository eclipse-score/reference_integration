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

pkg_files(
    name = "lifecycle_time_data_pkg_files",
    srcs = [
        ":lifecycle_time_configs",
        "//showcases/combined/lifecycle_time:lifecycle_time.score.json",
        "//showcases/combined/lifecycle_time/configs:logging.json",
        "@score_time//examples/time/vehicle_time",
    ],
    attributes = pkg_attributes(mode = "0755"),
    renames = {
        "@score_time//examples/time/vehicle_time": "bin/vehicle_time",
        "//showcases/combined/lifecycle_time:lifecycle_time.score.json": "configs/lifecycle_time.score.json",
        ":lifecycle_time_configs": "data/lifecycle_time/etc/",
        "//showcases/combined/lifecycle_time/configs:logging.json": "data/lifecycle_time/etc/logging.json",
    },
    visibility = ["//showcases:__pkg__"],
)

launch_manager_config(
    name = "lifecycle_time_configs",
    config = "//showcases/combined/lifecycle_time/configs:launch_manager_config.json",
    flatbuffer_out_dir = "etc",
)

score_pkg_bundle(
    name = "lifecycle_time",
    bins = [
        "@score_lifecycle//score/launch_manager:launch_manager",
        "@score_lifecycle//examples/control_application:control_daemon",
        "@score_time//examples/time/vehicle_time",
        "//showcases/simple_lifecycle:lifecycle_signal.sh",
    ],
    config_data = [
        "//showcases/combined/lifecycle_time:lifecycle_time.score.json",
    ],
    custom_layout = {
        ":lifecycle_time_configs": "etc/",
        "//showcases/combined/lifecycle_time/configs:logging.json": "etc/logging.json",
    },
    package_dir = "lifecycle_time",
)
