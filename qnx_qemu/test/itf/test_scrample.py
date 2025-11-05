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


def test_scrample_app_is_deployed(target_fixture):
    user = "qnxuser"
    with target_fixture.sut.ssh(username=user) as ssh:
        exit_code, stdout, stderr = execute_command_output(
            ssh, "test -f scrample"
        )
        assert exit_code == 0, "SSH command failed"


# def test_scrample_app_is_running(target_fixture):
#     user = "qnxuser"
#     with target_fixture.sut.ssh(username=user) as ssh:
#         exit_code, stdout, stderr = execute_command_output(
#             # ssh, "./scrample -n 5 -t 100 -m recv & ./scrample -n 20 -t 100 -m send"
#             # ssh, "./scrample -n 20 -t 100 -m send"
#             ssh, "./scrample -n 10 -t 100 -m send",
#             timeout = 30, max_exec_time = 180,
#             logger_in = logger, verbose = True,
#         )
#         assert exit_code == 0, "SSH command failed"
