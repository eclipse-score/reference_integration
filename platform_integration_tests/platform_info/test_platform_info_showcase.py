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
"""Platform integration test for the platform info service.

The platform deploys a platform info service (``//deploy/platform_info``) that
reports the S-CORE version the platform was built from over mw::com. The
``Platform Version Check`` showcase runs a consumer that brings no provider of
its own, so it only passes against a platform that deploys the service and
reports the S-CORE version the showcases were built for.
"""

from attribute_plugin import add_test_properties
from showcase_runner import run_showcases


@add_test_properties(
    partially_verifies=["stkh_req__communication__inter_process"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_platform_version(target):
    """A consumer process finds the platform info service deployed by the
    platform through mw::com service discovery and reads the S-CORE version
    the platform reports, sealed with a baselibs CRC32. The consumer brings no
    provider of its own, so this fails if the platform does not deploy a
    working service or runs a different S-CORE version."""

    output = run_showcases(target, "Platform Version Check")
    assert "platform_info_consumer: S-CORE version check passed" in output, (
        f"Platform did not pass the S-CORE version check:\n{output}"
    )
    assert "platform_info_consumer: FAILED" not in output, output
