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

from showcase_runner import run_showcases


def test_diagnostics_stack(target):
    """The gateway listens on 127.0.0.1:7690, the CDA loads the ECU databases and reports ready."""

    output = run_showcases(target, "Diagnostics Stack")
    assert "diagnostics_check: PASSED" in output, f"The diagnostics stack did not start:\n{output}"
    assert "diagnostics_check: FAILED" not in output, output
