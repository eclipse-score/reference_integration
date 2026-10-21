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

py_library(
    name = "module_tests",
    srcs = [
        "module_tests.py",
        "quality_runners.py",
    ],
    imports = ["."],
    deps = ["//scripts/known_good"],
)

score_py_pytest(
    name = "module_tests_tests",
    srcs = ["tests/test_module_tests.py"],
    pytest_config = "//:pyproject.toml",
    deps = [":module_tests"],
)
