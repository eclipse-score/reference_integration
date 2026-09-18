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

load("@rules_pkg//pkg:mappings.bzl", "REMOVE_BASE_DIRECTORY", "pkg_attributes", "pkg_files")
load("@score_rules_imagefs//rules/qnx:ifs.bzl", "qnx_ifs")

# score_rules_imagefs derives the mkifs placement directives from these
# rules_pkg targets, so the destination path, permissions and owner of every
# Bazel-provided file are declared here instead of in system.build.

pkg_files(
    name = "etc_scripts",
    srcs = [
        "//images/qnx_x86_64/configs:network_setup.sh",
        "//images/qnx_x86_64/configs:network_setup_dhcp.sh",
        "//images/qnx_x86_64/configs:startup.sh",
    ],
    attributes = pkg_attributes(mode = "0700"),
    prefix = "etc",
    visibility = ["//visibility:private"],
)

pkg_files(
    name = "etc_network_capture",
    srcs = ["//images/qnx_x86_64/configs:network_capture.sh"],
    attributes = pkg_attributes(mode = "0755"),
    prefix = "etc",
    renames = {"//images/qnx_x86_64/configs:network_capture.sh": "network_capture"},
    visibility = ["//visibility:private"],
)

# mkifs resolves a bare filename against its default /proc/boot prefix, which is
# how these were written before; the prefix is explicit now because
# score_rules_imagefs always emits an absolute destination. startup.sh and
# pci_server.cfg reference these by their /proc/boot path.
pkg_files(
    name = "boot_configs",
    srcs = [
        "//images/qnx_x86_64/configs:pci_hw.cfg",
        "//images/qnx_x86_64/configs:pci_server.cfg",
        "//images/qnx_x86_64/configs:qcrypto.conf",
    ],
    attributes = pkg_attributes(mode = "0444"),
    prefix = "proc/boot",
    visibility = ["//visibility:private"],
)

# These four carried no attribute block before, which made mkifs inherit the
# host file mode. All four are 0644 in git; pin it.
pkg_files(
    name = "etc_identity",
    srcs = [
        "//images/qnx_x86_64/configs:group",
        "//images/qnx_x86_64/configs:hostname",
        "//images/qnx_x86_64/configs:passwd",
        "//images/qnx_x86_64/configs:profile",
    ],
    attributes = pkg_attributes(mode = "0644"),
    prefix = "etc",
    visibility = ["//visibility:private"],
)

pkg_files(
    name = "etc_dhcpcd",
    srcs = ["//images/qnx_x86_64/configs:dhcpcd.conf"],
    attributes = pkg_attributes(mode = "0644"),
    prefix = "etc",
    visibility = ["//visibility:private"],
)

pkg_files(
    name = "ssh_config",
    srcs = ["//images/qnx_x86_64/configs:sshd_config"],
    attributes = pkg_attributes(mode = "0444"),
    prefix = "var/ssh",
    visibility = ["//visibility:private"],
)

pkg_files(
    name = "ssh_host_keys",
    srcs = [
        "//images/qnx_x86_64/configs:ssh_host_rsa_key",
        "//images/qnx_x86_64/configs:ssh_host_rsa_key.pub",
    ],
    attributes = pkg_attributes(
        gid = 0,
        mode = "0400",
        uid = 0,
    ),
    prefix = "var/ssh",
    visibility = ["//visibility:private"],
)

pkg_files(
    name = "etc_comm_configs",
    srcs = ["//feature_integration_tests/configs:etc_configs"],
    attributes = pkg_attributes(mode = "0777"),
    prefix = "etc",
    visibility = ["//visibility:private"],
)

pkg_files(
    name = "datarouter",
    srcs = ["@score_logging//score/datarouter"],
    attributes = pkg_attributes(mode = "0777"),
    prefix = "usr/bin/datarouter",
    visibility = ["//visibility:private"],
)

pkg_files(
    name = "datarouter_configs",
    srcs = ["//feature_integration_tests/configs/datarouter:etc_configs"],
    attributes = pkg_attributes(mode = "0644"),
    prefix = "usr/bin/datarouter/etc",
    visibility = ["//visibility:private"],
)

# REMOVE_BASE_DIRECTORY drops the bundle's contents at the image root, which is
# what `[perms=777] / = ${BUNDLE_PATH}` did.
pkg_files(
    name = "showcases",
    srcs = ["//showcases"],
    attributes = pkg_attributes(mode = "0777"),
    renames = {"//showcases": REMOVE_BASE_DIRECTORY},
    visibility = ["//visibility:private"],
)

qnx_ifs(
    name = "init",
    srcs = [
        ":boot_configs",
        ":datarouter",
        ":datarouter_configs",
        ":etc_comm_configs",
        ":etc_dhcpcd",
        ":etc_identity",
        ":etc_network_capture",
        ":etc_scripts",
        ":showcases",
        ":ssh_config",
        ":ssh_host_keys",
    ],
    build_file = "init.build",
    extra_build_files = ["system.build"],
    visibility = [
        "//visibility:public",
    ],
)
