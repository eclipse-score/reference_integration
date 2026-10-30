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

# Deployment of the S-CORE communication module (layer 2, see //deploy:README.md).
#
# Communication itself ships as a library. To make "the platform provides
# working inter-process communication" checkable, the platform deploys a
# heartbeat service on top of it; consumers in layer 3 must find it via
# mw::com service discovery and receive intact heartbeats from it.

load("@rules_cc//cc:defs.bzl", "cc_binary", "cc_library")
load("@rules_pkg//pkg:mappings.bzl", "pkg_attributes", "pkg_files", "strip_prefix")
load("@rules_python//python:defs.bzl", "py_binary")

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

# Service interface and payload check: the layer 2/3 contract of the heartbeat service.
cc_library(
    name = "heartbeat_interface",
    srcs = [
        "heartbeat.cpp",
        ":platform_info_data",
    ],
    hdrs = ["heartbeat.h"],
    visibility = ["//showcases:__subpackages__"],
    deps = [
        "@score_baselibs//score/hash/code/crc:crc_ieee",
        "@score_communication//score/mw/com",
    ],
)

cc_binary(
    name = "heartbeat_service",
    srcs = ["heartbeat_service.cpp"],
    deps = [
        ":heartbeat_interface",
        "@score_baselibs//score/string_manipulation/arguments",
        "@score_communication//score/mw/com",
    ],
)

# Heartbeat service binary (0777), placed as /usr/bin/communication/heartbeat_service.
pkg_files(
    name = "heartbeat_service_bin",
    srcs = [":heartbeat_service"],
    attributes = pkg_attributes(mode = "0777"),
    prefix = "usr/bin/communication",
    strip_prefix = strip_prefix.files_only(),
)

# mw::com configuration of the heartbeat service (0644), placed under
# /usr/bin/communication/etc. Consumers use this deployed file, so a platform
# that deploys a different service definition fails the check.
pkg_files(
    name = "heartbeat_service_configs",
    srcs = ["etc/mw_com_config.json"],
    attributes = pkg_attributes(mode = "0644"),
    prefix = "usr/bin/communication/etc",
    strip_prefix = strip_prefix.files_only(),
)
