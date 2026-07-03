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
#   Stage 1 (export): bazel run //scripts/known_good:resolve_deps -- \
#       --mod-graph graph.json --export artifacts/resolved_versions.json
#   Stage 2 (inject): bazel run //scripts/known_good:resolve_deps -- \
#       _module/MODULE.bazel --resolved-deps _resolved_deps/
py_binary(
    name = "resolve_deps",
    srcs = ["resolved_dependencies.py"],
    main = "resolved_dependencies.py",
    visibility = ["//visibility:public"],
    deps = [":known_good"],
)
