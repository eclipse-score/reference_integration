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
    partially_verifies=["logic_arc_int__lifecycle__controlif"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestLifecycleIpcControlIf(FitScenario):
    """Validate control/query IPC routing between lifecycle and communication layers."""

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.ipc_controlif"

    @pytest.fixture(scope="class", params=[True, False])
    def control_request_valid(self, request: pytest.FixtureRequest) -> bool:
        return bool(request.param)

    @pytest.fixture(scope="class", params=[True, False])
    def query_target_reachable(self, request: pytest.FixtureRequest) -> bool:
        return bool(request.param)

    @pytest.fixture(scope="class")
    def test_config(self, control_request_valid: bool, query_target_reachable: bool) -> dict[str, Any]:
        return {
            "test": {
                "control_request_valid": control_request_valid,
                "query_target_reachable": query_target_reachable,
                "control_target": "comm_control_router",
            }
        }

    def test_controlif_readiness(self, version: str, logs_info_level: LogContainer) -> None:
        """Verify the control interface path is announced as active."""
        assert version in ("rust", "cpp")

        ready_log = logs_info_level.find_log("event", value="controlif_ready")
        assert ready_log is not None, "Missing controlif_ready event"
        assert ready_log.status == "active"
        assert ready_log.control_target == "comm_control_router"

    def test_control_route_validation(
        self,
        version: str,
        control_request_valid: bool,
        logs_info_level: LogContainer,
    ) -> None:
        """Verify control IPC routing accepts only valid control requests."""
        assert version in ("rust", "cpp")

        if control_request_valid:
            routed = logs_info_level.find_log("event", value="control_route")
            assert routed is not None, "Expected control_route event for valid control request"
            assert routed.status == "routed"
            assert routed.reason == "valid_request"
            return

        rejected = logs_info_level.find_log("event", value="control_route_rejected")
        assert rejected is not None, "Expected control_route_rejected event for invalid control request"
        assert rejected.status == "rejected"
        assert rejected.reason == "invalid_request"

    def test_query_route_validation(
        self,
        version: str,
        query_target_reachable: bool,
        logs_info_level: LogContainer,
    ) -> None:
        """Verify query IPC routing behavior for reachable and unreachable targets."""
        assert version in ("rust", "cpp")

        if query_target_reachable:
            routed = logs_info_level.find_log("event", value="query_route")
            assert routed is not None, "Expected query_route event when query target is reachable"
            assert routed.status == "routed"
            assert routed.reason == "target_reachable"
            return

        failed = logs_info_level.find_log("event", value="query_route_failed")
        assert failed is not None, "Expected query_route_failed event when query target is unreachable"
        assert failed.status == "failed"
        assert failed.reason == "target_unreachable"
