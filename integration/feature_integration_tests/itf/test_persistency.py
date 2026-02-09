# *******************************************************************************
# Copyright (c) 2025 Contributors to the Eclipse Foundation
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
from itf.plugins.com.ping import ping
from itf.plugins.com.ssh import execute_command_output
import logging

logger = logging.getLogger(__name__)


def test_persistency_test_app_is_deployed(target_fixture):
    with target_fixture.sut.ssh() as ssh:
        exit_code, stdout, stderr = execute_command_output(
            ssh, "test -f cpp_tests_persistency"
        )
        assert exit_code == 0, "SSH command failed"

def test_persistency_test_app_is_running(target_fixture):
    with target_fixture.sut.ssh() as ssh:
        exit_code, stdout, stderr = execute_command_output(
            ssh, "./cpp_tests_persistency  --name basic.basic --input '{\"kvs_parameters\":{\"instance_id\":0}}'",
            timeout = 30, max_exec_time = 180,
            logger_in = logger, verbose = True,
        )

        logger.info (stdout)
        logger.info (stderr)

        assert exit_code == 0, "SSH command failed"
