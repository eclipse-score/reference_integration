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
# Communication ships as a library, so the only deployed artifacts are the
# system-wide configuration files every mw::com participant reads from /etc.

load("@rules_pkg//pkg:mappings.bzl", "pkg_attributes", "pkg_files", "strip_prefix")

package(default_visibility = ["//deploy:__pkg__"])

pkg_files(
    name = "etc_comm_configs",
    srcs = [
        "//feature_integration_tests/configs:etc/logging.json",
        "//feature_integration_tests/configs:etc/mw_com_config.json",
    ],
    attributes = pkg_attributes(mode = "0777"),
    prefix = "etc",
    strip_prefix = strip_prefix.files_only(),
)
