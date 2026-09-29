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
"""Platform integration tests.

These tests exercise the demo applications shipped in ``//showcases`` as
end-to-end platform integration tests. Each test drives one showcase on the
deployed target image through the showcase entrypoint
(``/showcases/bin/cli``) and asserts that it runs to completion.

Unlike the feature integration tests (which verify individual ``feat_req``),
these tests demonstrate platform-level capabilities and are therefore linked
to the stakeholder requirements (``stkh_req``) they partially verify via
``@add_test_properties``. docs-as-code's source code linker turns those
properties into ``testlink`` attributes on the referenced requirement needs,
which surface in the "Stakeholder Requirements" chapter of the platform
verification report.
"""

import logging

from attribute_plugin import add_test_properties

logger = logging.getLogger(__name__)

_CLI = "/showcases/bin/cli"


def _run_showcases(target, *names: str) -> None:
    """Run the named showcases via the showcase entrypoint and assert success.

    ``run_score`` in the showcase CLI prints a per-example completion banner
    and exits 0 once every app of an example has been spawned and joined, so
    both the exit code and the banner are checked to confirm the showcase ran
    end-to-end on the platform.
    """
    selection = ",".join(names)
    exit_code, out = target.execute(f"{_CLI} --examples='{selection}'")
    output = out.decode(errors="replace")
    logger.info(output)
    assert exit_code == 0, f"Showcase CLI exited with {exit_code}:\n{output}"
    for name in names:
        assert f"Example '{name}' finished successfully" in output, (
            f"Showcase '{name}' did not finish successfully:\n{output}"
        )


@add_test_properties(
    partially_verifies=["stkh_req__communication__inter_process"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_communication_showcase(target):
    """The communication showcase exchanges data between a sender and a
    receiver process, demonstrating inter-process communication on the
    platform."""

    _run_showcases(target, "Communication Sender Receiver Example")


@add_test_properties(
    partially_verifies=["stkh_req__dev_experience__logging_support"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_logging_showcase(target):
    """The logging showcase runs an application logging via ``mw::log`` with
    the console, remote (DLT) and file backends, demonstrating the platform's
    logging support."""

    _run_showcases(target, "LoggingApp Demo")


@add_test_properties(
    partially_verifies=["stkh_req__execution_model__processes"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_async_runtime_showcase(target):
    """The Kyron showcases run asynchronous applications on the safe async
    runtime, demonstrating the platform's process and task management."""

    _run_showcases(
        target,
        "Kyron select example",
        "Kyron safety task example",
        "Kyron basic example",
    )


@add_test_properties(
    partially_verifies=["stkh_req__dependability__safety_features_1"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_lifecycle_showcase(target):
    """The lifecycle showcase launches two supervised applications and records
    a malfunction, demonstrating the platform's health and lifecycle
    management."""

    _run_showcases(target, "Simple Health and lifecycle management example")


@add_test_properties(
    partially_verifies=["stkh_req__time__vehicle_time_api"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_vehicle_time_showcase(target):
    """The vehicle time showcase obtains a combined snapshot of the
    PTP-synchronized vehicle time and the local monotonic time, demonstrating
    the platform's vehicle time base API."""

    _run_showcases(target, "Vehicle Time Example")
