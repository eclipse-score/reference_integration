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
Feature integration tests for parallel health monitoring.

Tests verify that multiple health monitors can operate independently
and concurrently, supporting parallel application supervision.
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
        "feat_req__lifecycle__parallel_launch_support",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestParallelLaunching(LifecycleScenario):
    """
    Verify parallel health monitoring with multiple independent monitors.

    This test confirms that multiple health monitors can run independently
    and in parallel, supporting concurrent application supervision.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.parallel_launching"

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path) -> dict[str, Any]:
        return {
            "test": {
                "test_duration_ms": 200,
                "checkpoint_count": 4,
            }
        }

    def test_parallel_monitors_started(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that all parallel monitors were started successfully.

        The test checks the logs to ensure each monitor was started
        and reported its deadline.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            # For C++ scenarios, check stdout directly
            for i in range(4):
                assert f"Parallel monitor {i} started deadline" in results.stdout, f"Parallel monitor {i} did not start"
        else:
            # Verify that all parallel monitors started
            for i in range(4):
                monitor_logs = logs_info_level.get_logs(
                    field="message", pattern=f"Parallel monitor {i} started deadline"
                )
                assert len(monitor_logs) > 0, f"Parallel monitor {i} did not start"

    def test_parallel_monitors_completed(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that all parallel monitors completed successfully.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            # For C++ scenarios, check stdout directly
            for i in range(4):
                assert f"Parallel monitor {i} completed" in results.stdout, f"Parallel monitor {i} did not complete"
            assert "parallel monitors completed successfully" in results.stdout, (
                "Not all parallel monitors completed successfully"
            )
        else:
            # Verify that all monitors completed
            for i in range(4):
                completion_logs = logs_info_level.get_logs(field="message", pattern=f"Parallel monitor {i} completed")
                assert len(completion_logs) > 0, f"Parallel monitor {i} did not complete"

            # Verify final confirmation
            final_logs = logs_info_level.get_logs(
                field="message", pattern=r"All \d+ parallel monitors completed successfully"
            )
            assert len(final_logs) > 0, "No final confirmation of parallel completion"
