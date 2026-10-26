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
@add_test_properties(
    # partially_verifies=["<baselibs stakeholder req id>"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_baselibs_showcase(target):
    """..."""
    run_showcases(
        target,
        "Baselibs Builtin Logger Example",
        "Baselibs Custom Logger Example",
        "Baselibs C++ Logger Init Example",
    )
