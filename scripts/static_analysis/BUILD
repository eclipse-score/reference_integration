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
load("@score_tools//codeql:defs.bzl", "codeql_sca")

# POC: CodeQL analysis of the integrated modules with the production toolchain.
# Run with SCORE_CODEQL_INCLUDE_GLOBS='**/external/score_*/**' (see patches/tools).
codeql_sca(
    name = "sca_linux",
    configs = ["linux-x86_64"],
    safety_level = "ASIL",
    targets = [
        # Positive patterns only: negative ones are not forwarded to the compile-commands aquery.
        # Left out: lifecycle health_monitor/src/rust (miri/loom tests without toolchain), the
        # concurrency benchmark (dev-only google_benchmark) and the persistency test scenarios.
        "@score_baselibs//score/...",
        "@score_lifecycle//score/health_monitor:all",
        "@score_lifecycle//score/health_monitor/src/cpp/...",
        "@score_lifecycle//score/launch_manager:all",
        "@score_lifecycle//score/launch_manager/src/alive/...",
        "@score_lifecycle//score/launch_manager/src/lifecycle_client/...",
        "@score_lifecycle//score/launch_manager/src/lm_control/...",
        "@score_lifecycle//score/launch_manager/src/daemon:all",
        "@score_lifecycle//score/launch_manager/src/daemon/src/alive_monitor/...",
        "@score_lifecycle//score/launch_manager/src/daemon/src/common:all",
        "@score_lifecycle//score/launch_manager/src/daemon/src/common/concurrency/details/...",
        "@score_lifecycle//score/launch_manager/src/daemon/src/configuration/...",
        "@score_lifecycle//score/launch_manager/src/daemon/src/control/...",
        "@score_lifecycle//score/launch_manager/src/daemon/src/osal/...",
        "@score_lifecycle//score/launch_manager/src/daemon/src/process_group_manager/...",
        "@score_lifecycle//score/launch_manager/src/daemon/src/recovery_client/...",
        "@score_lifecycle//score/launch_manager/src/daemon/src/watchdog/...",
        "@score_persistency//score/kvs:all",
    ],
)
