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
load("@score_tooling//:defs.bzl", "copyright_checker", "setup_starpls", "use_format_targets")

# Docs-as-code
docs(
    data = [
        # Software components
        "@score_persistency//:needs_json",
        "@score_orchestrator//:needs_json",
        "@score_kyron//:needs_json",
        "@score_baselibs//:needs_json",
        "@score_baselibs_rust//:needs_json",
        # "@score_communication//:needs_json",  # no docs_sources
        # "@score_lifecycle_health//:needs_json",  # unreadable images - relative paths issue
        # "@score_logging//:needs_json",  # duplicated labels
        "@score_logging//:needs_json",
        # Tools
        "@score_platform//:needs_json",
        "@score_process//:needs_json",
        "@score_docs_as_code//:needs_json",
    ],
    source_dir = "docs",
)

# Bazel formatting
setup_starpls(
    name = "starpls_server",
    visibility = ["//visibility:public"],
)

# Copyright check
copyright_checker(
    name = "copyright",
    srcs = [
        ".github",
        "bazel_common",
        "docs",
        "feature_integration_tests",
        "images",
        "runners",
        "rust_coverage",
        "scripts",
        "showcases",
        "//:BUILD",
        "//:MODULE.bazel",
    ],
    config = "@score_tooling//cr_checker/resources:config",
    template = "@score_tooling//cr_checker/resources:templates",
    visibility = ["//visibility:public"],
)

# Add target for formatting checks
use_format_targets()

exports_files([
    "MODULE.bazel",
])
