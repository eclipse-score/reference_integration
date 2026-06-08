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
Feature integration tests for run targets.

Tests verify that the Launch Manager supports run targets to group and
manage collections of processes.
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
        "feat_req__lifecycle__run_target_support",
        "feat_req__lifecycle__start_named_run_target",
        "feat_req__lifecycle__switch_run_targets",
        "feat_req__lifecycle__process_state_comm",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestRunTargets(LifecycleScenario):
    """
    Verify run target support.

    This test confirms that the Launch Manager can define and manage
    run targets for grouping processes.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.run_targets"

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path) -> dict[str, Any]:
        return {
            "test": {
                "test_duration_ms": 200,
                "run_targets": ["startup", "running", "shutdown"],
                "initial_target": "startup",
            }
        }

    def test_run_target_defined(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that run targets can be defined.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            for target in ["startup", "running", "shutdown"]:
                assert f"Run target defined: {target}" in results.stdout, f"Run target {target} not defined"
        else:
            for target in ["startup", "running", "shutdown"]:
                target_logs = logs_info_level.get_logs(field="message", pattern=f"Run target defined: {target}")
                assert len(target_logs) > 0, f"Run target {target} not defined"

    def test_run_target_started(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that run target can be started.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Starting run target: startup" in results.stdout, "Run target not started"
        else:
            start_logs = logs_info_level.get_logs(field="message", pattern="Starting run target: startup")
            assert len(start_logs) > 0, "Run target not started"

    def test_run_target_switch(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that switching between run targets works.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert (
                "Switching from startup to running" in results.stdout
                or "Switching run targets" in results.stdout
            ), "Run target switch failed"
        else:
            switch_logs = logs_info_level.get_logs(field="message", pattern="Switching run targets")
            assert len(switch_logs) > 0, "Run target switch failed"

    def test_process_state_communication(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that process state can be communicated.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Process state reported" in results.stdout, "Process state not reported"
        else:
            state_logs = logs_info_level.get_logs(field="message", value="Process state reported")
            assert len(state_logs) > 0, "Process state not reported"
