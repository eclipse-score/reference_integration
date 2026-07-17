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
Feature integration tests for lifecycle with running Launch Manager daemon.

These tests validate actual supervision and lifecycle management behavior
by running test applications under a real Launch Manager daemon instance.

To run these tests:

    # Run both Rust and C++ variants
    pytest feature_integration_tests/test_cases/tests/lifecycle/test_process_launching_with_daemon.py -v

    # Run only Rust variant
    pytest feature_integration_tests/test_cases/tests/lifecycle/test_process_launching_with_daemon.py -v -k rust

    # Run only C++ variant
    pytest feature_integration_tests/test_cases/tests/lifecycle/test_process_launching_with_daemon.py -v -k cpp

For detailed documentation, see ../../LIFECYCLE_TESTS_SUMMARY.md
"""

import json
import re
import subprocess
import time
import os
from pathlib import Path
from typing import Any

import pytest
from daemon_helpers import launch_manager_daemon
from test_properties import add_test_properties

pytestmark = [
    pytest.mark.parametrize("version", ["rust", "cpp"], scope="class"),
]


@pytest.mark.daemon
@add_test_properties(
    partially_verifies=[
        "feat_req__lifecycle__launch_support",
        "feat_req__lifecycle__parallel_launch_support",
        "feat_req__lifecycle__process_ordering",
        "feat_req__lifecycle__process_launch_args",
        "feat_req__lifecycle__uid_gid_support",
        "feat_req__lifecycle__launch_priority_support",
        "feat_req__lifecycle__scheduling_policy",
        "feat_req__lifecycle__retries_configurable",
        "feat_req__lifecycle__secpol_non_root",
        "feat_req__lifecycle__waitfor_support",
        "feat_req__lifecycle__cond_process_start",
        "feat_req__lifecycle__dependency_check",
        "feat_req__lifecycle__monitor_abnormal_term",
    ],
    test_type="integration",
    derivation_technique="end-to-end-testing",
)
class TestProcessLaunchingWithDaemon:
    """
    Verify lifecycle management with running Launch Manager daemon.

    These tests demonstrate end-to-end integration including:
    - Process launching under supervision
    - Execution state reporting to the daemon
    - Process monitoring and health checks
    - Recovery actions on failure
    """

    @staticmethod
    def _pgrep_cmdline_pattern(binary_path: str) -> str:
        """Build POSIX ERE pattern matching binary with optional arguments."""
        return rf"^{re.escape(binary_path)}([[:space:]]|$)"

    @staticmethod
    def _is_running(binary_path: str) -> bool:
        result = subprocess.run(
            ["pgrep", "-f", TestProcessLaunchingWithDaemon._pgrep_cmdline_pattern(binary_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0

    @staticmethod
    def _first_pid(binary_path: str) -> str | None:
        result = subprocess.run(
            ["pgrep", "-f", TestProcessLaunchingWithDaemon._pgrep_cmdline_pattern(binary_path)],
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
        """Read Linux /proc start time ticks for stable launch-order checks."""
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
    def _proc_cmdline(pid: str) -> list[str]:
        """Read process cmdline from /proc and split NUL-separated arguments."""
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
        return [arg.decode("utf-8") for arg in raw.split(b"\0") if arg]

    @staticmethod
    def _proc_environ(pid: str) -> dict[str, str]:
        """Read process environment from /proc as a key/value mapping."""
        raw = Path(f"/proc/{pid}/environ").read_bytes()
        env: dict[str, str] = {}
        for item in raw.split(b"\0"):
            if not item:
                continue
            key, sep, value = item.partition(b"=")
            if not sep:
                continue
            env[key.decode("utf-8")] = value.decode("utf-8")
        return env

    @staticmethod
    def _proc_status_ids(pid: str) -> tuple[int, int] | None:
        """Read effective uid/gid from /proc status for a process."""
        try:
            lines = Path(f"/proc/{pid}/status").read_text(encoding="utf-8").splitlines()
        except OSError:
            return None
        uid_line = next((line for line in lines if line.startswith("Uid:")), None)
        gid_line = next((line for line in lines if line.startswith("Gid:")), None)
        if uid_line is None or gid_line is None:
            return None
        try:
            uid_parts = uid_line.split()[1:]
            gid_parts = gid_line.split()[1:]
            # /proc status format: real effective saved filesystem
            return int(uid_parts[1]), int(gid_parts[1])
        except (IndexError, ValueError):
            return None

    @staticmethod
    def _proc_sched_policy_and_priority(pid: str) -> tuple[str, int] | None:
        """Read scheduler policy and RT priority from chrt output for a process."""
        result = subprocess.run(["chrt", "-p", pid], capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return None

        policy = None
        priority = None
        for line in result.stdout.splitlines():
            lower = line.lower().strip()
            if lower.startswith("scheduling policy"):
                policy = line.split(":", 1)[1].strip()
            elif lower.startswith("scheduling priority"):
                try:
                    priority = int(line.split(":", 1)[1].strip())
                except ValueError:
                    return None

        if policy is None or priority is None:
            return None
        return policy, priority

    @staticmethod
    def _wait_until(predicate, timeout_s: float, interval_s: float = 0.2) -> bool:
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            if predicate():
                return True
            time.sleep(interval_s)
        return False

    def test_startup_launches_supervised_apps(self, launch_manager_daemon: dict[str, Any], version: str) -> None:
        """
        Verify the initial Startup run target launches supervised processes.
        """
        daemon_info = launch_manager_daemon
        daemon = daemon_info["daemon"]
        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"
        app_path = str(daemon_info["apps"][version])

        started = self._wait_until(lambda: self._is_running(app_path), timeout_s=8.0)
        assert started, f"{app_name} was not launched in the initial Startup run target"
        assert daemon.is_running(), "Launch Manager daemon stopped unexpectedly"

    def test_dependency_gates_rust_startup(self, launch_manager_daemon: dict[str, Any], version: str) -> None:
        """Verify the Rust supervised app only appears after the C++ dependency is running."""
        daemon_info = launch_manager_daemon
        cpp_path = str(daemon_info["apps"]["cpp"])
        rust_path = str(daemon_info["apps"]["rust"])

        started = self._wait_until(
            lambda: self._is_running(cpp_path) and self._is_running(rust_path),
            timeout_s=8.0,
        )
        assert started, "cpp_supervised_app and rust_supervised_app should both be running before ordering check"

        cpp_pid = self._first_pid(cpp_path)
        rust_pid = self._first_pid(rust_path)
        assert cpp_pid is not None, "Could not resolve PID for cpp_supervised_app"
        assert rust_pid is not None, "Could not resolve PID for rust_supervised_app"

        cpp_start = self._proc_start_ticks(cpp_pid)
        rust_start = self._proc_start_ticks(rust_pid)
        assert cpp_start is not None, f"Could not resolve process start ticks for cpp_supervised_app pid={cpp_pid}"
        assert rust_start is not None, f"Could not resolve process start ticks for rust_supervised_app pid={rust_pid}"
        assert cpp_start <= rust_start, (
            "rust_supervised_app started before its configured dependency "
            f"(cpp_start={cpp_start}, rust_start={rust_start})"
        )

    def test_startup_declares_and_launches_multiple_processes(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """Verify startup run target includes multiple processes and both are launched."""
        config_path = Path(__file__).resolve().parents[3] / "configs" / "lifecycle_daemon_config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        startup_deps = config["run_targets"]["Startup"]["depends_on"]

        assert isinstance(startup_deps, list), "Startup depends_on should be a list"
        assert len(startup_deps) >= 2, "Startup run target should define multiple process dependencies"
        assert "cpp_supervised_app" in startup_deps, "cpp_supervised_app missing in Startup depends_on"
        assert "rust_supervised_app" in startup_deps, "rust_supervised_app missing in Startup depends_on"

        daemon_info = launch_manager_daemon
        cpp_path = str(daemon_info["apps"]["cpp"])
        rust_path = str(daemon_info["apps"]["rust"])
        both_running = self._wait_until(
            lambda: self._is_running(cpp_path) and self._is_running(rust_path),
            timeout_s=8.0,
        )
        assert both_running, "Startup should launch all configured supervised processes"

    def test_launch_process_arguments_are_applied(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """Verify launched process cmdline includes configured lifecycle arguments."""
        daemon_info = launch_manager_daemon
        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"
        app_path = str(daemon_info["apps"][version])

        started = self._wait_until(lambda: self._is_running(app_path), timeout_s=8.0)
        assert started, f"{app_name} was not launched before argument verification"

        pid = self._first_pid(app_path)
        assert pid is not None, f"Could not resolve PID for {app_name}"
        cmdline = self._proc_cmdline(pid)

        assert cmdline, f"Could not read command line arguments for {app_name} pid={pid}"
        assert "-d50" in cmdline, f"Configured launch argument '-d50' missing in {app_name} cmdline: {cmdline}"

    def test_launch_process_environment_is_applied(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """Verify launched process environment contains configured identifiers."""
        daemon_info = launch_manager_daemon
        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"
        app_path = str(daemon_info["apps"][version])

        started = self._wait_until(lambda: self._is_running(app_path), timeout_s=8.0)
        assert started, f"{app_name} was not launched before environment verification"

        pid = self._first_pid(app_path)
        assert pid is not None, f"Could not resolve PID for {app_name}"
        proc_env = self._proc_environ(pid)

        assert proc_env.get("PROCESSIDENTIFIER") == app_name, (
            f"PROCESSIDENTIFIER mismatch for {app_name}: {proc_env.get('PROCESSIDENTIFIER')}"
        )
        assert proc_env.get("IDENTIFIER") == app_name, (
            f"IDENTIFIER mismatch for {app_name}: {proc_env.get('IDENTIFIER')}"
        )

    def test_config_defines_uid_gid_scheduling_and_priority(
        self, launch_manager_daemon: dict[str, Any], version: str
    ) -> None:
        """Verify lifecycle config defines launch user/group and scheduling defaults."""
        config_path = Path(__file__).resolve().parents[3] / "configs" / "lifecycle_daemon_config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))

        sandbox = config["defaults"]["deployment_config"]["sandbox"]
        assert isinstance(sandbox.get("uid"), int), "Expected integer uid in sandbox defaults"
        assert isinstance(sandbox.get("gid"), int), "Expected integer gid in sandbox defaults"
        assert isinstance(sandbox.get("scheduling_priority"), int), "Expected integer scheduling priority"
        assert isinstance(sandbox.get("scheduling_policy"), str), "Expected scheduling policy string"

    def test_launched_process_uid_gid_matches_config_when_applied(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """Verify launched process runs with configured effective uid/gid when runtime applies sandbox identity."""
        daemon_info = launch_manager_daemon
        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"
        app_path = str(daemon_info["apps"][version])

        config_path = Path(__file__).resolve().parents[3] / "configs" / "lifecycle_daemon_config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        sandbox = config["defaults"]["deployment_config"]["sandbox"]
        expected_uid = int(sandbox["uid"])
        expected_gid = int(sandbox["gid"])

        started = self._wait_until(lambda: self._is_running(app_path), timeout_s=8.0)
        assert started, f"{app_name} was not launched before uid/gid verification"

        pid = self._first_pid(app_path)
        assert pid is not None, f"Could not resolve PID for {app_name}"
        proc_ids = self._proc_status_ids(pid)
        assert proc_ids is not None, f"Could not read /proc status uid/gid for {app_name} pid={pid}"

        effective_uid, effective_gid = proc_ids
        assert effective_uid == expected_uid, (
            f"Effective uid mismatch for {app_name}: expected {expected_uid}, got {effective_uid}"
        )
        assert effective_gid == expected_gid, (
            f"Effective gid mismatch for {app_name}: expected {expected_gid}, got {effective_gid}"
        )

    def test_launched_process_scheduling_matches_config_when_applied(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """Verify launched process uses configured scheduler policy and priority when applied."""
        daemon_info = launch_manager_daemon
        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"
        app_path = str(daemon_info["apps"][version])

        config_path = Path(__file__).resolve().parents[3] / "configs" / "lifecycle_daemon_config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        sandbox = config["defaults"]["deployment_config"]["sandbox"]
        configured_policy = sandbox["scheduling_policy"]
        configured_priority = int(sandbox["scheduling_priority"])

        started = self._wait_until(lambda: self._is_running(app_path), timeout_s=8.0)
        assert started, f"{app_name} was not launched before scheduling verification"

        pid = self._first_pid(app_path)
        assert pid is not None, f"Could not resolve PID for {app_name}"
        sched = self._proc_sched_policy_and_priority(pid)
        if sched is None:
            pytest.skip("Could not inspect scheduling metadata via chrt in this environment")

        policy, rt_priority = sched
        expected_policy = configured_policy.removeprefix("SCHED_").upper()
        assert policy.upper() == expected_policy, (
            f"Scheduling policy mismatch for {app_name}: expected {expected_policy}, got {policy}"
        )
        assert rt_priority == configured_priority, (
            f"Scheduling priority mismatch for {app_name}: expected {configured_priority}, got {rt_priority}"
        )

    def test_launch_manager_and_apps_are_not_running_as_root(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """Verify launch setup executes without root privileges in this integration setup."""
        daemon_info = launch_manager_daemon
        daemon = daemon_info["daemon"]
        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"
        app_path = str(daemon_info["apps"][version])

        assert os.geteuid() != 0, "Test environment unexpectedly runs as root"
        assert daemon.pid() > 0, "Launch Manager daemon pid should be available"

        started = self._wait_until(lambda: self._is_running(app_path), timeout_s=8.0)
        assert started, f"{app_name} was not launched before non-root verification"

        pid = self._first_pid(app_path)
        assert pid is not None, f"Could not resolve PID for {app_name}"
        proc_ids = self._proc_status_ids(pid)
        assert proc_ids is not None, f"Could not read /proc status uid/gid for {app_name} pid={pid}"
        effective_uid, _ = proc_ids
        assert effective_uid != 0, f"{app_name} is unexpectedly running as root"

    def test_config_defines_startup_retry_policy(self, launch_manager_daemon: dict[str, Any], version: str) -> None:
        """Verify lifecycle config defines configurable restart attempts on startup readiness failure."""
        config_path = Path(__file__).resolve().parents[3] / "configs" / "lifecycle_daemon_config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))

        restart_cfg = config["defaults"]["deployment_config"]["ready_recovery_action"]["restart"]
        attempts = restart_cfg.get("number_of_attempts")
        assert isinstance(attempts, int), "Expected integer number_of_attempts in ready_recovery_action.restart"
        assert attempts >= 0, "Expected non-negative number_of_attempts in startup retry policy"

    def test_supervised_app_recovery(self, launch_manager_daemon: dict[str, Any], version: str) -> None:
        """
        Verify that daemon restarts supervised app on failure.

        This test:
        1. Starts supervised application
        2. Kills the application process
        3. Verifies daemon detects failure and restarts it
        4. Validates recovery action execution
        """
        daemon_info = launch_manager_daemon
        daemon = daemon_info["daemon"]
        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"
        app_path = str(daemon_info["apps"][version])

        started = self._wait_until(lambda: self._is_running(app_path), timeout_s=8.0)
        assert started, f"{app_name} was not running before recovery test"

        old_pid = self._first_pid(app_path)
        assert old_pid is not None, f"Could not resolve PID for {app_name}"

        subprocess.run(["kill", "-9", old_pid], check=True)

        restarted = self._wait_until(
            lambda: (new_pid := self._first_pid(app_path)) is not None and new_pid != old_pid,
            timeout_s=12.0,
        )
        assert restarted, f"{app_name} was not restarted after forced termination"

        # Verify daemon is still running after recovery
        assert daemon.is_running(), "Launch Manager daemon should still be running"


@pytest.mark.daemon
@pytest.mark.manual
@add_test_properties(
    partially_verifies=[
        "feat_req__lifecycle__liveliness_detection",
        "feat_req__lifecycle__smart_watchdog_config",
    ],
    test_type="integration",
    derivation_technique="end-to-end-testing",
)
class TestHealthMonitoringWithDaemon:
    """
    Tests for health monitoring and watchdog with daemon.

    Marked as manual because these tests require specific setup
    and longer execution times.

    Run with: pytest -v -m manual
    """

    def test_watchdog_detection(self, launch_manager_daemon: dict[str, Any], version: str) -> None:
        """
        Verify watchdog detects unresponsive applications.

        This test would:
        1. Start an app that stops reporting health
        2. Verify daemon detects the failure
        3. Validate recovery action is triggered
        """
        daemon = launch_manager_daemon["daemon"]
        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"

        # Setup: stop the supervised process to emulate a non-reporting workload.
        app_path = str(launch_manager_daemon["apps"][version])
        result = subprocess.run(
            ["pgrep", "-f", TestProcessLaunchingWithDaemon._pgrep_cmdline_pattern(app_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            pytest.skip(f"{app_name} not active; activate Running run target before manual watchdog check")

        pid = result.stdout.strip().split("\n")[0]
        subprocess.run(["kill", "-STOP", pid], check=True)
        try:
            # Allow supervision/watchdog loop to detect stalled process.
            time.sleep(4.0)
            logs = daemon.get_logs()
            watchdog_patterns = [
                rf"Got kRunning timeout for process.*\(\s*{re.escape(app_name)}\s*\)",
                rf"unexpected termination of process.*\(\s*{re.escape(app_name)}\s*\)",
                rf"Alive Supervision \(\s*{re.escape(app_name)}_alive_supervision\s*\) switched to FAILED",
                rf"Alive Supervision \(\s*{re.escape(app_name)}_alive_supervision\s*\) switched to EXPIRED",
            ]
            assert any(re.search(pattern, logs) for pattern in watchdog_patterns), (
                f"No target-specific watchdog diagnostics found for {app_name}.\nDaemon logs:\n{logs}"
            )
        finally:
            subprocess.run(["kill", "-CONT", pid], check=False)
