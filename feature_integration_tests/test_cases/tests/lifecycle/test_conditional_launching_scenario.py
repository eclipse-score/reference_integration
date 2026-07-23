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
"""Scenario-level lifecycle tests for conditional launching.

These tests exercise the lifecycle scenario binaries directly and verify that
the scenario logs reflect the configured wait-condition prefixes and timing
values.
"""

from typing import Any

import pytest
from fit_scenario import ResultCode
from lifecycle_scenario import LifecycleScenario
from test_properties import add_test_properties
from testing_utils import ScenarioResult

pytestmark = [pytest.mark.parametrize("version", ["rust", "cpp"], scope="class")]


@add_test_properties(
    partially_verifies=[
        "feat_req__lifecycle__total_wait_time_support",
        "feat_req__lifecycle__polling_interval",
        "feat_req__lifecycle__path_condition_check",
        "feat_req__lifecycle__env_variable_cond_check",
        "feat_req__lifecycle__dependency_check",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestConditionalLaunchingScenario(LifecycleScenario):
    """Validate scenario-level conditional-launch parsing and logging."""

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.conditional_launching"

    @pytest.fixture(scope="class")
    def test_config(self) -> dict[str, Any]:
        return {
            "test": {
                "wait_conditions": [
                    "path:/tmp/lifecycle_launch_ready.flag",
                    "env:LM_CONDITION_READY",
                    "process:cpp_supervised_app",
                ],
                "polling_interval_ms": 123,
                "timeout_ms": 456,
            },
        }

    @staticmethod
    def _assert_logged_message(results: ScenarioResult, logs_info_level: Any, expected: str) -> None:
        log = None
        if hasattr(logs_info_level, "find_log"):
            log = logs_info_level.find_log("message", value=expected)
        if log is not None:
            return

        stdout = getattr(results, "stdout", None)
        if stdout is not None:
            assert expected in stdout, f"Expected scenario output to contain: {expected}\nstdout:\n{stdout}"
            return

        raise AssertionError(f"Could not verify scenario message: {expected}")

    def test_wait_condition_messages_are_logged(
        self,
        results: ScenarioResult,
        logs_info_level: Any,
        version: str,
    ) -> None:
        """Verify the scenario logs each supported condition prefix."""
        assert results.return_code == ResultCode.SUCCESS
        expected_messages = [
            "Testing conditional launching",
            "Checking path condition: /tmp/lifecycle_launch_ready.flag",
            "Checking env condition: LM_CONDITION_READY",
            "Checking process condition: cpp_supervised_app",
            "All dependencies satisfied",
        ]
        for expected in expected_messages:
            self._assert_logged_message(results, logs_info_level, expected)

    def test_timeout_and_polling_interval_are_logged(
        self,
        results: ScenarioResult,
        logs_info_level: Any,
        version: str,
    ) -> None:
        """Verify the scenario logs the configured wait timing values."""
        assert results.return_code == ResultCode.SUCCESS
        self._assert_logged_message(results, logs_info_level, "Polling interval: 123ms")
        self._assert_logged_message(results, logs_info_level, "Condition timeout: 456ms")
