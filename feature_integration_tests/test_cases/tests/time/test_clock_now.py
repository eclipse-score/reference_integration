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
from fit_scenario import FitScenario, ResultCode
from test_properties import add_test_properties
from testing_utils import LogContainer, ScenarioResult

# score_time is C++ only; there is no Rust variant of the clock library.
pytestmark = pytest.mark.parametrize("version", ["cpp"], scope="class")


class ClockScenario(FitScenario):
    """Common base for score_time clock scenarios.

    ``build_tools`` is inherited from ``FitScenario``. The ``version`` parameter
    is declared on ``test_config`` so it appears in the fixture dependency chain;
    ``FitScenario.build_tools`` then resolves it dynamically via
    ``request.getfixturevalue("version")`` and selects the C++ target.
    """

    @pytest.fixture(scope="class")
    def test_config(self, version: str) -> dict[str, Any]:
        return {}


@add_test_properties(
    partially_verifies=["FR-9"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestSystemClockNow(ClockScenario):
    """
    Verify SystemClock::Now() returns a live reading through the public Clock API.

    The C++ scenario compares the reading against the host system clock within
    tolerance and fails the process otherwise. Python confirms the process
    succeeded and that the reading was emitted. Partially verifies FR-9
    (Absolute Time Base API): a live, non-zero reading through the public API.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "time.system_clock_now"

    def test_returns_success(self, results: ScenarioResult) -> None:
        assert results.return_code == ResultCode.SUCCESS

    def test_reading_logged(self, logs_info_level: LogContainer) -> None:
        log = logs_info_level.find_log("clock", value="system")
        assert log is not None
        assert log.value_ns > 0


@add_test_properties(
    partially_verifies=["FR-14"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestSteadyClockNow(ClockScenario):
    """
    Verify SteadyClock::Now() is monotonic across two consecutive readings.

    The C++ scenario fails the process if the second reading precedes the first.
    Python confirms success and that the logged readings are non-decreasing.
    Partially verifies FR-14 (Monotonic Clock API): non-decreasing readings.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "time.steady_clock_now"

    def test_returns_success(self, results: ScenarioResult) -> None:
        assert results.return_code == ResultCode.SUCCESS

    def test_readings_monotonic(self, logs_info_level: LogContainer) -> None:
        log = logs_info_level.find_log("clock", value="steady")
        assert log is not None
        assert log.second_ns >= log.first_ns


@add_test_properties(
    partially_verifies=["FR-13"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestHighResSteadyClockNow(ClockScenario):
    """
    Verify HighResSteadyClock::Now() is live and monotonic.

    The C++ scenario fails the process on a zero or non-monotonic reading.
    Python confirms success and that the logged readings are non-zero and
    non-decreasing. Partially verifies FR-13 (High Precision Clock API): a
    non-zero, non-decreasing high-resolution reading.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "time.high_res_steady_clock_now"

    def test_returns_success(self, results: ScenarioResult) -> None:
        assert results.return_code == ResultCode.SUCCESS

    def test_readings_monotonic(self, logs_info_level: LogContainer) -> None:
        log = logs_info_level.find_log("clock", value="high_res_steady")
        assert log is not None
        assert log.first_ns > 0
        assert log.second_ns >= log.first_ns


@add_test_properties(
    partially_verifies=["FR-14"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestSteadyClockProgression(ClockScenario):
    """
    Verify SteadyClock::Now() stays monotonic across a burst of ticks and
    progresses by roughly a known sleep duration.

    The C++ scenario takes several readings, asserts the sequence is
    non-decreasing, sleeps for a known duration, takes a final reading and
    asserts it does not precede the last pre-sleep reading. Python confirms
    success and that the post-sleep reading advanced by roughly the sleep
    duration. Partially verifies FR-14 (Monotonic Clock API) / TC-FR14-001:
    repeated Now() calls are non-decreasing and the clock progresses over time.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "time.steady_clock_progression"

    @pytest.fixture(scope="class")
    def test_config(self, version: str) -> dict[str, Any]:
        return {"tick_count": 5, "sleep_ms": 100}

    def test_returns_success(self, results: ScenarioResult) -> None:
        assert results.return_code == ResultCode.SUCCESS

    def test_readings_monotonic(self, logs_info_level: LogContainer) -> None:
        log = logs_info_level.find_log("clock", value="steady")
        assert log is not None
        assert log.last_ns >= log.first_ns
        assert log.final_ns >= log.last_ns

    def test_clock_progressed_during_sleep(self, logs_info_level: LogContainer) -> None:
        log = logs_info_level.find_log("clock", value="steady")
        assert log is not None
        expected_ns = log.sleep_ms * 1_000_000
        # Allow generous scheduling jitter: the clock must have advanced by at
        # least half the sleep, proving the elapsed time is observable.
        assert log.final_ns - log.last_ns >= expected_ns // 2
