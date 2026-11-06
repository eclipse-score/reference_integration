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
    name = "platform_run_lm_config",
    config = "launch_manager_config.json",
    flatbuffer_out_dir = "etc",
)

# Only the launch manager configuration lives here: the daemons come from
# //deploy and the test applications from the other showcase bundles.
score_pkg_bundle(
    name = "platform_run",
    bins = [],
    config_data = [
        "//showcases/platform_run:platform_run.score.json",
    ],
    custom_layout = {
        ":platform_run_lm_config": "etc/",
        "//showcases/platform_run:logging.json": "etc/logging.json",
        "//showcases/platform_run:logging_com_api_example.json": "etc/logging_com_api_example.json",
        "//showcases/platform_run:logging_platform_info_consumer.json": "etc/logging_platform_info_consumer.json",
        "//showcases/platform_run:logging_platform_info_service.json": "etc/logging_platform_info_service.json",
    },
)
