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
"""Startup-retry FITs for `ready_recovery_action.restart.number_of_attempts`.

`flaky_startup_app` aborts on its first `crashes_before_success` launches (rendered per class)
and counts every launch in a file, so the daemon's retry count is observed exactly:

- `TestRetrySucceedsWithinConfiguredAttempts`: crashes use up all retries, then the app runs.
- `TestRetryExhaustionTriggersRecovery`: the app always crashes; the daemon must stop after
  1 + `number_of_attempts` launches and stay alive.

Limitation for `retries_configurable`: only the single configured value (2) is exercised; the
count is not varied across runs.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from daemon_helpers import (
    is_running,
    read_retry_attempt_count,
    wait_until,
)
from lifecycle_scenario import RetryDaemonScenario
from test_properties import add_test_properties


def _number_of_attempts(retry_daemon: dict[str, Any]) -> int:
    """flaky_startup_app's `number_of_attempts`, read from the rendered config."""
    config = json.loads(retry_daemon["runtime_config"].read_text(encoding="utf-8"))
    deployment = config["components"]["flaky_startup_app"]["deployment_config"]
    return int(deployment["ready_recovery_action"]["restart"]["number_of_attempts"])


class TestRetrySucceedsWithinConfiguredAttempts(RetryDaemonScenario):
    """The component crashes exactly `number_of_attempts` times, then succeeds."""

    crashes_before_success = 2

    @add_test_properties(
        partially_verifies=["feat_req__lifecycle__retries_configurable"],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
    )
    def test_component_recovers_within_configured_attempts(self, retry_daemon: dict[str, Any]) -> None:
        """Exactly `crashes_before_success + 1` launches happen, the last one stays running (pgrep),
        and no further launch follows within 1.5 s."""
        app_path = retry_daemon["app_path"]
        counter_path = retry_daemon["counter_path"]
        expected_attempts = retry_daemon["crashes_before_success"] + 1
        assert retry_daemon["crashes_before_success"] <= _number_of_attempts(retry_daemon), (
            "crashes_before_success must fit within number_of_attempts for this test to be meaningful"
        )

        # Wait on the counter, not is_running(): a crashing attempt is briefly visible to pgrep.
        reached = wait_until(lambda: read_retry_attempt_count(counter_path) >= expected_attempts, timeout_s=8.0)
        assert reached, "flaky_startup_app never reached the expected number of launch attempts"

        attempts = read_retry_attempt_count(counter_path)
        assert attempts == expected_attempts, (
            f"Expected exactly {expected_attempts} launch attempts (crashes_before_success + 1 success), got {attempts}"
        )

        started = wait_until(lambda: is_running(app_path), timeout_s=2.0)
        assert started, "flaky_startup_app never reached Running after its last launch attempt"

        relaunched = wait_until(lambda: read_retry_attempt_count(counter_path) != attempts, timeout_s=1.5)
        assert not relaunched, "Component was relaunched again after it was already Running"
        assert is_running(app_path), "flaky_startup_app stopped running after recovering"


class TestRetryExhaustionTriggersRecovery(RetryDaemonScenario):
    """The component always crashes, exhausting `number_of_attempts`."""

    crashes_before_success = 999

    @add_test_properties(
        partially_verifies=["feat_req__lifecycle__retries_configurable"],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
    )
    def test_daemon_gives_up_after_configured_attempts(self, retry_daemon: dict[str, Any]) -> None:
        """Exactly `1 + number_of_attempts` launches happen, none follows within 2 s, the app is
        not running and the daemon is still up.

        Limitation: the run target's `recovery_action` (switch to `fallback_run_target`) is only
        inferred from the daemon staying up without relaunching; it is not asserted directly.
        """
        app_path = retry_daemon["app_path"]
        counter_path = retry_daemon["counter_path"]
        number_of_attempts = _number_of_attempts(retry_daemon)

        settled = wait_until(
            lambda: read_retry_attempt_count(counter_path) >= number_of_attempts + 1,
            timeout_s=8.0,
        )
        assert settled, "flaky_startup_app never reached the configured number of launch attempts"

        # Would catch a daemon that keeps retrying past the budget.
        attempts_after_exhaustion = read_retry_attempt_count(counter_path)
        kept_retrying = wait_until(
            lambda: read_retry_attempt_count(counter_path) != attempts_after_exhaustion,
            timeout_s=2.0,
        )
        assert not kept_retrying, (
            f"Daemon kept restarting the component past the configured number_of_attempts={number_of_attempts}"
        )
        assert attempts_after_exhaustion == number_of_attempts + 1, (
            f"Expected exactly {number_of_attempts + 1} launch attempts before giving up, got "
            f"{attempts_after_exhaustion}"
        )
        assert not is_running(app_path), "flaky_startup_app is still running after exhausting its retries"
        assert retry_daemon["daemon"].is_running(), "launch_manager exited after the component exhausted its retries"
