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

exports_files(["requirements.txt.lock"])

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
        "--rust-target-path=$(rootpath //feature_integration_tests/test_scenarios/rust:rust_test_scenarios)",
    ],
    data = [
        "conftest.py",
        "fit_scenario.py",
        "lifecycle_scenario.py",
        "test_properties.py",
        "//feature_integration_tests/test_scenarios/rust:rust_test_scenarios",
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

# Daemon-driven lifecycle tests against a real launch_manager. No -m rust/cpp filter: these tests
# don't use the scenario binaries, and some carry no language marker, so a filter would deselect them.
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
        "tests/lifecycle/conftest.py",
        "//feature_integration_tests/configs:lifecycle_daemon_config.json",
        "@flatbuffers//:flatc",
        "@score_lifecycle//examples/cpp_supervised_app",
        "@score_lifecycle//examples/rust_supervised_app",
        "@score_lifecycle//score/launch_manager",
        "@score_lifecycle//score/launch_manager/src/daemon/src/configuration:lm_flatcfg_fbs",
        "@score_lifecycle//score/launch_manager/src/daemon/src/configuration/config_schema:launch_manager.schema.json",
        "@score_lifecycle//scripts/config_mapping:lifecycle_config",
    ],
    env = {
        "FIT_CPP_SUPERVISED_APP_PATH": "$(rootpath @score_lifecycle//examples/cpp_supervised_app)",
        "FIT_LAUNCH_MANAGER_PATH": "$(rootpath @score_lifecycle//score/launch_manager)",
        "FIT_FLATC_PATH": "$(rootpath @flatbuffers//:flatc)",
        "FIT_LIFECYCLE_CONFIG_SCHEMA_PATH": "$(rootpath @score_lifecycle//score/launch_manager/src/daemon/src/configuration/config_schema:launch_manager.schema.json)",
        "FIT_LIFECYCLE_CONFIG_TOOL_PATH": "$(rootpath @score_lifecycle//scripts/config_mapping:lifecycle_config)",
        "FIT_LIFECYCLE_DAEMON_CONFIG_PATH": "$(rootpath //feature_integration_tests/configs:lifecycle_daemon_config.json)",
        "FIT_LIFECYCLE_LM_SCHEMA_PATH": "$(rootpath @score_lifecycle//score/launch_manager/src/daemon/src/configuration:lm_flatcfg_fbs)",
        "FIT_RUST_SUPERVISED_APP_PATH": "$(rootpath @score_lifecycle//examples/rust_supervised_app)",
        "RUST_BACKTRACE": "1",
    },
    env_inherit = ["FIT_ENABLE_SETCAP"],
    pytest_config = "//:pyproject.toml",
    # Under the default linux-sandbox, PR_SET_NO_NEW_PRIVS makes the setcap grant inert, so the
    # uid/gid/scheduling tests skip (as in CI). They run only with --spawn_strategy=local and
    # --test_env=FIT_ENABLE_SETCAP=1 (see README.md).
    # "exclusive": launch_manager uses fixed POSIX shm names on the host-wide /dev/shm, so no other
    # launch_manager-driven target may run concurrently.
    tags = ["exclusive"],
    deps = all_requirements,
)

# Dedicated, isolated coverage for ready_recovery_action.restart.number_of_attempts. Each daemon
# invocation generates its own single-component config and runtime tree under TEST_TMPDIR.
score_py_pytest(
    name = "fit_lifecycle_retries",
    timeout = "long",
    srcs = [
        "tests/lifecycle/test_retry_exhaustion.py",
    ],
    args = [
        "--traces=all",
    ],
    data = [
        "conftest.py",
        "daemon_helpers.py",
        "fit_scenario.py",
        "lifecycle_scenario.py",
        "test_properties.py",
        "//feature_integration_tests/configs:lifecycle_daemon_retry_config.json",
        "//feature_integration_tests/test_cases/support_apps/flaky_startup_app",
        "@flatbuffers//:flatc",
        "@score_lifecycle//score/launch_manager",
        "@score_lifecycle//score/launch_manager/src/daemon/src/configuration:lm_flatcfg_fbs",
        "@score_lifecycle//score/launch_manager/src/daemon/src/configuration/config_schema:launch_manager.schema.json",
        "@score_lifecycle//scripts/config_mapping:lifecycle_config",
    ],
    env = {
        "FIT_FLAKY_STARTUP_APP_PATH": "$(rootpath //feature_integration_tests/test_cases/support_apps/flaky_startup_app)",
        "FIT_FLATC_PATH": "$(rootpath @flatbuffers//:flatc)",
        "FIT_LAUNCH_MANAGER_PATH": "$(rootpath @score_lifecycle//score/launch_manager)",
        "FIT_LIFECYCLE_CONFIG_SCHEMA_PATH": "$(rootpath @score_lifecycle//score/launch_manager/src/daemon/src/configuration/config_schema:launch_manager.schema.json)",
        "FIT_LIFECYCLE_CONFIG_TOOL_PATH": "$(rootpath @score_lifecycle//scripts/config_mapping:lifecycle_config)",
        "FIT_LIFECYCLE_LM_SCHEMA_PATH": "$(rootpath @score_lifecycle//score/launch_manager/src/daemon/src/configuration:lm_flatcfg_fbs)",
        "FIT_LIFECYCLE_RETRY_CONFIG_PATH": "$(rootpath //feature_integration_tests/configs:lifecycle_daemon_retry_config.json)",
    },
    pytest_config = "//:pyproject.toml",
    # See fit_lifecycle_daemon: launch_manager's fixed /dev/shm names forbid concurrent targets.
    tags = ["exclusive"],
    deps = all_requirements,
)

test_suite(
    name = "fit",
    tests = [
        ":fit_cpp",
        ":fit_lifecycle_daemon",
        ":fit_lifecycle_retries",
        ":fit_rust",
    ],
)
