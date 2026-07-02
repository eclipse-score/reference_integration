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
        "feat_req__lifecycle__dependency_check",
        "feat_req__lifecycle__check_dependency_exec",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestLifecycleCommDependencyActivation(FitScenario):
    """Verify communication component activation is gated by dependency checks and executability."""

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.comm_dependency_activation"

    @pytest.fixture(scope="class", params=[True, False])
    def dependency_available(self, request: pytest.FixtureRequest) -> bool:
        return bool(request.param)

    @pytest.fixture(scope="class", params=[True, False])
    def dependency_executable(self, request: pytest.FixtureRequest) -> bool:
        return bool(request.param)

    @pytest.fixture(scope="class")
    def test_config(self, dependency_available: bool, dependency_executable: bool) -> dict[str, Any]:
        return {
            "test": {
                "dependency_available": dependency_available,
                "dependency_executable": dependency_executable,
                "component": "comm_router",
            }
        }

    def test_dependency_checks_are_reported(
        self,
        version: str,
        dependency_available: bool,
        dependency_executable: bool,
        logs_info_level: LogContainer,
    ) -> None:
        """Ensure lifecycle emits dependency presence and execution-check diagnostics."""
        assert version in ("rust", "cpp")

        dep_log = logs_info_level.find_log("event", value="dependency_check")
        assert dep_log is not None, "Missing dependency_check event"
        assert dep_log.component == "comm_router"
        assert dep_log.available is dependency_available

        exec_log = logs_info_level.find_log("event", value="dependency_exec_check")
        assert exec_log is not None, "Missing dependency_exec_check event"
        assert exec_log.component == "comm_router"
        assert exec_log.executable is dependency_executable

    def test_activation_is_dependency_gated(
        self,
        version: str,
        dependency_available: bool,
        dependency_executable: bool,
        logs_info_level: LogContainer,
    ) -> None:
        """Verify comm activation only happens when dependency exists and can execute."""
        assert version in ("rust", "cpp")

        can_activate = dependency_available and dependency_executable

        if can_activate:
            active_log = logs_info_level.find_log("event", value="comm_activation")
            assert active_log is not None, "Expected comm_activation event when dependency checks pass"
            assert active_log.status == "activated"
            assert active_log.reason == "dependency_ready"

            blocked_log = logs_info_level.find_log("event", value="comm_activation_blocked")
            assert blocked_log is None, "comm_activation_blocked must not be emitted when activation succeeds"
            return

        blocked_log = logs_info_level.find_log("event", value="comm_activation_blocked")
        assert blocked_log is not None, "Expected comm_activation_blocked event when dependency checks fail"
        assert blocked_log.status == "blocked"

        if not dependency_available:
            assert blocked_log.reason == "dependency_missing"
            return

        assert blocked_log.reason == "dependency_not_executable"
