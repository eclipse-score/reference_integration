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
load("@score_itf//:defs.bzl", "py_itf_test")

# QNX only (the Linux Docker target offers no SSH): skipped when the pit suite runs for Linux.
py_itf_test(
    name = "ssh",
    srcs = ["test_ssh.py"],
    args = select({
        "//platform_integration_tests:config_qnx_x86_64": [
            "--qemu-config=$(location //feature_integration_tests/configs:qemu_bridge_config.json)",
            "--qemu-image=$(location //images/qnx_x86_64:image)",
        ],
        "//conditions:default": [],
    }),
    data = select({
        "//platform_integration_tests:config_qnx_x86_64": [
            "//feature_integration_tests/configs:qemu_bridge_config.json",
            "//images/qnx_x86_64:image",
        ],
        "//conditions:default": [],
    }),
    plugins = select({
        "//platform_integration_tests:config_qnx_x86_64": [
            "@score_itf//score/itf/plugins:qemu_plugin",
        ],
        "//conditions:default": [],
    }),
    tags = [
        "manual",
    ],
    target_compatible_with = select({
        "//platform_integration_tests:config_qnx_x86_64": [],
        "//conditions:default": ["@platforms//:incompatible"],
    }),
)
