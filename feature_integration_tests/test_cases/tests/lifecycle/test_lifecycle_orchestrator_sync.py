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
        "feat_req__lifecycle__run_target_support",
        "feat_req__lifecycle__switch_run_targets",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestLifecycleOrchestratorSync(FitScenario):
    """Ensure run-target transitions remain synchronized with orchestrator-visible process states."""

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.orchestrator_sync"

    @pytest.fixture(scope="class", params=[True, False])
    def run_target_switch_success(self, request: pytest.FixtureRequest) -> bool:
        return bool(request.param)

    @pytest.fixture(scope="class", params=[True, False])
    def orchestrator_state_synced(self, request: pytest.FixtureRequest) -> bool:
        return bool(request.param)

    @pytest.fixture(scope="class")
    def test_config(
        self,
        run_target_switch_success: bool,
        orchestrator_state_synced: bool,
    ) -> dict[str, Any]:
        return {
            "test": {
                "run_target_switch_success": run_target_switch_success,
                "orchestrator_state_synced": orchestrator_state_synced,
                "from_target": "Startup",
                "to_target": "Nominal",
            }
        }

    def test_run_target_support_announced(self, version: str, logs_info_level: LogContainer) -> None:
        """Verify lifecycle advertises run-target support to orchestrator integration layer."""
        assert version in ("rust", "cpp")

        support_log = logs_info_level.find_log("event", value="run_target_support")
        assert support_log is not None, "Missing run_target_support event"
        assert support_log.status == "enabled"

    def test_switch_and_orchestrator_sync(
        self,
        version: str,
        run_target_switch_success: bool,
        orchestrator_state_synced: bool,
        logs_info_level: LogContainer,
    ) -> None:
        """Validate switch result and whether orchestrator-visible states are synchronized."""
        assert version in ("rust", "cpp")

        if run_target_switch_success:
            switch_log = logs_info_level.find_log("event", value="run_target_switched")
            assert switch_log is not None, "Expected run_target_switched event"
            assert switch_log.from_target == "Startup"
            assert switch_log.to_target == "Nominal"
        else:
            switch_fail = logs_info_level.find_log("event", value="run_target_switch_failed")
            assert switch_fail is not None, "Expected run_target_switch_failed event"
            assert switch_fail.reason == "switch_rejected"

        if run_target_switch_success and orchestrator_state_synced:
            sync_ok = logs_info_level.find_log("event", value="orchestrator_state_sync_consistent")
            assert sync_ok is not None, "Expected orchestrator_state_sync_consistent event"
            assert sync_ok.status == "consistent"
            return

        sync_bad = logs_info_level.find_log("event", value="orchestrator_state_sync_inconsistent")
        assert sync_bad is not None, "Expected orchestrator_state_sync_inconsistent event"
        assert sync_bad.status == "inconsistent"

        if not run_target_switch_success:
            assert sync_bad.reason == "run_target_switch_failed"
            return

        assert sync_bad.reason == "orchestrator_state_desync"
