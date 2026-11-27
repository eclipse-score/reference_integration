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


def _unexpected_termination(component: str) -> re.Pattern:
    # The launch manager prefixes process logs with "Name: <component>, PID: <pid>".
    return re.compile(rf"Name:\s*{component}\s*,\s*PID:\s*\d+\s+unexpected termination of process")


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
    # score_lifecycle v0.10+: LM logs "Completed the request for Run Target <name>".
    assert "Completed the request for Run Target Startup" in output, (
        f"Launch manager did not reach Startup state:\n{output}"
    )
    # state_manager needs working_dir to find mw_com_config.json at startup.
    assert not _unexpected_termination("state_manager").search(output), (
        f"state_manager crashed — mw_com_config.json missing or working_dir misconfigured:\n{output}"
    )
    # SIGUSR1 stops C++ heartbeat reporting; LM then kills the app and recovers.
    signal_started = output.find("App 2: starting /showcases/bin/lifecycle_signal.sh")
    assert signal_started >= 0, f"The SIGUSR1 injection script did not start:\n{output}"
    cpp_terminated = _unexpected_termination("cpp_supervised_app").search(output)
    assert cpp_terminated, f"LM did not detect cpp_supervised_app termination via SIGUSR1:\n{output}"
    assert signal_started < cpp_terminated.start(), (
        f"LM killed cpp_supervised_app before the SIGUSR1 injection script started:\n{output}"
    )
    # The apps run with -m1000; a missed deadline would cause the failure instead of SIGUSR1.
    assert "stopped too late" not in output, (
        f"A supervised app missed its deadline, so the failure was not caused by SIGUSR1:\n{output}"
    )
    assert "Problem discovered, activating recovery state: fallback_run_target" in output, (
        f"Launch manager did not enter fallback after the malfunction:\n{output}"
    )
    assert "Completed the request for Run Target fallback_run_target" in output, (
        f"Launch manager did not complete the fallback_run_target transition:\n{output}"
    )
    # lifecycle_signal.sh (delay=6s) sends SIGTERM; LM shuts down through Off.
    assert "Completed the request for Run Target Off" in output, (
        f"Launch manager did not reach Off state on shutdown:\n{output}"
    )
    assert (
        output.index("Completed the request for Run Target Startup")
        < cpp_terminated.start()
        < output.index("Problem discovered, activating recovery state: fallback_run_target")
        < output.index("Completed the request for Run Target fallback_run_target")
        < output.index("Completed the request for Run Target Off")
    ), f"Lifecycle state transitions are out of order:\n{output}"
