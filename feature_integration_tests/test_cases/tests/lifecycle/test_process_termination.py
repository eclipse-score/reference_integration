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
Feature integration tests for process termination.

Tests verify that the Launch Manager can terminate processes properly
with configurable timeouts and signal handling.
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
        "feat_req__lifecycle__configurable_timeout",
        "feat_req__lifecycle__process_termination",
        "feat_req__lifecycle__termination_dependency",
        "feat_req__lifecycle__time_to_wait_config",
        "feat_req__lifecycle__slow_shutdown_support",
        "feat_req__lifecycle__fast_shutdown_support",
        "feat_req__lifecycle__shutdown_signal",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestProcessTermination(LifecycleScenario):
    """
    Verify process termination support.

    This test confirms that the Launch Manager can terminate processes
    with proper signal handling and timeout configuration.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.process_termination"

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path) -> dict[str, Any]:
        return {
            "test": {
                "test_duration_ms": 200,
                "stop_timeout_ms": 1234,
                "sigterm_to_sigkill_delay_ms": 777,
            }
        }

    def test_stop_timeout_configured(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that stop timeout is configured.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Stop timeout: 1234ms" in results.stdout, "Stop timeout not configured"
        else:
            timeout_logs = logs_info_level.get_logs(field="message", pattern="Stop timeout: 1234ms")
            assert len(timeout_logs) > 0, "Stop timeout not configured"

    def test_signal_delay_configured(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that SIGTERM to SIGKILL delay is configured.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "SIGTERM to SIGKILL delay: 777ms" in results.stdout, "Signal delay not configured"
        else:
            delay_logs = logs_info_level.get_logs(field="message", pattern="SIGTERM to SIGKILL delay: 777ms")
            assert len(delay_logs) > 0, "Signal delay not configured"

    def test_graceful_shutdown(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that graceful shutdown works.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Graceful shutdown initiated" in results.stdout, "Graceful shutdown failed"
        else:
            shutdown_logs = logs_info_level.get_logs(field="message", value="Graceful shutdown initiated")
            assert len(shutdown_logs) > 0, "Graceful shutdown failed"

    def test_dependency_order_termination(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that processes are terminated in dependency order.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Terminating in dependency order" in results.stdout, "Dependency order termination not followed"
        else:
            order_logs = logs_info_level.get_logs(field="message", value="Terminating in dependency order")
            assert len(order_logs) > 0, "Dependency order termination not followed"

    def test_fast_shutdown(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that fast shutdown (without affecting processes) works.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Fast shutdown completed" in results.stdout, "Fast shutdown failed"
        else:
            fast_logs = logs_info_level.get_logs(field="message", value="Fast shutdown completed")
            assert len(fast_logs) > 0, "Fast shutdown failed"
