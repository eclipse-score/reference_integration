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
"""Tests of the FIT's own conditional-launching scenario binary (rust and cpp), not of launch_manager.

The scenario polls `path:`, `env:` and `process:` wait conditions; these tests really create or
withhold each condition and check what the stub reports. No test here drives launch_manager, so
none carries a `partially_verifies` claim: lifecycle requirement coverage lives in
test_conditional_launching.py and test_process_launching_with_daemon.py.
"""

import os
import subprocess
import sys
import time
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from fit_scenario import ResultCode
from lifecycle_scenario import LifecycleScenario
from testing_utils import ScenarioResult

pytestmark = [pytest.mark.parametrize("version", ["rust", "cpp"], scope="class")]

_CONDITION_ENV_VAR = "LM_CONDITION_READY"
_CONDITION_PROCESS_NAME = "sleep"


class TestConditionalLaunchingScenario(LifecycleScenario):
    """All three conditions are really satisfied before the scenario starts."""

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.conditional_launching"

    @pytest.fixture(scope="class")
    def flag_path(self, temp_dir: Path) -> Path:
        return temp_dir / "lifecycle_launch_ready.flag"

    @pytest.fixture(scope="class", autouse=True)
    def satisfied_preconditions(self, flag_path: Path) -> Generator[None, None, None]:
        """Create the flag file, set the env var (inherited by the scenario) and keep a `sleep`
        process alive for the class; all three are undone afterwards."""
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
        # Explicit dependency so the preconditions exist before `results` runs the scenario.
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
        """The scenario exits successfully."""
        assert results.return_code == ResultCode.SUCCESS, (
            f"Expected success with satisfied preconditions, got: {results}"
        )

    def test_each_condition_is_individually_confirmed_satisfied(
        self,
        logs_info_level: Any,
        flag_path: Path,
        version: str,
    ) -> None:
        """The scenario logs "Condition satisfied" for each condition and "All dependencies satisfied"."""
        expected_messages = [
            f"Condition satisfied: path:{flag_path}",
            f"Condition satisfied: env:{_CONDITION_ENV_VAR}",
            f"Condition satisfied: process:{_CONDITION_PROCESS_NAME}",
            "All dependencies satisfied",
        ]
        for expected in expected_messages:
            log = logs_info_level.find_log("message", value=expected)
            assert log is not None, f"Expected scenario to log: {expected}"

    def test_timeout_and_polling_interval_are_logged(
        self,
        logs_info_level: Any,
        version: str,
    ) -> None:
        """The scenario logs the configured polling interval and timeout. Only the logged values
        are checked; that polling actually uses them is covered by the late-condition test."""
        assert logs_info_level.find_log("message", value="Polling interval: 50ms") is not None
        assert logs_info_level.find_log("message", value="Condition timeout: 2000ms") is not None


class TestConditionalLaunchingScenarioTimesOutOnUnmetConditions(LifecycleScenario):
    """No condition is ever satisfied: the scenario must fail with a timeout. Catches a stub that
    reports success without checking the conditions."""

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
        """Non-success exit with a wait-condition timeout ("Timed out" ... "condition") on stderr."""
        assert results.return_code != ResultCode.SUCCESS, (
            f"Expected failure when wait conditions are never satisfied, got: {results}"
        )
        assert results.stderr is not None
        assert "Timed out" in results.stderr and "condition" in results.stderr, (
            f"Expected a wait-condition timeout error on stderr, got: {results.stderr}"
        )


class TestConditionalLaunchingScenarioDetectsConditionArrivingLate(LifecycleScenario):
    """The path condition becomes true 0.5 s into a 3 s wait. Catches a stub that checks only once
    (at start or at timeout) instead of polling."""

    _DELAY_BEFORE_CONDITION_MET_S = 0.5
    _TIMEOUT_MS = 3000
    _POLLING_INTERVAL_MS = 100

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.conditional_launching"

    @pytest.fixture(scope="class")
    def flag_path(self, temp_dir: Path) -> Path:
        return temp_dir / "lifecycle_launch_ready_late.flag"

    @pytest.fixture(scope="class")
    def test_config(self, flag_path: Path) -> dict[str, Any]:
        return {
            "test": {
                "wait_conditions": [f"path:{flag_path}"],
                "polling_interval_ms": self._POLLING_INTERVAL_MS,
                "timeout_ms": self._TIMEOUT_MS,
            },
        }

    @pytest.fixture(scope="class")
    def results(
        self,
        command: list[str],
        execution_timeout: float,
        flag_path: Path,
    ) -> Generator[ScenarioResult, None, None]:
        # Overrides the base `results` fixture so the delayed flag writer starts together with the
        # scenario; the autouse report fixture runs `results` before the test body, so arming it
        # in the test would be too late. A helper subprocess (not a Python timer thread) writes
        # the flag, so the delay does not depend on the test runner's thread scheduling.
        start = time.monotonic()
        trigger = subprocess.Popen(
            [
                sys.executable,
                "-c",
                (
                    "import pathlib, sys, time; "
                    "time.sleep(float(sys.argv[1])); "
                    "pathlib.Path(sys.argv[2]).write_text('ready', encoding='utf-8')"
                ),
                str(self._DELAY_BEFORE_CONDITION_MET_S),
                str(flag_path),
            ]
        )
        try:
            result = self._run_command(command, execution_timeout)
            # Fixture and test get different instances, so share the timing via the class.
            type(self)._elapsed_s = time.monotonic() - start
        finally:
            trigger.terminate()
            try:
                trigger.wait(timeout=1)
            except subprocess.TimeoutExpired:
                trigger.kill()
                trigger.wait(timeout=1)
        yield result
        flag_path.unlink(missing_ok=True)

    def test_condition_satisfied_partway_through_the_wait_is_detected_promptly(
        self,
        results: ScenarioResult,
        version: str,
    ) -> None:
        """Success no earlier than the 0.5 s delay and well before the 3 s timeout."""
        result = results
        elapsed_s = self._elapsed_s

        assert result.return_code == ResultCode.SUCCESS, f"Expected success once the condition became true: {result}"
        assert elapsed_s >= self._DELAY_BEFORE_CONDITION_MET_S, (
            f"Scenario reported success ({elapsed_s:.2f}s) before the condition could possibly have been "
            f"true ({self._DELAY_BEFORE_CONDITION_MET_S}s) - it isn't actually observing the real condition."
        )
        margin_s = self._TIMEOUT_MS / 1000 - self._DELAY_BEFORE_CONDITION_MET_S
        assert elapsed_s < self._DELAY_BEFORE_CONDITION_MET_S + margin_s / 2, (
            f"Scenario took {elapsed_s:.2f}s to detect a condition that became true after "
            f"{self._DELAY_BEFORE_CONDITION_MET_S}s - this is close to the full {self._TIMEOUT_MS}ms timeout, "
            "suggesting it isn't re-checking at the configured polling interval."
        )


class TestConditionalLaunchingScenarioRejectsUnsupportedPrefix(LifecycleScenario):
    """An unknown wait-condition prefix is a configuration error, reported without waiting."""

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.conditional_launching"

    _TIMEOUT_MS = 2000

    @pytest.fixture(scope="class")
    def test_config(self) -> dict[str, Any]:
        return {
            "test": {
                "wait_conditions": ["badprefix:value"],
                "polling_interval_ms": 20,
                "timeout_ms": self._TIMEOUT_MS,
            },
        }

    def expect_command_failure(self) -> bool:
        return True

    def capture_stderr(self) -> bool:
        return True

    @pytest.fixture(scope="class")
    def results(self, command: list[str], execution_timeout: float) -> ScenarioResult:
        # Overrides the base `results` fixture to time the one scenario run (a second run in the
        # test body would execute the binary twice). Fixture and test get different instances,
        # so the timing is shared via the class.
        start = time.monotonic()
        result = self._run_command(command, execution_timeout)
        type(self)._elapsed_s = time.monotonic() - start
        return result

    def test_unsupported_prefix_is_rejected_immediately(
        self,
        results: ScenarioResult,
        version: str,
    ) -> None:
        """Non-success exit with "Unsupported wait condition prefix" on stderr, in under half the timeout."""
        result = results
        elapsed_s = self._elapsed_s

        assert result.return_code != ResultCode.SUCCESS, (
            f"Expected failure for an unsupported wait-condition prefix, got: {result}"
        )
        assert result.stderr is not None
        assert "Unsupported wait condition prefix" in result.stderr, (
            f"Expected an unsupported-prefix validation error on stderr, got: {result.stderr}"
        )
        assert elapsed_s < (self._TIMEOUT_MS / 1000) / 2, (
            f"Rejection took {elapsed_s:.2f}s, close to the full {self._TIMEOUT_MS}ms timeout - "
            "the prefix should be validated up front, not discovered by waiting it out."
        )


class TestConditionalLaunchingScenarioRejectsEmptyConditions(LifecycleScenario):
    """An empty `wait_conditions` list is a configuration error (not "nothing to wait for"),
    reported without waiting."""

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.conditional_launching"

    _TIMEOUT_MS = 2000

    @pytest.fixture(scope="class")
    def test_config(self) -> dict[str, Any]:
        return {
            "test": {
                "wait_conditions": [],
                "polling_interval_ms": 20,
                "timeout_ms": self._TIMEOUT_MS,
            },
        }

    def expect_command_failure(self) -> bool:
        return True

    def capture_stderr(self) -> bool:
        return True

    @pytest.fixture(scope="class")
    def results(self, command: list[str], execution_timeout: float) -> ScenarioResult:
        # Same override as TestConditionalLaunchingScenarioRejectsUnsupportedPrefix.results.
        start = time.monotonic()
        result = self._run_command(command, execution_timeout)
        type(self)._elapsed_s = time.monotonic() - start
        return result

    def test_empty_conditions_are_rejected_immediately(
        self,
        results: ScenarioResult,
        version: str,
    ) -> None:
        """Non-success exit with "Wait conditions were not provided" on stderr, in under half the timeout."""
        result = results
        elapsed_s = self._elapsed_s

        assert result.return_code != ResultCode.SUCCESS, (
            f"Expected failure for an empty wait_conditions list, got: {result}"
        )
        assert result.stderr is not None
        assert "Wait conditions were not provided" in result.stderr, (
            f"Expected a missing/empty wait_conditions validation error on stderr, got: {result.stderr}"
        )
        assert elapsed_s < (self._TIMEOUT_MS / 1000) / 2, (
            f"Rejection took {elapsed_s:.2f}s, close to the full {self._TIMEOUT_MS}ms timeout - "
            "an empty condition list should be validated up front, not discovered by waiting it out."
        )
