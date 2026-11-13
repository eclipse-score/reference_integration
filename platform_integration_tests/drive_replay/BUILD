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

py_itf_test(
    name = "drive_replay",
    srcs = ["test_drive_replay.py"],
    args = select({
        "//platform_integration_tests:config_linux_x86_64": [
            "--dlt-config=$(location //feature_integration_tests/configs:dlt_config_x86_64.json)",
            "--docker-image-bootstrap=$(location //images/linux_x86_64:image_load)",
            "--docker-image=score_showcases:latest",
        ],
        "//conditions:default": [],
    }),
    data = select({
        "//platform_integration_tests:config_linux_x86_64": [
            "//feature_integration_tests/configs:dlt_config_x86_64.json",
            "//images/linux_x86_64:image_load",
        ],
        "//conditions:default": [],
    }) + ["conftest.py"],
    plugins = select({
        "//platform_integration_tests:config_linux_x86_64": [
            "@score_itf//score/itf/plugins:dlt_plugin",
            "@score_itf//score/itf/plugins:docker_plugin",
        ],
        "//conditions:default": [],
    }) + [
        "@score_itf//score/itf/plugins:attribute_plugin",
    ],
    tags = [
        "manual",
    ],
    target_compatible_with = select({
        "//platform_integration_tests:config_linux_x86_64": [],
        "//conditions:default": ["@platforms//:incompatible"],
    }),
    deps = [
        "//platform_integration_tests:showcase_runner",
    ],
)
