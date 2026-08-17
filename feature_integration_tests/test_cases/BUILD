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

# Tests targets
#
# fit_rust_orch has no fit_cpp_orch counterpart: every test currently under tests/basic/ is
# @pytest.mark.rust-only, so there is nothing for a cpp target to select today. If a
# cpp-marked test is ever added under tests/basic/, add a matching fit_cpp_orch
# (`-m cpp`, --cpp-target-path) target - otherwise it would silently never run in CI.
score_py_pytest(
    name = "fit_rust_orch",
    timeout = "long",
    srcs = glob(["tests/basic/**/*.py"]),
    args = [
        "-m rust",
        "--traces=all",
        "--rust-target-path=$(rootpath //feature_integration_tests/test_scenarios/rust:rust_test_scenarios)",
    ],
    data = [
        "conftest.py",
        "fit_scenario.py",
        "persistency_scenario.py",
        "test_properties.py",
        "//feature_integration_tests/test_scenarios/rust:rust_test_scenarios",
    ],
    env = {
        "RUST_BACKTRACE": "1",
    },
    pytest_config = "//:pyproject.toml",
    deps = all_requirements,
)

score_py_pytest(
    name = "fit_rust_persistency",
    timeout = "long",
    srcs = glob(["tests/persistency/**/*.py"]),
    args = [
        "-m rust",
        "--traces=all",
        "--rust-target-path=$(rootpath //feature_integration_tests/test_scenarios/rust:rust_test_scenarios)",
    ],
    data = [
        "conftest.py",
        "fit_scenario.py",
        "persistency_scenario.py",
        "test_properties.py",
        "//feature_integration_tests/test_scenarios/rust:rust_test_scenarios",
    ],
    env = {
        "RUST_BACKTRACE": "1",
    },
    pytest_config = "//:pyproject.toml",
    deps = all_requirements,
)

score_py_pytest(
    name = "fit_rust_scenario_lifecycle",
    timeout = "long",
    srcs = ["tests/lifecycle/test_conditional_launching_scenario.py"],
    args = [
        "-m rust",
        "--traces=all",
        "--rust-target-path=$(rootpath //feature_integration_tests/test_scenarios/rust:rust_lifecycle_test_scenarios)",
    ],
    data = [
        "conftest.py",
        "fit_scenario.py",
        "lifecycle_scenario.py",
        "test_properties.py",
        "//feature_integration_tests/test_scenarios/rust:rust_lifecycle_test_scenarios",
    ],
    env = {
        "RUST_BACKTRACE": "1",
    },
    pytest_config = "//:pyproject.toml",
    deps = all_requirements,
)

test_suite(
    name = "fit_rust",
    tests = [
        ":fit_rust_orch",
        ":fit_rust_persistency",
        ":fit_rust_scenario_lifecycle",
    ],
)

score_py_pytest(
    name = "fit_cpp_persistency",
    timeout = "long",
    srcs = glob(["tests/persistency/**/*.py"]),
    args = [
        "-m cpp",
        "--traces=all",
        "--cpp-target-path=$(rootpath //feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios)",
    ],
    data = [
        "conftest.py",
        "fit_scenario.py",
        "persistency_scenario.py",
        "test_properties.py",
        "//feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios",
    ],
    pytest_config = "//:pyproject.toml",
    deps = all_requirements,
)

score_py_pytest(
    name = "fit_cpp_scenario_lifecycle",
    timeout = "long",
    srcs = ["tests/lifecycle/test_conditional_launching_scenario.py"],
    args = [
        "-m cpp",
        "--traces=all",
        "--cpp-target-path=$(rootpath //feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios)",
    ],
    data = [
        "conftest.py",
        "fit_scenario.py",
        "lifecycle_scenario.py",
        "test_properties.py",
        "//feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios",
    ],
    pytest_config = "//:pyproject.toml",
    deps = all_requirements,
)

test_suite(
    name = "fit_cpp",
    tests = [
        ":fit_cpp_persistency",
        ":fit_cpp_scenario_lifecycle",
    ],
)

# Daemon-driven lifecycle tests (test_conditional_launching.py, test_process_launching_with_daemon.py)
# exercise launch_manager against both supervised apps together and don't depend on which
# scenario-binary language variant is under test elsewhere, so they run once here rather than
# being routed - and silently deselected - by the rust/cpp scenario-binary language marker.
score_py_pytest(
    name = "fit_lifecycle_daemon",
    timeout = "long",
    srcs = [
        "tests/lifecycle/test_conditional_launching.py",
        "tests/lifecycle/test_process_launching_with_daemon.py",
    ],
    args = [
        "--traces=all",
    ],
    data = [
        "conftest.py",
        "daemon_helpers.py",
        "test_properties.py",
        "//feature_integration_tests/configs:lifecycle_daemon_config",
        "@score_lifecycle_health//examples/control_application:control_daemon",
        "@score_lifecycle_health//examples/control_application:lmcontrol",
        "@score_lifecycle_health//examples/cpp_supervised_app",
        "@score_lifecycle_health//examples/rust_supervised_app",
        "@score_lifecycle_health//score/launch_manager",
    ],
    env = {
        "FIT_CPP_SUPERVISED_APP_PATH": "$(rootpath @score_lifecycle_health//examples/cpp_supervised_app)",
        "FIT_LAUNCH_MANAGER_PATH": "$(rootpath @score_lifecycle_health//score/launch_manager)",
        "FIT_LIFECYCLE_DAEMON_CONFIG_PATH": "$(rootpath //feature_integration_tests/configs:lifecycle_daemon_config)",
        "FIT_RUST_SUPERVISED_APP_PATH": "$(rootpath @score_lifecycle_health//examples/rust_supervised_app)",
        "RUST_BACKTRACE": "1",
    },
    env_inherit = ["FIT_ENABLE_SETCAP"],
    pytest_config = "//:pyproject.toml",
    # Lifecycle daemon tests drive a shared launch_manager daemon and cannot run concurrently with each other.
    # Runs sandboxed: PR_SET_NO_NEW_PRIVS blocks setuid (sudo) / file-capability (setcap) escalation
    # at exec time, so sandbox_privileged is always False here and the uid/gid/scheduling tests
    # skip themselves accordingly (see daemon_helpers._grant_sandbox_capabilities). Everything
    # else only signals same-uid processes and needs no privilege escalation. FIT_ENABLE_SETCAP=1
    # is for local/manual runs outside the sandbox where the sestcap grant can actually take effect.
    tags = ["exclusive"],
    deps = all_requirements,
)

test_suite(
    name = "fit",
    tests = [
        ":fit_cpp",
        ":fit_lifecycle_daemon",
        ":fit_rust",
    ],
)
