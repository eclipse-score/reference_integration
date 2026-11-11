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

# Platform info service (layer 2, see //deploy:README.md): a platform service of
# its own, not part of any S-CORE module. It reports the S-CORE version the
# platform was built from over mw::com; consumers in layer 3 find it via service
# discovery and compare the version with the one they were built for.

load("@rules_cc//cc:defs.bzl", "cc_binary", "cc_library", "cc_test")
load("@rules_pkg//pkg:mappings.bzl", "pkg_attributes", "pkg_files", "strip_prefix")
load("@rules_python//python:defs.bzl", "py_binary")
load("@score_tooling//python_basics:defs.bzl", "score_py_pytest")

package(default_visibility = ["//deploy:__pkg__"])

py_binary(
    name = "gen_platform_info",
    srcs = ["gen_platform_info.py"],
)

# The S-CORE module versions the platform is built from, as compile-time constants.
genrule(
    name = "platform_info_data",
    srcs = ["//:known_good.json"],
    outs = ["platform_info_data.h"],
    cmd = "$(execpath :gen_platform_info) $(execpath //:known_good.json) $@",
    tools = [":gen_platform_info"],
)

score_py_pytest(
    name = "gen_platform_info_test",
    srcs = ["gen_platform_info_test.py"],
    pytest_config = "//:pyproject.toml",
    deps = [":gen_platform_info"],
)

# Service interface and version check: the layer 2/3 contract of the platform info service.
cc_library(
    name = "platform_info_interface",
    srcs = [
        "platform_info.cpp",
        ":platform_info_data",
    ],
    hdrs = ["platform_info.h"],
    visibility = ["//showcases:__subpackages__"],
    deps = [
        "@score_baselibs//score/hash/code/crc:crc_ieee",
        "@score_communication//score/mw/com",
    ],
)

cc_test(
    name = "platform_info_test",
    srcs = ["platform_info_test.cpp"],
    deps = [
        ":platform_info_interface",
        "@googletest//:gtest_main",
    ],
)

cc_binary(
    name = "platform_info_service",
    srcs = ["platform_info_service.cpp"],
    deps = [
        ":platform_info_interface",
        "@score_baselibs//score/string_manipulation/arguments",
        "@score_communication//score/mw/com",
        "@score_logging//score/mw/log",
    ],
)

# Platform info service binary (0755), placed as /usr/bin/platform_info/platform_info_service.
pkg_files(
    name = "platform_info_service_bin",
    srcs = [":platform_info_service"],
    attributes = pkg_attributes(mode = "0755"),
    prefix = "usr/bin/platform_info",
    strip_prefix = strip_prefix.files_only(),
)

# mw::com configuration of the platform info service (0644), placed under
# /usr/bin/platform_info/etc. Consumers use this deployed file, so a platform
# that deploys a different service definition fails the check.
pkg_files(
    name = "platform_info_service_configs",
    srcs = [
        "etc/logging.json",
        "etc/mw_com_config.json",
    ],
    attributes = pkg_attributes(mode = "0644"),
    prefix = "usr/bin/platform_info/etc",
    strip_prefix = strip_prefix.files_only(),
)
