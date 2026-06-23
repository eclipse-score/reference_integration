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
Feature integration tests for process management.

Tests verify that the Launch Manager can manage processes including
adoption, multiple instances, and dependency management.
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
        "feat_req__lifecycle__running_processes",
        "feat_req__lifecycle__drop_supervsion",
        "feat_req__lifecycle__multi_start_support",
        "feat_req__lifecycle__consistent_dependencies",
        "feat_req__lifecycle__stop_process_dependents",
        "feat_req__lifecycle__stop_order_spec",
        "feat_req__lifecycle__oci_compliant",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestProcessManagement(LifecycleScenario):
    """
    Verify process management capabilities.

    This test confirms that the Launch Manager can adopt processes,
    manage multiple instances, and handle dependencies correctly.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.process_management"

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path) -> dict[str, Any]:
        return {
            "test": {
                "test_duration_ms": 250,
                "instance_count": 3,
                "process_name": "test_app",
            }
        }

    def test_process_adoption(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that process adoption works.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Adopted running process" in results.stdout, "Process adoption failed"
        else:
            adoption_logs = logs_info_level.get_logs(field="message", value="Adopted running process")
            assert len(adoption_logs) > 0, "Process adoption failed"

    def test_multiple_instances(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that multiple instances can be launched.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            for i in range(3):
                assert f"Instance {i} started" in results.stdout, f"Instance {i} did not start"
        else:
            for i in range(3):
                instance_logs = logs_info_level.get_logs(field="message", pattern=f"Instance {i} started")
                assert len(instance_logs) > 0, f"Instance {i} did not start"

    def test_dependency_validation(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that dependency validation works.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Dependencies validated" in results.stdout, "Dependency validation failed"
        else:
            validation_logs = logs_info_level.get_logs(field="message", value="Dependencies validated")
            assert len(validation_logs) > 0, "Dependency validation failed"

    def test_stop_order(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that stop order can be specified.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Stop order configured" in results.stdout, "Stop order not configured"
        else:
            stop_logs = logs_info_level.get_logs(field="message", value="Stop order configured")
            assert len(stop_logs) > 0, "Stop order not configured"
