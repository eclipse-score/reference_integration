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
        "logic_arc_int__lifecycle__deadline_monitor_if",
        "logical_monitor_if",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestLifecycleIpcDeadlineMonitorIf(FitScenario):
    """Validate deadline monitor checkpoint IPC between Health Monitor and Launch Manager."""

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.ipc_deadline_monitor_if"

    @pytest.fixture(scope="class", params=[True, False])
    def checkpoint_on_time(self, request: pytest.FixtureRequest) -> bool:
        return bool(request.param)

    @pytest.fixture(scope="class")
    def test_config(self, checkpoint_on_time: bool) -> dict[str, Any]:
        return {
            "test": {
                "checkpoint_on_time": checkpoint_on_time,
                "monitor_name": "deadline_monitor",
                "checkpoint_id": "cp_01",
            }
        }

    def test_deadline_monitor_interface_active(self, version: str, logs_info_level: LogContainer) -> None:
        """Ensure deadline monitor interface is active and target modules are connected."""
        assert version in ("rust", "cpp")

        interface_log = logs_info_level.find_log("event", value="deadline_monitor_if_ready")
        assert interface_log is not None, "Missing deadline_monitor_if_ready event"
        assert interface_log.status == "active"
        assert interface_log.monitor_name == "deadline_monitor"

    def test_checkpoint_ipc_routing(self, version: str, logs_info_level: LogContainer) -> None:
        """Verify checkpoint IPC message reaches Launch Manager from Health Monitor."""
        assert version in ("rust", "cpp")

        checkpoint_log = logs_info_level.find_log("event", value="checkpoint_ipc")
        assert checkpoint_log is not None, "Missing checkpoint_ipc event"
        assert checkpoint_log.checkpoint_id == "cp_01"
        assert checkpoint_log.source_component == "health_monitor"
        assert checkpoint_log.target_component == "launch_manager"

    def test_deadline_evaluation(
        self,
        version: str,
        checkpoint_on_time: bool,
        logs_info_level: LogContainer,
    ) -> None:
        """Validate on-time checkpoint acceptance and timeout handling behavior."""
        assert version in ("rust", "cpp")

        if checkpoint_on_time:
            accepted = logs_info_level.find_log("event", value="deadline_checkpoint_accepted")
            assert accepted is not None, "Expected deadline_checkpoint_accepted when checkpoint is on time"
            assert accepted.status == "accepted"
            assert accepted.reason == "within_deadline"

            timeout = logs_info_level.find_log("event", value="deadline_timeout")
            assert timeout is None, "deadline_timeout must not be emitted for on-time checkpoint"
            return

        timeout = logs_info_level.find_log("event", value="deadline_timeout")
        assert timeout is not None, "Expected deadline_timeout when checkpoint misses deadline"
        assert timeout.status == "timeout"
        assert timeout.reason == "checkpoint_missed"
