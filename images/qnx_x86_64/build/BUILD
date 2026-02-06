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
        ":system.build",
        ":system_dir",
        ":scripts",
        ":configs",
        "//showcases:showcases_all",
        "//feature_integration_tests/configs:etc_configs",
        "@score_persistency//tests/test_scenarios/cpp:test_scenarios",        
    ],
    ext_repo_maping = {
        "BUNDLE_PATH": "$(location //showcases:showcases_all)"
    },
    visibility = [
        "//visibility:public",
    ],
)

filegroup(
    name = "system_dir",
    srcs = [
        "system.build",
        "init.build",
    ],
)

