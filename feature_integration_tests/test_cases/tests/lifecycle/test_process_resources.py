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
Feature integration tests for process resource management.

Tests verify that the Launch Manager can configure process resources
including priority, scheduling policy, CPU affinity, and resource limits.
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
        "feat_req__lifecycle__launch_priority_support",
        "feat_req__lifecycle__scheduling_policy",
        "feat_req__lifecycle__runmask_support",
        "feat_req__lifecycle__process_rlimit_support",
        "feat_req__lifecycle__aslr_support",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestProcessResources(LifecycleScenario):
    """
    Verify process resource management configuration.

    This test confirms that processes can be launched with specific
    resource constraints including priority, scheduling, and limits.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.process_resources"

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path) -> dict[str, Any]:
        return {
            "test": {
                "test_duration_ms": 150,
                "priority": 10,
                "scheduling_policy": "SCHED_RR",
                "cpu_affinity": [0, 1],
            }
        }

    def test_priority_configured(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that process priority is configured.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Process priority: 10" in results.stdout, "Process priority not configured"
        else:
            priority_logs = logs_info_level.get_logs(field="message", pattern="Process priority: 10")
            assert len(priority_logs) > 0, "Process priority not configured"

    def test_scheduling_policy(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that scheduling policy is configured.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Scheduling policy: SCHED_RR" in results.stdout, "Scheduling policy not configured"
        else:
            sched_logs = logs_info_level.get_logs(field="message", pattern="Scheduling policy: SCHED_RR")
            assert len(sched_logs) > 0, "Scheduling policy not configured"

    def test_cpu_affinity(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that CPU affinity (runmask) is configured.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "CPU affinity: [0, 1]" in results.stdout, "CPU affinity not configured"
        else:
            affinity_logs = logs_info_level.get_logs(field="message", pattern="CPU affinity: \\[0, 1\\]")
            assert len(affinity_logs) > 0, "CPU affinity not configured"

    def test_resource_limits(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that resource limits are configured.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Resource limits applied" in results.stdout, "Resource limits not applied"
        else:
            rlimit_logs = logs_info_level.get_logs(field="message", value="Resource limits applied")
            assert len(rlimit_logs) > 0, "Resource limits not applied"
