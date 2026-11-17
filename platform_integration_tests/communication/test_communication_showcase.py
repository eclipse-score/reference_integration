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

import re

from attribute_plugin import add_test_properties
from showcase_runner import run_showcases


@add_test_properties(
    partially_verifies=["stkh_req__communication__inter_process"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_communication_showcase(target):
    """The communication showcase exchanges tire-pressure data between a
    producer process and a consumer process, demonstrating inter-process
    communication on the platform."""

    output = run_showcases(target, "Communication Sender Receiver Example")
    # SAMPLE_COUNT=5 in chapter_3; == 5 is intentional (not >= 1).
    assert output.count("Tire data sent") == 5, (
        f"Expected 5 sends from producer (one per loop iteration), got:\n{output}"
    )
    # Rust Debug for f32 omits ".0" on whole numbers; >= 1 because sync discovery may drop the first sample.
    pressures = [float(m) for m in re.findall(r"Tire \{ pressure: (\d+(?:\.\d+)?) \}", output)]
    assert len(pressures) >= 1, f"Consumer received no tire pressure samples:\n{output}"
    assert all(5.0 <= p <= 9.0 for p in pressures), (
        f"Received tire pressures out of expected range [5.0, 9.0]: {pressures}:\n{output}"
    )
    assert "Successfully unoffered the service" in output, (
        f"Producer did not successfully unoffer the service:\n{output}"
    )
    assert "Producer operation completed" in output, f"Producer did not complete:\n{output}"
    assert "Consumer operation completed" in output, f"Consumer did not complete:\n{output}"
