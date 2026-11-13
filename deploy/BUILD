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

load("@rules_pkg//pkg:mappings.bzl", "pkg_filegroup", "pkg_mkdirs")
load("@rules_pkg//pkg:tar.bzl", "pkg_tar")

exports_files(["README.md"])

# The S-CORE platform as deployed by this distribution: every binary and
# configuration file that an S-CORE module contributes to the shipped image.
# This is the system under test for the conformance showcases; it must stay
# free of anything that only exists to demonstrate or test the platform.
#
# Consumed by the QNX images via qnx_ifs srcs.
pkg_filegroup(
    name = "platform_bundle",
    srcs = [
        "//deploy/config_management:config_daemon_bin",
        "//deploy/config_management:config_daemon_configs",
        "//deploy/lifecycle:launch_manager_bin",
        "//deploy/logging:datarouter_bin",
        "//deploy/logging:datarouter_configs",
        "//deploy/platform_info:platform_info_service_bin",
        "//deploy/platform_info:platform_info_service_configs",
    ],
    visibility = ["//visibility:public"],
)

# Writable persistent-storage directory; on QNX this is provided by a RAM disk
# symlink in the IFS image (common_init.build); on Linux it must be created.
pkg_mkdirs(
    name = "data_dir",
    dirs = ["data"],
)

# Same content as :platform_bundle, as a tar for oci_image consumers.
pkg_tar(
    name = "platform_tar",
    srcs = [
        ":data_dir",
        ":platform_bundle",
    ],
    visibility = ["//visibility:public"],
)
