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

load("@score_rules_imagefs//rules/qnx:ifs.bzl", "qnx_ifs")

# The architecture-independent configuration files are shared via
# //images/qnx_common/configs; the application packaging (datarouter
# binary/configs, communication configs, persistency test binary) via
# //images/common/apps. The aarch64 QEMU virt image has no arch-specific
# configuration files of its own.

qnx_ifs(
    name = "init",
    srcs = [
        "//images/common/apps:cpp_tests_persistency_bin",
        "//images/common/apps:datarouter_bin",
        "//images/common/apps:datarouter_configs",
        "//images/common/apps:etc_comm_configs",
        "//images/qnx_common/configs:etc_configs",
        "//images/qnx_common/configs:etc_network_capture",
        "//images/qnx_common/configs:etc_scripts",
        "//images/qnx_common/configs:qcrypto_config",
        "//images/qnx_common/configs:var_ssh_config",
        "//images/qnx_common/configs:var_ssh_keys",
        "//showcases:showcases_bundle",
    ],
    build_file = "init.build",
    extra_build_files = [
        "//images/qnx_common/build:common_init.build",
        "//images/qnx_common/build:common_system.build",
    ],
    visibility = [
        "//visibility:public",
    ],
)
