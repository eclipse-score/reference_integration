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

config_setting(
    name = "config_linux_x86_64",
    constraint_values = [
        "@platforms//os:linux",
        "@platforms//cpu:x86_64",
        "@score_bazel_platforms//runtime_es:posix",
    ],
)

config_setting(
    name = "config_qnx_x86_64",
    constraint_values = [
        "@platforms//os:qnx",
        "@platforms//cpu:x86_64",
        "@score_bazel_platforms//runtime_es:posix",
    ],
)

filegroup(
    name = "all_tests",
    srcs = [
        "test_showcases.py",
        "test_ssh.py",
    ],
)

py_itf_test(
    name = "itf",
    srcs = [
        ":all_tests",
    ],
    args = select(
        {
            ":config_linux_x86_64": [
                "--docker-image-bootstrap=$(location //images/linux_x86_64:image_load)",
                "--docker-image=score_showcases:latest",
            ],
            ":config_qnx_x86_64": [
                "--qemu-config=$(location //feature_integration_tests/configs:qemu_bridge_config.json)",
                "--qemu-image=$(location //images/qnx_x86_64:image)",
            ],
        },
        no_match_error = "Unsupported platform",
    ),
    data = select({
        ":config_linux_x86_64": [
            "//images/linux_x86_64:image_load",
        ],
        ":config_qnx_x86_64": [
            "//feature_integration_tests/configs:qemu_bridge_config.json",
            "//images/qnx_x86_64:image",
        ],
    }),
    plugins = select(
        {
            ":config_linux_x86_64": [
                "@score_itf//score/itf/plugins:docker_plugin",
            ],
            ":config_qnx_x86_64": [
                "@score_itf//score/itf/plugins:qemu_plugin",
            ],
        },
        no_match_error = "Unsupported platform",
    ),
    tags = [
        "manual",
    ],
)

# Backward compatible aliases for CI jobs - these should be removed once the CI jobs are updated to use the new target names
test_suite(
    name = "linux_x86_64",
    tags = [
        "manual",
    ],
    tests = [":itf"],
)

test_suite(
    name = "qnx_x86_64",
    tags = [
        "manual",
    ],
    tests = [":itf"],
)
