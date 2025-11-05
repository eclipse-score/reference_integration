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
load("@rules_shell//shell:sh_binary.bzl", "sh_binary")
load("@score_itf//:defs.bzl", "py_itf_test")


sh_binary(
    name = "run_qemu",
    srcs = ["scripts/run_qemu.sh"],
    args = [
        "$(location @toolchains_qnx_sdp//:host_dir)",
        "$(location //build:init)",
    ],
    data = [
        "//build:init",
        "@toolchains_qnx_sdp//:host_all",
        "@toolchains_qnx_sdp//:host_dir",
    ],
)

sh_binary(
    name = "run_qemu_portforward",
    srcs = ["scripts/run_qemu_portforward.sh"],
    args = [
        "$(location @toolchains_qnx_sdp//:host_dir)",
        "$(location //build:init)",
    ],
    data = [
        "//build:init",
        "@toolchains_qnx_sdp//:host_all",
        "@toolchains_qnx_sdp//:host_dir",
    ],
)


sh_binary(
    name = "test_qemu_bridge",
    srcs = ["test/test_qnx_qemu_bridge.sh"],
    args = [
        "$(location @toolchains_qnx_sdp//:host_dir)",
        "$(location //build:init)",
        "--timeout=90",
        "--ssh-port=2222",
        "--boot-wait=15",
    ],
    data = [
        "//build:init",
        "@toolchains_qnx_sdp//:host_all",
        "@toolchains_qnx_sdp//:host_dir",
    ],
)

sh_binary(
    name = "test_qemu_portforward",
    srcs = ["test/test_qnx_qemu_portforward.sh"],
    args = [
        "$(location @toolchains_qnx_sdp//:host_dir)",
        "$(location //build:init)",
        "--timeout=90",
        "--ssh-port=2222",
        "--boot-wait=15",
    ],
    data = [
        "//build:init",
        "@toolchains_qnx_sdp//:host_all",
        "@toolchains_qnx_sdp//:host_dir",
    ],
)

py_itf_test(
    name = "test_ssh_qemu",
    srcs = [
        "test/itf/test_ssh.py",
    ],
    args = [
        "--target_config=$(location target_config.json)",
        "--ecu=s_core_ecu_qemu",
        "--qemu_image=$(location //build:init)",
    ],
    plugins = [
        "itf.plugins.base.base_plugin",
    ],
    data = [
        "//build:init",
        "target_config.json",
    ],
)

py_itf_test(
    name = "test_scrample_qemu",
    srcs = [
        "test/itf/test_scrample.py",
    ],
    args = [
        "--target_config=$(location target_config.json)",
        "--ecu=s_core_ecu_qemu",
        "--qemu_image=$(location //build:init)",
    ],
    plugins = [
        "itf.plugins.base.base_plugin",
    ],
    data = [
        "//build:init",
        "target_config.json",
    ],
)
