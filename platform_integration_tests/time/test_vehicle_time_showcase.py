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
"""Platform integration tests for the score_time clock showcases.

Each test drives one of the four clock showcases defined in ``time.score.json``
and verifies that the time handler returned a real, positive value — not zero
or garbage output from an uninitialised clock source.

See ``test_communication_showcase`` for background on these platform
integration tests. All such tests in this package are combined into a single
suite by the ``pit`` target in this package's ``BUILD`` file.
"""

import re

from attribute_plugin import add_test_properties
from showcase_runner import run_showcases


@add_test_properties(
    partially_verifies=["stkh_req__time__vehicle_time_api"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_vehicle_time_showcase(target):
    """The vehicle time showcase obtains a combined snapshot of the
    vehicle time and the local monotonic HIRS time via VehicleTimeHandler.

    Note: ``time.score.json`` does not start a time daemon, so the vehicle
    clock falls back to the local HIRS clock and ``is_reliable=no`` is the
    expected state.  This test covers the API surface only; synchronization
    quality requires a time daemon and is tracked separately."""

    output = run_showcases(target, "Vehicle Time Example")
    assert "hirs=" in output, f"No hirs= field in output:\n{output}"
    match = re.search(r"vehicle=(\d+)\.(\d+)", output)
    assert match is not None, f"Could not parse vehicle= timestamp:\n{output}"
    assert int(match.group(1)) > 0, f"vehicle time seconds must be positive, got: {match.group(1)}"
    # No time daemon in this showcase; is_reliable=no is expected and intentional.
    assert "is_reliable=no" in output, f"Expected is_reliable=no (no time_daemon in this showcase):\n{output}"


@add_test_properties(
    partially_verifies=["stkh_req__time__absolute_time_api"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_system_time_showcase(target):
    """The system time showcase reads the wall-clock (Unix epoch) time via the
    score_time SystemTimeHandler, demonstrating the platform's system time API."""

    output = run_showcases(target, "System Time Example")
    match = re.search(r"unix=(\d+)\.(\d+)", output)
    assert match is not None, f"Could not parse unix= timestamp:\n{output}"
    assert int(match.group(1)) > 0, f"unix time seconds must be positive, got: {match.group(1)}"


@add_test_properties(
    partially_verifies=["stkh_req__time__monotonic_clock_api"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_steady_time_showcase(target):
    """The steady time showcase reads the monotonic POSIX clock via the
    score_time SteadyTimeHandler, demonstrating the platform's steady time API."""

    output = run_showcases(target, "Steady Time Example")
    # seconds.nanoseconds format: "510.130 s" means 510 s and 130 ns, not a float.
    samples = [(int(s), int(n)) for s, n in re.findall(r"monotonic=(\d+)\.(\d+) s", output)]
    assert len(samples) >= 2, f"Expected at least 2 monotonic= samples:\n{output}"
    assert samples[0][0] > 0, f"Steady time seconds must be positive, got: {samples[0][0]}"
    assert all(a <= b for a, b in zip(samples, samples[1:])), f"Steady clock went backwards: {samples}"


@add_test_properties(
    partially_verifies=["stkh_req__time__high_res_clock_api"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_high_res_steady_time_showcase(target):
    """The high-resolution steady time showcase reads the HPTP-local clock
    via the score_time HighResSteadyTimeHandler, demonstrating the platform's
    high-precision time API."""

    output = run_showcases(target, "High Resolution Steady Time Example")
    # \b so "vehicle_time=" is not matched.
    samples = [(int(s), int(n)) for s, n in re.findall(r"\btime=(\d+)\.(\d+) s", output)]
    assert len(samples) >= 2, f"Expected at least 2 time= samples:\n{output}"
    assert samples[0][0] > 0, f"High-res steady time seconds must be positive, got: {samples[0][0]}"
    # No monotonicity check: HighResSteadyClock = CLOCK_REALTIME on Linux (eclipse-score/time#310).
