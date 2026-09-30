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

package(default_visibility = ["//platform_integration_tests:__subpackages__"])

config_setting(
    name = "config_linux_x86_64",
    constraint_values = [
        "@platforms//os:linux",
        "@platforms//cpu:x86_64",
        "@score_bazel_platforms//runtime_es:posix",
    ],
)

config_setting(
    name = "config_qnx_x86_64",
    constraint_values = [
        "@platforms//os:qnx",
        "@platforms//cpu:x86_64",
        "@score_bazel_platforms//runtime_es:posix",
    ],
)

py_library(
    name = "showcase_runner",
    srcs = ["showcase_runner.py"],
    # Lets sibling packages `import showcase_runner` as a flat top-level
    # module instead of `platform_integration_tests.showcase_runner`.
    imports = ["."],
)

# Collects the per-module showcase tests below into the single suite that CI
# runs (see the top-level module docstring of each test for the rationale).
test_suite(
    name = "pit",
    tags = [
        "manual",
    ],
    tests = [
        "//platform_integration_tests/communication",
        "//platform_integration_tests/kyron",
        "//platform_integration_tests/lifecycle",
        "//platform_integration_tests/logging",
        "//platform_integration_tests/time",
    ],
)
