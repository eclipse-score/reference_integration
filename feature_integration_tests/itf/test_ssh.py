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

import score.itf


@score.itf.plugins.core.requires_capabilities("ssh")
def test_ssh_with_default_user(target):
    with target.ssh() as ssh:
        exit_code, stdout, stderr = ssh.execute_command_output(
            "echo 'Username:' $USER && uname -a"
        )
        assert exit_code == 0, "SSH command failed"
        assert "Username: root" in stdout[0], "Expected username not found in output"
        assert "QNX Qnx_S-core 8.0.0" in stdout[1], (
            "Expected QNX kernel information not found in output"
        )
        assert stderr == [], "Expected no error output"


@score.itf.plugins.core.requires_capabilities("ssh")
def test_ssh_with_qnx_user(target):
    user = "qnxuser"
    with target.ssh(username=user) as ssh:
        exit_code, stdout, stderr = ssh.execute_command_output(
            "echo 'Username:' $USER && uname -a"
        )
        assert exit_code == 0, "SSH command failed"
        assert f"Username: {user}" in stdout[0], "Expected username not found in output"
        assert "QNX Qnx_S-core 8.0.0" in stdout[1], (
            "Expected QNX kernel information not found in output"
        )
        assert stderr == [], "Expected no error output"
