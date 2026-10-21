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

# Shared offline overlay tooling for ext4 rootfs injection via debugfs.
# Used by image targets that cannot use loop mounts (no CAP_SYS_ADMIN in CI).
#
# The inject_overlay.py script takes a source image, partition number,
# overlay tar, and output path. It extracts the root partition, injects
# the tar contents via debugfs -w, and writes the modified partition back.

load("@rules_python//python:defs.bzl", "py_binary")

py_binary(
    name = "inject_overlay",
    srcs = ["inject_overlay.py"],
    deps = ["@rules_python//python/runfiles"],
    visibility = ["//visibility:public"],
)
