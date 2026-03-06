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
load("@pip_score_venv_test//:requirements.bzl", "all_requirements")
load("@rules_python//python:defs.bzl", "py_binary", "py_library")
load("@rules_python//python:pip.bzl", "compile_pip_requirements")
load("@score_tooling//python_basics:defs.bzl", "score_py_pytest")

# In order to update the requirements, change the `requirements.in` file and run:
# `bazel run //src:requirements.update`.
# This will update the `requirements.txt` file.
# To upgrade all dependencies to their latest versions, run:
# `bazel run //src:requirements.update -- --upgrade`.
compile_pip_requirements(
    name = "requirements",
    srcs = [
        "requirements.in",
        "@score_tooling//python_basics:requirements.txt",
    ],
    requirements_txt = "requirements.txt",
    tags = [
        "manual",
    ],
)

# Library target
py_library(
    name = "lib",
    srcs = glob(["lib/**/*.py"]),
    visibility = ["//visibility:public"],
)

# CLI binary target
py_binary(
    name = "tooling",
    srcs = glob([
        "cli/**/*.py",
    ]),
    main = "cli/main.py",
    visibility = ["//visibility:public"],
    deps = [":lib"],
)

# Tests target
score_py_pytest(
    name = "tooling_tests",
    srcs = glob(["tests/**/*.py"]),
    data = [
        ":lib/assets/report_template.html",
    ],
    pytest_config = "//:pyproject.toml",
    deps = [
        ":lib",
    ] + all_requirements,
)
