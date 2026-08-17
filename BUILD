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
load("@score_sbom//:defs.bzl", "sbom")
load("@score_tooling//:defs.bzl", "setup_starpls", "use_format_targets")

# Docs-as-code
docs(
    data = [
        # Software components
        "@score_persistency//:needs_json",
        "@score_orchestrator//:needs_json",
        "@score_kyron//:needs_json",
        # "@score_baselibs//:needs_json",  # score_tooling is dev_dependency
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

# Add target for formatting checks
use_format_targets()

exports_files([
    "MODULE.bazel",
    "MODULE.bazel.lock",
    "pyproject.toml",
    "known_good.json",
])

sbom(
    name = "sbom",
    auto_cdxgen = False,
    auto_crates_cache = True,
    component_name = "score_reference_integration",
    generation_context = "build",
    module_lockfiles = [":MODULE.bazel.lock"],
    output_formats = [
        "spdx",
    ],
    targets = [
        "//feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios",
        "//feature_integration_tests/test_scenarios/rust:rust_test_scenarios",
        "//showcases/cli:cli",
        "//showcases/orchestration_persistency:orch_per_example",
        "@score_communication//score/mw/com/example/com-api-example:com-api-example",
        "@score_kyron//examples:main_macro",
        "@score_kyron//examples:safety_task",
        "@score_kyron//examples:select",
        "@score_logging//score/test/component/dlt_generator_app:dlt_generator",
        "@score_logging//score/test/component/logging_app:logging_app",
        "@score_time//examples/time/high_res_steady_time",
        "@score_time//examples/time/steady_time",
        "@score_time//examples/time/system_time",
        "@score_time//examples/time/vehicle_time",
    ],
)

# Product SBOM alias with an explicit lifecycle-oriented name.
alias(
    name = "product_sbom",
    actual = ":sbom",
    visibility = ["//visibility:public"],
)

# Qualification inventory for Python-based build and test tools. This is kept
# separate from the product SBOM because build-time dependencies are not
# product/runtime dependencies.
sbom(
    name = "build_tools_sbom",
    testonly = True,
    auto_cdxgen = False,
    auto_crates_cache = False,
    component_name = "score_reference_integration_build_tools",
    # Pip repositories are represented authoritatively by python_lockfiles;
    # exclude their generated Bazel aliases to avoid duplicate components.
    exclude_patterns = ["rules_python++pip+"],
    generation_context = "build",
    java_files = ["@score_docs_as_code//src:plantuml.jar"],
    output_formats = ["spdx"],
    python_lockfiles = [
        "//feature_integration_tests/test_cases:requirements.txt.lock",
        "//scripts/tooling:requirements.txt",
        "@score_docs_as_code//src:requirements_lock",
    ],
    targets = [
        "//:docs_combo_experimental",
        "//feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios",
        "//scripts/tooling:checkout_repos",
        "//scripts/tooling:recategorize_guidelines",
        "//scripts/tooling:tooling",
        "@score_docs_as_code//src:plantuml",
    ],
)
