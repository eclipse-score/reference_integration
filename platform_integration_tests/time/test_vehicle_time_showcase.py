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
    PTP-synchronized vehicle time and the local monotonic HIRS time,
    demonstrating the platform's vehicle time base API."""

    output = run_showcases(target, "Vehicle Time Example")
    # Both time fields must co-appear — proves the full combined report was produced.
    assert "vehicle=" in output, f"No vehicle= field in output:\n{output}"
    assert "hirs=" in output, f"No hirs= field in output:\n{output}"
    # The vehicle timestamp is a Unix-epoch float; a positive value proves the
    # time API returned a real reading, not zero or an uninitialised source.
    match = re.search(r"vehicle=(\d+\.\d+)", output)
    assert match is not None, f"Could not parse vehicle= timestamp:\n{output}"
    assert float(match.group(1)) > 0.0, (
        f"vehicle time must be positive, got: {match.group(1)}"
    )


@add_test_properties(
    partially_verifies=["stkh_req__time__vehicle_time_api"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_system_time_showcase(target):
    """The system time showcase reads the wall-clock (Unix epoch) time via the
    score_time SystemTimeHandler, demonstrating the platform's system time API."""

    output = run_showcases(target, "System Time Example")
    assert "unix=" in output, f"No unix= field in output:\n{output}"
    match = re.search(r"unix=(\d+\.\d+)", output)
    assert match is not None, f"Could not parse unix= timestamp:\n{output}"
    assert float(match.group(1)) > 0.0, (
        f"unix time must be positive, got: {match.group(1)}"
    )


@add_test_properties(
    partially_verifies=["stkh_req__time__vehicle_time_api"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_steady_time_showcase(target):
    """The steady time showcase reads the monotonic POSIX clock via the
    score_time SteadyTimeHandler, demonstrating the platform's steady time API."""

    output = run_showcases(target, "Steady Time Example")
    assert "monotonic=" in output, f"No monotonic= field in output:\n{output}"
    match = re.search(r"monotonic=(\d+\.\d+)", output)
    assert match is not None, f"Could not parse monotonic= timestamp:\n{output}"
    assert float(match.group(1)) > 0.0, (
        f"monotonic time must be positive, got: {match.group(1)}"
    )


@add_test_properties(
    partially_verifies=["stkh_req__time__vehicle_time_api"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_high_res_steady_time_showcase(target):
    """The high-resolution steady time showcase reads the HPTP-local monotonic
    clock via the score_time HighResSteadyTimeHandler, demonstrating the
    platform's high-precision time API."""

    output = run_showcases(target, "High Resolution Steady Time Example")
    assert "time=" in output, f"No time= field in output:\n{output}"
    # Use word boundary so we don't match "vehicle_time=" or similar prefixes.
    match = re.search(r"\btime=(\d+\.\d+)", output)
    assert match is not None, f"Could not parse time= field:\n{output}"
    assert float(match.group(1)) > 0.0, (
        f"high_res_steady time must be positive, got: {match.group(1)}"
    )
