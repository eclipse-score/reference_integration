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
load("@rules_cc//cc:cc_library.bzl", "cc_library")
load("@score_lifecycle_health//:defs.bzl", "launch_manager_config")
load("//bazel_common:bundlers.bzl", "score_pkg_bundle")

launch_manager_config(
    name = "lifecycle_configs",
    config = "//showcases/simple_lifecycle/configs:launch_manager_config.json",
)

score_pkg_bundle(
    name = "simple_lifecycle",
    bins = [
        "@score_lifecycle_health//src/launch_manager_daemon:launch_manager",
        "@score_lifecycle_health//examples/cpp_supervised_app",
        "@score_lifecycle_health//examples/rust_supervised_app",
        "@score_lifecycle_health//examples/control_application:control_daemon",
        ":lifecycle_signal.sh",
    ],
    config_data = [
        "//showcases/simple_lifecycle:simple_lifecycle.score.json",
    ],
    custom_layout = {
        ":lifecycle_configs": "etc/",
    },
)
