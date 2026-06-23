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
Feature integration tests for logging support.

Tests verify that the Launch Manager provides comprehensive logging
for process launches, state transitions, and system events.
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
        "feat_req__lifecycle__slog2_logging",
        "feat_req__lifecycle__process_logging_support",
        "feat_req__lifecycle__log_timestamp",
        "feat_req__lifecycle__dag_logging_controlif",
        "feat_req__lifecycle__dependency_visu",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestLogging(LifecycleScenario):
    """
    Verify logging support.

    This test confirms that the Launch Manager provides comprehensive
    logging for analysis and debugging.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.logging_support"

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path) -> dict[str, Any]:
        return {
            "test": {
                "test_duration_ms": 200,
                "enable_dag_logging": True,
            }
        }

    def test_process_launch_logged(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that process launches are logged.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Process launch logged" in results.stdout, "Process launch not logged"
        else:
            launch_logs = logs_info_level.get_logs(field="message", value="Process launch logged")
            assert len(launch_logs) > 0, "Process launch not logged"

    def test_state_transitions_logged(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that state transitions are logged.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "State transition logged" in results.stdout, "State transitions not logged"
        else:
            transition_logs = logs_info_level.get_logs(field="message", value="State transition logged")
            assert len(transition_logs) > 0, "State transitions not logged"

    def test_timestamp_present(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that log entries contain timestamps.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Log timestamp present" in results.stdout, "Timestamps not in logs"
        else:
            timestamp_logs = logs_info_level.get_logs(field="message", value="Log timestamp present")
            assert len(timestamp_logs) > 0, "Timestamps not in logs"

    def test_dag_logging(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that DAG (dependency graph) can be logged.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "DAG logged in human-readable format" in results.stdout, "DAG logging failed"
        else:
            dag_logs = logs_info_level.get_logs(field="message", value="DAG logged in human-readable format")
            assert len(dag_logs) > 0, "DAG logging failed"

    def test_interaction_logged(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that interactions with external monitors are logged.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "External monitor interaction logged" in results.stdout, "Interactions not logged"
        else:
            interaction_logs = logs_info_level.get_logs(field="message", value="External monitor interaction logged")
            assert len(interaction_logs) > 0, "Interactions not logged"
