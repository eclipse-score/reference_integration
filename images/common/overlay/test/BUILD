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
# *******************************************************************************/

# Tests for the offline overlay injection tooling.
#
# Uses small synthetic MBR/p2 images to verify the injection logic
# without requiring a full OS image download.

load("@rules_pkg//pkg:pkg.bzl", "pkg_tar")
load("@rules_python//python:defs.bzl", "py_test")

# Create a small test tar with known content
pkg_tar(
    name = "test_overlay",
    srcs = ["test_file.txt"],
    package_dir = "/opt/test",
    visibility = ["//visibility:public"],
)

py_test(
    name = "inject_overlay_test",
    srcs = ["inject_overlay_test.py"],
    deps = [
        "//images/common/overlay:inject_overlay",
    ],
    data = [":test_overlay"],
    tags = ["requires-root-partition"],
    visibility = ["//visibility:public"],
)
