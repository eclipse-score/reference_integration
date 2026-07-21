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

# Grouped per suite so future additions don't mix into one undifferentiated
# list; all_tests below is the union of these groups plus shared utilities.
filegroup(
    name = "communication_tests",
    srcs = [
        "comm_helpers.py",
        "test_communication.py",
    ],
)

filegroup(
    name = "all_tests",
    srcs = [
        "test_properties.py",
        "test_remote_logging.py",
        "test_showcases.py",
        "test_ssh.py",
        ":communication_tests",
    ],
)

py_itf_test(
    name = "itf",
    srcs = [
        ":all_tests",
    ],
    # @add_test_properties(...) (feature_integration_tests/itf/test_properties.py)
    # writes PartiallyVerifies/FullyVerifies properties into the JUnit XML
    # report, matching the convention already used by
    # feature_integration_tests/test_cases (persistency FIT). The
    # score_itf//score/itf/plugins:attribute_plugin entry below (not a raw
    # score_tooling dep) activates the plugin and injects the required
    # "-p attribute_plugin" pytest arg automatically.
    args = select(
        {
            ":config_linux_x86_64": [
                "--dlt-config=$(location //feature_integration_tests/configs:dlt_config_x86_64.json)",
                "--docker-image-bootstrap=$(location //images/linux_x86_64:image_load)",
                "--docker-image=score_showcases:latest",
            ],
            ":config_qnx_x86_64": [
                "--dlt-config=$(location //feature_integration_tests/configs:dlt_config_qnx_x86_64.json)",
                "--qemu-config=$(location //feature_integration_tests/configs:qemu_bridge_config.json)",
                "--qemu-image=$(location //images/qnx_x86_64:image)",
            ],
        },
        no_match_error = "Unsupported platform",
    ),
    data = select({
        ":config_linux_x86_64": [
            "//feature_integration_tests/configs:dlt_config_x86_64.json",
            "//images/linux_x86_64:image_load",
        ],
        ":config_qnx_x86_64": [
            "//feature_integration_tests/configs:dlt_config_qnx_x86_64.json",
            "//feature_integration_tests/configs:qemu_bridge_config.json",
            "//images/qnx_x86_64:image",
        ],
    }) + ["conftest.py"],
    plugins = select(
        {
            ":config_linux_x86_64": [
                "@score_itf//score/itf/plugins:dlt_plugin",
                "@score_itf//score/itf/plugins:docker_plugin",
            ],
            ":config_qnx_x86_64": [
                "@score_itf//score/itf/plugins:dlt_plugin",
                "@score_itf//score/itf/plugins:qemu_plugin",
            ],
        },
        no_match_error = "Unsupported platform",
    ) + [
        "@score_itf//score/itf/plugins:attribute_plugin",
    ],
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
