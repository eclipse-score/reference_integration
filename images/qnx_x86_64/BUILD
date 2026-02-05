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

alias(
    name = "image",
    actual = "//build:init",
    visibility = ["//visibility:public"],
)

# For now we keep this not in /feature_integration_tests but locally within images

py_itf_test(
    name = "test_ssh",
    srcs = [
        "//feature_integration_tests/itf:test_ssh.py",
    ],
    args = [
        "--target_config=$(location //feature_integration_tests/configs:qemu_target_config.json)",
        "--ecu=s_core_ecu_qemu",
        "--qemu_image=$(location :image)",
    ],
    plugins = [
        "itf.plugins.base.base_plugin",
    ],
    data = [
        ":image",
        "//feature_integration_tests/configs:qemu_target_config.json",
    ],
)

# py_itf_test(
#     name = "test_scrample",
#     srcs = [
#         "feature_integration_tests/itf/test_scrample.py",
#     ],
#     args = [
#         "--target_config=$(location feature_integration_tests/configs/qemu_target_config.json)",
#         "--ecu=s_core_ecu_qemu",
#         "--qemu_image=$(location :image)",
#     ],
#     plugins = [
#         "itf.plugins.base.base_plugin",
#     ],
#     data = [
#         ":image",
#         "target_config.json",
#     ],
# )

# py_itf_test(
#     name = "test_persistency",
#     srcs = [
#         "feature_integration_tests/itf/test_persistency.py",
#     ],
#     args = [
#         "--target_config=$(location target_config.json)",
#         "--ecu=s_core_ecu_qemu",
#         "--qemu_image=$(location :image)",
#     ],
#     plugins = [
#         "itf.plugins.base.base_plugin",
#     ],
#     data = [
#         ":image",
#         "target_config.json",
#     ],
# )
