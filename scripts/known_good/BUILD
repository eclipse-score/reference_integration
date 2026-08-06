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
# Used as a dep by //scripts/tooling and by the resolve_deps binary below.
py_library(
    name = "known_good",
    srcs = glob(
        ["**/*.py"],
        exclude = ["tests/**"],
    ),
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
#       bazel mod graph --output=json > graph.json
#       bazel run //scripts/known_good:resolve_deps -- \
#           --mod-graph graph.json --export _resolved_deps/resolved_versions.json
#   Writes the manifest and stores graph.json next to it; both are published as the
#   stage1-resolved-deps artifact. Paths are resolved against BUILD_WORKSPACE_DIRECTORY,
#   so graph.json does not need to be listed in data = [...].
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
