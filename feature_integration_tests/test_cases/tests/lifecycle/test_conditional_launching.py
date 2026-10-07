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
Dependency-based launching FITs against a real launch_manager on lifecycle_daemon_config.json,
where rust_supervised_app `depends_on` cpp_supervised_app. (test_conditional_launching_scenario.py
only tests the FIT's own scenario stub.)
"""

import json
from pathlib import Path
from typing import Any

import pytest
from daemon_helpers import (
    is_running,
    start_launch_manager_daemon,
    stop_launch_manager_daemon,
    wait_until,
)
from test_properties import add_test_properties


@pytest.mark.parametrize("version", ["rust", "cpp"], scope="class")
class TestConditionalLaunchingWithDaemon:
    """Startup launch of each supervised app, per `version`, via the class-scoped fixture."""

    @add_test_properties(
        partially_verifies=["feat_req__lifecycle__launch_support"],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
    )
    def test_startup_launches_conditioned_processes(self, launch_manager_daemon: dict[str, Any], version: str) -> None:
        """The `version` app is running (pgrep) within 8 s of daemon start."""
        daemon_info = launch_manager_daemon
        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"
        app_path = str(daemon_info["apps"][version])

        started = wait_until(lambda: is_running(app_path), timeout_s=8.0)
        assert started, f"{app_name} was not launched in conditional startup"


class TestConditionalLaunchingBlocksOnMissingDependency:
    """rust startup is gated on cpp, observed by withholding cpp.

    Own daemon, in its own class so the class-scoped fixture is torn down first (fixed shm
    names; see daemon_helpers._live_daemons). Not parametrized: runs once.
    """

    @add_test_properties(
        partially_verifies=[
            "feat_req__lifecycle__conditional_startup",
            "feat_req__lifecycle__process_ordering",
        ],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
    )
    def test_rust_stays_down_until_cpp_dependency_becomes_available(
        self, tmp_path_factory: pytest.TempPathFactory
    ) -> None:
        """While cpp is non-executable, rust must stay down for 4 s and the daemon must log the cpp
        launch failure at least twice (it keeps retrying rather than aborting). After cpp is made
        executable, cpp and then rust must be running within 8 s each.

        Limitations: "running" is pgrep process existence; rust has a single dependency, so this
        does not distinguish single-edge gating from multi-dependency behavior.
        No `cond_process_start` claim: that requirement is about starting on the return value
        of earlier processes, which this config does not use.
        """
        # Precondition: without this edge the negative check below would pass vacuously.
        config_path = Path(__file__).resolve().parents[3] / "configs" / "lifecycle_daemon_config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        rust_depends_on = config["components"]["rust_supervised_app"]["component_properties"].get("depends_on", [])
        assert "cpp_supervised_app" in rust_depends_on, (
            "Expected rust_supervised_app to depend on cpp_supervised_app in lifecycle daemon config"
        )

        daemon_info = start_launch_manager_daemon(
            tmp_path_factory,
            blocked_apps=frozenset({"cpp"}),
            wait_for_apps=False,
        )
        try:
            cpp_path = daemon_info["apps"]["cpp"]
            rust_path = str(daemon_info["apps"]["rust"])

            # cpp is mode 0000, so its exec fails: rust must not appear meanwhile.
            rust_started_early = wait_until(lambda: is_running(rust_path), timeout_s=4.0)
            assert not rust_started_early, (
                "rust_supervised_app started even though its cpp_supervised_app dependency "
                "was withheld (non-executable); dependency gating was not enforced"
            )

            # >= 2 path-specific launch failures: the daemon keeps retrying cpp, not giving up once.
            cpp_launch_failure = f"File does not exist or is not executable: {cpp_path}"
            failures_observed = wait_until(
                lambda: daemon_info["daemon"].get_logs().count(cpp_launch_failure) >= 2,
                4.0,
            )
            assert failures_observed, (
                "Expected repeated cpp launch failures while it was withheld; matching daemon logs:\n"
                + "\n".join(
                    line for line in daemon_info["daemon"].get_logs().splitlines() if cpp_launch_failure in line
                )
            )

            # Unblock cpp: it, then its dependent rust, must start.
            cpp_path.chmod(0o755)
            cpp_started = wait_until(lambda: is_running(cpp_path), timeout_s=8.0)
            assert cpp_started, "cpp_supervised_app did not start after becoming executable"
            rust_started = wait_until(lambda: is_running(rust_path), timeout_s=8.0)
            assert rust_started, (
                "rust_supervised_app did not start after its cpp_supervised_app dependency became available"
            )
        finally:
            stop_launch_manager_daemon(daemon_info)
