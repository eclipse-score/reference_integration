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
load("@rules_pkg//pkg:mappings.bzl", "pkg_filegroup")
load("//bazel_common:bundlers.bzl", "score_pkg_bundle")

score_pkg_bundle(
    name = "showcases",
    bins = ["//showcases/cli"],
    other_package_files = [
        "//showcases/standalone:comm_pkg_files",
        "//showcases/standalone:kyron_pkg_files",
        "//showcases/standalone:time_pkg_files",
        "//showcases/standalone:logging_pkg_files",
        "//showcases/standalone:config_management_pkg_files",
        "//showcases/standalone:persistency_pkg_files",
        "//showcases/simple_lifecycle:simple_lifecycle_pkg_files",
        "//showcases/standalone:baselibs_pkg_files",
        "//showcases/platform_run:platform_run_pkg_files",
        "//showcases/standalone:platform_info_pkg_files",
        "//showcases/combined/lifecycle_comm:lifecycle_comm_pkg_files",
        "//showcases/combined/lifecycle_kyron:lifecycle_kyron_pkg_files",
        "//showcases/combined/lifecycle_time:lifecycle_time_pkg_files",
        "//showcases/combined/kyron_logging:kyron_logging_showcase_pkg_files",
        "//showcases/combined/lifecycle_time_comm:lifecycle_time_comm_pkg_files",
        "//showcases/combined/lifecycle_kyron_comm:lifecycle_kyron_comm_pkg_files",
    ],
    package_dir = "showcases",
)

pkg_filegroup(
    name = "showcases_bundle",
    srcs = [
        ":showcases_pkg_files",
        "//showcases/combined/kyron_logging:kyron_logging_showcase_pkg_files",
        "//showcases/combined/lifecycle_comm:lifecycle_comm_pkg_files",
        "//showcases/combined/lifecycle_kyron:lifecycle_kyron_pkg_files",
        "//showcases/combined/lifecycle_kyron_comm:lifecycle_kyron_comm_pkg_files",
        "//showcases/combined/lifecycle_time:lifecycle_time_pkg_files",
        "//showcases/combined/lifecycle_time_comm:lifecycle_time_comm_pkg_files",
        "//showcases/platform_run:platform_run_pkg_files",
        "//showcases/simple_lifecycle:simple_lifecycle_pkg_files",
        "//showcases/standalone:baselibs_pkg_files",
        "//showcases/standalone:comm_pkg_files",
        "//showcases/standalone:config_management_pkg_files",
        "//showcases/standalone:kyron_pkg_files",
        "//showcases/standalone:logging_pkg_files",
        "//showcases/standalone:persistency_pkg_files",
        "//showcases/standalone:platform_info_pkg_files",
        "//showcases/standalone:time_pkg_files",
    ],
    prefix = "showcases",
    visibility = ["//visibility:public"],
)
