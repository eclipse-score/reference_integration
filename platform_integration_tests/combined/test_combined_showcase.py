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
"""Platform integration test for the lifecycle-managed communication showcase.

See ``test_communication_showcase`` for background on these platform
integration tests. All such tests in this package are combined into a single
suite by the ``pit`` target in this package's ``BUILD`` file.
"""

from attribute_plugin import add_test_properties
from showcase_runner import run_showcases


@add_test_properties(
    partially_verifies=[
        "stkh_req__communication__inter_process",
        "stkh_req__dependability__safety_features_1",
    ],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_lifecycle_comm_showcase(target):
    """The lifecycle-managed communication showcase starts the communication
    API example as a supervised process under the lifecycle launch manager,
    demonstrating score_lifecycle and score_communication working together on
    the platform."""

    run_showcases(target, "Lifecycle-managed Communication Example")
