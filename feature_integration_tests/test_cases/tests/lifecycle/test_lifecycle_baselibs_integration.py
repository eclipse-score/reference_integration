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
        "feat_req__baselibs__structured_logging",
        "feat_req__baselibs__json_serialization",
        "feat_req__baselibs__monotonic_time_measurement",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestLifecycleBaselibsIntegration(FitScenario):
    """Verify lifecycle flow integrates with common baselibs utilities."""

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.baselibs_integration"

    @pytest.fixture(scope="class", params=[True, False])
    def json_payload_valid(self, request: pytest.FixtureRequest) -> bool:
        return bool(request.param)

    @pytest.fixture(scope="class", params=[True, False])
    def log_backend_ready(self, request: pytest.FixtureRequest) -> bool:
        return bool(request.param)

    @pytest.fixture(scope="class", params=["valid", "missing", "malformed"])
    def deadline_budget_mode(self, request: pytest.FixtureRequest) -> str:
        return str(request.param)

    @pytest.fixture(scope="class")
    def test_config(
        self,
        json_payload_valid: bool,
        log_backend_ready: bool,
        deadline_budget_mode: str,
    ) -> dict[str, Any]:
        config = {
            "test": {
                "json_payload_valid": json_payload_valid,
                "log_backend_ready": log_backend_ready,
            }
        }
        if deadline_budget_mode == "valid":
            config["test"]["deadline_budget_ms"] = 20
        elif deadline_budget_mode == "malformed":
            config["test"]["deadline_budget_ms"] = "invalid"

        return config

    def test_common_baselibs_utility_usage(
        self,
        version: str,
        json_payload_valid: bool,
        log_backend_ready: bool,
        deadline_budget_mode: str,
        logs_info_level: LogContainer,
    ) -> None:
        """Ensure lifecycle invokes logging, JSON processing and monotonic timing utilities."""
        assert version in ("rust", "cpp")

        bootstrap_log = logs_info_level.find_log("event", value="lifecycle_baselibs_bootstrap")
        assert bootstrap_log is not None, "Missing lifecycle_baselibs_bootstrap event"
        assert bootstrap_log.used_logging is log_backend_ready
        assert bootstrap_log.used_json is json_payload_valid
        assert bootstrap_log.used_monotonic_clock is True

        timing_log = logs_info_level.find_log("event", value="lifecycle_baselibs_timing")
        assert timing_log is not None, "Missing lifecycle_baselibs_timing event"
        if deadline_budget_mode == "valid":
            assert timing_log.deadline_budget_ms == 20
        else:
            assert timing_log.deadline_budget_ms == 0

        assert timing_log.measured_duration_ms >= 0

        json_log = logs_info_level.find_log("event", value="lifecycle_baselibs_json")
        assert json_log is not None, "Missing lifecycle_baselibs_json event"
        assert json_log.valid is json_payload_valid

    def test_integration_outcome(
        self,
        version: str,
        json_payload_valid: bool,
        log_backend_ready: bool,
        logs_info_level: LogContainer,
    ) -> None:
        """Validate successful integration only when JSON payload and logging backend are ready."""
        assert version in ("rust", "cpp")

        integrated = json_payload_valid and log_backend_ready
        status_log = logs_info_level.find_log("event", value="lifecycle_baselibs_integration_status")
        assert status_log is not None, "Missing lifecycle_baselibs_integration_status event"
        assert status_log.status == ("integrated" if integrated else "degraded")

        degraded_log = logs_info_level.find_log("event", value="lifecycle_baselibs_degraded")
        if integrated:
            assert degraded_log is None, "lifecycle_baselibs_degraded must not be emitted on integrated path"
            return

        assert degraded_log is not None, "Expected lifecycle_baselibs_degraded event on degraded path"
        if not json_payload_valid:
            assert degraded_log.reason == "invalid_json_payload"
            return

        assert degraded_log.reason == "logging_backend_unavailable"
