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
    name = "lifecycle_kyron_configs",
    config = "//showcases/combined/lifecycle_kyron/configs:launch_manager_config.json",
    flatbuffer_out_dir = "etc",
)

score_pkg_bundle(
    name = "lifecycle_kyron",
    bins = [],
    config_data = [
        "//showcases/combined/lifecycle_kyron:lifecycle_kyron.score.json",
    ],
    custom_layout = {
        ":lifecycle_kyron_configs": "etc/",
        "//showcases/combined/lifecycle_kyron/configs:logging.json": "etc/logging.json",
    },
    package_dir = "lifecycle_kyron",
)
