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

from typing import Any

import pytest
from fit_scenario import FitScenario
from test_properties import add_test_properties
from testing_utils import LogContainer

pytestmark = pytest.mark.parametrize("version", ["rust", "cpp"], scope="class")


@add_test_properties(
    partially_verifies=[
        "feat_req__lifecycle__process_logging_support",
        "feat_req__lifecycle__log_timestamp",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestLifecycleLoggingCorrelation(FitScenario):
    """Validate failure diagnostics correlated with timestamped daemon logs."""

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.logging_correlation"

    @pytest.fixture(scope="class", params=[True, False])
    def failure_detected(self, request: pytest.FixtureRequest) -> bool:
        return bool(request.param)

    @pytest.fixture(scope="class", params=[True, False])
    def daemon_timestamped_logs(self, request: pytest.FixtureRequest) -> bool:
        return bool(request.param)

    @pytest.fixture(scope="class")
    def test_config(self, failure_detected: bool, daemon_timestamped_logs: bool) -> dict[str, Any]:
        return {
            "test": {
                "failure_detected": failure_detected,
                "daemon_timestamped_logs": daemon_timestamped_logs,
                "daemon_name": "launch_manager_daemon",
            }
        }

    def test_process_logging_support_and_timestamp(
        self,
        version: str,
        daemon_timestamped_logs: bool,
        logs_info_level: LogContainer,
    ) -> None:
        """Ensure lifecycle process logging support and timestamp attributes are emitted."""
        assert version in ("rust", "cpp")

        support_log = logs_info_level.find_log("event", value="process_logging_support")
        assert support_log is not None, "Missing process_logging_support event"
        assert support_log.status == "enabled"
        assert support_log.daemon_name == "launch_manager_daemon"

        ts_log = logs_info_level.find_log("event", value="daemon_log_timestamp")
        assert ts_log is not None, "Missing daemon_log_timestamp event"
        assert ts_log.daemon_name == "launch_manager_daemon"

        if daemon_timestamped_logs:
            assert ts_log.timestamp_mode == "timestamped"
            return

        assert ts_log.timestamp_mode == "untimestamped"

    def test_failure_diagnostics_correlation(
        self,
        version: str,
        failure_detected: bool,
        daemon_timestamped_logs: bool,
        logs_info_level: LogContainer,
    ) -> None:
        """Verify diagnostics are correlated only when failures and timestamped daemon logs coexist."""
        assert version in ("rust", "cpp")

        if not failure_detected:
            no_failure = logs_info_level.find_log("event", value="failure_not_detected")
            assert no_failure is not None, "Expected failure_not_detected event"
            assert no_failure.action == "correlation_skipped"
            return

        if daemon_timestamped_logs:
            correlated = logs_info_level.find_log("event", value="failure_diagnostic_correlated")
            assert correlated is not None, "Expected failure_diagnostic_correlated event"
            assert correlated.status == "correlated"
            assert correlated.correlation_key == "pid:42@ts:1700000000"
            return

        failed = logs_info_level.find_log("event", value="failure_diagnostic_correlation_failed")
        assert failed is not None, "Expected failure_diagnostic_correlation_failed event"
        assert failed.status == "uncorrelated"
        assert failed.reason == "missing_timestamp"
