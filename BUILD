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
        {"bundle": "@score_persistency//:docs_bundle", "mount_at": "_collections/score_persistency", "attach_to": "sw_components"},
        {"bundle": "@score_orchestrator//:docs_bundle", "mount_at": "_collections/score_orchestrator", "attach_to": "sw_components"},
        {"bundle": "@score_kyron//:docs_bundle", "mount_at": "_collections/score_kyron", "attach_to": "sw_components"},
        {"bundle": "@score_baselibs//:docs_bundle", "mount_at": "_collections/score_baselibs", "attach_to": "sw_components"},
        # score_logging's docs reference a PlantUML file outside the bundle root
        # (score/mw/log/design/backend/mw_log_recorders.puml), which sphinx-mounts
        # rejects as a bundle confinement violation. Excluded until fixed upstream.
        {"bundle": "@score_platform//:docs_bundle", "mount_at": "_collections/score_platform", "attach_to": "process_methods_tools"},
        {"bundle": "@score_process_description//:docs_bundle", "mount_at": "_collections/score_process_description", "attach_to": "process_methods_tools"},
        # score_docs_as_code's own docs reference test-fixture files outside its
        # bundle root (src/tests/docs_bzl/...), which sphinx-mounts rejects as a
        # bundle confinement violation. Excluded until fixed upstream.
    ],
    data = [
        # Software components
        # score_persistency, score_orchestrator, score_kyron, score_baselibs are
        # included via `bundles` above (full docs, incl. their needs); listing
        # their needs_json here too would define the same need IDs twice.
        # "@score_communication//:needs_json",  # no docs_sources
        # "@score_lifecycle//:needs_json",  # unreadable images - relative paths issue
        # "@score_logging//:needs_json",  # unreadable images - relative paths issue (mw_log_recorders.puml)
        # Tools: score_platform, score_process_description are included via
        # `bundles` above too; see note above.
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

# Add target for formatting checks
use_format_targets()

exports_files([
    "MODULE.bazel",
    "pyproject.toml",
    "known_good.json",
])
