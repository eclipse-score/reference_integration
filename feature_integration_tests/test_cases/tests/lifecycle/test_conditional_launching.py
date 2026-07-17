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
Feature integration tests for conditional launching against a real Launch Manager.

Unlike scenario-stub checks, these tests validate behavior from an actual
launch_manager process started with lifecycle daemon configuration.
"""

import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any

import pytest
from daemon_helpers import launch_manager_daemon
from test_properties import add_test_properties

pytestmark = [
    pytest.mark.daemon,
    pytest.mark.parametrize("version", ["rust", "cpp"], scope="class"),
]


@add_test_properties(
    partially_verifies=[
        "feat_req__lifecycle__launch_support",
        "feat_req__lifecycle__waitfor_support",
        "feat_req__lifecycle__cond_process_start",
        "feat_req__lifecycle__dependency_check",
        "feat_req__lifecycle__process_ordering",
    ],
    test_type="integration",
    derivation_technique="end-to-end-testing",
)
class TestConditionalLaunchingWithDaemon:
    """Verify dependency-based conditional launching with real daemon behavior."""

    @staticmethod
    def _pgrep_cmdline_pattern(binary_path: str) -> str:
        """Build POSIX ERE pattern matching binary with optional arguments."""
        return rf"^{re.escape(binary_path)}([[:space:]]|$)"

    @staticmethod
    def _is_running(binary_path: str) -> bool:
        result = subprocess.run(
            ["pgrep", "-f", TestConditionalLaunchingWithDaemon._pgrep_cmdline_pattern(binary_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0

    @staticmethod
    def _first_pid(binary_path: str) -> str | None:
        result = subprocess.run(
            ["pgrep", "-f", TestConditionalLaunchingWithDaemon._pgrep_cmdline_pattern(binary_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return None
        lines = [line for line in result.stdout.splitlines() if line]
        return lines[0] if lines else None

    @staticmethod
    def _proc_start_ticks(pid: str) -> int | None:
        try:
            stat_fields = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").split()
        except OSError:
            return None
        if len(stat_fields) <= 21:
            return None
        try:
            return int(stat_fields[21])
        except ValueError:
            return None

    @staticmethod
    def _wait_until(predicate, timeout_s: float, interval_s: float = 0.2) -> bool:
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            if predicate():
                return True
            time.sleep(interval_s)
        return False

    def test_startup_launches_conditioned_processes(self, launch_manager_daemon: dict[str, Any], version: str) -> None:
        """Verify supervised processes are launched as part of conditional startup."""
        daemon_info = launch_manager_daemon
        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"
        app_path = str(daemon_info["apps"][version])

        started = self._wait_until(lambda: self._is_running(app_path), timeout_s=8.0)
        assert started, f"{app_name} was not launched in conditional startup"

    def test_rust_launch_is_conditioned_on_cpp_dependency(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """Verify rust app starts no earlier than its configured C++ dependency."""
        daemon_info = launch_manager_daemon
        cpp_path = str(daemon_info["apps"]["cpp"])
        rust_path = str(daemon_info["apps"]["rust"])

        started = self._wait_until(
            lambda: self._is_running(cpp_path) and self._is_running(rust_path),
            timeout_s=8.0,
        )
        assert started, "cpp_supervised_app and rust_supervised_app should both be running"

        cpp_pid = self._first_pid(cpp_path)
        rust_pid = self._first_pid(rust_path)
        assert cpp_pid is not None, "Could not resolve PID for cpp_supervised_app"
        assert rust_pid is not None, "Could not resolve PID for rust_supervised_app"

        cpp_start = self._proc_start_ticks(cpp_pid)
        rust_start = self._proc_start_ticks(rust_pid)
        assert cpp_start is not None, f"Could not resolve start ticks for cpp_supervised_app pid={cpp_pid}"
        assert rust_start is not None, f"Could not resolve start ticks for rust_supervised_app pid={rust_pid}"
        assert cpp_start <= rust_start, (
            "rust_supervised_app started before its configured dependency "
            f"(cpp_start={cpp_start}, rust_start={rust_start})"
        )

    def test_rust_never_runs_without_cpp_running(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """Verify conditional gating keeps rust app from running before cpp is active."""
        daemon_info = launch_manager_daemon
        cpp_path = str(daemon_info["apps"]["cpp"])
        rust_path = str(daemon_info["apps"]["rust"])

        deadline = time.time() + 8.0
        while time.time() < deadline:
            rust_running = self._is_running(rust_path)
            cpp_running = self._is_running(cpp_path)
            if rust_running and not cpp_running:
                pytest.fail("rust_supervised_app became running before cpp_supervised_app was active")
            if rust_running and cpp_running:
                return
            time.sleep(0.2)

        assert False, "Timed out waiting for rust_supervised_app to reach running state"

    def test_dependency_is_declared_in_lifecycle_config(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """Verify runtime configuration defines rust conditional dependency on cpp."""
        config_path = Path(__file__).resolve().parents[3] / "configs" / "lifecycle_daemon_config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))

        rust_component = config["components"]["rust_supervised_app"]["component_properties"]
        depends_on = rust_component.get("depends_on", [])
        assert "cpp_supervised_app" in depends_on, (
            "Expected rust_supervised_app to depend on cpp_supervised_app in lifecycle daemon config"
        )
