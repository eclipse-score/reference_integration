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

# Configs + unique binary only; shared lifecycle bins (launch_manager, control_daemon,
# lifecycle_signal.sh) are provided once by simple_lifecycle_pkg_files in showcases_bundle.
pkg_files(
    name = "lifecycle_kyron_data_pkg_files",
    srcs = [
        ":lifecycle_kyron_configs",
        "//showcases/combined/lifecycle_kyron:lifecycle_kyron.score.json",
        "//showcases/combined/lifecycle_kyron/configs:logging.json",
        "@score_kyron//examples:safety_task",
    ],
    attributes = pkg_attributes(mode = "0755"),
    renames = {
        "@score_kyron//examples:safety_task": "bin/safety_task",
        "//showcases/combined/lifecycle_kyron:lifecycle_kyron.score.json": "configs/lifecycle_kyron.score.json",
        ":lifecycle_kyron_configs": "data/lifecycle_kyron/etc/",
        "//showcases/combined/lifecycle_kyron/configs:logging.json": "data/lifecycle_kyron/etc/logging.json",
    },
    visibility = ["//showcases:__pkg__"],
)

launch_manager_config(
    name = "lifecycle_kyron_configs",
    config = "//showcases/combined/lifecycle_kyron/configs:launch_manager_config.json",
    flatbuffer_out_dir = "etc",
)

score_pkg_bundle(
    name = "lifecycle_kyron",
    bins = [
        "@score_lifecycle//score/launch_manager:launch_manager",
        "@score_lifecycle//examples/control_application:control_daemon",
        "@score_kyron//examples:safety_task",
        "//showcases/simple_lifecycle:lifecycle_signal.sh",
    ],
    config_data = [
        "//showcases/combined/lifecycle_kyron:lifecycle_kyron.score.json",
    ],
    custom_layout = {
        ":lifecycle_kyron_configs": "etc/",
        "//showcases/combined/lifecycle_kyron/configs:logging.json": "etc/logging.json",
    },
    package_dir = "lifecycle_kyron",
)
