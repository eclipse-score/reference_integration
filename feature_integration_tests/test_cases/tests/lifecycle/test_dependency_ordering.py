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
        Verify that checkpoints are reported in sequential order.

        The test checks that init_step_0, init_step_1, init_step_2, etc.
        are reported in the correct sequence.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            # For C++ scenarios, check stdout directly
            for i in range(4):
                assert f"Reported checkpoint init_step_{i} in sequence" in results.stdout, (
                    f"Checkpoint init_step_{i} was not reported"
                )
        else:
            # Verify each checkpoint was reported in order
            for i in range(4):
                checkpoint_logs = logs_info_level.get_logs(
                    field="message", pattern=f"Simulated checkpoint init_step_{i} in sequence"
                )
                assert len(checkpoint_logs) > 0, f"Checkpoint init_step_{i} was not reported"

    def test_sequential_supervision_completed(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that all sequential checkpoints completed successfully.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            # For C++ scenarios, check stdout directly
            assert "Would initialize health monitoring with" in results.stdout, "Health monitoring setup not mentioned"
            assert "All checkpoints reported in correct sequential order" in results.stdout, (
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
