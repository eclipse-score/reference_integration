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

load("@score_toolchains_qnx//rules/fs:ifs.bzl", "qnx_ifs")

filegroup(
    name = "scripts",
    srcs = [
        "//configs:startup.sh",
    ],
    visibility = ["//visibility:private"],
)

filegroup(
    name = "configs",
    srcs = [
        "//configs:pci_server.cfg",
        "//configs:pci_hw.cfg",
        "//configs:qcrypto.conf",
        "//configs:passwd",
        "//configs:group",
        "//configs:sshd_config",
        "//configs:ssh_host_rsa_key",
        "//configs:ssh_host_rsa_key.pub",
        "//configs:hostname",
        "//configs:network_setup.sh",
        "//configs:network_capture.sh",
        "//configs:profile",
        "//configs:dhcpcd.conf",
        "//configs:network_setup_dhcp.sh",
    ],
    visibility = ["//visibility:private"],
)

qnx_ifs(
    name = "init",
    build_file = "init.build",
    srcs = [
        "system.build",
        ":scripts",
        ":configs",
        "@score_scrample//src:scrample",
        "//scrample_integration:etc_configs",
        "//datarouter_integration:etc_configs",
        "@score_persistency//tests/cpp_test_scenarios:cpp_test_scenarios",
        "@score_logging//score/datarouter:datarouter",
    ],
    ext_repo_maping = {
        "SCRAMPLE_PATH": "$(location @score_scrample//src:scrample)",
        "CPP_TEST_SCENARIOS_PATH": "$(location @score_persistency//tests/cpp_test_scenarios:cpp_test_scenarios)",
        "DATAROUTER_PATH": "$(location @score_logging//score/datarouter:datarouter)",
    },
    visibility = [
        "//:__pkg__"
    ],
)
