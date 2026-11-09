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

# Architecture-independent application packaging shared by the per-image targets.
#
# These pkg_files reference external module binaries/configs that Bazel resolves
# per platform (not per architecture), so a single definition works for every
# image. Consumers:
#   - QNX images (qnx_x86_64, qnx_aarch64): reference these directly in qnx_ifs srcs.
#   - Linux image (linux_x86_64): wraps them in a pkg_tar for oci_image.
# autosd/ebclfsa images do not ship these applications.

load("@rules_pkg//pkg:mappings.bzl", "pkg_attributes", "pkg_files", "strip_prefix")

# Datarouter binary (0777), placed under /usr/bin/datarouter.
pkg_files(
    name = "datarouter_bin",
    srcs = ["@score_logging//score/datarouter"],
    attributes = pkg_attributes(mode = "0777"),
    prefix = "usr/bin/datarouter",
    strip_prefix = strip_prefix.files_only(),
    visibility = ["//visibility:public"],
)

# Datarouter configuration files (0644), placed under /usr/bin/datarouter/etc.
pkg_files(
    name = "datarouter_configs",
    srcs = [
        "//feature_integration_tests/configs/datarouter:etc/log-channels.json",
        "//feature_integration_tests/configs/datarouter:etc/logging.json",
    ],
    attributes = pkg_attributes(mode = "0644"),
    prefix = "usr/bin/datarouter/etc",
    strip_prefix = strip_prefix.files_only(),
    visibility = ["//visibility:public"],
)

# Communication framework configuration in /etc (0777).
pkg_files(
    name = "etc_comm_configs",
    srcs = [
        "//feature_integration_tests/configs:etc/logging.json",
        "//feature_integration_tests/configs:etc/mw_com_config.json",
    ],
    attributes = pkg_attributes(mode = "0777"),
    prefix = "etc",
    strip_prefix = strip_prefix.files_only(),
    visibility = ["//visibility:public"],
)

# Persistency C++ test scenarios binary, placed as /cpp_tests_persistency (0777).
pkg_files(
    name = "cpp_tests_persistency_bin",
    srcs = ["@score_persistency//score/kvs/tests/test_scenarios/cpp:test_scenarios"],
    attributes = pkg_attributes(mode = "0777"),
    renames = {"@score_persistency//score/kvs/tests/test_scenarios/cpp:test_scenarios": "cpp_tests_persistency"},
    visibility = ["//visibility:public"],
)
