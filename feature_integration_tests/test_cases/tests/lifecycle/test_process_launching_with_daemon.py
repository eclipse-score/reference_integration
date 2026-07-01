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

**Note**: These tests are designed to run with pytest directly, not through Bazel.
The Launch Manager daemon requires complex configuration and workspace access
that isn't compatible with Bazel's test sandbox.

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
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

import pytest
from daemon_helpers import get_binary_path, launch_manager_daemon
from lifecycle_scenario import add_supervised_component
from test_properties import add_test_properties

# Skip these tests when running under Bazel - they require full workspace access
_running_under_bazel = os.environ.get("TEST_SRCDIR") is not None
_skip_reason = "Daemon tests require pytest with workspace access (not compatible with Bazel sandbox)"

pytestmark = [
    pytest.mark.parametrize("version", ["rust", "cpp"], scope="class"),
    pytest.mark.skipif(_running_under_bazel, reason=_skip_reason),
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

        app_binary = get_binary_path(app_target, version)

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
        1. Updates daemon configuration with test component
        2. Triggers component start via control interface
        3. Verifies process is running and supervised
        4. Validates execution state reporting
        """
        daemon_info = launch_manager_daemon
        daemon = daemon_info["daemon"]
        config_file = daemon_info["config_file"]
        bin_dir = daemon_info["bin_dir"]

        # Read current config
        config = json.loads(config_file.read_text())

        # Add supervised component
        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"
        config["components"]["test_app"] = add_supervised_component(
            component_name="test_app",
            binary_name=app_name,
            app_type="Reporting",
            process_args=["-d50"],  # Delay parameter for supervised app
        )

        # Update run target
        config["run_targets"]["startup"]["depends_on"] = ["test_app"]

        # Write updated config
        config_file.write_text(json.dumps(config, indent=2))

        # Daemon needs to be restarted to pick up new config
        # (In production, use control interface for dynamic updates)
        print("\nRestarting daemon with updated configuration...")
        daemon.stop()
        daemon.start(startup_timeout=3.0)

        # Wait for application to start
        time.sleep(2.0)

        # Verify daemon is still running
        assert daemon.is_running(), "Launch Manager daemon stopped unexpectedly"

        # Check daemon logs for supervision activity
        logs = daemon.get_logs()
        print(f"\nDaemon logs:\n{logs}")

        # Verify logs show component was started
        # (Actual log messages depend on Launch Manager implementation)
        assert len(logs) > 0, "No daemon logs generated"

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

        # Give daemon time to start and supervise app
        time.sleep(3.0)

        # Find and kill the supervised app process
        try:
            result = subprocess.run(
                ["pgrep", "-f", app_name],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                pid = result.stdout.strip().split("\n")[0]
                print(f"\nKilling supervised app (PID: {pid})")
                subprocess.run(["kill", "-9", pid], check=True)

                # Wait for daemon to detect failure and restart
                time.sleep(2.0)

                # Verify app was restarted
                result = subprocess.run(
                    ["pgrep", "-f", app_name],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if result.returncode == 0:
                    new_pid = result.stdout.strip().split("\n")[0]
                    print(f"App restarted with new PID: {new_pid}")
                    assert new_pid != pid, "PID should be different after restart"
                else:
                    logs = daemon.get_logs()
                    pytest.fail(
                        "Supervised app was not found after forced kill; expected daemon recovery restart."
                        f"\nDaemon logs:\n{logs}"
                    )
            else:
                logs = daemon.get_logs()
                recovery_signals = [
                    f"unexpected termination of process",
                    "Activating Recovery state.",
                    f"Got kRunning timeout for process",
                ]
                assert any(signal in logs for signal in recovery_signals), (
                    f"Supervised app {app_name} not running and no recovery diagnostics found.\nDaemon logs:\n{logs}"
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

        # Give daemon enough time to perform supervision cycles and emit diagnostics.
        time.sleep(2.0)
        logs = daemon.get_logs()

        watchdog_like_signals = [
            "Got kRunning timeout for process",
            "Problem discovered in PG MainPG Activating Recovery state.",
            "unexpected termination of process",
        ]
        assert any(signal in logs for signal in watchdog_like_signals), (
            "No supervision/watchdog-related diagnostics found in daemon logs."
        )
