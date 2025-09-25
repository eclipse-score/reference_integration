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
from itf.plugins.com.ssh import execute_command


def test_ssh_with_default_user(target_fixture):
    with target_fixture.sut.ssh() as ssh:
        execute_command(ssh, "echo 'Username:' $USER && uname -a")


def test_ssh_with_qnx_user(target_fixture):
    with target_fixture.sut.ssh(username="qnxuser") as ssh:
        execute_command(ssh, "echo 'Username:' $USER && uname -a")
