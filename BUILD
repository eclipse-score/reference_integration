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
