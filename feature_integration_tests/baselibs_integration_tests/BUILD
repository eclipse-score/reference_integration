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

package(default_visibility = ["//feature_integration_tests/baselibs_integration_tests:__subpackages__"])

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

py_library(
    name = "demo_runner",
    srcs = ["demo_runner.py"],
    # Lets the test `import demo_runner` as a flat top-level module.
    imports = ["."],
)

py_itf_test(
    name = "bit",
    srcs = ["test_baselibs_features.py"],
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
    ) + [
        # Records PartiallyVerifies (via the `@add_test_properties` decorator)
        # into the JUnit XML. docs-as-code's source code linker turns those
        # properties into `testlink` attributes on the referenced baselibs
        # feature requirement needs.
        "@score_itf//score/itf/plugins:attribute_plugin",
    ],
    tags = [
        "manual",
    ],
    deps = [
        ":demo_runner",
    ],
)
