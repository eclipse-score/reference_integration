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
from testing_utils import BazelTools, BuildTools, LogContainer, ScenarioResult

# score_time is C++ only; there is no Rust variant of the clock library.
pytestmark = pytest.mark.parametrize("version", ["cpp"], scope="class")


class ClockScenario(FitScenario):
    """Common base for score_time clock scenarios (no scenario input required)."""

    @pytest.fixture(scope="class")
    def build_tools(self, version: str) -> BuildTools:
        # Consume the parametrized `version` and select the C++ scenario binary.
        return BazelTools(option_prefix=version)

    @pytest.fixture(scope="class")
    def test_config(self) -> dict[str, Any]:
        return {}


class TestSystemClockNow(ClockScenario):
    """
    Verify SystemClock::Now() returns a live reading through the public Clock API.

    The C++ scenario compares the reading against the host system clock within
    tolerance and fails the process otherwise. Python confirms the process
    succeeded and that the reading was emitted.
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


class TestSteadyClockNow(ClockScenario):
    """
    Verify SteadyClock::Now() is monotonic across two consecutive readings.

    The C++ scenario fails the process if the second reading precedes the first.
    Python confirms success and that the logged readings are non-decreasing.
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


class TestHighResSteadyClockNow(ClockScenario):
    """
    Verify HighResSteadyClock::Now() is live and monotonic.

    The C++ scenario fails the process on a zero or non-monotonic reading.
    Python confirms success and that the logged readings are non-zero and
    non-decreasing.
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
