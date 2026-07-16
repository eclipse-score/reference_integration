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
load("@score_lifecycle_health//:defs.bzl", "launch_manager_config")

exports_files(
    [
        "dlt_config_qnx_x86_64.json",
        "dlt_config_x86_64.json",
        "qemu_bridge_config.json",
        "lifecycle_daemon_config.json",
    ],
)

exports_files([
    "etc/logging.json",
    "etc/mw_com_config.json",
])

filegroup(
    name = "etc_configs",
    srcs = [
        "etc/logging.json",
        "etc/mw_com_config.json",
    ],
    visibility = ["//visibility:public"],
)

launch_manager_config(
    name = "lifecycle_daemon_config",
    config = ":lifecycle_daemon_config.json",
    flatbuffer_out_dir = "etc",
    visibility = ["//visibility:public"],
)
