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
"""Helper for driving the baselibs test app on the deployed target."""

import logging

logger = logging.getLogger(__name__)

_TEST_APP_BIN = "/usr/bin/baselibs_test_app"


def run_test_app(target, subcommand: str) -> str:
    """Run one subcommand of the test app on the target and return its stdout.

    Asserts the binary exits successfully so every feature test fails loudly if
    the exercised baselibs library misbehaves on the target.
    """
    exit_code, out = target.execute(f"{_TEST_APP_BIN} {subcommand}")
    output = out.decode(errors="replace").strip()
    logger.info("baselibs_test_app %s -> (%s) %s", subcommand, exit_code, output)
    assert exit_code == 0, f"baselibs_test_app {subcommand} exited with {exit_code}:\n{output}"
    return output
