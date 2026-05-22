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
Feature integration tests for monitoring, notification, and recovery.

Tests verify that the Launch Manager can monitor processes, detect failures,
and execute recovery actions including watchdog support.
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
        "feat_req__lifecycle__monitor_abnormal_term",
        "feat_req__lifecycle__ext_monitor_notify",
        "feat_req__lifecycle__recovery_action_support",
        "feat_req__lifecycle__recov_run_target_switch",
        "feat_req__lifecycle__smart_watchdog_config",
        "feat_req__lifecycle__configurable_wait_time",
        "feat_req__lifecycle__monitoring_processes",
        "feat_req__lifecycle__failure_detect",
        "feat_req__lifecycle__liveliness_detection",
        "feat_req__lifecycle__process_monitoring",
        "feat_req__lifecycle__process_failure_react",
        "feat_req__lifecycle__multi_instance_support",
        "feat_req__lifecycle__lm_self_health_check",
        "feat_req__lifecycle__lm_ext_watchdog_notify",
        "feat_req__lifecycle__lm_ext_wdg_failed_test",
        "feat_req__lifecycle__lm_ext_watchdog_cfg",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestMonitoringAndRecovery(LifecycleScenario):
    """
    Verify monitoring, notification, and recovery support.

    This test confirms that the Launch Manager can monitor process health,
    detect failures, and execute recovery actions.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.monitoring_and_recovery"

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path) -> dict[str, Any]:
        return {
            "test": {
                "test_duration_ms": 400,
                "watchdog_interval_ms": 100,
                "recovery_wait_ms": 200,
                "max_restart_attempts": 3,
            }
        }

    def test_process_monitoring(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that process monitoring is active.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Process monitoring started" in results.stdout, "Process monitoring not started"
        else:
            monitoring_logs = logs_info_level.get_logs(field="message", value="Process monitoring started")
            assert len(monitoring_logs) > 0, "Process monitoring not started"

    def test_watchdog_configured(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that watchdog is configured.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Watchdog interval: 100ms" in results.stdout, "Watchdog not configured"
        else:
            watchdog_logs = logs_info_level.get_logs(field="message", pattern="Watchdog interval: 100ms")
            assert len(watchdog_logs) > 0, "Watchdog not configured"

    def test_liveliness_detection(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that liveliness detection works.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Liveliness check performed" in results.stdout, "Liveliness detection not performed"
        else:
            liveliness_logs = logs_info_level.get_logs(field="message", value="Liveliness check performed")
            assert len(liveliness_logs) > 0, "Liveliness detection not performed"

    def test_recovery_action_configured(
        self, results: ScenarioResult, logs_info_level: LogContainer, version: str
    ) -> None:
        """
        Verify that recovery action is configured.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Recovery action: restart (max 3 attempts)" in results.stdout, "Recovery action not configured"
        else:
            recovery_logs = logs_info_level.get_logs(
                field="message", pattern="Recovery action: restart \\(max 3 attempts\\)"
            )
            assert len(recovery_logs) > 0, "Recovery action not configured"

    def test_failure_detection(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that failure detection works.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Failure detection enabled" in results.stdout, "Failure detection not enabled"
        else:
            failure_logs = logs_info_level.get_logs(field="message", value="Failure detection enabled")
            assert len(failure_logs) > 0, "Failure detection not enabled"

    def test_external_notification(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that external notification works.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "External monitor notified" in results.stdout, "External notification failed"
        else:
            notify_logs = logs_info_level.get_logs(field="message", value="External monitor notified")
            assert len(notify_logs) > 0, "External notification failed"

    def test_self_health_check(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that Launch Manager self health check works.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Self health check passed" in results.stdout, "Self health check failed"
        else:
            health_logs = logs_info_level.get_logs(field="message", value="Self health check passed")
            assert len(health_logs) > 0, "Self health check failed"
