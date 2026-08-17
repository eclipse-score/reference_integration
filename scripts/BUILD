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
load("@rules_python//python:defs.bzl", "py_library")
load("@score_tooling//python_basics:defs.bzl", "score_py_pytest")

# The Stage-2 driver and the report aggregator.
py_library(
    name = "quality_scripts",
    srcs = [
        "aggregate_quality_report.py",
        "quality_runners.py",
    ],
    visibility = ["//visibility:public"],
    deps = ["//scripts/known_good:known_good"],
)

# No `data` needed: the tests point STAGE2_RC at a temp file rather than reading
# ci/stage2/module.bazelrc, so they do not depend on runfiles layout.
score_py_pytest(
    name = "quality_scripts_tests",
    srcs = glob(["tests/**/*.py"]),
    pytest_config = "//:pyproject.toml",
    deps = [":quality_scripts"],
)

# One label for every Python unit test, so CI runs all of them by naming a single target.
test_suite(
    name = "all_python_unit_tests",
    tests = [
        ":quality_scripts_tests",
        "//scripts/known_good:known_good_tests",
        "//scripts/tooling:tooling_tests",
    ],
    visibility = ["//visibility:public"],
)
