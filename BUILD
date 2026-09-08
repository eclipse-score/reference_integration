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
load("//bazel_common:docs_bundles.bzl", "DOCS_BUNDLES")

# Alias causing doc build here being independet of what doc-as-code do.
# This allows to changge labels of real doc build indepedent of pull_request_target
# helping being more flexible on releases
alias(
    name = "docs_shim",
    actual = "//:docs",
)

# Docs-as-code
#
# The bundle mounts are generated from known_good.json into
# //bazel_common:docs_bundles.bzl: every module is mounted under its group's section
# (target_sw -> modules/, tooling -> process_methods_tools/) unless it sets
# '"docs": false' there. Change the module list in known_good.json, not here, and
# regenerate with scripts/known_good/update_module_from_known_good.py.
docs(
    bundles = DOCS_BUNDLES,
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
