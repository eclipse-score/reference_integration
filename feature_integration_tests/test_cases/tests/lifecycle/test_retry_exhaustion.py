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
"""Real retry-exhaustion coverage for `feat_req__lifecycle__retries_configurable`.

Drives a dedicated `flaky_startup_app` (see support_apps/flaky_startup_app) whose
crash-before-success count is fixed in the launch_manager config, so both sides of
`ready_recovery_action.restart.number_of_attempts` are exercised deterministically
instead of relying on a real, racy startup failure:

- `TestRetrySucceedsWithinConfiguredAttempts`: the component crashes fewer times
  than the configured attempts allow, so it must recover and reach Running.
- `TestRetryExhaustionTriggersRecovery`: the component always crashes, so the
  daemon must give up after exactly the configured attempts and execute the run
  target's `recovery_action` (switch to `fallback_run_target`) instead of
  restarting forever.
"""

from __future__ import annotations

from typing import Any

import pytest
from daemon_helpers import (
    is_running,
    read_retry_attempt_count,
    start_flaky_retry_daemon,
    stop_flaky_retry_daemon,
    wait_until,
)
from test_properties import add_test_properties

# Must match "number_of_attempts" in both lifecycle_daemon_retry_*_config.json.
_NUMBER_OF_ATTEMPTS = 2


@pytest.fixture(scope="class")
def recovers_daemon(tmp_path_factory: pytest.TempPathFactory):
    daemon_info = start_flaky_retry_daemon(
        tmp_path_factory,
        "//feature_integration_tests/configs:lifecycle_daemon_retry_recovers_config.json",
        crashes_before_success=2,
    )
    try:
        yield daemon_info
    finally:
        stop_flaky_retry_daemon(daemon_info)


@pytest.fixture(scope="class")
def exhausts_daemon(tmp_path_factory: pytest.TempPathFactory):
    daemon_info = start_flaky_retry_daemon(
        tmp_path_factory,
        "//feature_integration_tests/configs:lifecycle_daemon_retry_exhausts_config.json",
        crashes_before_success=999,
    )
    try:
        yield daemon_info
    finally:
        stop_flaky_retry_daemon(daemon_info)


class TestRetrySucceedsWithinConfiguredAttempts:
    """The component crashes fewer times than `number_of_attempts` allows."""

    @add_test_properties(
        partially_verifies=["feat_req__lifecycle__retries_configurable"],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
    )
    def test_component_recovers_within_configured_attempts(self, recovers_daemon: dict[str, Any]) -> None:
        """Daemon retries a failing component up to `number_of_attempts` and lets
        it reach Running once it stops crashing.
        """
        app_path = recovers_daemon["app_path"]
        counter_path = recovers_daemon["counter_path"]
        expected_attempts = recovers_daemon["crashes_before_success"] + 1

        # Check the attempt counter before is_running(): a crashing attempt is still
        # technically "running" for the microseconds before it aborts, so polling
        # is_running() first can catch that transient window rather than the
        # eventual successful attempt.
        reached = wait_until(lambda: read_retry_attempt_count(counter_path) >= expected_attempts, timeout_s=8.0)
        assert reached, "flaky_startup_app never reached the expected number of launch attempts"

        attempts = read_retry_attempt_count(counter_path)
        assert attempts == expected_attempts, (
            f"Expected exactly {expected_attempts} launch attempts (crashes_before_success + 1 success), got {attempts}"
        )

        started = wait_until(lambda: is_running(app_path), timeout_s=2.0)
        assert started, "flaky_startup_app never reached Running after its last launch attempt"

        # Once healthy it should stay up: no further restarts.
        relaunched = wait_until(lambda: read_retry_attempt_count(counter_path) != attempts, timeout_s=1.5)
        assert not relaunched, "Component was relaunched again after it was already Running"
        assert is_running(app_path), "flaky_startup_app stopped running after recovering"


class TestRetryExhaustionTriggersRecovery:
    """The component always crashes, exceeding `number_of_attempts`."""

    @add_test_properties(
        partially_verifies=["feat_req__lifecycle__retries_configurable"],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
    )
    def test_daemon_gives_up_after_configured_attempts(self, exhausts_daemon: dict[str, Any]) -> None:
        """Daemon stops restarting a component once `number_of_attempts` is
        exhausted, instead of retrying forever, and executes the run target's
        `recovery_action` (switch to `fallback_run_target`).
        """
        app_path = exhausts_daemon["app_path"]
        counter_path = exhausts_daemon["counter_path"]

        settled = wait_until(
            lambda: read_retry_attempt_count(counter_path) >= _NUMBER_OF_ATTEMPTS + 1,
            timeout_s=8.0,
        )
        assert settled, "flaky_startup_app never reached the configured number of launch attempts"

        # Give the daemon a chance to keep retrying, if it hasn't actually given up.
        attempts_after_exhaustion = read_retry_attempt_count(counter_path)
        kept_retrying = wait_until(
            lambda: read_retry_attempt_count(counter_path) != attempts_after_exhaustion,
            timeout_s=2.0,
        )
        assert not kept_retrying, (
            f"Daemon kept restarting the component past the configured number_of_attempts={_NUMBER_OF_ATTEMPTS}"
        )
        assert attempts_after_exhaustion == _NUMBER_OF_ATTEMPTS + 1, (
            f"Expected exactly {_NUMBER_OF_ATTEMPTS + 1} launch attempts before giving up, got "
            f"{attempts_after_exhaustion}"
        )
        assert not is_running(app_path), (
            "flaky_startup_app is still running after exhausting retries; recovery_action "
            "(switch_run_target -> fallback_run_target) should have stopped further attempts"
        )
        assert exhausts_daemon["daemon"].is_running(), "Launch Manager daemon crashed instead of switching run target"
