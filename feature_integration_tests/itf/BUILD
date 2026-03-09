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
load("@score_itf//score/itf/plugins:plugins.bzl", "dlt", "docker", "qemu")

filegroup(
    name = "all_tests",
    srcs = [
        "test_showcases.py",
        "test_ssh.py",
    ],
)

py_itf_test(
    name = "linux_x86_64",
    srcs = [
        ":all_tests",
    ],
    args = [
        "--dlt-config=$(location //feature_integration_tests/configs:dlt_config_x86_64.json)",
        "--docker-image-bootstrap=$(location //images/linux_x86_64:image_tarball)",
        "--docker-image=score_showcases:latest",
    ],
    data = [
        "//feature_integration_tests/configs:dlt_config_x86_64.json",
        "//images/linux_x86_64:image_tarball",
    ],
    plugins = [
        dlt,
        docker,
    ],
    tags = [
        "manual",
    ],
)

py_itf_test(
    name = "qnx_x86_64",
    srcs = [
        ":all_tests",
    ],
    args = [
        "--dlt-config=$(location //feature_integration_tests/configs:dlt_config_qnx_x86_64.json)",
        "--qemu-config=$(location //feature_integration_tests/configs:qemu_bridge_config.json)",
        "--qemu-image=$(location //images/qnx_x86_64:image)",
    ],
    data = [
        "//feature_integration_tests/configs:dlt_config_qnx_x86_64.json",
        "//feature_integration_tests/configs:qemu_bridge_config.json",
        "//images/qnx_x86_64:image",
    ],
    plugins = [
        dlt,
        qemu,
    ],
    tags = [
        "manual",
    ],
)
