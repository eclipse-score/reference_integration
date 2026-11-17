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
"""Platform integration test for the logging showcase.

See ``test_communication_showcase`` for background on these platform
integration tests. All such tests in this package are combined into a single
suite by the ``pit`` target in this package's ``BUILD`` file.
"""

from attribute_plugin import add_test_properties
from showcase_runner import run_showcases


@add_test_properties(
    partially_verifies=["stkh_req__dev_experience__logging_support"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_logging_showcase(target):
    """The logging showcase runs an application logging via ``mw::log`` with
    the console and remote (DLT) backends, demonstrating the platform's
    logging support."""

    output = run_showcases(target, "LoggingApp Demo")
    # Config missing → mw::log falls back to APID "NONE".
    assert "mw::log initialization error" not in output, (
        f"mw::log fell back to console logging — config was not found:\n{output}"
    )
    # Split: concurrent DLT output can interleave lines, breaking a full-line match.
    assert "EXA DFLT" in output, f"logging_app APID/CTID not found — logging config was not applied:\n{output}"
    assert "Logging Application DoLogging" in output, f"logging_app did not reach its main log path:\n{output}"
    assert "LGGG LOGG" in output, f"dlt_generator APID/CTID not found — logging config was not applied:\n{output}"
    assert "DLT generator finished." in output, f"dlt_generator did not complete its run:\n{output}"
