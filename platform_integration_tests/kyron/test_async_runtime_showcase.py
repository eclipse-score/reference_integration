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
    # "panicked" only appears on Linux; QNX drops stderr.
    assert "Test 3" in output, f"Kyron select did not reach Test 3:\n{output}"
    assert "panicked" not in output, f"Kyron select binary panicked:\n{output}"
    assert "Worker-N: passing_safety_task" in output, f"safety_task passing_safety_task body did not run:\n{output}"
    assert "Worker-N: failing_safety_task" in output, f"safety_task failing_safety_task body did not run:\n{output}"
    assert "Dedicated worker (dw1): passing_non_safety_task" in output, (
        f"safety_task dedicated task did not run:\n{output}"
    )
    assert "Program finished running." in output, f"safety_task did not reach its terminal line:\n{output}"
    assert all(f"Message from task {i}" in output for i in range(10)), (
        f"main_macro did not produce all 10 task messages:\n{output}"
    )
