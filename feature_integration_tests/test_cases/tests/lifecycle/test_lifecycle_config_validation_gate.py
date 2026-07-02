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
        "feat_req__lifecycle__offline_config_valid",
        "feat_req__lifecycle__consistent_dependencies",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestLifecycleConfigValidationGate(FitScenario):
    """Verify invalid lifecycle configs are rejected offline and valid configs stay executable."""

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.config_validation_gate"

    @pytest.fixture(scope="class", params=[True, False])
    def config_schema_valid(self, request: pytest.FixtureRequest) -> bool:
        return bool(request.param)

    @pytest.fixture(scope="class", params=[True, False])
    def dependencies_consistent(self, request: pytest.FixtureRequest) -> bool:
        return bool(request.param)

    @pytest.fixture(scope="class")
    def test_config(self, config_schema_valid: bool, dependencies_consistent: bool) -> dict[str, Any]:
        return {
            "test": {
                "config_schema_valid": config_schema_valid,
                "dependencies_consistent": dependencies_consistent,
            }
        }

    def test_offline_validation_gate(
        self,
        version: str,
        config_schema_valid: bool,
        dependencies_consistent: bool,
        logs_info_level: LogContainer,
    ) -> None:
        """Validate offline gate outcome based on config schema and dependency consistency."""
        assert version in ("rust", "cpp")

        gate_log = logs_info_level.find_log("event", value="offline_config_validation")
        assert gate_log is not None, "Missing offline_config_validation event"
        assert gate_log.schema_valid is config_schema_valid
        assert gate_log.dependencies_consistent is dependencies_consistent

        is_valid = config_schema_valid and dependencies_consistent
        if is_valid:
            assert gate_log.status == "accepted"
            return

        assert gate_log.status == "rejected"

    def test_executable_outcome(
        self,
        version: str,
        config_schema_valid: bool,
        dependencies_consistent: bool,
        logs_info_level: LogContainer,
    ) -> None:
        """Verify executable path for valid config and rejection path for invalid config."""
        assert version in ("rust", "cpp")

        is_valid = config_schema_valid and dependencies_consistent
        if is_valid:
            executable_log = logs_info_level.find_log("event", value="lifecycle_config_executable")
            assert executable_log is not None, "Expected lifecycle_config_executable event for valid config"
            assert executable_log.status == "executable"

            rejected_log = logs_info_level.find_log("event", value="lifecycle_config_rejected")
            assert rejected_log is None, "lifecycle_config_rejected must not be emitted for valid config"
            return

        rejected_log = logs_info_level.find_log("event", value="lifecycle_config_rejected")
        assert rejected_log is not None, "Expected lifecycle_config_rejected event for invalid config"
        assert rejected_log.status == "rejected"

        if not config_schema_valid:
            assert rejected_log.reason == "invalid_schema"
            return

        assert rejected_log.reason == "inconsistent_dependencies"
