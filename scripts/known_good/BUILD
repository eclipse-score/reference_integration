# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
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
load("@rules_python//python:defs.bzl", "py_binary", "py_library")
load("@score_tooling//python_basics:defs.bzl", "score_py_pytest")

# Library target: the known_good package (models + generators).
# Depended on by the test and binary targets below. Note //scripts/tooling has its own separate
# lib/known_good package and does not use this one.
py_library(
    name = "known_good",
    srcs = glob(
        ["**/*.py"],
        exclude = ["tests/**"],
    ),
    # scripts/ on sys.path, so "from known_good...." resolves under 'bazel run' as it does for
    # "python3 scripts/...". Propagates to every consumer of this library.
    imports = [".."],
    visibility = ["//visibility:public"],
)

# Tests for the known_good package (currently: ResolvedDependencies).
# Not part of //scripts/tooling:tooling_tests, whose glob is scoped to scripts/tooling/tests/.
score_py_pytest(
    name = "known_good_tests",
    srcs = glob(["tests/**/*.py"]),
    data = ["//:known_good.json"],
    pytest_config = "//:pyproject.toml",
    deps = [":known_good"],
)

# Runnable binary for the resolve + inject workflow.
#
# Stage 1 (export) — 'bazel mod graph' is a prerequisite; run it first and pass the result:
#       bazel mod graph --verbose --output=json > graph.json
#       bazel run //scripts/known_good:resolve_deps -- \
#           --mod-graph graph.json --export _resolved_deps/resolved_versions.json
#   Writes the manifest, graph.json and resolved_pins_report.json side by side; all three are
#   published as the stage1-resolved-deps artifact. Paths are resolved against
#   BUILD_WORKSPACE_DIRECTORY, so graph.json does not need to be listed in data = [...].
#
#   '--verbose' adds 'originalVersion' to each edge, the only record of a consumer asking for a
#   version other than the one ref_int imposes. It is a strict superset, so Stage 2 reads the same
#   graph.json either way; without it the export still succeeds, with every verdict 'unknown'.
#
# Stage 2 (inject) — consumes that same directory:
#       bazel run //scripts/known_good:resolve_deps -- \
#           _module/MODULE.bazel --resolved-deps _resolved_deps/
#   The manifest supplies each module's resolved version; graph.json identifies the
#   module-under-test's transitive closure so all of it is pinned, not only direct deps.
py_binary(
    name = "resolve_deps",
    srcs = ["resolved_dependencies.py"],
    main = "resolved_dependencies.py",
    visibility = ["//visibility:public"],
    deps = [":known_good"],
)

# The Stage-2 matrix, derived from known_good.json rather than hardcoded in the workflow.
py_binary(
    name = "list_modules",
    srcs = ["list_modules.py"],
    data = ["//:known_good.json"],
    main = "list_modules.py",
    visibility = ["//visibility:public"],
    deps = [":known_good"],
)

# The Stage-2 resolution gate: did the module really build against ref_int's pins and patches.
py_binary(
    name = "verify_stage2_resolution",
    srcs = ["verify_stage2_resolution.py"],
    main = "verify_stage2_resolution.py",
    visibility = ["//visibility:public"],
    deps = [":known_good"],
)
