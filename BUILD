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
load("@rules_rust//rust:defs.bzl", "rust_clippy")

docs(
    data = [
        "@score_platform//:needs_json",
        "@score_process//:needs_json",
        # Persistency cannot be included, as it does not contain any needs.
        # -> sphinx-needs bug?
        # "@score_persistency//:needs_json",
    ],
    source_dir = "docs",
)

# Simple filegroup target to demonstrate the build system works
filegroup(
    name = "readme",
    srcs = ["README.md"],
    visibility = ["//visibility:public"],
)

rust_clippy(
    name = "clippy",
    testonly = True,
    tags = ["manual"],
    visibility = ["//visibility:public"],
    deps = [
        "//feature_integration_tests/rust_test_scenarios:rust_test_scenarios",
#        "//feature_showcase/rust:kyron_example",
        "//feature_showcase/rust:orch_per_example",
    ],
)
