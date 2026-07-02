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
        "feat_req__lifecycle__secpol_non_root",
        "feat_req__lifecycle__support_secpol_type",
        "feat_req__security__sandbox_isolation",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestLifecycleSecurityIsolation(FitScenario):
    """Validate security policy enforcement and privilege isolation across lifecycle/security modules."""

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.security_isolation"

    @pytest.fixture(scope="class", params=["strict", "unknown_type"])
    def secpol_type(self, request: pytest.FixtureRequest) -> str:
        return str(request.param)

    @pytest.fixture(scope="class", params=[True, False])
    def run_as_root_attempt(self, request: pytest.FixtureRequest) -> bool:
        return bool(request.param)

    @pytest.fixture(scope="class")
    def test_config(self, secpol_type: str, run_as_root_attempt: bool) -> dict[str, Any]:
        return {
            "test": {
                "secpol_type": secpol_type,
                "run_as_root_attempt": run_as_root_attempt,
            }
        }

    def test_secpol_type_support(self, version: str, secpol_type: str, logs_info_level: LogContainer) -> None:
        """Verify supported/unsupported secpol type handling from lifecycle to security integration."""
        assert version in ("rust", "cpp")

        policy_log = logs_info_level.find_log("component", value="security_crypto")
        assert policy_log is not None, "Missing security/crypto policy log"
        assert policy_log.policy_domain == "secpol"
        assert policy_log.secpol_type == secpol_type

        support_log = logs_info_level.find_log("event", value="secpol_type_support")
        assert support_log is not None, "Missing secpol_type_support event"
        if secpol_type == "strict":
            assert support_log.status == "accepted"
            assert support_log.supported is True
            return

        assert support_log.status == "rejected"
        assert support_log.supported is False

    def test_non_root_enforcement_and_sandbox_isolation(
        self,
        version: str,
        run_as_root_attempt: bool,
        logs_info_level: LogContainer,
    ) -> None:
        """Verify non-root policy enforcement and sandbox isolation status."""
        assert version in ("rust", "cpp")

        non_root_log = logs_info_level.find_log("event", value="non_root_enforced")
        assert non_root_log is not None, "Missing non_root_enforced event"
        assert int(non_root_log.effective_uid) != 0

        if run_as_root_attempt:
            attempt_log = logs_info_level.find_log("event", value="privilege_escalation_attempt")
            assert attempt_log is not None, "Missing privilege_escalation_attempt event"
            assert int(attempt_log.requested_uid) == 0
            assert non_root_log.status == "denied_root"
        else:
            assert non_root_log.status == "non_root_ok"

        sandbox_log = logs_info_level.find_log("event", value="sandbox_isolation")
        assert sandbox_log is not None, "Missing sandbox_isolation event"
        assert sandbox_log.status == "active"
        assert sandbox_log.boundary == "process_container"
