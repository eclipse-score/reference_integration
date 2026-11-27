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
load("@rules_python//python:defs.bzl", "py_library")
load("@score_itf//:defs.bzl", "py_itf_test")
load("@score_tooling//python_basics:defs.bzl", "score_py_pytest")

py_library(
    name = "diagnostics_orchestration",
    srcs = ["diagnostics_orchestration.py"],
    imports = ["."],
    deps = ["//platform_integration_tests:showcase_runner"],
)

score_py_pytest(
    name = "diagnostics_orchestration_test",
    size = "small",
    srcs = ["test_diagnostics_orchestration.py"],
    pytest_config = "//:pyproject.toml",
    deps = [":diagnostics_orchestration"],
)

py_itf_test(
    name = "diagnostics",
    size = "large",
    srcs = ["test_diagnostics_showcase.py"],
    args = select({
        "//platform_integration_tests:config_linux_x86_64": [
            "--docker-image-bootstrap=$(location //images/linux_x86_64:image_load)",
            "--docker-image=score_showcases:latest",
        ],
        "//platform_integration_tests:config_qnx_x86_64": [
            "--qemu-config=$(location //feature_integration_tests/configs:qemu_bridge_config.json)",
            "--qemu-image=$(location //images/qnx_x86_64:image)",
        ],
    }),
    data = select({
        "//platform_integration_tests:config_linux_x86_64": [
            "//images/linux_x86_64:image_load",
        ],
        "//platform_integration_tests:config_qnx_x86_64": [
            "//feature_integration_tests/configs:qemu_bridge_config.json",
            "//images/qnx_x86_64:image",
        ],
    }),
    plugins = select({
        "//platform_integration_tests:config_linux_x86_64": [
            "@score_itf//score/itf/plugins:docker_plugin",
        ],
        "//platform_integration_tests:config_qnx_x86_64": [
            "@score_itf//score/itf/plugins:qemu_plugin",
        ],
    }) + [
        "@score_itf//score/itf/plugins:attribute_plugin",
    ],
    tags = [
        "manual",
    ],
    deps = [
        ":diagnostics_orchestration",
        "//platform_integration_tests:showcase_runner",
    ],
)
