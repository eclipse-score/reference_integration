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
load("@score_tooling//:defs.bzl", "rust_coverage_report")

docs(
    data = [
        "@score_platform//:needs_json",
        #"@score_persistency//:needs_json",  # cannot be included, as it does not contain any needs?
        #"@score_orchestrator//:needs_json",  # some issue about score_toolchains_qnx?
        #"@score_communication//:needs_json",  # no docs yet?
        # "@score_feo//:needs_json",
        "@score_docs_as_code//:needs_json",
        "@score_process//:needs_json",
    ],
    source_dir = "docs",
)

# Rust coverage
rust_coverage_report(
    name = "rust_coverage_score_baselibs_rust",
    bazel_configs = [
        "linux-x86_64",
        "ferrocene-coverage",
    ],
    query = 'kind("rust_test", @score_baselibs_rust//src/...)',
    visibility = ["//visibility:public"],
)

rust_coverage_report(
    name = "rust_coverage_score_communication",
    bazel_configs = [
        "linux-x86_64",
        "ferrocene-coverage",
    ],
    query = 'kind("rust_test", @score_communication//score/...)',
    visibility = ["//visibility:public"],
)

rust_coverage_report(
    name = "rust_coverage_score_persistency",
    bazel_configs = [
        "linux-x86_64",
        "ferrocene-coverage",
    ],
    query = 'kind("rust_test", @score_persistency//src/...)',
    visibility = ["//visibility:public"],
)

rust_coverage_report(
    name = "rust_coverage_score_orchestrator",
    bazel_configs = [
        "linux-x86_64",
        "ferrocene-coverage",
    ],
    query = 'kind("rust_test", @score_orchestrator//src/...)',
    visibility = ["//visibility:public"],
)

rust_coverage_report(
    name = "rust_coverage_score_kyron",
    bazel_configs = [
        "linux-x86_64",
        "ferrocene-coverage",
    ],
    query = 'kind("rust_test", @score_kyron//src/...)',
    visibility = ["//visibility:public"],
)

rust_coverage_report(
    name = "rust_coverage_score_lifecycle_health",
    bazel_configs = [
        "linux-x86_64",
        "ferrocene-coverage",
    ],
    query = 'kind("rust_test", @score_lifecycle_health//src/...)',
    visibility = ["//visibility:public"],
)

rust_coverage_report(
    name = "rust_coverage_score_logging",
    bazel_configs = [
        "linux-x86_64",
        "ferrocene-coverage",
    ],
    query = 'kind("rust_test", @score_logging//score/...)',
    visibility = ["//visibility:public"],
)
