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
        # "@score_baselibs//:needs_json",  # score_tooling is dev_dependency
        "@score_baselibs_rust//:needs_json",
        # "@score_communication//:needs_json",  # no docs_sources
        # "@score_lifecycle_health//:needs_json",  # unreadable images - relative paths issue
        "@score_logging//:needs_json",  # duplicated labels
        # Tools
        "@score_platform//:needs_json",
        "@score_process//:needs_json",
        "@score_docs_as_code//:needs_json",
    ],
    known_good = "known_good.json",
    source_dir = "docs",
)

# Bazel formatting
setup_starpls(
    name = "starpls_server",
    visibility = ["//visibility:public"],
)

# Copyright check
#
# NOTE: CI enforces copyright headers via the pre-commit `copyright` hook
# (see //.pre-commit-config.yaml and .github/workflows/copyright.yml), not this
# Bazel target. `bazel run //:copyright.check` currently fails to analyze because
# its "docs" src pulls in the docs() -> needs_json graph, which references
# @score_process/@score_platform; those are dev_dependencies in the score modules
# and so are not visible when reference_integration aggregates them.
# Tracked in https://github.com/eclipse-score/reference_integration/issues/166.
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
    "pyproject.toml",
    "known_good.json",
])
