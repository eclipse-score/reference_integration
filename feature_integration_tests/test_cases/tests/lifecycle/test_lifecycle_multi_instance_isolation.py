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
    partially_verifies=["feat_req__lifecycle__multi_instance_support"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestLifecycleMultiInstanceIsolation(FitScenario):
    """Validate supervision and monitoring isolation across multiple Launch Manager instances."""

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.multi_instance_isolation"

    @pytest.fixture(scope="class", params=[True, False])
    def cross_instance_interference(self, request: pytest.FixtureRequest) -> bool:
        return bool(request.param)

    @pytest.fixture(scope="class")
    def test_config(self, cross_instance_interference: bool) -> dict[str, Any]:
        return {
            "test": {
                "instance_a": "lm_instance_a",
                "instance_b": "lm_instance_b",
                "cross_instance_interference": cross_instance_interference,
            }
        }

    def test_instances_are_announced(self, version: str, logs_info_level: LogContainer) -> None:
        """Ensure both lifecycle instances are visible and independently monitored."""
        assert version in ("rust", "cpp")

        a_log = logs_info_level.find_log("event", value="instance_registered_a")
        assert a_log is not None, "Missing registration log for instance A"
        assert a_log.instance_name == "lm_instance_a"

        b_log = logs_info_level.find_log("event", value="instance_registered_b")
        assert b_log is not None, "Missing registration log for instance B"
        assert b_log.instance_name == "lm_instance_b"

    def test_supervision_and_monitoring_isolation(
        self,
        version: str,
        cross_instance_interference: bool,
        logs_info_level: LogContainer,
    ) -> None:
        """Verify supervision events remain isolated unless deliberate interference is injected."""
        assert version in ("rust", "cpp")

        if cross_instance_interference:
            violated = logs_info_level.find_log("event", value="instance_isolation_violated")
            assert violated is not None, "Expected instance_isolation_violated under interference"
            assert violated.status == "violated"
            assert violated.reason == "cross_instance_interference"
            return

        isolated = logs_info_level.find_log("event", value="instance_isolation_ok")
        assert isolated is not None, "Expected instance_isolation_ok when no interference is present"
        assert isolated.status == "isolated"
        assert isolated.supervision_scope == "per_instance"

        violated = logs_info_level.find_log("event", value="instance_isolation_violated")
        assert violated is None, "instance_isolation_violated must not be emitted for isolated flow"
