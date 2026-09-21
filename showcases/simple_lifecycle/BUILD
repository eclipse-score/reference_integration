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
load("@rules_pkg//pkg:mappings.bzl", "pkg_attributes", "pkg_files")
load("@score_lifecycle//:defs.bzl", "launch_manager_config")
load("//bazel_common:bundlers.bzl", "score_pkg_bundle")

launch_manager_config(
    name = "lifecycle_configs",
    config = "//showcases/simple_lifecycle/configs:launch_manager_config.json",
    flatbuffer_out_dir = "etc",
)

# launch_manager itself runs with the package's data dir as its cwd (see
# simple_lifecycle.score.json's "dir"), but ProcessGroupManager chdirs each
# supervised component into "bin_dir" before exec'ing it, and mw::com resolves
# "./etc/mw_com_config.json" relative to that cwd. So the config needs to be
# staged next to the binaries (bin/etc/), not just under data/simple_lifecycle/
# like the other custom_layout entries below -- otherwise every component that
# uses mw::com (e.g. control_daemon, the state_manager component) fails mw::com
# initialization on launch and gets stuck in launch_manager's restart loop.
pkg_files(
    name = "simple_lifecycle_bin_mw_com_config_pkg",
    srcs = ["//showcases/simple_lifecycle/configs:mw_com_config.json"],
    attributes = pkg_attributes(mode = "0444"),
    prefix = "bin/etc",
)

score_pkg_bundle(
    name = "simple_lifecycle",
    bins = [
        "@score_lifecycle//score/launch_manager:launch_manager",
        "@score_lifecycle//examples/cpp_supervised_app",
        "@score_lifecycle//examples/rust_supervised_app",
        "@score_lifecycle//examples/control_application:control_daemon",
        ":lifecycle_signal.sh",
    ],
    config_data = [
        "//showcases/simple_lifecycle:simple_lifecycle.score.json",
    ],
    custom_layout = {
        ":lifecycle_configs": "etc/",
        "//showcases/simple_lifecycle/configs:logging.json": "etc/logging.json",
        "//showcases/simple_lifecycle/configs:mw_com_config.json": "etc/mw_com_config.json",
    },
    other_package_files = [":simple_lifecycle_bin_mw_com_config_pkg"],
)
