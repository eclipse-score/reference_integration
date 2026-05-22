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
"""
Feature integration tests for conditional launching.

Tests verify that the Launch Manager supports conditional process launching
based on various conditions including process state, environment variables,
paths, and dependencies.
"""

from pathlib import Path
from typing import Any

import pytest
from fit_scenario import ResultCode
from lifecycle_scenario import LifecycleScenario
from test_properties import add_test_properties
from testing_utils import LogContainer, ScenarioResult

pytestmark = pytest.mark.parametrize("version", ["rust", "cpp"], scope="class")


@add_test_properties(
    partially_verifies=[
        "feat_req__lifecycle__waitfor_support",
        "feat_req__lifecycle__cond_process_start",
        "feat_req__lifecycle__total_wait_time_support",
        "feat_req__lifecycle__polling_interval",
        "feat_req__lifecycle__validate_conditions",
        "feat_req__lifecycle__validation_conditions",
        "feat_req__lifecycle__launcher_status_storage",
        "feat_req__lifecycle__condition_check_method",
        "feat_req__lifecycle__config_actions_cond",
        "feat_req__lifecycle__path_condition_check",
        "feat_req__lifecycle__env_variable_cond_check",
        "feat_req__lifecycle__dependency_check",
        "feat_req__lifecycle__check_dependency_exec",
        "feat_req__lifecycle__define_swc_dependencies",
        "feat_req__lifecycle__stop_sequence",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestConditionalLaunching(LifecycleScenario):
    """
    Verify conditional process launching support.

    This test confirms that the Launch Manager can conditionally launch
    processes based on various criteria and wait conditions.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.conditional_launching"

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path) -> dict[str, Any]:
        return {
            "test": {
                "test_duration_ms": 300,
                "wait_conditions": ["path:/tmp/ready", "env:STARTUP_COMPLETE", "process:init_done"],
                "polling_interval_ms": 50,
                "timeout_ms": 5000,
            }
        }

    def test_path_condition_check(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that path-based condition checking works.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Checking path condition: /tmp/ready" in results.stdout, "Path condition not checked"
        else:
            path_logs = logs_info_level.get_logs(field="message", pattern="Checking path condition: /tmp/ready")
            assert len(path_logs) > 0, "Path condition not checked"

    def test_env_condition_check(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that environment variable condition checking works.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Checking env condition: STARTUP_COMPLETE" in results.stdout, "Environment condition not checked"
        else:
            env_logs = logs_info_level.get_logs(field="message", pattern="Checking env condition: STARTUP_COMPLETE")
            assert len(env_logs) > 0, "Environment condition not checked"

    def test_process_condition_check(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that process state condition checking works.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Checking process condition: init_done" in results.stdout, "Process condition not checked"
        else:
            process_logs = logs_info_level.get_logs(field="message", pattern="Checking process condition: init_done")
            assert len(process_logs) > 0, "Process condition not checked"

    def test_polling_interval_configured(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that polling interval is configured correctly.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Polling interval: 50ms" in results.stdout, "Polling interval not configured"
        else:
            polling_logs = logs_info_level.get_logs(field="message", pattern="Polling interval: 50ms")
            assert len(polling_logs) > 0, "Polling interval not configured"

    def test_condition_timeout_configured(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that condition timeout is configured.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Condition timeout: 5000ms" in results.stdout, "Condition timeout not configured"
        else:
            timeout_logs = logs_info_level.get_logs(field="message", pattern="Condition timeout: 5000ms")
            assert len(timeout_logs) > 0, "Condition timeout not configured"

    def test_dependency_check(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that dependency checking works.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "All dependencies satisfied" in results.stdout, "Dependency check failed"
        else:
            dep_logs = logs_info_level.get_logs(field="message", value="All dependencies satisfied")
            assert len(dep_logs) > 0, "Dependency check failed"
