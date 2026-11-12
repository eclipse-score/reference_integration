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
load("@score_lifecycle//:defs.bzl", "launch_manager_config")
load("//bazel_common:bundlers.bzl", "score_pkg_bundle")

launch_manager_config(
    name = "lifecycle_time_comm_configs",
    config = "//showcases/combined/lifecycle_time_comm/configs:launch_manager_config.json",
    flatbuffer_out_dir = "etc",
)

score_pkg_bundle(
    name = "lifecycle_time_comm",
    bins = [],
    config_data = [
        "//showcases/combined/lifecycle_time_comm:lifecycle_time_comm.score.json",
    ],
    custom_layout = {
        ":lifecycle_time_comm_configs": "etc/",
        "//showcases/combined/lifecycle_time_comm/configs:logging.json": "etc/logging.json",
        "@score_communication//score/mw/com/example/com-api-example:etc/mw_com_config.json": "etc/mw_com_config.json",
    },
    package_dir = "lifecycle_time_comm",
)
