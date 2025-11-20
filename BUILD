# *******************************************************************************
# Copyright (c) 2025 Contributors to the Eclipse Foundation
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

load("@score_docs_as_code//:docs.bzl", "docs")

docs(
    data = [
        "@score_platform//:needs_json",
        #"@score_persistency//:needs_json",  # cannot be included, as it does not contain any needs?
        #"@score_orchestrator//:needs_json",  # some issue about score_toolchains_qnx?
        #"@score_communication//:needs_json",  # no docs yet?
        "@score_feo//:needs_json",
        "@score_docs_as_code//:needs_json",
        "@score_process//:needs_json",
    ],
    source_dir = "docs",
)

# Simple filegroup target to demonstrate the build system works
filegroup(
    name = "readme",
    srcs = ["README.md"],
    visibility = ["//visibility:public"],
)
