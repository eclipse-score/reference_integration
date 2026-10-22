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

# Deployment of the S-CORE lifecycle module (layer 2, see //deploy:README.md).
#
# Only the launch manager daemon is deployed here. The applications it
# supervises, and the launch manager configuration that declares them, are
# payload of whoever uses the platform - for this repository that is the
# lifecycle showcase in //showcases/simple_lifecycle.

load("@rules_pkg//pkg:mappings.bzl", "pkg_attributes", "pkg_files", "strip_prefix")

package(default_visibility = ["//deploy:__pkg__"])

# Launch manager binary (0777), placed as /usr/bin/launch_manager.
pkg_files(
    name = "launch_manager_bin",
    srcs = ["@score_lifecycle//score/launch_manager"],
    attributes = pkg_attributes(mode = "0777"),
    prefix = "usr/bin",
    strip_prefix = strip_prefix.files_only(),
)
