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
        "@score_baselibs//score/...",
        "@score_lifecycle//score/...",
        "@score_persistency//score/kvs/...",
        # Same exclusions as the module tests in known_good.json (no toolchain on linux-x86_64).
        "-@score_lifecycle//score/health_monitor/src/rust:miri_tests",
        "-@score_lifecycle//score/health_monitor/src/rust:loom_tests",
        # Needs the dev-only dependency google_benchmark of lifecycle.
        "-@score_lifecycle//score/launch_manager/src/daemon/src/common/concurrency:mpmc_concurrent_queue_benchmark",
        "-@score_persistency//score/kvs/tests/test_scenarios/...",
        "-@score_persistency//score/kvs/tests/test_cases/...",
    ],
)
