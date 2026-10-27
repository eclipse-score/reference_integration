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
"""Platform integration tests for combined multi-module showcases.

Each test verifies that the named showcase actually runs its modules together:
lifecycle reaches the Startup run target, no fallback is triggered, and the
module under test produces its expected output.
"""

from attribute_plugin import add_test_properties
from showcase_runner import run_showcases


@add_test_properties(
    partially_verifies=[
        "stkh_req__communication__inter_process",
        "stkh_req__execution_model__processes",
    ],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_lifecycle_comm_showcase(target):
    """The lifecycle-managed communication showcase launches the communication
    API example as a process under the lifecycle launch manager, demonstrating
    score_lifecycle and score_communication working together on the platform."""

    output = run_showcases(target, "Lifecycle-managed Communication Example")
    assert "Completed the request for PG to State Startup" in output
    assert "activating recovery state" not in output
    assert "samples received" in output


@add_test_properties(
    partially_verifies=[
        "stkh_req__execution_model__processes",
    ],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_lifecycle_kyron_showcase(target):
    """The lifecycle-managed Kyron showcase launches a kyron async runtime
    process under the lifecycle launch manager, demonstrating score_lifecycle
    and score_kyron working together on the platform."""

    output = run_showcases(target, "Lifecycle-managed Kyron Async Showcase")
    assert "Completed the request for PG to State Startup" in output
    assert "activating recovery state" not in output
    assert "Program finished running." in output


@add_test_properties(
    partially_verifies=[
        "stkh_req__time__vehicle_time_api",
        "stkh_req__execution_model__processes",
    ],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_lifecycle_time_showcase(target):
    """The lifecycle-managed time showcase launches a score_time vehicle-time
    reporting process under the lifecycle launch manager, demonstrating
    score_lifecycle and score_time working together on the platform."""

    output = run_showcases(target, "Lifecycle-managed Time Reporting Showcase")
    assert "Completed the request for PG to State Startup" in output
    assert "activating recovery state" not in output
    assert "vehicle=" in output


@add_test_properties(
    partially_verifies=[
        "stkh_req__execution_model__processes",
    ],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_kyron_logging_showcase(target):
    """The Kyron async logging showcase runs a single binary that combines
    the score_kyron async runtime with score_log (baselibs), demonstrating
    both modules working together within one process."""

    output = run_showcases(target, "Kyron Async Logging")
    assert "All async tasks completed" in output


@add_test_properties(
    partially_verifies=[
        "stkh_req__time__vehicle_time_api",
        "stkh_req__communication__inter_process",
        "stkh_req__execution_model__processes",
    ],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_lifecycle_time_comm_showcase(target):
    """The lifecycle-managed time and communication showcase launches both a
    score_time vehicle-time reporter and a score_communication IPC example
    under the lifecycle launch manager, demonstrating all three modules
    working together on the platform."""

    output = run_showcases(target, "Lifecycle-managed Time and Communication Showcase")
    assert "Completed the request for PG to State Startup" in output
    assert "activating recovery state" not in output
    assert "vehicle=" in output
    assert "samples received" in output


@add_test_properties(
    partially_verifies=[
        "stkh_req__execution_model__processes",
        "stkh_req__communication__inter_process",
    ],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_lifecycle_kyron_comm_showcase(target):
    """The lifecycle-managed Kyron and communication showcase launches both a
    score_kyron async runtime process and a score_communication IPC example
    under the lifecycle launch manager, demonstrating all three modules
    working together on the platform."""

    output = run_showcases(target, "Lifecycle-managed Kyron and Communication Showcase")
    assert "Completed the request for PG to State Startup" in output
    assert "activating recovery state" not in output
    assert "Program finished running." in output
    assert "samples received" in output
