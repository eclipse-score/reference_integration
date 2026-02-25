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
load("@score_itf//score/itf/plugins:plugins.bzl", "dlt", "qemu")

alias(
    name = "image",
    actual = "//images/qnx_x86_64/build:init",
    visibility = ["//visibility:public"],
)

sh_binary(
    name = "run",
    srcs = ["//runners/qemu_x86_64/scripts:run_qemu.sh"],
    args = [
        "$(location @toolchains_qnx_sdp//:host_dir)",
        "$(location :image)",
    ],
    data = [
        ":image",
        "@toolchains_qnx_sdp//:host_all",
        "@toolchains_qnx_sdp//:host_dir",
    ],
)

# For now we keep this not in /feature_integration_tests but locally within images

py_itf_test(
    name = "test_qnx_8_x86_64",
    srcs = [
        "//feature_integration_tests/itf:all_tests",
    ],
    args = [
        "--qemu-config=$(location //feature_integration_tests/configs:qemu_bridge_config.json)",
        "--qemu-image=$(location :image)",
    ],
    data = [
        ":image",
        "//feature_integration_tests/configs:qemu_bridge_config.json",
    ],
    plugins = [
        qemu,
    ],
    tags = [
        "local",
        "manual",
    ],
)
