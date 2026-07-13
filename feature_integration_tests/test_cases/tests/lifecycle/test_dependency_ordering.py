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
Feature integration tests for health monitoring with sequential checkpoints.

Tests verify health monitoring APIs support ordered checkpoint reporting
which enables dependency-based application initialization sequences.
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
        "feat_req__lifecycle__process_ordering",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestDependencyOrdering(LifecycleScenario):
    """
    Verify health monitoring with sequential checkpoint reporting.

    This test confirms that applications can report checkpoints in a specific
    order using logical supervision, which supports ordered initialization
    and dependency-based startup sequences.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.dependency_ordering"

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path) -> dict[str, Any]:
        return {
            "test": {
                "test_duration_ms": 300,
                "checkpoint_count": 4,
            }
        }

    def test_sequential_checkpoints_reported(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that checkpoints are reported in sequential (non-decreasing index) order.

        The test locates the emission position of each init_step_{i} marker and
        asserts those positions are sorted, so an out-of-order emission would fail.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            # For C++ scenarios, check stdout directly and record emission order.
            lines = results.stdout.splitlines()
            positions = []
            for i in range(4):
                marker = f"Simulated checkpoint init_step_{i} in sequence"
                matching = [idx for idx, line in enumerate(lines) if marker in line]
                assert len(matching) > 0, f"Checkpoint init_step_{i} was not reported"
                positions.append(matching[0])
        else:
            # Verify each checkpoint was reported and capture its log sequence index.
            messages = [entry.message for entry in logs_info_level]
            positions = []
            for i in range(4):
                marker = f"Simulated checkpoint init_step_{i} in sequence"
                matching = [idx for idx, message in enumerate(messages) if marker in message]
                assert len(matching) > 0, f"Checkpoint init_step_{i} was not reported"
                positions.append(matching[0])

        assert positions == sorted(positions), f"Checkpoints were not reported in non-decreasing order: {positions}"

    def test_sequential_supervision_completed(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that all sequential checkpoints completed successfully.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            # For C++ scenarios, check stdout directly
            assert "Health monitor initialized with" in results.stdout, "Health monitoring setup not mentioned"
            assert "All checkpoints simulated in correct sequential order" in results.stdout, (
                "No confirmation of sequential checkpoint reporting"
            )
        else:
            # Verify health monitor was initialized
            init_logs = logs_info_level.get_logs(
                field="message", pattern="Health monitor initialized with.*sequential deadline monitors"
            )
            assert len(init_logs) > 0, "Health monitor not initialized"

            completion_logs = logs_info_level.get_logs(
                field="message", value="All checkpoints simulated in correct sequential order"
            )
            assert len(completion_logs) > 0, "No confirmation of sequential checkpoint reporting"
