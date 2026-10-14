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
    visibility = ["//visibility:public"],
)

# Tests for the known_good package.
# Not part of //scripts/tooling:tooling_tests, whose glob is scoped to scripts/tooling/tests/.
score_py_pytest(
    name = "known_good_tests",
    srcs = glob(["tests/**/*.py"]),
    data = ["//:known_good.json"],
    pytest_config = "//:pyproject.toml",
    deps = [":known_good"],
)
