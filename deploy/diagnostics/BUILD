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

load("@rules_pkg//pkg:mappings.bzl", "pkg_filegroup")
load("@rules_shell//shell:sh_test.bzl", "sh_test")

package(default_visibility = ["//deploy:__pkg__"])

# OpenSOVD gateway (SOVD server of the platform; with SOVD_UPSTREAM_URL it forwards what it does
# not hold to the CDA) and the Classic Diagnostic Adapter, placed under /usr/bin/diagnostics.
pkg_filegroup(
    name = "diagnostics_bin",
    srcs = [
        "@score_diagnostics//score/opensovd-cda:cda_files",
        "@score_diagnostics//score/opensovd-core:gateway_files",
    ],
    prefix = "usr/bin/diagnostics",
)

# The OpenSOVD library reports its own pinned revision and reproducible date.
sh_test(
    name = "gateway_stamp_test",
    srcs = ["gateway_stamp_test.sh"],
    args = [
        "$(location @score_diagnostics//score/opensovd-core:opensovd-gateway)",
        "$(location //:MODULE.bazel)",
    ],
    data = [
        "//:MODULE.bazel",
        "@score_diagnostics//score/opensovd-core:opensovd-gateway",
    ],
)
