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
"""Platform integration test for the lifecycle showcase.

See ``test_communication_showcase`` for background on these platform
integration tests. All such tests in this package are combined into a single
suite by the ``pit`` target in this package's ``BUILD`` file.
"""

from attribute_plugin import add_test_properties
from showcase_runner import run_showcases


@add_test_properties(
    partially_verifies=["stkh_req__dependability__health_management"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_lifecycle_showcase(target):
    """The lifecycle showcase launches two supervised applications and records
    a malfunction, demonstrating the platform's health and lifecycle
    management."""

    output = run_showcases(target, "Simple Health and lifecycle management example")

    # The CLI exits 0 even if LM keeps restarting a crashing app, so check LM's log too.
    assert "unexpected termination" not in output, output
    for marker in (
        "Successfully activated Run Target Startup",
        "Completed the request for Run Target fallback_run_target",
        "Launch Manager completed with exit code value: 0",
    ):
        assert marker in output, f"Missing '{marker}' in lifecycle showcase output:\n{output}"
