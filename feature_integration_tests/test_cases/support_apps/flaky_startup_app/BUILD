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
load("@rules_cc//cc:defs.bzl", "cc_binary")

# Plain "Native" supervised app (no launch_manager lifecycle API integration) used
# only to deterministically drive ready_recovery_action.restart in
# lifecycle_daemon_retries_config.json. See main.cpp for behavior.
cc_binary(
    name = "flaky_startup_app",
    srcs = ["main.cpp"],
    visibility = ["//feature_integration_tests:__subpackages__"],
    deps = [
        "@score_lifecycle_health//score/launch_manager:lifecycle_cc",
    ],
)
