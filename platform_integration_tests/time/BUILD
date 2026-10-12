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
    name = "time",
    srcs = ["test_vehicle_time_showcase.py"],
    args = select(
        {
            "//platform_integration_tests:config_linux_x86_64": [
                "--docker-image-bootstrap=$(location //images/linux_x86_64:image_load)",
                "--docker-image=score_showcases:latest",
            ],
            "//platform_integration_tests:config_qnx_x86_64": [
                "--qemu-config=$(location //feature_integration_tests/configs:qemu_bridge_config.json)",
                "--qemu-image=$(location //images/qnx_x86_64:image)",
            ],
        },
        no_match_error = "Unsupported platform",
    ),
    data = select({
        "//platform_integration_tests:config_linux_x86_64": [
            "//images/linux_x86_64:image_load",
        ],
        "//platform_integration_tests:config_qnx_x86_64": [
            "//feature_integration_tests/configs:qemu_bridge_config.json",
            "//images/qnx_x86_64:image",
        ],
    }),
    plugins = select(
        {
            "//platform_integration_tests:config_linux_x86_64": [
                "@score_itf//score/itf/plugins:docker_plugin",
            ],
            "//platform_integration_tests:config_qnx_x86_64": [
                "@score_itf//score/itf/plugins:qemu_plugin",
            ],
        },
        no_match_error = "Unsupported platform",
    ) + [
        # Records PartiallyVerifies (via the `@add_test_properties` decorator)
        # into the JUnit XML. docs-as-code's source code linker turns those
        # properties into `testlink` attributes on the referenced stakeholder
        # requirement needs.
        "@score_itf//score/itf/plugins:attribute_plugin",
    ],
    tags = [
        "manual",
    ],
    deps = [
        "//platform_integration_tests:showcase_runner",
    ],
)
