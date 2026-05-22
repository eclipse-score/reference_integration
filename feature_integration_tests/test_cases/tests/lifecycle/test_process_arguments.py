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
Feature integration tests for process launching with arguments.

Tests verify that the Launch Manager can launch processes with specified
arguments and working directories.
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
        "feat_req__lifecycle__process_launch_args",
        "feat_req__lifecycle__cwd_support",
        "feat_req__lifecycle__process_input_output",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestProcessArguments(LifecycleScenario):
    """
    Verify process launching with arguments and working directory.

    This test confirms that processes can be launched with custom arguments
    and working directory settings.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.process_arguments"

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path) -> dict[str, Any]:
        return {
            "test": {
                "test_duration_ms": 100,
                "args": ["--mode", "test", "--verbose"],
                "working_dir": "/tmp",
            }
        }

    def test_process_args_received(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that process received command line arguments.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Received arguments: --mode test --verbose" in results.stdout, "Process arguments were not received"
        else:
            args_logs = logs_info_level.get_logs(field="message", pattern="Received arguments: --mode test --verbose")
            assert len(args_logs) > 0, "Process arguments were not received"

    def test_working_directory_set(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that working directory was properly set.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Working directory: /tmp" in results.stdout, "Working directory was not set correctly"
        else:
            cwd_logs = logs_info_level.get_logs(field="message", pattern="Working directory: /tmp")
            assert len(cwd_logs) > 0, "Working directory was not set correctly"
