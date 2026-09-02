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
load("@score_tooling//:defs.bzl", "setup_starpls")
load("@score_tooling//third_party/format:macros.bzl", "use_format_targets")

# Docs-as-code
docs(
    bundles = [
        # Software components
        # "@score_communication//:needs_json",  # no docs_sources
        {
            "bundle": "@score_lifecycle//:docs_bundle",
            "mount_at": "sw_components/score_lifecycle",
        },
        {
            "bundle": "@score_logging//:docs_bundle",
            "mount_at": "sw_components/score_logging",
        },
        {
            "bundle": "@score_persistency//:docs_bundle",
            "mount_at": "sw_components/score_persistency",
        },
        {
            "bundle": "@score_orchestrator//:docs_bundle",
            "mount_at": "sw_components/score_orchestrator",
        },
        {
            "bundle": "@score_kyron//:docs_bundle",
            "mount_at": "sw_components/score_kyron",
        },
        {
            "bundle": "@score_baselibs//:docs_bundle",
            "mount_at": "sw_components/score_baselibs",
        },

        # Process methods and tools (PMT)
        {
            "bundle": "@score_platform//:docs_bundle",
            "mount_at": "process_methods_tools/score_platform",
        },
        {
            "bundle": "@score_process_description//:docs_bundle",
            "mount_at": "process_methods_tools/score_process_description",
        },
        {
            "bundle": "@score_docs_as_code//:docs_bundle",
            "mount_at": "process_methods_tools/score_docs_as_code",
        },
    ],
    known_good = "known_good.json",
    source_dir = "docs",
)

# Bazel formatting
setup_starpls(
    name = "starpls_server",
    visibility = ["//visibility:public"],
)

# Add target for formatting checks
use_format_targets()

exports_files([
    "MODULE.bazel",
    "pyproject.toml",
    "known_good.json",
])
