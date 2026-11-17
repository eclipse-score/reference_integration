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
"""Platform integration test for the Kyron async runtime showcases.

See ``test_communication_showcase`` for background on these platform
integration tests. All such tests in this package are combined into a single
suite by the ``pit`` target in this package's ``BUILD`` file.
"""

from attribute_plugin import add_test_properties
from showcase_runner import run_showcases


@add_test_properties(
    partially_verifies=["stkh_req__execution_model__processes"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_async_runtime_showcase(target):
    """The Kyron showcases run asynchronous applications on the safe async
    runtime, demonstrating the platform's process and task management."""

    output = run_showcases(
        target,
        "Kyron select example",
        "Kyron safety task example",
        "Kyron basic example",
    )
    # select.rs: all three select! ordering scenarios completed.
    assert "Test 1" in output, f"Kyron select Test 1 did not complete:\n{output}"
    assert "Test 2" in output, f"Kyron select Test 2 did not complete:\n{output}"
    assert "Test 3" in output, f"Kyron select Test 3 did not complete:\n{output}"
    # safety_task.rs: all tasks were dispatched before joining.
    assert "Spawned all tasks" in output, (
        f"safety_task did not spawn all tasks:\n{output}"
    )
    assert "Program finished running." in output, (
        f"safety_task did not reach its terminal line:\n{output}"
    )
    # main_macro.rs: at least one async task ran on the runtime.
    assert "Message from task" in output, (
        f"main_macro produced no task messages:\n{output}"
    )
