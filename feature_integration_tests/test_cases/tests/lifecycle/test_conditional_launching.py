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
from pathlib import Path
from typing import Any

import pytest
from daemon_helpers import (
    first_pid,
    is_running,
    launch_manager_daemon,
    start_launch_manager_daemon,
    stop_launch_manager_daemon,
    wait_until,
)
from test_properties import add_test_properties

pytestmark = [pytest.mark.daemon]


@pytest.mark.parametrize("version", ["rust", "cpp"], scope="class")
class TestConditionalLaunchingWithDaemon:
    """Verify dependency-based conditional launching with real daemon behavior."""

    @add_test_properties(
        partially_verifies=["feat_req__lifecycle__launch_support"],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
    )
    def test_startup_launches_conditioned_processes(self, launch_manager_daemon: dict[str, Any], version: str) -> None:
        """Verify supervised processes are launched as part of conditional startup."""
        daemon_info = launch_manager_daemon
        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"
        app_path = str(daemon_info["apps"][version])

        started = wait_until(lambda: is_running(app_path), timeout_s=8.0)
        assert started, f"{app_name} was not launched in conditional startup"


class TestConditionalLaunchingDependencyOrdering:
    """Verify cpp-before-rust ordering and its declaration in config.

    Not parametrized on `version`: both tests inspect the fixed cpp/rust pair
    (or the static config) regardless of which scenario variant is under test
    elsewhere, so parametrizing here would only re-run identical assertions.
    """

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

    @add_test_properties(
        partially_verifies=[
            "feat_req__lifecycle__process_ordering",
            "feat_req__lifecycle__cond_process_start",
        ],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
    )
    def test_rust_launch_is_conditioned_on_cpp_dependency(
        self,
        launch_manager_daemon: dict[str, Any],
    ) -> None:
        """Verify rust app starts no earlier than its configured C++ dependency."""
        daemon_info = launch_manager_daemon
        cpp_path = str(daemon_info["apps"]["cpp"])
        rust_path = str(daemon_info["apps"]["rust"])

        started = wait_until(
            lambda: is_running(cpp_path) and is_running(rust_path),
            timeout_s=8.0,
        )
        assert started, "cpp_supervised_app and rust_supervised_app should both be running"

        cpp_pid = first_pid(cpp_path)
        rust_pid = first_pid(rust_path)
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

    @add_test_properties(
        partially_verifies=["feat_req__lifecycle__define_swc_dependencies"],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
    )
    def test_dependency_is_declared_in_lifecycle_config(self, launch_manager_daemon: dict[str, Any]) -> None:
        """Verify runtime configuration defines rust conditional dependency on cpp."""
        config_path = Path(__file__).resolve().parents[3] / "configs" / "lifecycle_daemon_config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))

        rust_component = config["components"]["rust_supervised_app"]["component_properties"]
        depends_on = rust_component.get("depends_on", [])
        assert "cpp_supervised_app" in depends_on, (
            "Expected rust_supervised_app to depend on cpp_supervised_app in lifecycle daemon config"
        )


class TestConditionalLaunchingBlocksOnMissingDependency:
    """Verify rust startup is actually gated on cpp, not merely correlated with it.

    Runs its own launch_manager instance (rather than the shared class-scoped
    `launch_manager_daemon` fixture) with cpp_supervised_app withheld, so it can
    observe the negative case: rust must not start while its dependency cannot.
    Safe to run its own daemon here because the bazel targets for these tests
    are tagged tags = ["exclusive"], guaranteeing no other lifecycle daemon is
    using the shared runtime_root/lock at the same time.

    Not parametrized on `version`: dependency gating is independent of which
    scenario variant is under test elsewhere, so this runs exactly once.
    """

    @add_test_properties(
        partially_verifies=[
            "feat_req__lifecycle__waitfor_support",
            "feat_req__lifecycle__dependency_check",
            "feat_req__lifecycle__cond_process_start",
        ],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
    )
    def test_rust_stays_down_until_cpp_dependency_becomes_available(
        self, tmp_path_factory: pytest.TempPathFactory
    ) -> None:
        """Verify rust does not start while cpp is withheld, and does once cpp is unblocked."""
        daemon_info = start_launch_manager_daemon(
            tmp_path_factory,
            blocked_apps=frozenset({"cpp"}),
            wait_for_apps=False,
        )
        try:
            cpp_path = daemon_info["apps"]["cpp"]
            rust_path = str(daemon_info["apps"]["rust"])

            # cpp cannot execute (mode 0o000): rust must not appear while it's withheld.
            rust_started_early = wait_until(lambda: is_running(rust_path), timeout_s=4.0)
            assert not rust_started_early, (
                "rust_supervised_app started even though its cpp_supervised_app dependency "
                "was withheld (non-executable); dependency gating was not enforced"
            )

            # Unblock cpp: rust should now be allowed to start.
            cpp_path.chmod(0o755)
            rust_started = wait_until(lambda: is_running(rust_path), timeout_s=8.0)
            assert rust_started, (
                "rust_supervised_app did not start after its cpp_supervised_app dependency became available"
            )
        finally:
            stop_launch_manager_daemon(daemon_info)
