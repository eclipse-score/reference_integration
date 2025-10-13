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

# load("@score_docs_as_code//:docs.bzl", "docs")

# docs(
#     data = [
#         # TODO: add all modules that have docs
#     ],
#     source_dir = "docs",
# )

# Simple filegroup target to demonstrate the build system works
filegroup(
    name = "readme",
    srcs = ["README.md"],
    visibility = ["//visibility:public"],
)

# Try to build feo rust components using local cargo
load("@rules_rust//rust:defs.bzl", "rust_library")

# This might work if we can access the feo source directly
# rust_library(
#     name = "feo_integration_test", 
#     srcs = ["@feo//feo:src/lib.rs"],
#     deps = ["@cargo//:tracing"],
# )
