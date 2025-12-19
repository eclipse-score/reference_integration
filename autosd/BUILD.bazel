# *******************************************************************************
# Copyright (c) 2024 Contributors to the Eclipse Foundation
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
load("@rules_rpm//rpm:defs.bzl", "rpm_package")

rpm_package(
    name = "lola-demo",
    binaries = [
        "@score_communication//score/mw/com/example/ipc_bridge:ipc_bridge_cpp",
    ],
    config_dir = "/etc/lola",
    data = [
        "@score_communication//score/mw/com/example/ipc_bridge:etc/mw_com_config.json",
    ],
    data_dir = "/usr/share/lola/examples",
    description = "LOLA middleware communication libraries for development including core communication, configuration components, and example client/server binaries for testing",
    libraries = [
        "@score_communication//score/mw/com:com",
        "@score_communication//score/mw/com:config_schema",
    ],
    summary = "LOLA Demo",
    version = "1.0.0",
)
