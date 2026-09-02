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

test_suite(
    name = "fit_rust",
    tests = [
        ":fit_rust_persistency",
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

test_suite(
    name = "fit_cpp",
    tests = [
        ":fit_cpp_persistency",
    ],
)

# Cross-module lifecycle<->persistency recovery test and the control-interface
# (activate_target) architectural test. Both parametrize on rust/cpp and need the
# scenario binaries (for the persistency probe) in addition to the daemon deps
# fit_lifecycle_daemon already needs, so they run once per language rather than
# being folded into fit_lifecycle_daemon (which is language-agnostic).
score_py_pytest(
    name = "fit_rust_lifecycle_persistency",
    timeout = "long",
    srcs = [
        "tests/lifecycle/test_lifecycle_persistency_recovery.py",
        "tests/lifecycle/test_lifecycle_state_manager.py",
    ],
    args = [
        "-m rust",
        "--traces=all",
        "--rust-target-path=$(rootpath //feature_integration_tests/test_scenarios/rust:rust_test_scenarios)",
    ],
    data = [
        "conftest.py",
        "daemon_helpers.py",
        "fit_scenario.py",
        "persistency_scenario.py",
        "test_properties.py",
        "//feature_integration_tests/configs:lifecycle_daemon_config.json",
        "//feature_integration_tests/test_scenarios/rust:rust_test_scenarios",
        "@flatbuffers//:flatc",
        "@score_lifecycle_health//examples/control_application:control_daemon",
        "@score_lifecycle_health//examples/control_application:lmcontrol",
        "@score_lifecycle_health//examples/cpp_supervised_app",
        "@score_lifecycle_health//examples/rust_supervised_app",
        "@score_lifecycle_health//score/launch_manager",
        "@score_lifecycle_health//score/launch_manager/src/daemon/src/alive_monitor/config:hm_flatcfg.fbs",
        "@score_lifecycle_health//score/launch_manager/src/daemon/src/alive_monitor/config:hmcore_flatcfg.fbs",
        "@score_lifecycle_health//score/launch_manager/src/daemon/src/configuration/config_schema:launch_manager.schema.json",
        "@score_lifecycle_health//score/launch_manager/src/daemon/src/configuration/config_schema:lm_flatcfg.fbs",
        "@score_lifecycle_health//scripts/config_mapping:lifecycle_config",
    ],
    env = {
        "FIT_CPP_SUPERVISED_APP_PATH": "$(rootpath @score_lifecycle_health//examples/cpp_supervised_app)",
        "FIT_LAUNCH_MANAGER_PATH": "$(rootpath @score_lifecycle_health//score/launch_manager)",
        "FIT_FLATC_PATH": "$(rootpath @flatbuffers//:flatc)",
        "FIT_LIFECYCLE_CONFIG_SCHEMA_PATH": "$(rootpath @score_lifecycle_health//score/launch_manager/src/daemon/src/configuration/config_schema:launch_manager.schema.json)",
        "FIT_LIFECYCLE_CONFIG_TOOL_PATH": "$(rootpath @score_lifecycle_health//scripts/config_mapping:lifecycle_config)",
        "FIT_LIFECYCLE_DAEMON_CONFIG_PATH": "$(rootpath //feature_integration_tests/configs:lifecycle_daemon_config.json)",
        "FIT_LIFECYCLE_HMCORE_SCHEMA_PATH": "$(rootpath @score_lifecycle_health//score/launch_manager/src/daemon/src/alive_monitor/config:hmcore_flatcfg.fbs)",
        "FIT_LIFECYCLE_HM_SCHEMA_PATH": "$(rootpath @score_lifecycle_health//score/launch_manager/src/daemon/src/alive_monitor/config:hm_flatcfg.fbs)",
        "FIT_LIFECYCLE_LM_SCHEMA_PATH": "$(rootpath @score_lifecycle_health//score/launch_manager/src/daemon/src/configuration/config_schema:lm_flatcfg.fbs)",
        "FIT_LMCONTROL_PATH": "$(rootpath @score_lifecycle_health//examples/control_application:lmcontrol)",
        "FIT_RUST_SUPERVISED_APP_PATH": "$(rootpath @score_lifecycle_health//examples/rust_supervised_app)",
        "RUST_BACKTRACE": "1",
    },
    env_inherit = ["FIT_ENABLE_SETCAP"],
    pytest_config = "//:pyproject.toml",
    deps = all_requirements,
)

score_py_pytest(
    name = "fit_cpp_lifecycle_persistency",
    timeout = "long",
    srcs = [
        "tests/lifecycle/test_lifecycle_persistency_recovery.py",
        "tests/lifecycle/test_lifecycle_state_manager.py",
    ],
    args = [
        "-m cpp",
        "--traces=all",
        "--cpp-target-path=$(rootpath //feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios)",
    ],
    data = [
        "conftest.py",
        "daemon_helpers.py",
        "fit_scenario.py",
        "persistency_scenario.py",
        "test_properties.py",
        "//feature_integration_tests/configs:lifecycle_daemon_config.json",
        "//feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios",
        "@flatbuffers//:flatc",
        "@score_lifecycle_health//examples/control_application:control_daemon",
        "@score_lifecycle_health//examples/control_application:lmcontrol",
        "@score_lifecycle_health//examples/cpp_supervised_app",
        "@score_lifecycle_health//examples/rust_supervised_app",
        "@score_lifecycle_health//score/launch_manager",
        "@score_lifecycle_health//score/launch_manager/src/daemon/src/alive_monitor/config:hm_flatcfg.fbs",
        "@score_lifecycle_health//score/launch_manager/src/daemon/src/alive_monitor/config:hmcore_flatcfg.fbs",
        "@score_lifecycle_health//score/launch_manager/src/daemon/src/configuration/config_schema:launch_manager.schema.json",
        "@score_lifecycle_health//score/launch_manager/src/daemon/src/configuration/config_schema:lm_flatcfg.fbs",
        "@score_lifecycle_health//scripts/config_mapping:lifecycle_config",
    ],
    env = {
        "FIT_CPP_SUPERVISED_APP_PATH": "$(rootpath @score_lifecycle_health//examples/cpp_supervised_app)",
        "FIT_LAUNCH_MANAGER_PATH": "$(rootpath @score_lifecycle_health//score/launch_manager)",
        "FIT_FLATC_PATH": "$(rootpath @flatbuffers//:flatc)",
        "FIT_LIFECYCLE_CONFIG_SCHEMA_PATH": "$(rootpath @score_lifecycle_health//score/launch_manager/src/daemon/src/configuration/config_schema:launch_manager.schema.json)",
        "FIT_LIFECYCLE_CONFIG_TOOL_PATH": "$(rootpath @score_lifecycle_health//scripts/config_mapping:lifecycle_config)",
        "FIT_LIFECYCLE_DAEMON_CONFIG_PATH": "$(rootpath //feature_integration_tests/configs:lifecycle_daemon_config.json)",
        "FIT_LIFECYCLE_HMCORE_SCHEMA_PATH": "$(rootpath @score_lifecycle_health//score/launch_manager/src/daemon/src/alive_monitor/config:hmcore_flatcfg.fbs)",
        "FIT_LIFECYCLE_HM_SCHEMA_PATH": "$(rootpath @score_lifecycle_health//score/launch_manager/src/daemon/src/alive_monitor/config:hm_flatcfg.fbs)",
        "FIT_LIFECYCLE_LM_SCHEMA_PATH": "$(rootpath @score_lifecycle_health//score/launch_manager/src/daemon/src/configuration/config_schema:lm_flatcfg.fbs)",
        "FIT_LMCONTROL_PATH": "$(rootpath @score_lifecycle_health//examples/control_application:lmcontrol)",
        "FIT_RUST_SUPERVISED_APP_PATH": "$(rootpath @score_lifecycle_health//examples/rust_supervised_app)",
    },
    env_inherit = ["FIT_ENABLE_SETCAP"],
    pytest_config = "//:pyproject.toml",
    deps = all_requirements,
)

test_suite(
    name = "fit",
    tests = [
        ":fit_cpp",
        ":fit_cpp_lifecycle_persistency",
        ":fit_rust",
        ":fit_rust_lifecycle_persistency",
    ],
)
