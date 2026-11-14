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

load("@rules_pkg//pkg:mappings.bzl", "pkg_filegroup")
load("@score_lifecycle//:defs.bzl", "launch_manager_config")
load("//bazel_common:bundlers.bzl", "score_pkg_bundle")

# The launch manager starts the CDA and the gateway, like it starts the daemons of the platform run.
launch_manager_config(
    name = "diagnostics_lm_config",
    config = "launch_manager_config.json",
    flatbuffer_out_dir = "etc",
)

# Showcase for the OpenSOVD gateway and the classic diagnostic adapter (CDA) that the platform
# deploys in /usr/bin/diagnostics. The ECU databases are test data (the databases of the CDA's ECU
# simulator), so they are part of the showcases and not of the platform.
score_pkg_bundle(
    name = "diagnostics",
    bins = [],
    config_data = [":diagnostics.score.json"],
    custom_layout = {
        ":check.sh": "check.sh",
        ":service.sh": "service.sh",
        ":opensovd-cda.toml": "opensovd-cda.toml",
        ":diagnostics_lm_config": "etc/",
        # The launch manager offers its control service over mw::com and needs this config to start.
        "@score_lifecycle//score/launch_manager:example_com_config": "etc/mw_com_config.json",
    },
    package_dir = "diagnostics",
)

# The configuration of the CDA: the paths and the address of this showcase, followed by the settings
# that the ECUs of the CDA's ECU simulator need (some of them only work with it). The CDA listens on
# the loopback address only: its clients use the gateway.
genrule(
    name = "cda_config",
    srcs = [
        ":cda-paths.toml",
        "@score_diagnostics//score/opensovd-cda:cda-ecu-sim.toml",
    ],
    outs = ["opensovd-cda.toml"],
    cmd = "cat $(SRCS) > $@",
)

pkg_filegroup(
    name = "diagnostics_databases",
    srcs = ["@score_diagnostics//score/opensovd-cda:cda_test_databases_files"],
    prefix = "data/diagnostics/databases",
    visibility = ["//visibility:public"],
)
