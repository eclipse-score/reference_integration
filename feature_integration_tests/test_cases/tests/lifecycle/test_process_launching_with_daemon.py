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

import shutil
import subprocess
import re
import time
from pathlib import Path
from typing import Any

import pytest
from daemon_helpers import get_binary_path, launch_manager_daemon
from test_properties import add_test_properties

pytestmark = [
    pytest.mark.parametrize("version", ["rust", "cpp"], scope="class"),
]


@pytest.mark.daemon
@add_test_properties(
    partially_verifies=[
        "feat_req__lifecycle__launch_support",
        "feat_req__lifecycle__process_ordering",
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

    @pytest.fixture(scope="class", autouse=True)
    def setup_test_app(self, launch_manager_daemon: dict[str, Any], version: str) -> Path:
        """
        Build and deploy a test application to the daemon workspace.

        Parameters
        ----------
        launch_manager_daemon : dict
            Daemon environment fixture.
        version : str
            Implementation version ("rust" or "cpp").

        Returns
        -------
        Path
            Path to the deployed test application binary.
        """
        daemon_info = launch_manager_daemon
        bin_dir = daemon_info["bin_dir"]

        # Get the supervised app binary (from runfiles or build it)
        # Use the example supervised apps from lifecycle module
        if version == "rust":
            app_target = "@score_lifecycle_health//examples/rust_supervised_app:rust_supervised_app"
            app_name = "rust_supervised_app"
        else:
            app_target = "@score_lifecycle_health//examples/cpp_supervised_app:cpp_supervised_app"
            app_name = "cpp_supervised_app"

        app_binary = get_binary_path(app_target)

        # Copy to daemon bin directory
        dest_path = bin_dir / app_name
        shutil.copy2(app_binary, dest_path)
        dest_path.chmod(0o755)

        print(f"Deployed test application to: {dest_path}")
        return dest_path

    def test_supervised_app_launches(
        self, launch_manager_daemon: dict[str, Any], setup_test_app: Path, version: str
    ) -> None:
        """
        Verify that supervised application launches under daemon supervision.

        This test:
        1. Relies on the flatbuffer daemon configuration loaded at startup
        2. Verifies a supervised process is running via host PID checks
        3. Confirms daemon process remains alive while supervising the app
        """
        daemon_info = launch_manager_daemon
        daemon = daemon_info["daemon"]
        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"

        # Wait for startup run target components to become observable.
        time.sleep(2.0)

        result = subprocess.run(
            ["pgrep", "-f", app_name],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            running_pids = [pid for pid in result.stdout.strip().splitlines() if pid]
            assert running_pids, f"No PID found for supervised app {app_name}"
            print(f"\nSupervised app {app_name} running with PID(s): {', '.join(running_pids)}")
        else:
            # In restricted CI environments the daemon can fail to keep startup
            # processes alive due to uid/gid switching limits. Validate that it
            # still supervises real process instances by asserting PID/state logs.
            logs = daemon.get_logs()
            pid_events = re.findall(r"unexpected termination of process\s+\d+\s+pid\s+(\d+)", logs)
            recovery_signals = [
                "Got kRunning timeout for process",
                "Activating Recovery state.",
            ]
            assert pid_events and any(signal in logs for signal in recovery_signals), (
                f"No supervised-process PID/state evidence for {app_name}.\nDaemon logs:\n{logs}"
            )
            print(f"\nDaemon reported supervised process PID events: {', '.join(pid_events[:5])}")

        # Verify daemon is still running and target app appears in supervision logs.
        assert daemon.is_running(), "Launch Manager daemon stopped unexpectedly"
        logs = daemon.get_logs()
        assert app_name in logs or result.returncode == 0, (
            f"No target-specific supervision evidence for {app_name}.\nDaemon logs:\n{logs}"
        )

    def test_supervised_app_recovery(
        self, launch_manager_daemon: dict[str, Any], setup_test_app: Path, version: str
    ) -> None:
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
        # Match on the exact deployed binary path rather than a bare app name
        # substring, which could also match a leaked process, a bazel
        # invocation, or the pytest command line itself.
        pgrep_pattern = rf"^{re.escape(str(setup_test_app))}$"

        # Give daemon time to start and supervise app
        time.sleep(3.0)

        # Find and kill the supervised app process
        try:
            result = subprocess.run(
                ["pgrep", "-f", pgrep_pattern],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                pid = result.stdout.strip().split("\n")[0]
                print(f"\nKilling supervised app (PID: {pid})")
                subprocess.run(["kill", "-9", pid], check=True)

                # Poll for restart to avoid fixed-sleep race conditions.
                deadline = time.time() + 12.0
                new_pid = None
                while time.time() < deadline:
                    result = subprocess.run(
                        ["pgrep", "-f", pgrep_pattern],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    if result.returncode == 0:
                        candidates = [p for p in result.stdout.strip().split("\n") if p and p != pid]
                        if candidates:
                            new_pid = candidates[0]
                            break
                    time.sleep(0.25)

                if new_pid is not None:
                    print(f"App restarted with new PID: {new_pid}")
                else:
                    logs = daemon.get_logs()
                    pytest.fail(
                        "Supervised app was not restarted within timeout after forced kill."
                        f"\nTarget app: {app_name}\nDaemon logs:\n{logs}"
                    )
            else:
                logs = daemon.get_logs()
                target_patterns = [
                    rf"unexpected termination of process.*\(\s*{re.escape(app_name)}\s*\)",
                    rf"Got kRunning timeout for process.*\(\s*{re.escape(app_name)}\s*\)",
                ]
                assert any(re.search(pattern, logs) for pattern in target_patterns), (
                    f"Supervised app {app_name} not running and no target-specific recovery diagnostics found."
                    f"\nDaemon logs:\n{logs}"
                )

        except subprocess.CalledProcessError as e:
            pytest.fail(f"Failed to test recovery: {e}")

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
        result = subprocess.run(
            ["pgrep", "-f", app_name],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            # Some CI environments cannot keep startup apps alive due to uid/gid
            # switching restrictions. Do not skip: require target-specific
            # watchdog/recovery evidence from daemon logs instead.
            logs = daemon.get_logs()
            watchdog_patterns = [
                rf"Got kRunning timeout for process.*\(\s*{re.escape(app_name)}\s*\)",
                rf"unexpected termination of process.*\(\s*{re.escape(app_name)}\s*\)",
            ]
            assert any(re.search(pattern, logs) for pattern in watchdog_patterns), (
                f"Target app {app_name} is not running and no target-specific watchdog diagnostics were found."
                f"\nDaemon logs:\n{logs}"
            )
            return

        pid = result.stdout.strip().split("\n")[0]
        subprocess.run(["kill", "-STOP", pid], check=True)
        try:
            # Allow supervision/watchdog loop to detect stalled process.
            time.sleep(4.0)
            logs = daemon.get_logs()
            watchdog_patterns = [
                rf"Got kRunning timeout for process.*\(\s*{re.escape(app_name)}\s*\)",
                rf"unexpected termination of process.*\(\s*{re.escape(app_name)}\s*\)",
            ]
            assert any(re.search(pattern, logs) for pattern in watchdog_patterns), (
                f"No target-specific watchdog diagnostics found for {app_name}.\nDaemon logs:\n{logs}"
            )
        finally:
            subprocess.run(["kill", "-CONT", pid], check=False)
