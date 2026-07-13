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
Feature integration tests for control interface support in lifecycle.

Tests verify that the Launch Manager can wait for custom conditions
signaled from applications via the Control Interface.
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
        "feat_req__lifecycle__custom_cond_support",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestControlInterfaceSupport(LifecycleScenario):
    """
    Verify control interface support for custom conditions.

    This test confirms that applications can signal custom conditions
    through the control interface API, enabling conditional launch sequences.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.control_interface_support"

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path) -> dict[str, Any]:
        return {
            "test": {
                "test_duration_ms": 200,
                "condition_name": "custom_startup_barrier",
            }
        }

    def test_custom_condition_signaled(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that custom condition was signaled via control interface.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Signaling custom condition: custom_startup_barrier" in results.stdout, (
                "Custom condition was not signaled"
            )
        else:
            condition_logs = logs_info_level.get_logs(
                field="message", pattern="Signaling custom condition: custom_startup_barrier"
            )
            assert len(condition_logs) > 0, "Custom condition was not signaled"

    def test_control_interface_integration(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that control interface API completed successfully.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Control interface signal completed" in results.stdout, "Control interface signal did not complete"
        else:
            completion_logs = logs_info_level.get_logs(field="message", value="Control interface signal completed")
            assert len(completion_logs) > 0, "Control interface signal did not complete"
