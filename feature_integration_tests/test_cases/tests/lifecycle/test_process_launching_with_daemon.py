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
"""

import json
import re
import subprocess
import time
import os
from pathlib import Path
from typing import Any

import pytest
from daemon_helpers import (
    first_pid,
    is_running,
    pgrep_cmdline_pattern,
    signal_process,
    start_launch_manager_daemon,
    stop_launch_manager_daemon,
    wait_until,
)
from test_properties import add_test_properties

pytestmark = [
    pytest.mark.parametrize("version", ["rust", "cpp"], scope="class"),
]


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
            # e.g. "pid 400132's current scheduling policy: SCHED_OTHER"
            if "scheduling policy" in lower:
                policy = line.split(":", 1)[1].strip()
            elif "scheduling priority" in lower:
                try:
                    priority = int(line.split(":", 1)[1].strip())
                except ValueError:
                    return None

        if policy is None or priority is None:
            return None
        return policy, priority

    # Dependency-gating coverage (rust-on-cpp startup order) lives in
    # test_conditional_launching.py; not duplicated here.

    @add_test_properties(
        partially_verifies=["feat_req__lifecycle__launch_support"],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
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
        daemon = daemon_info["daemon"]
        cpp_path = str(daemon_info["apps"]["cpp"])
        rust_path = str(daemon_info["apps"]["rust"])
        both_running = wait_until(
            lambda: is_running(cpp_path) and is_running(rust_path),
            timeout_s=8.0,
        )
        assert both_running, "Startup should launch all configured supervised processes"
        assert daemon.is_running(), "Launch Manager daemon stopped unexpectedly"

    @add_test_properties(
        partially_verifies=["feat_req__lifecycle__process_launch_args"],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
    )
    def test_launch_process_arguments_are_applied(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """Verify launched process cmdline includes every configured lifecycle argument.

        Expected args are read from the config itself, not hardcoded, so the test
        tracks config drift.
        """
        daemon_info = launch_manager_daemon
        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"
        app_path = str(daemon_info["apps"][version])

        config_path = Path(__file__).resolve().parents[3] / "configs" / "lifecycle_daemon_config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        configured_args = config["components"][app_name]["component_properties"]["process_arguments"]
        assert configured_args, f"{app_name} does not configure any process_arguments to verify against"

        started = wait_until(lambda: is_running(app_path), timeout_s=8.0)
        assert started, f"{app_name} was not launched before argument verification"

        pid = first_pid(app_path)
        assert pid is not None, f"Could not resolve PID for {app_name}"
        cmdline = self._proc_cmdline(pid)

        assert cmdline, f"Could not read command line arguments for {app_name} pid={pid}"
        for configured_arg in configured_args:
            assert configured_arg in cmdline, (
                f"Configured launch argument {configured_arg!r} missing in {app_name} cmdline: {cmdline}"
            )

    @add_test_properties(
        partially_verifies=["feat_req__lifecycle__process_launch_args"],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
    )
    def test_launch_process_environment_is_applied(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """Verify launched process environment matches every configured environment variable.

        Expected variables are read from the config itself, not hardcoded, so the
        test tracks config drift.
        """
        daemon_info = launch_manager_daemon
        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"
        app_path = str(daemon_info["apps"][version])

        config_path = Path(__file__).resolve().parents[3] / "configs" / "lifecycle_daemon_config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        configured_env = config["components"][app_name]["deployment_config"]["environmental_variables"]
        assert configured_env, f"{app_name} does not configure any environmental_variables to verify against"

        started = wait_until(lambda: is_running(app_path), timeout_s=8.0)
        assert started, f"{app_name} was not launched before environment verification"

        pid = first_pid(app_path)
        assert pid is not None, f"Could not resolve PID for {app_name}"
        proc_env = self._proc_environ(pid)

        for key, expected_value in configured_env.items():
            assert proc_env.get(key) == expected_value, (
                f"{key} mismatch for {app_name}: expected {expected_value!r}, got {proc_env.get(key)!r}"
            )

    def test_config_defines_uid_gid_scheduling_and_priority(self, version: str) -> None:
        """Sanity-check the lifecycle config's shape for launch user/group and scheduling defaults.

        No requirement tag here: this only confirms the config file is well-formed, not
        that launch_manager applies it - that's covered by
        test_launched_process_uid_gid_matches_config_when_applied and
        test_launched_process_scheduling_matches_config_when_applied below, which inspect
        the real launched process. `version` is unused but required by the class-scope
        parametrize on this class.
        """
        config_path = Path(__file__).resolve().parents[3] / "configs" / "lifecycle_daemon_config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))

        sandbox = config["defaults"]["deployment_config"]["sandbox"]
        assert isinstance(sandbox.get("uid"), int), "Expected integer uid in sandbox defaults"
        assert isinstance(sandbox.get("gid"), int), "Expected integer gid in sandbox defaults"
        assert isinstance(sandbox.get("scheduling_priority"), int), "Expected integer scheduling priority"
        assert isinstance(sandbox.get("scheduling_policy"), str), "Expected scheduling policy string"

    # Not decorated with @add_test_properties: this test is unconditionally skipped in CI/CD
    # (see below), so it never actually exercises feat_req__lifecycle__uid_gid_support and
    # shouldn't claim to verify it until it can run there.
    # Skipped in CI/CD (both rust/cpp): requires launch_manager to gain cap_setuid/cap_setgid via
    # setcap, which needs both FIT_ENABLE_SETCAP=1 (unset in the GitHub Actions workflow) and
    # unsandboxed execution (linux-sandbox's PR_SET_NO_NEW_PRIVS makes the grant inert at exec
    # time even if setcap itself succeeds). See feature_integration_tests/README.md for details.
    def test_launched_process_uid_gid_matches_config_when_applied(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """Verify launched process runs with configured effective uid/gid when runtime applies sandbox identity."""
        daemon_info = launch_manager_daemon
        if not daemon_info["sandbox_privileged"]:
            pytest.skip(
                "launch_manager was not granted cap_setuid/cap_setgid in this environment; "
                f"sandbox uid/gid cannot be applied. Reason: {daemon_info['sandbox_privileged_reason']}"
            )

        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"
        app_path = str(daemon_info["apps"][version])

        config_path = Path(__file__).resolve().parents[3] / "configs" / "lifecycle_daemon_config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        sandbox = config["defaults"]["deployment_config"]["sandbox"]
        expected_uid = int(sandbox["uid"])
        expected_gid = int(sandbox["gid"])

        started = wait_until(lambda: is_running(app_path), timeout_s=8.0)
        assert started, f"{app_name} was not launched before uid/gid verification"

        pid = first_pid(app_path)
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
        # Only meaningful when the configured sandbox uid actually differs from the runner's own
        # uid; some local/dev configs (e.g. lifecycle_daemon_config.json's uid 1001) coincide with
        # a common dev-user uid, in which case effective_uid == os.getuid() even when the sandbox
        # identity was genuinely applied, and this check can't tell the two cases apart.
        if expected_uid != os.getuid():
            assert effective_uid != os.getuid(), (
                f"{app_name} is running as the test runner's own uid ({effective_uid}); sandbox "
                "identity was not actually applied"
            )

    # Not decorated with @add_test_properties: this test is unconditionally skipped in CI/CD
    # (see below), so it never actually exercises feat_req__lifecycle__launch_priority_support /
    # feat_req__lifecycle__scheduling_policy and shouldn't claim to verify them until it can run there.
    # Skipped in CI/CD (both rust/cpp): requires launch_manager to gain cap_sys_nice via setcap,
    # which needs both FIT_ENABLE_SETCAP=1 (unset in the GitHub Actions workflow) and unsandboxed
    # execution (linux-sandbox's PR_SET_NO_NEW_PRIVS makes the grant inert at exec time even if
    # setcap itself succeeds). See feature_integration_tests/README.md for details.
    def test_launched_process_scheduling_matches_config_when_applied(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """Verify launched process uses configured scheduler policy and priority when applied."""
        daemon_info = launch_manager_daemon
        if not daemon_info["sandbox_privileged"]:
            pytest.skip(
                "launch_manager was not granted cap_sys_nice in this environment; "
                f"scheduling policy cannot be applied. Reason: {daemon_info['sandbox_privileged_reason']}"
            )

        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"
        app_path = str(daemon_info["apps"][version])

        config_path = Path(__file__).resolve().parents[3] / "configs" / "lifecycle_daemon_config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        component_sandbox = config["components"][app_name].get("deployment_config", {}).get("sandbox")
        sandbox = component_sandbox or config["defaults"]["deployment_config"]["sandbox"]
        configured_policy = sandbox["scheduling_policy"]
        configured_priority = int(sandbox["scheduling_priority"])

        started = wait_until(lambda: is_running(app_path), timeout_s=8.0)
        assert started, f"{app_name} was not launched before scheduling verification"

        # Pid can go stale between resolution and the chrt call if the app restarts;
        # retry against a fresh pid rather than failing on that race.
        sched = None
        pid = None
        for _ in range(20):
            pid = first_pid(app_path)
            if pid is None:
                time.sleep(0.1)
                continue
            sched = self._proc_sched_policy_and_priority(pid)
            if sched is not None:
                break
            time.sleep(0.1)
        assert pid is not None, f"Could not resolve PID for {app_name}"
        assert sched is not None, f"Could not read scheduling metadata via chrt for {app_name} pid={pid}"

        policy, rt_priority = sched
        expected_policy = configured_policy.upper()
        assert policy.upper() == expected_policy, (
            f"Scheduling policy mismatch for {app_name}: expected {expected_policy}, got {policy}"
        )
        assert rt_priority == configured_priority, (
            f"Scheduling priority mismatch for {app_name}: expected {configured_priority}, got {rt_priority}"
        )

    @add_test_properties(
        partially_verifies=["feat_req__lifecycle__scheduling_policy", "feat_req__lifecycle__launch_priority_support"],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
    )
    def test_scheduling_policy_is_non_default_and_applied(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """Verify the launched process's scheduling policy differs from launch_manager's own.

        Both apps carry a non-default sandbox policy (`rust_supervised_app`: `SCHED_RR`/`10`,
        `cpp_supervised_app`: `SCHED_FIFO`/`20`) vs. the OS default `SCHED_OTHER`/`0` that
        launch_manager itself runs under. Comparing the launched app against the daemon's own
        scheduling, rather than against a fixed constant, proves the policy was actually applied
        rather than coincidentally matching the process's inherited default.
        """
        daemon_info = launch_manager_daemon
        if not daemon_info["sandbox_privileged"]:
            pytest.skip(
                "launch_manager was not granted cap_sys_nice in this environment; "
                f"scheduling policy cannot be applied. Reason: {daemon_info['sandbox_privileged_reason']}"
            )

        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"
        app_path = str(daemon_info["apps"][version])

        started = wait_until(lambda: is_running(app_path), timeout_s=8.0)
        assert started, f"{app_name} was not launched before scheduling verification"

        daemon_sched = self._proc_sched_policy_and_priority(str(daemon_info["daemon"].pid()))
        assert daemon_sched is not None, "Could not read scheduling metadata via chrt for launch_manager"

        pid = None
        app_sched = None
        for _ in range(20):
            pid = first_pid(app_path)
            if pid is None:
                time.sleep(0.1)
                continue
            app_sched = self._proc_sched_policy_and_priority(pid)
            if app_sched is not None:
                break
            time.sleep(0.1)
        assert pid is not None, f"Could not resolve PID for {app_name}"
        assert app_sched is not None, f"Could not read scheduling metadata via chrt for {app_name} pid={pid}"

        assert app_sched != daemon_sched, (
            f"{app_name}'s scheduling {app_sched} matches launch_manager's own {daemon_sched}; "
            "sandbox scheduling policy was not actually applied"
        )

    @add_test_properties(
        partially_verifies=["feat_req__lifecycle__secpol_non_root"],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
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

        started = wait_until(lambda: is_running(app_path), timeout_s=8.0)
        assert started, f"{app_name} was not launched before non-root verification"

        pid = first_pid(app_path)
        assert pid is not None, f"Could not resolve PID for {app_name}"
        proc_ids = self._proc_status_ids(pid)
        assert proc_ids is not None, f"Could not read /proc status uid/gid for {app_name} pid={pid}"
        effective_uid, _ = proc_ids
        assert effective_uid != 0, f"{app_name} is unexpectedly running as root"


class TestSupervisedAppRecovery:
    """Kill-and-restart recovery against a dedicated launch_manager instance.

    Kept out of TestProcessLaunchingWithDaemon so its own daemon never overlaps that class's
    `launch_manager_daemon` fixture: concurrent daemons collide on launch_manager's fixed
    POSIX shm names (see daemon_helpers._live_daemons).
    """

    @add_test_properties(
        partially_verifies=[
            "feat_req__lifecycle__monitor_abnormal_term",
            "feat_req__lifecycle__recovery_action_support",
        ],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
    )
    def test_supervised_app_recovery(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        version: str,
    ) -> None:
        """Verify daemon restarts a killed supervised app in place per the retry policy.

        Also confirms the other supervised app is left untouched, proving recovery
        went through `ready_recovery_action.restart` rather than a run-target switch.

        Does not claim `feat_req__lifecycle__retries_configurable`: this only exercises a
        single restart within the configured attempt budget, it never varies or exhausts
        `number_of_attempts`, so the "configurable" half of that requirement is unverified.
        """
        daemon_info = start_launch_manager_daemon(tmp_path_factory)
        try:
            daemon = daemon_info["daemon"]
            app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"
            app_path = str(daemon_info["apps"][version])
            other_version = "cpp" if version == "rust" else "rust"
            other_app_path = str(daemon_info["apps"][other_version])

            started = wait_until(lambda: is_running(app_path), timeout_s=8.0)
            assert started, f"{app_name} was not running before recovery test"

            old_pid = first_pid(app_path)
            assert old_pid is not None, f"Could not resolve PID for {app_name}"
            other_old_pid = first_pid(other_app_path)
            assert other_old_pid is not None, "Could not resolve PID for the other supervised app"

            sent, reason = signal_process(old_pid, "-9", sandbox_privileged=daemon_info["sandbox_privileged"])
            assert sent, f"Could not signal {app_name} (pid={old_pid}): {reason}"

            restarted = wait_until(
                lambda: (new_pid := first_pid(app_path)) is not None and new_pid != old_pid,
                timeout_s=12.0,
            )
            assert restarted, f"{app_name} was not restarted after forced termination"

            assert daemon.is_running(), "Launch Manager daemon should still be running after recovery"

            other_new_pid = first_pid(other_app_path)
            assert other_new_pid == other_old_pid, (
                "The other supervised app was relaunched too, indicating recovery switched the "
                "whole run target instead of retrying only the failed app per the configured "
                "restart policy"
            )
        finally:
            stop_launch_manager_daemon(daemon_info)


class TestParallelLaunch:
    """Verify genuinely parallel launch of independent components.

    Runs its own launch_manager instance (rather than the shared class-scoped
    `launch_manager_daemon` fixture used by TestProcessLaunchingWithDaemon), for two reasons:

    1. It renders the config with `independent_apps=True` (no depends_on between the
       two apps), unlike the shared fixture's config - that's the whole point.
    2. It is a separate class, so the shared fixture is torn down before this daemon starts;
       overlapping daemons collide on launch_manager's fixed POSIX shm names.

    Parametrized on `version` only because the module-level `pytestmark` applies it
    to every class in this file; parallel launch itself is independent of which
    scenario variant is under test elsewhere, so `version` is unused here.
    """

    @add_test_properties(
        partially_verifies=["feat_req__lifecycle__parallel_launch_support"],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
    )
    def test_independent_processes_launch_without_waiting_on_each_other(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        version: str,
    ) -> None:
        """Verify two independent components launch in parallel, not one-after-the-other.

        `lifecycle_daemon_config.json` has rust_supervised_app depend on
        cpp_supervised_app, so it cannot demonstrate parallel launch - both apps
        eventually running there is equally consistent with strict serialization.

        Renders that config with `independent_apps=True`, so neither app depends on
        the other, and stalls one app at a time: it is replaced by a
        stub that runs but never reports Running, so a serialized launcher would sit
        on it for the full `ready_timeout` (10 s, plus retries) before starting the
        next. The other app must be up within 4 s of daemon startup -
        well under one `ready_timeout` - regardless of which one is stalled, so the
        pass window cannot be met by strictly sequential launch in either order.

        `version` is unused but required by the module-scope parametrize.
        """
        ready_timeout_s = 10.0  # rendered over the base config's 2.0 s
        parallel_window_s = 4.0  # + ~1 s daemon startup grace, still well under ready_timeout
        assert parallel_window_s < ready_timeout_s / 2
        for stalled, other in (("cpp", "rust"), ("rust", "cpp")):
            daemon_info = start_launch_manager_daemon(
                tmp_path_factory,
                stalled_apps=frozenset({stalled}),
                wait_for_apps=False,
                independent_apps=True,
                ready_timeout_s=ready_timeout_s,
            )
            try:
                stalled_path = str(daemon_info["apps"][stalled])
                other_path = str(daemon_info["apps"][other])
                other_started = wait_until(lambda: is_running(other_path), timeout_s=parallel_window_s)
                assert other_started, (
                    f"{other}_supervised_app did not start within {parallel_window_s}s while "
                    f"{stalled}_supervised_app was stalled (ready_timeout={ready_timeout_s}s), even "
                    "though neither depends on the other - launch is serialized, not parallel"
                )
                # Rules out a vacuous pass: the stalled stub must be up too, i.e. both were
                # in flight concurrently rather than the stub simply never being launched.
                assert is_running(stalled_path), f"stalled {stalled}_supervised_app stub was never launched"
            finally:
                stop_launch_manager_daemon(daemon_info)


class TestHealthMonitoringWithDaemon:
    """Health monitoring / watchdog tests with daemon."""

    @add_test_properties(
        partially_verifies=[
            "feat_req__lifecycle__liveliness_detection",
            "feat_req__lifecycle__smart_watchdog_config",
        ],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
    )
    def test_watchdog_detection(self, launch_manager_daemon: dict[str, Any], version: str) -> None:
        """Verify watchdog detects an unresponsive app (stopped, not reporting health) and reacts."""
        daemon = launch_manager_daemon["daemon"]
        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"

        # Stop the supervised process to emulate a non-reporting workload.
        app_path = str(launch_manager_daemon["apps"][version])
        result = subprocess.run(
            ["pgrep", "-f", pgrep_cmdline_pattern(app_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        # The fixture already waited for the app to reach Running, so a missing process here
        # means it died under supervision - a genuine failure, not a skip.
        assert result.returncode == 0, f"{app_name} died before the watchdog check"

        pid = result.stdout.strip().split("\n")[0]
        sandbox_privileged = launch_manager_daemon["sandbox_privileged"]
        sent, reason = signal_process(pid, "-STOP", sandbox_privileged=sandbox_privileged)
        assert sent, f"Could not signal {app_name} (pid={pid}): {reason}"
        try:
            watchdog_patterns = [
                rf"Got kRunning timeout for process.*\(\s*{re.escape(app_name)}\s*\)",
                rf"unexpected termination of process.*\(\s*{re.escape(app_name)}\s*\)",
                rf"Alive Supervision \(\s*{re.escape(app_name)}\s*\) switched to FAILED",
                rf"Alive Supervision \(\s*{re.escape(app_name)}\s*\) switched to EXPIRED",
            ]
            # Poll rather than sleep: detection latency varies under CI load.
            detected = wait_until(
                lambda: any(re.search(pattern, daemon.get_logs()) for pattern in watchdog_patterns),
                timeout_s=8.0,
            )
            assert detected, (
                f"No target-specific watchdog diagnostics found for {app_name}.\nDaemon logs:\n{daemon.get_logs()}"
            )
        finally:
            signal_process(pid, "-CONT", sandbox_privileged=sandbox_privileged)
