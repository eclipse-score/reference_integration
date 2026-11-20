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
    ],
)
