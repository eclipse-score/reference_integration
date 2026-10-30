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
"""Platform integration test for the communication showcase.

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

All such tests in this package are combined into a single suite by the
``pit`` target in this package's ``BUILD`` file.
"""

from attribute_plugin import add_test_properties
from showcase_runner import run_showcases


@add_test_properties(
    partially_verifies=["stkh_req__communication__inter_process"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_communication_showcase(target):
    """The communication showcase exchanges data between a sender and a
    receiver process, demonstrating inter-process communication on the
    platform."""

    run_showcases(target, "Communication Sender Receiver Example")


@add_test_properties(
    partially_verifies=["stkh_req__communication__inter_process"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_communication_platform_heartbeat(target):
    """A consumer process finds the heartbeat service deployed by the platform
    through mw::com service discovery, reads the S-CORE version the platform
    reports and receives heartbeats from it whose baselibs CRC32 is intact.
    The consumer brings no provider of its own, so this fails if the platform
    does not deploy a working service or runs a different S-CORE version."""

    output = run_showcases(target, "Communication Platform Heartbeat")
    assert "heartbeat_consumer: platform runs S-CORE" in output, (
        f"Platform did not report its S-CORE version:\n{output}"
    )
    assert "heartbeat_consumer: received" in output, f"Consumer did not receive heartbeats from the platform:\n{output}"
    assert "heartbeat_consumer: FAILED" not in output, output
