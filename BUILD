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

# ============================================================================
# SBOM Generation Targets
# ============================================================================
load("@score_tooling//sbom:defs.bzl", "sbom")

# SBOM for score_baselibs
sbom(
    name = "sbom_baselibs",
    targets = [
        "@score_baselibs//score/concurrency:concurrency",
        "@score_baselibs//score/memory/shared:shared",
    ],
    module_lockfiles = [
        "@score_crates//:MODULE.bazel.lock",
        ":MODULE.bazel.lock",
    ],
    component_name = "score_baselibs",
    auto_crates_cache = True,
    auto_cdxgen = True,
    sbom_authors = ["Eclipse SCORE Team"],
    generation_context = "build",
)

# SBOM for score_communication
sbom(
    name = "sbom_communication",
    targets = [
        "@score_communication//score/mw/com:com",
    ],
    module_lockfiles = [
        "@score_crates//:MODULE.bazel.lock",
        ":MODULE.bazel.lock",
    ],
    component_name = "score_communication",
    auto_crates_cache = True,
    auto_cdxgen = True,
    sbom_authors = ["Eclipse SCORE Team"],
    generation_context = "build",
)

# SBOM for score_persistency
sbom(
    name = "sbom_persistency",
    targets = [
        "@score_persistency//src/rust/rust_kvs:rust_kvs",
    ],
    module_lockfiles = [
        "@score_crates//:MODULE.bazel.lock",
        ":MODULE.bazel.lock",
    ],
    component_name = "score_persistency",
    auto_crates_cache = True,
    auto_cdxgen = True,
    sbom_authors = ["Eclipse SCORE Team"],
    generation_context = "build",
)

# SBOM for score_kyron
sbom(
    name = "sbom_kyron_module",
    targets = [
        "@score_kyron//src/kyron:libkyron",
        "@score_kyron//src/kyron-foundation:libkyron_foundation",
    ],
    module_lockfiles = [
        "@score_crates//:MODULE.bazel.lock",
        ":MODULE.bazel.lock",
    ],
    component_name = "score_kyron",
    auto_crates_cache = True,
    auto_cdxgen = True,
    sbom_authors = ["Eclipse SCORE Team"],
    generation_context = "build",
)

# SBOM for score_orchestrator
sbom(
    name = "sbom_orchestrator",
    targets = [
        "@score_orchestrator//src/orchestration:liborchestration",
    ],
    module_lockfiles = [
        "@score_crates//:MODULE.bazel.lock",
        ":MODULE.bazel.lock",
    ],
    component_name = "score_orchestrator",
    auto_crates_cache = True,
    auto_cdxgen = True,
    sbom_authors = ["Eclipse SCORE Team"],
    generation_context = "build",
)

# SBOM for score_feo
sbom(
    name = "sbom_feo",
    targets = [
        "@score_feo//feo:libfeo_rust",
        "@score_feo//feo:libfeo_recording_rust",
        "@score_feo//feo-com:libfeo_com_rust",
        "@score_feo//feo-log:libfeo_log_rust",
        "@score_feo//feo-time:libfeo_time_rust",
        "@score_feo//feo-tracing:libfeo_tracing_rust",
    ],
    module_lockfiles = [
        "@score_crates//:MODULE.bazel.lock",
        ":MODULE.bazel.lock",
    ],
    component_name = "score_feo",
    auto_crates_cache = True,
    auto_cdxgen = True,
    sbom_authors = ["Eclipse SCORE Team"],
    generation_context = "build",
)

# SBOM for score_logging
sbom(
    name = "sbom_logging",
    targets = [
        "@score_logging//score/datarouter:log",
    ],
    module_lockfiles = [
        "@score_crates//:MODULE.bazel.lock",
        ":MODULE.bazel.lock",
    ],
    component_name = "score_logging",
    auto_crates_cache = True,
    auto_cdxgen = True,
    sbom_authors = ["Eclipse SCORE Team"],
    generation_context = "build",
)
