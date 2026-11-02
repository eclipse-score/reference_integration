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

load("@rules_pkg//pkg:mappings.bzl", "pkg_attributes", "pkg_files", "strip_prefix")
load("@score_rules_imagefs//rules/qnx:ifs.bzl", "qnx_ifs")

# x86_64-specific early hardware init fragment, sourced by the common
# /etc/startup.sh, placed as /etc/startup-hw.sh (0700).
pkg_files(
    name = "etc_startup_hw",
    srcs = ["//images/qnx_x86_64/configs:startup-hw.sh"],
    attributes = pkg_attributes(mode = "0700"),
    prefix = "etc",
    strip_prefix = strip_prefix.files_only(),
)

# x86_64 PCI configuration files in /proc/boot (0444).
#
# These must live in /proc/boot (the boot IFS) because pci-server and the
# pci_hw module read them during early boot, before the on-disk root
# filesystem is available. On the pre-migration image they were bare-name
# mkifs entries, which mkifs places under its default /proc/boot prefix;
# the "proc/boot" pkg_files prefix reproduces that exact layout.
pkg_files(
    name = "pci_configs",
    srcs = [
        "//images/qnx_x86_64/configs:pci_hw.cfg",
        "//images/qnx_x86_64/configs:pci_server.cfg",
    ],
    attributes = pkg_attributes(mode = "0444"),
    prefix = "proc/boot",
    strip_prefix = strip_prefix.files_only(),
)

# The architecture-independent configuration files are shared via
# //images/qnx_common/configs; the application packaging (datarouter
# binary/configs, communication configs, persistency test binary) via
# //images/common/apps.

qnx_ifs(
    name = "init",
    srcs = [
        ":etc_startup_hw",
        ":pci_configs",
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
        "system.build",
    ],
    visibility = [
        "//visibility:public",
    ],
)
