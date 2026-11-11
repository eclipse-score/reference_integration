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

import re

from attribute_plugin import add_test_properties
from showcase_runner import run_showcases

# Printed by control_daemon's run target activation callback for every
# completed transition, whether requested via lmcontrol or by a recovery action.
_ACTIVATED = re.compile(r"Successfully activated Run Target (\S+)")

# Any of these means an lmcontrol request did not reach the launch manager.
_CONTROL_ERRORS = (
    "Could not connect to control socket",
    "Request could not be sent",
    "failed with error",
)

# Printed when the launch manager (or an app) aborts, e.g. on a bad config.
_CRASH_MARKERS = (
    "log fatal",
    "Assertion failed",
)


def _assert_no_crash(output: str) -> None:
    for marker in _CRASH_MARKERS:
        assert marker not in output, f"Showcase process aborted ({marker!r}):\n{output}"


def _assert_run_target_sequence(output: str, expected: list[str]) -> None:
    """Assert the launch manager activated exactly ``expected``, in order.

    The initial ``Startup`` activation may complete before control_daemon
    registers its callback, so a leading ``Startup`` is optional.
    """
    _assert_no_crash(output)
    for error in _CONTROL_ERRORS:
        assert error not in output, f"Run target request failed ({error!r}):\n{output}"

    activated = _ACTIVATED.findall(output)
    if activated[:1] == ["Startup"]:
        activated = activated[1:]
    assert activated == expected, f"Expected run target activations {expected}, got {activated}:\n{output}"


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
    _assert_no_crash(output)


@add_test_properties(
    partially_verifies=["stkh_req__dependability__safety_features_1"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_lifecycle_run_target_switching_showcase(target):
    """lmcontrol drives the launch manager between the Startup and Running
    run targets, starting and stopping the C, C++ and Rust example apps."""

    output = run_showcases(target, "Lifecycle run target switching example")
    _assert_run_target_sequence(output, ["Running", "Startup"])


@add_test_properties(
    partially_verifies=["stkh_req__dependability__safety_features_1"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_lifecycle_crash_recovery_showcase(target):
    """A killed supervised app makes the launch manager recover to the
    fallback run target, after which lmcontrol restores Running."""

    output = run_showcases(target, "Lifecycle crash recovery example")
    # fallback_run_target only activates if the SIGKILL hit cpp_supervised_app;
    # the second Running activation requires the launch manager to restart it,
    # since Running depends on the app reaching its Running process state.
    _assert_run_target_sequence(output, ["Running", "fallback_run_target", "Running"])
