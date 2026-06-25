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
"""
Feature integration tests for I/O and file descriptor management.

Tests verify that the Launch Manager supports standard handle redirection,
file descriptor inheritance control, and process detachment.
"""

from pathlib import Path
from typing import Any

import pytest
from fit_scenario import ResultCode
from lifecycle_scenario import LifecycleScenario
from test_properties import add_test_properties
from testing_utils import LogContainer, ScenarioResult

pytestmark = pytest.mark.parametrize("version", ["rust", "cpp"], scope="class")


@add_test_properties(
    partially_verifies=[
        "feat_req__lifecycle__std_handle_redir",
        "feat_req__lifecycle__fd_inheritance",
        "feat_req__lifecycle__detach_parent_process",
        "feat_req__lifecycle__retries_configurable",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestIOAndFileDescriptors(LifecycleScenario):
    """
    Verify I/O and file descriptor management.

    This test confirms that standard handles can be redirected,
    file descriptor inheritance can be controlled, and processes
    can be detached from parent.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.io_and_file_descriptors"

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path) -> dict[str, Any]:
        return {
            "test": {
                "test_duration_ms": 150,
                "redirect_stdout": "/tmp/app.log",
                "redirect_stderr": "/tmp/app_error.log",
                "close_fds": True,
                "detach_from_parent": True,
                "max_retries": 3,
            }
        }

    def test_stdout_redirection(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that stdout can be redirected.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "stdout redirected to /tmp/app.log" in results.stdout, "stdout redirection failed"
        else:
            stdout_logs = logs_info_level.get_logs(field="message", pattern="stdout redirected to /tmp/app.log")
            assert len(stdout_logs) > 0, "stdout redirection failed"

    def test_stderr_redirection(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that stderr can be redirected.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "stderr redirected to /tmp/app_error.log" in results.stdout, "stderr redirection failed"
        else:
            stderr_logs = logs_info_level.get_logs(field="message", pattern="stderr redirected to /tmp/app_error.log")
            assert len(stderr_logs) > 0, "stderr redirection failed"

    def test_fd_inheritance_control(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that file descriptor inheritance can be controlled.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "File descriptors closed on exec" in results.stdout, "FD inheritance control failed"
        else:
            fd_logs = logs_info_level.get_logs(field="message", value="File descriptors closed on exec")
            assert len(fd_logs) > 0, "FD inheritance control failed"

    def test_process_detachment(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that process can be detached from parent.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Process detached from parent" in results.stdout, "Process detachment failed"
        else:
            detach_logs = logs_info_level.get_logs(field="message", value="Process detached from parent")
            assert len(detach_logs) > 0, "Process detachment failed"

    def test_retry_configuration(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that retry attempts can be configured.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Max retries configured: 3" in results.stdout, "Retry configuration failed"
        else:
            retry_logs = logs_info_level.get_logs(field="message", pattern="Max retries configured: 3")
            assert len(retry_logs) > 0, "Retry configuration failed"
