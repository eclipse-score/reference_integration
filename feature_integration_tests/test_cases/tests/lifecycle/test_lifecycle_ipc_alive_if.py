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
        "logic_arc_int__lifecycle__alive_if",
        "feat_req__lifecycle__liveliness_detection",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestLifecycleIpcAliveIf(FitScenario):
    """Verify heartbeat IPC between Health Monitor and Launch Manager with failure propagation."""

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.ipc_alive_if"

    @pytest.fixture(scope="class", params=[True, False])
    def heartbeat_alive(self, request: pytest.FixtureRequest) -> bool:
        return bool(request.param)

    @pytest.fixture(scope="class")
    def test_config(self, heartbeat_alive: bool) -> dict[str, Any]:
        return {
            "test": {
                "heartbeat_alive": heartbeat_alive,
                "failure_action": "switch_to_safe_state",
            }
        }

    def test_alive_if_link_is_active(self, version: str, logs_info_level: LogContainer) -> None:
        """Ensure Launch Manager reports the alive_if link as active."""
        assert version in ("rust", "cpp")

        launch_manager_log = logs_info_level.find_log("component", value="launch_manager")
        assert launch_manager_log is not None, "Missing Launch Manager lifecycle log"
        assert launch_manager_log.api == "alive_if"

        ipc_log = logs_info_level.find_log("event", value="heartbeat_ipc")
        assert ipc_log is not None, "Missing heartbeat IPC log"
        assert ipc_log.status == "active"

    def test_liveliness_detection_and_failure_propagation(
        self,
        version: str,
        heartbeat_alive: bool,
        logs_info_level: LogContainer,
    ) -> None:
        """Verify healthy heartbeat path and timeout propagation path."""
        assert version in ("rust", "cpp")

        if heartbeat_alive:
            healthy_log = logs_info_level.find_log("event", value="liveliness_ok")
            assert healthy_log is not None, "Expected liveliness_ok event when heartbeat is present"
            assert healthy_log.source_component == "health_monitor"
            assert healthy_log.propagated_to == "launch_manager"

            failure_log = logs_info_level.find_log("event", value="failure_propagated")
            assert failure_log is None, "failure_propagated must not be emitted for healthy heartbeat"
            return

        failed_log = logs_info_level.find_log("event", value="liveliness_failed")
        assert failed_log is not None, "Expected liveliness_failed event when heartbeat times out"
        assert failed_log.source_component == "health_monitor"
        assert failed_log.propagated_to == "launch_manager"

        propagated_log = logs_info_level.find_log("event", value="failure_propagated")
        assert propagated_log is not None, "Expected failure_propagated event for heartbeat timeout"
        assert propagated_log.action == "switch_to_safe_state"
        assert propagated_log.reason == "heartbeat_timeout"
