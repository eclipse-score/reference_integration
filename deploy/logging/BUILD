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

# Deployment of the S-CORE logging module (layer 2, see //deploy:README.md).

load("@rules_pkg//pkg:mappings.bzl", "pkg_attributes", "pkg_files", "strip_prefix")

package(default_visibility = ["//deploy:__pkg__"])

# Datarouter binary (0777), placed under /usr/bin/datarouter.
pkg_files(
    name = "datarouter_bin",
    srcs = ["@score_logging//score/datarouter"],
    attributes = pkg_attributes(mode = "0777"),
    prefix = "usr/bin/datarouter",
    strip_prefix = strip_prefix.files_only(),
)

# Datarouter configuration files (0644), placed under /usr/bin/datarouter/etc.
pkg_files(
    name = "datarouter_configs",
    srcs = [
        "etc/log-channels.json",
        "etc/logging.json",
    ],
    attributes = pkg_attributes(mode = "0644"),
    prefix = "usr/bin/datarouter/etc",
    strip_prefix = strip_prefix.files_only(),
)
