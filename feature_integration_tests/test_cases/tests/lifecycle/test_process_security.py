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
"""
Feature integration tests for process security and privilege management.

Tests verify that the Launch Manager can configure process security settings
including UID/GID, capabilities, security policies, and supplementary groups.
"""

from pathlib import Path
from typing import Any

import pytest
from fit_scenario import ResultCode
from lifecycle_scenario import LifecycleScenario
from test_properties import add_test_properties
from testing_utils import LogContainer, ScenarioResult

pytestmark = pytest.mark.parametrize("version", ["rust", "cpp"], scope="class")


@add_test_properties(
    partially_verifies=[
        "feat_req__lifecycle__uid_gid_support",
        "feat_req__lifecycle__capability_support",
        "feat_req__lifecycle__support_secpol_type",
        "feat_req__lifecycle__secpol_non_root",
        "feat_req__lifecycle__supplementary_groups",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestProcessSecurity(LifecycleScenario):
    """
    Verify process security and privilege configuration.

    This test confirms that processes can be launched with specific
    security settings including user/group IDs, capabilities, and policies.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.process_security"

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path) -> dict[str, Any]:
        return {
            "test": {
                "test_duration_ms": 150,
                "uid": 1000,
                "gid": 1000,
                "supplementary_groups": [100, 200],
            }
        }

    def test_uid_gid_configured(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that UID/GID configuration is applied.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Process UID: 1000, GID: 1000" in results.stdout, "UID/GID not configured correctly"
        else:
            uid_gid_logs = logs_info_level.get_logs(field="message", pattern="Process UID: 1000, GID: 1000")
            assert len(uid_gid_logs) > 0, "UID/GID not configured correctly"

    def test_supplementary_groups(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that supplementary groups are configured.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Supplementary groups: [100, 200]" in results.stdout, "Supplementary groups not configured"
        else:
            groups_logs = logs_info_level.get_logs(field="message", pattern="Supplementary groups: \\[100, 200\\]")
            assert len(groups_logs) > 0, "Supplementary groups not configured"

    def test_security_policy(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that security policy configuration is applied.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Security policy applied" in results.stdout, "Security policy not applied"
        else:
            policy_logs = logs_info_level.get_logs(field="message", value="Security policy applied")
            assert len(policy_logs) > 0, "Security policy not applied"
