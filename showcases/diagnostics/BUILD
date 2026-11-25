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
load("@rules_python//python:defs.bzl", "py_test")
load("@score_lifecycle//:defs.bzl", "launch_manager_config")
load("//bazel_common:bundlers.bzl", "score_pkg_bundle")

# The launch manager starts the CDA and the gateway, like it starts the daemons of the platform run.
# The Raspberry Pi images set the address of the gateway in it, see images/network.
exports_files(
    ["launch_manager_config.json"],
    visibility = ["//images/network:__pkg__"],
)

launch_manager_config(
    name = "diagnostics_lm_config",
    config = "launch_manager_config.json",
    flatbuffer_out_dir = "etc",
)

# Platform Run and other showcases use instance 1. Keep both ends of the
# diagnostics control service on instance 2 so the managers can share /tmp.
# Its application ID must also differ for LoLa's crash recovery bookkeeping.
genrule(
    name = "diagnostics_com_config",
    srcs = ["@score_lifecycle//score/launch_manager:example_com_config"],
    outs = ["mw_com_config.json"],
    cmd = " && ".join([
        "[ \"$$(grep -c '\"instanceId\": 1,' $(SRCS))\" = 2 ]",
        "[ \"$$(grep -c '\"applicationID\": 1000' $(SRCS))\" = 1 ]",
        "sed -e 's/\"instanceId\": 1,/\"instanceId\": 2,/g' -e 's/\"applicationID\": 1000/\"applicationID\": 1001/' $(SRCS) > $@",
    ]),
)

py_test(
    name = "diagnostics_com_config_test",
    srcs = ["diagnostics_com_config_test.py"],
    args = [
        "$(location @score_lifecycle//score/launch_manager:example_com_config)",
        "$(location :diagnostics_com_config)",
    ],
    data = [
        ":diagnostics_com_config",
        "@score_lifecycle//score/launch_manager:example_com_config",
    ],
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
        ":diagnostics_com_config": "etc/mw_com_config.json",
    },
    package_dir = "diagnostics",
)

# The configuration of the CDA: the paths and the address of this showcase, followed by the settings
# that the ECUs of the CDA's ECU simulator need (some of them only work with it). The CDA listens on
# a Unix domain socket only, /run/opensovd-cda.sock: its clients use the gateway.
genrule(
    name = "cda_config",
    srcs = [
        ":cda-config.toml",
        "@score_diagnostics//score/opensovd-cda:cda-ecu-sim.toml",
    ],
    outs = ["opensovd-cda.toml"],
    cmd = "cat $(SRCS) > $@",
    # The Raspberry Pi images set the DoIP tester address in it, see images/network.
    visibility = ["//images/network:__pkg__"],
)

pkg_filegroup(
    name = "diagnostics_databases",
    srcs = ["@score_diagnostics//score/opensovd-cda:cda_test_databases_files"],
    prefix = "data/diagnostics/databases",
    visibility = ["//visibility:public"],
)
