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
Feature integration tests for control interface commands.

Tests verify that the Launch Manager provides control and query commands
for managing component states.
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
        "feat_req__lifecycle__control_commands",
        "feat_req__lifecycle__query_commands",
        "feat_req__lifecycle__controlif_status",
        "feat_req__lifecycle__request_run_target_start",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestControlInterfaceCommands(LifecycleScenario):
    """
    Verify control interface command support.

    This test confirms that the Launch Manager provides commands to
    control and query component states.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.control_interface_commands"

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path) -> dict[str, Any]:
        return {
            "test": {
                "test_duration_ms": 200,
                "commands": ["start", "stop", "status", "activate_run_target"],
            }
        }

    def test_control_commands_available(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that control commands are available.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Control commands available: start, stop, activate_run_target" in results.stdout, (
                "Control commands not available"
            )
        else:
            commands_logs = logs_info_level.get_logs(
                field="message", pattern="Control commands available: start, stop, activate_run_target"
            )
            assert len(commands_logs) > 0, "Control commands not available"

    def test_query_commands_available(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that query commands are available.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Query commands available: status" in results.stdout, "Query commands not available"
        else:
            query_logs = logs_info_level.get_logs(field="message", pattern="Query commands available: status")
            assert len(query_logs) > 0, "Query commands not available"

    def test_status_reporting(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that status reporting works.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Component status: running" in results.stdout, "Status reporting failed"
        else:
            status_logs = logs_info_level.get_logs(field="message", pattern="Component status: running")
            assert len(status_logs) > 0, "Status reporting failed"

    def test_run_target_activation(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that run target activation command works.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Run target activation command executed" in results.stdout, "Run target activation failed"
        else:
            activation_logs = logs_info_level.get_logs(field="message", value="Run target activation command executed")
            assert len(activation_logs) > 0, "Run target activation failed"
