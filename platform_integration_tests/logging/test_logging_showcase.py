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
    the console, remote (DLT) and file backends, demonstrating the platform's
    logging support."""

    run_showcases(target, "LoggingApp Demo")
