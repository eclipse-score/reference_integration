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
Feature integration tests for debug mode and terminal support.

Tests verify that the Launch Manager supports launching processes in debug mode,
with debugger waiting state, and terminal/session leader support.
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
        "feat_req__lifecycle__debug_support",
        "feat_req__lifecycle__support_held_state",
        "feat_req__lifecycle__terminal_support",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestDebugAndTerminal(LifecycleScenario):
    """
    Verify debug mode and terminal support.

    This test confirms that processes can be launched in debug mode
    and as terminal/session leaders.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.debug_and_terminal"

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path) -> dict[str, Any]:
        return {
            "test": {
                "test_duration_ms": 150,
                "debug_mode": True,
                "wait_for_debugger": True,
                "create_session": True,
            }
        }

    def test_debug_mode_enabled(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that debug mode can be enabled.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Debug mode enabled" in results.stdout, "Debug mode not enabled"
        else:
            debug_logs = logs_info_level.get_logs(field="message", value="Debug mode enabled")
            assert len(debug_logs) > 0, "Debug mode not enabled"

    def test_debugger_wait_state(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that process can wait for debugger connection.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Waiting for debugger connection" in results.stdout, "Debugger wait state not supported"
        else:
            wait_logs = logs_info_level.get_logs(field="message", value="Waiting for debugger connection")
            assert len(wait_logs) > 0, "Debugger wait state not supported"

    def test_terminal_session_leader(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that process can be launched as session leader.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Launched as session leader" in results.stdout, "Session leader creation failed"
        else:
            session_logs = logs_info_level.get_logs(field="message", value="Launched as session leader")
            assert len(session_logs) > 0, "Session leader creation failed"


@add_test_properties(
    partially_verifies=[
        "feat_req__lifecycle__debug_support",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestDebugModeDisabled(LifecycleScenario):
    """
    Verify that debug mode and terminal support flags are actually config-driven,
    by disabling them and asserting the negative-path messages.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.debug_and_terminal"

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path) -> dict[str, Any]:
        return {
            "test": {
                "test_duration_ms": 150,
                "debug_mode": False,
                "wait_for_debugger": False,
                "create_session": False,
            }
        }

    def test_debug_mode_disabled(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that debug mode can be disabled via configuration.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Debug mode disabled" in results.stdout, "Debug mode was not disabled"
        else:
            debug_logs = logs_info_level.get_logs(field="message", value="Debug mode disabled")
            assert len(debug_logs) > 0, "Debug mode was not disabled"

    def test_debugger_wait_disabled(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that waiting for a debugger can be disabled via configuration.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Not waiting for debugger connection" in results.stdout, "Debugger wait was not disabled"
        else:
            wait_logs = logs_info_level.get_logs(field="message", value="Not waiting for debugger connection")
            assert len(wait_logs) > 0, "Debugger wait was not disabled"

    def test_session_leader_disabled(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that session leader creation can be disabled via configuration.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Launched without new session" in results.stdout, "Session leader path not disabled"
        else:
            session_logs = logs_info_level.get_logs(field="message", value="Launched without new session")
            assert len(session_logs) > 0, "Session leader path not disabled"
