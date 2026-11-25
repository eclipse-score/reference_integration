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

# Transitional: the tests moved to //platform_integration_tests. build_and_test_qnx.yml
# runs via pull_request_target, i.e. from main, and still calls this target until this
# change is merged. Delete this package afterwards.
test_suite(
    name = "itf",
    tags = [
        "manual",
    ],
    tests = [
        "//platform_integration_tests/logging:remote_logging",
        "//platform_integration_tests/ssh",
    ],
)
