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
from itf.plugins.com.ssh import execute_command_output, execute_command, _read_output_with_timeout, command_with_etc
import logging

logger = logging.getLogger(__name__)


def test_lifecycle_apps_are_deployed(target_fixture):
    with target_fixture.sut.ssh() as ssh:
        exit_code, stdout, stderr = execute_command_output(
            ssh, "test -f /lifecycle/launch_manager/launch_manager &&" \
                 "test -f /lifecycle/cpp_supervised_app/cpp_supervised_app &&" \
                 "test -f /lifecycle/control_daemon/control_daemon"
        )
        assert exit_code == 0, "SSH command failed"

def test_lifecycle_test_app_is_running(target_fixture):
    with target_fixture.sut.ssh() as ssh:
        # Using a more complex cmd is not working with `execute_command_output`
        # Therefore, the command had to be put into a separate script.
        cmd = "/lifecycle/start.sh" 
        exit_code, stdout, stderr = execute_command_output(ssh, cmd,
            timeout = 30, max_exec_time = 180,
            logger_in = logger, verbose = True)

        logger.info (stdout)
        logger.info (stderr)

        assert exit_code == 0, "SSH command failed"
