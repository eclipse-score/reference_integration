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
Feature integration tests for lifecycle client API integration.

Tests verify that applications can properly integrate with the lifecycle
framework by reporting execution states to the Launch Manager.
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
        "feat_req__lifecycle__launch_support",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestProcessLaunchingSupport(LifecycleScenario):
    """
    Verify that applications can report execution state to Launch Manager.

    This test confirms that the lifecycle client API allows applications to
    properly signal their execution state, which is essential for Launch Manager
    to monitor and manage application lifecycles.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.process_launching_support"

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path) -> dict[str, Any]:
        return {
            "test": {
                "test_duration_ms": 100,
                "checkpoint_count": 3,
            }
        }

    def test_execution_state_reported(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that the lifecycle client API was called.

        The lifecycle client API integration is demonstrated even when
        Launch Manager is not available in the test environment.
        """
        assert results.return_code == ResultCode.SUCCESS

        # Verify that lifecycle client API was called
        if version == "cpp":
            assert "Lifecycle client API called" in results.stdout, "Lifecycle client API was not called"
        else:
            api_logs = logs_info_level.get_logs(field="message", pattern="Lifecycle client API called")
            assert len(api_logs) > 0, "Lifecycle client API was not called"

    def test_lifecycle_client_integration(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that lifecycle client integration completed successfully.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Testing lifecycle client API integration" in results.stdout, (
                "Lifecycle client integration test not started"
            )
            assert "Application completed successfully" in results.stdout, "Application did not complete successfully"
        else:
            integration_logs = logs_info_level.get_logs(
                field="message", value="Testing lifecycle client API integration"
            )
            assert len(integration_logs) > 0, "Lifecycle client integration test not started"

            completion_logs = logs_info_level.get_logs(field="message", value="Application completed successfully")
            assert len(completion_logs) > 0, "Application did not complete successfully"
