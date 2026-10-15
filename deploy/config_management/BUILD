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

# Deployment of the S-CORE config management module (layer 2, see //deploy:README.md).

load("@rules_pkg//pkg:mappings.bzl", "pkg_attributes", "pkg_files", "strip_prefix")

package(default_visibility = ["//deploy:__pkg__"])

# Config daemon binary (0777), placed as /usr/bin/config_management/config_daemon.
pkg_files(
    name = "config_daemon_bin",
    srcs = ["@score_config_management//score/config_management/config_daemon/code:config_daemon"],
    attributes = pkg_attributes(mode = "0777"),
    prefix = "usr/bin/config_management",
    strip_prefix = strip_prefix.files_only(),
)

# Config daemon configuration (0644), placed under
# /usr/bin/config_management/etc. Both files are shipped by the upstream
# module, so they belong to the deployment and not to the showcase that
# drives the daemon.
pkg_files(
    name = "config_daemon_configs",
    srcs = [
        "@score_config_management//score/config_management/config_daemon/code/plugins/demo_json:demo_parameters",
        "@score_config_management//score/config_management/config_daemon/code/services/details/mw_com:mw_com_config",
    ],
    attributes = pkg_attributes(mode = "0644"),
    prefix = "usr/bin/config_management/etc",
    renames = {
        "@score_config_management//score/config_management/config_daemon/code/services/details/mw_com:mw_com_config": "mw_com_config.json",
        "@score_config_management//score/config_management/config_daemon/code/plugins/demo_json:demo_parameters": "demo_parameters.json",
    },
)
