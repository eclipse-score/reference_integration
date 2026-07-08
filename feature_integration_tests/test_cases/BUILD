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
load("@rules_python//python:pip.bzl", "compile_pip_requirements")
load("@score_lifecycle_health//:defs.bzl", "launch_manager_config")
load("@score_tooling//python_basics:defs.bzl", "score_py_pytest")

# In order to update the requirements, change the `requirements.txt` file and run:
# `bazel run //feature_integration_tests/test_cases:requirements.update`.
# This will update the `requirements.txt.lock` file.
# To upgrade all dependencies to their latest versions, run:
# `bazel run //feature_integration_tests/test_cases:requirements.update -- --upgrade`.
compile_pip_requirements(
    name = "requirements",
    srcs = [
        "requirements.txt",
        "@score_tooling//python_basics:requirements.txt",
    ],
    extra_args = [
        "--no-annotate",
    ],
    requirements_txt = "requirements.txt.lock",
    tags = [
        "manual",
    ],
)

launch_manager_config(
    name = "daemon_lifecycle_configs",
    config = "//feature_integration_tests/test_cases/configs:daemon_launch_manager_config.json",
)

# Tests targets
score_py_pytest(
    name = "fit_rust",
    srcs = glob(["tests/**/*.py"]),
    args = [
        "-m rust",
        "--traces=all",
        "--rust-target-path=$(rootpath //feature_integration_tests/test_scenarios/rust:rust_test_scenarios)",
        "-k 'not with_daemon'",
    ],
    data = [
        "conftest.py",
        "daemon_helpers.py",
        "fit_scenario.py",
        "lifecycle_scenario.py",
        "persistency_scenario.py",
        "test_properties.py",
        "//feature_integration_tests/test_scenarios/rust:rust_test_scenarios",
    ],
    env = {
        "RUST_BACKTRACE": "1",
    },
    pytest_config = "//:pyproject.toml",
    tags = ["no-sandbox"],
    deps = all_requirements,
)

score_py_pytest(
    name = "fit_cpp",
    srcs = glob(["tests/**/*.py"]),
    args = [
        "-m cpp",
        "--traces=all",
        "--cpp-target-path=$(rootpath //feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios)",
        "-k 'not with_daemon'",
    ],
    data = [
        "conftest.py",
        "daemon_helpers.py",
        "fit_scenario.py",
        "lifecycle_scenario.py",
        "persistency_scenario.py",
        "test_properties.py",
        "//feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios",
    ],
    pytest_config = "//:pyproject.toml",
    tags = ["no-sandbox"],
    deps = all_requirements,
)

# Daemon integration tests (Rust)
score_py_pytest(
    name = "fit_daemon_rust",
    srcs = glob(["tests/**/*.py"]),
    args = [
        "-m rust",
        "--traces=all",
        "--rust-target-path=$(rootpath //feature_integration_tests/test_scenarios/rust:rust_test_scenarios)",
        "-k with_daemon",
    ],
    data = [
        "conftest.py",
        "daemon_helpers.py",
        "fit_scenario.py",
        "lifecycle_scenario.py",
        "persistency_scenario.py",
        "test_properties.py",
        ":daemon_lifecycle_configs",
        "//feature_integration_tests/test_scenarios/rust:rust_test_scenarios",
        "@score_lifecycle_health//examples/control_application:control_daemon",
        "@score_lifecycle_health//examples/cpp_supervised_app",
        "@score_lifecycle_health//examples/rust_supervised_app",
        "@score_lifecycle_health//src/launch_manager_daemon:launch_manager",
    ],
    env = {
        "RUST_BACKTRACE": "1",
    },
    pytest_config = "//:pyproject.toml",
    tags = [
        "exclusive",
        "no-sandbox",
    ],
    deps = all_requirements,
)

# Daemon integration tests (C++)
score_py_pytest(
    name = "fit_daemon_cpp",
    srcs = glob(["tests/**/*.py"]),
    args = [
        "-m cpp",
        "--traces=all",
        "--cpp-target-path=$(rootpath //feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios)",
        "-k with_daemon",
    ],
    data = [
        "conftest.py",
        "daemon_helpers.py",
        "fit_scenario.py",
        "lifecycle_scenario.py",
        "persistency_scenario.py",
        "test_properties.py",
        ":daemon_lifecycle_configs",
        "//feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios",
        "@score_lifecycle_health//examples/control_application:control_daemon",
        "@score_lifecycle_health//examples/cpp_supervised_app",
        "@score_lifecycle_health//examples/rust_supervised_app",
        "@score_lifecycle_health//src/launch_manager_daemon:launch_manager",
    ],
    pytest_config = "//:pyproject.toml",
    tags = [
        "exclusive",
        "no-sandbox",
    ],
    deps = all_requirements,
)

test_suite(
    name = "fit",
    tests = [
        ":fit_cpp",
        ":fit_daemon_cpp",
        ":fit_daemon_rust",
        ":fit_rust",
    ],
)
