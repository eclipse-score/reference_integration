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
        "logic_arc_int__lifecycle__lifecycle_if",
        "feat_req__lifecycle__process_state_comm",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestLifecycleApplicationIf(FitScenario):
    """Verify state reporting and daemon-gated signaling for lifecycle application interface."""

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.application_if"

    @pytest.fixture(scope="class", params=[True, False])
    def daemon_enabled(self, request: pytest.FixtureRequest) -> bool:
        return bool(request.param)

    @pytest.fixture(scope="class")
    def test_config(self, daemon_enabled: bool) -> dict[str, Any]:
        return {
            "test": {
                "daemon_enabled": daemon_enabled,
                "signal_name": "SIGUSR1",
            }
        }

    def test_application_state_is_reported(self, version: str, logs_info_level: LogContainer) -> None:
        """Ensure the SCORE application publishes a lifecycle state report."""
        assert version in ("rust", "cpp")
        app_state_log = logs_info_level.find_log("component", value="score_application")
        assert app_state_log is not None, "Missing SCORE application state report log"
        assert app_state_log.state == "state_reported"
        assert app_state_log.api == "lifecycle_if"

    def test_conditional_signal_path(
        self,
        version: str,
        daemon_enabled: bool,
        logs_info_level: LogContainer,
    ) -> None:
        """Verify signal dispatch behavior depends on daemon availability."""
        assert version in ("rust", "cpp")
        if daemon_enabled:
            daemon_log = logs_info_level.find_log("component", value="control_daemon")
            assert daemon_log is not None, "Missing control daemon running state log"
            assert daemon_log.state == "running"

            dispatched = logs_info_level.find_log("event", value="signal_dispatched")
            assert dispatched is not None, "Expected signal_dispatched log when daemon is running"
            assert dispatched.condition == "daemon_running"
            assert dispatched.signal_name == "SIGUSR1"
            assert dispatched.target_process == "score_application"
            return

        skipped = logs_info_level.find_log("event", value="signal_skipped")
        assert skipped is not None, "Expected signal_skipped log when daemon is not running"
        assert skipped.condition == "daemon_not_running"
        assert skipped.signal_name == "SIGUSR1"
        assert skipped.target_process == "score_application"
