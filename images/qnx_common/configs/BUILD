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

# Architecture-independent QNX image configuration files shared by the per-arch
# qnx_ifs targets (//images/qnx_x86_64/build, //images/qnx_aarch64/build).
# Only files that are byte-identical across architectures live here; arch-specific
# bits (x86 PCI configs, the x86 startup-hw.sh hardware fragment) stay in the
# respective images/<arch>/configs packages.

load("@rules_pkg//pkg:mappings.bzl", "pkg_attributes", "pkg_files", "strip_prefix")

# Executable startup/network scripts in /etc (0700).
pkg_files(
    name = "etc_scripts",
    srcs = [
        "network_setup.sh",
        "network_setup_dhcp.sh",
        "startup.sh",
    ],
    attributes = pkg_attributes(mode = "0700"),
    prefix = "etc",
    strip_prefix = strip_prefix.files_only(),
    visibility = ["//visibility:public"],
)

# Network capture helper, placed as /etc/network_capture (0755, .sh dropped).
pkg_files(
    name = "etc_network_capture",
    srcs = ["network_capture.sh"],
    attributes = pkg_attributes(mode = "0755"),
    renames = {"network_capture.sh": "etc/network_capture"},
    visibility = ["//visibility:public"],
)

# Crypto configuration file in /proc/boot (0444).
#
# Kept in /proc/boot (the boot IFS) to match the pre-migration bare-name mkifs
# entry, so libqcrypto finds it via its default boot search path.
pkg_files(
    name = "qcrypto_config",
    srcs = ["qcrypto.conf"],
    attributes = pkg_attributes(mode = "0444"),
    prefix = "proc/boot",
    strip_prefix = strip_prefix.files_only(),
    visibility = ["//visibility:public"],
)

# Plain /etc configuration files (0644).
pkg_files(
    name = "etc_configs",
    srcs = [
        "dhcpcd.conf",
        "group",
        "hostname",
        "passwd",
        "profile",
    ],
    attributes = pkg_attributes(mode = "0644"),
    prefix = "etc",
    strip_prefix = strip_prefix.files_only(),
    visibility = ["//visibility:public"],
)

# SSH daemon configuration in /var/ssh (0444).
pkg_files(
    name = "var_ssh_config",
    srcs = ["sshd_config"],
    attributes = pkg_attributes(mode = "0444"),
    prefix = "var/ssh",
    strip_prefix = strip_prefix.files_only(),
    visibility = ["//visibility:public"],
)

# SSH host keys in /var/ssh (0400, root-owned).
pkg_files(
    name = "var_ssh_keys",
    srcs = [
        "ssh_host_rsa_key",
        "ssh_host_rsa_key.pub",
    ],
    attributes = pkg_attributes(
        gid = 0,
        mode = "0400",
        uid = 0,
    ),
    prefix = "var/ssh",
    strip_prefix = strip_prefix.files_only(),
    visibility = ["//visibility:public"],
)
