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
"""Platform integration test for the diagnostics stack.

The platform deploys the OpenSOVD gateway and the classic diagnostic adapter (CDA) in
``/usr/bin/diagnostics`` (``//deploy/diagnostics``). The ``Diagnostics Stack`` showcase starts
both with the ECU databases of the showcases, so it only passes against a platform that deploys
working binaries.
"""

from attribute_plugin import add_test_properties
from diagnostics_orchestration import check_diagnostics_and_platform_run_coexist
from showcase_runner import run_showcases


@add_test_properties(
    partially_verifies=["stkh_req__diagnostics__via_sovd"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_diagnostics_stack(target):
    """The gateway listens on 127.0.0.1:7690, the CDA loads the ECU databases and reports ready."""

    output = run_showcases(target, "Diagnostics Stack")
    assert "diagnostics_check: PASSED" in output, f"The diagnostics stack did not start:\n{output}"
    assert "diagnostics_check: FAILED" not in output, output


@add_test_properties(
    partially_verifies=[
        "stkh_req__diagnostics__via_sovd",
        "stkh_req__execution_model__processes",
    ],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_diagnostics_and_platform_run_coexist(target):
    """The boot-time diagnostics manager and Platform Run share the same /tmp."""
    check_diagnostics_and_platform_run_coexist(target)
