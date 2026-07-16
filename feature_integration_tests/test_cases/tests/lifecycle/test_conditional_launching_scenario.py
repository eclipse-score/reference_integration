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
"""Scenario-level lifecycle tests for conditional launching.

Unlike scenario logging smoke tests, these exercise the scenario binary's actual
wait-condition evaluation: preconditions (a path, an env var, a running process) are
really established or really withheld, so the assertions verify that the scenario
observes and enforces them, not merely that it echoes back what was configured.
"""

import os
import subprocess
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from fit_scenario import ResultCode
from lifecycle_scenario import LifecycleScenario
from test_properties import add_test_properties
from testing_utils import ScenarioResult

pytestmark = [pytest.mark.parametrize("version", ["rust", "cpp"], scope="class")]

_CONDITION_ENV_VAR = "LM_CONDITION_READY"
_CONDITION_PROCESS_NAME = "sleep"


@add_test_properties(
    partially_verifies=[
        "feat_req__lifecycle__total_wait_time_support",
        "feat_req__lifecycle__polling_interval",
        "feat_req__lifecycle__path_condition_check",
        "feat_req__lifecycle__env_variable_cond_check",
        "feat_req__lifecycle__dependency_check",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestConditionalLaunchingScenario(LifecycleScenario):
    """Verify the scenario actually waits for and detects satisfied conditions."""

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.conditional_launching"

    @pytest.fixture(scope="class")
    def flag_path(self, temp_dir: Path) -> Path:
        return temp_dir / "lifecycle_launch_ready.flag"

    @pytest.fixture(scope="class", autouse=True)
    def satisfied_preconditions(self, flag_path: Path) -> Generator[None, None, None]:
        """Really establish the preconditions the scenario is told to wait for.

        The flag file is created up front (path condition already met), the env var is
        set in this process (inherited by the scenario subprocess), and a real `sleep`
        process is kept alive for the duration of the scenario run (process condition).
        Torn down afterwards so this class does not leak state into later tests.
        """
        flag_path.write_text("ready", encoding="utf-8")
        os.environ[_CONDITION_ENV_VAR] = "1"
        process = subprocess.Popen([_CONDITION_PROCESS_NAME, "30"])
        try:
            yield
        finally:
            process.kill()
            process.wait()
            del os.environ[_CONDITION_ENV_VAR]
            flag_path.unlink(missing_ok=True)

    @pytest.fixture(scope="class")
    def test_config(self, flag_path: Path, satisfied_preconditions: None) -> dict[str, Any]:
        # Depends on `satisfied_preconditions` explicitly (rather than relying on autouse
        # ordering) so preconditions are guaranteed established before `results` executes.
        return {
            "test": {
                "wait_conditions": [
                    f"path:{flag_path}",
                    f"env:{_CONDITION_ENV_VAR}",
                    f"process:{_CONDITION_PROCESS_NAME}",
                ],
                "polling_interval_ms": 50,
                "timeout_ms": 2000,
            },
        }

    def test_conditions_already_satisfied_allow_immediate_success(
        self,
        results: ScenarioResult,
        version: str,
    ) -> None:
        """Verify the scenario succeeds once path/env/process conditions are all really met."""
        assert results.return_code == ResultCode.SUCCESS, (
            f"Expected success with satisfied preconditions, got: {results}"
        )

    def test_each_condition_is_individually_confirmed_satisfied(
        self,
        logs_info_level: Any,
        flag_path: Path,
        version: str,
    ) -> None:
        """Verify the scenario reports each condition as satisfied, not just configured."""
        expected_messages = [
            f"Condition satisfied: path:{flag_path}",
            f"Condition satisfied: env:{_CONDITION_ENV_VAR}",
            f"Condition satisfied: process:{_CONDITION_PROCESS_NAME}",
            "All dependencies satisfied",
        ]
        for expected in expected_messages:
            log = logs_info_level.find_log("message", value=expected)
            assert log is not None, f"Expected scenario to log: {expected}"

    def test_timeout_and_polling_interval_are_honored(
        self,
        logs_info_level: Any,
        version: str,
    ) -> None:
        """Verify the scenario logs the configured wait timing values."""
        assert logs_info_level.find_log("message", value="Polling interval: 50ms") is not None
        assert logs_info_level.find_log("message", value="Condition timeout: 2000ms") is not None


@add_test_properties(
    partially_verifies=[
        "feat_req__lifecycle__total_wait_time_support",
        "feat_req__lifecycle__path_condition_check",
        "feat_req__lifecycle__env_variable_cond_check",
        "feat_req__lifecycle__dependency_check",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestConditionalLaunchingScenarioTimesOutOnUnmetConditions(LifecycleScenario):
    """Verify the scenario fails when its wait conditions are never satisfied.

    Without this, an implementation that always reports success regardless of whether
    a path exists, an env var is set, or a process is running would still pass the
    happy-path test above.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.conditional_launching"

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path) -> dict[str, Any]:
        missing_path = temp_dir / "never_created.flag"
        return {
            "test": {
                "wait_conditions": [
                    f"path:{missing_path}",
                    "env:LM_CONDITION_NEVER_SET",
                    "process:process_that_does_not_exist_anywhere",
                ],
                "polling_interval_ms": 20,
                "timeout_ms": 200,
            },
        }

    def expect_command_failure(self) -> bool:
        return True

    def capture_stderr(self) -> bool:
        return True

    def test_scenario_fails_when_conditions_stay_unmet(self, results: ScenarioResult, version: str) -> None:
        """Verify the scenario reports failure - and specifically a wait-condition timeout,
        not merely any nonzero exit - when conditions are never satisfied."""
        assert results.return_code != ResultCode.SUCCESS, (
            f"Expected failure when wait conditions are never satisfied, got: {results}"
        )
        assert results.stderr is not None
        assert "Timed out" in results.stderr and "condition" in results.stderr, (
            f"Expected a wait-condition timeout error on stderr, got: {results.stderr}"
        )


@add_test_properties(
    partially_verifies=["feat_req__lifecycle__validate_conditions"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestConditionalLaunchingScenarioRejectsUnsupportedPrefix(LifecycleScenario):
    """Verify an unsupported wait-condition prefix is rejected as invalid configuration,
    distinct from a legitimate condition that simply times out unmet."""

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.conditional_launching"

    @pytest.fixture(scope="class")
    def test_config(self) -> dict[str, Any]:
        return {
            "test": {
                "wait_conditions": ["badprefix:value"],
                "polling_interval_ms": 20,
                "timeout_ms": 200,
            },
        }

    def expect_command_failure(self) -> bool:
        return True

    def capture_stderr(self) -> bool:
        return True

    def test_unsupported_prefix_is_rejected_immediately(self, results: ScenarioResult, version: str) -> None:
        """Verify validation rejects the condition outright rather than waiting out the timeout."""
        assert results.return_code != ResultCode.SUCCESS, (
            f"Expected failure for an unsupported wait-condition prefix, got: {results}"
        )
        assert results.stderr is not None
        assert "Unsupported wait condition prefix" in results.stderr, (
            f"Expected an unsupported-prefix validation error on stderr, got: {results.stderr}"
        )
