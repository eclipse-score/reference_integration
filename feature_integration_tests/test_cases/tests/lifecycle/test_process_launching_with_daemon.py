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
Lifecycle FITs against a real launch_manager supervising rust_supervised_app and cpp_supervised_app.

`version` selects which of the two supervised apps a test inspects; both always run under the
same daemon. Run via Bazel (the helpers resolve binaries from the target's FIT_*_PATH env vars):

    bazel test //feature_integration_tests/test_cases:fit_lifecycle_daemon
    bazel test //feature_integration_tests/test_cases:fit_lifecycle_daemon --test_arg=-k --test_arg=rust
"""

import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any

import pytest
from daemon_helpers import (
    first_pid,
    is_running,
    read_proc_file,
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
    """Launch-parameter checks (args, env, uid/gid, scheduling, non-root) against one daemon per
    `version`, provided by the class-scoped `launch_manager_daemon` fixture. Tests here must not
    start their own daemon (fixed shm names; see daemon_helpers._live_daemons)."""

    @staticmethod
    def _proc_cmdline(pid: str) -> list[str]:
        """Return `/proc/<pid>/cmdline` as a list of arguments."""
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
        return [arg.decode("utf-8") for arg in raw.split(b"\0") if arg]

    @staticmethod
    def _proc_environ(pid: str) -> dict[str, str]:
        """Return `/proc/<pid>/environ` as a dict (via the privileged `cat` when staged)."""
        raw = read_proc_file(pid, "environ")
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
        """Return the effective `(uid, gid)` from `/proc/<pid>/status`, or None if unreadable."""
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
        """Return `(policy, priority)` parsed from `chrt -p <pid>`, or None on failure."""
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

    # Dependency gating (rust waits for cpp) is covered in test_conditional_launching.py.

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
        """Both processes in the Startup run target's `depends_on` are running (pgrep) and the
        daemon is still up. `version` is unused: the check covers both apps."""
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
        partially_verifies=["feat_req__lifecycle__launch_support"],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
    )
    def test_launch_process_arguments_are_applied(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """Every configured `process_arguments` entry is present in the live app's cmdline.
        Expected values come from the config, so the test tracks config changes."""
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
        partially_verifies=["feat_req__lifecycle__launch_support"],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
    )
    def test_launch_process_environment_is_applied(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """Every configured `environmental_variables` entry has the configured value in the live
        app's /proc environ. Expected values come from the config."""
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

    # No requirement claim: skips in CI, which neither sets
    # FIT_ENABLE_SETCAP=1 nor runs unsandboxed, both needed for the setcap grant. See README.md.
    def test_launched_process_uid_gid_matches_config_when_applied(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """With capabilities granted, the live app's effective uid equals the rendered sandbox uid
        and differs from the runner's. Skips without the grant, or if the uid was not remapped.

        Limitation: the rendered gid is the runner's own (see `_generate_runtime_config`), so the
        gid assertion cannot prove setgid() was applied.
        """
        daemon_info = launch_manager_daemon
        if not daemon_info["sandbox_privileged"]:
            pytest.skip(
                "launch_manager was not granted cap_setuid/cap_setgid in this environment; "
                f"sandbox uid/gid cannot be applied. Reason: {daemon_info['sandbox_privileged_reason']}"
            )

        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"
        app_path = str(daemon_info["apps"][version])

        # The rendered config, not the source JSON: under capabilities the helper remaps the
        # sandbox uid away from the runner's own (daemon_helpers._SANDBOX_UID).
        config = json.loads(daemon_info["runtime_config"].read_text(encoding="utf-8"))
        component_sandbox = config["components"][app_name].get("deployment_config", {}).get("sandbox")
        sandbox = component_sandbox or config["defaults"]["deployment_config"]["sandbox"]
        expected_uid = int(sandbox["uid"])
        expected_gid = int(sandbox["gid"])
        if expected_uid == os.getuid():
            # Happens when the kill/cat copies could not be staged (uid not remapped); matching uids pass
            # whether or not launch_manager applied the sandbox identity.
            pytest.skip(
                f"Sandbox uid {expected_uid} equals the test runner's own uid; cannot distinguish an "
                f"applied sandbox identity from an inherited one. Reason: {daemon_info['sandbox_privileged_reason']}"
            )

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
        # Consistency check only: passes whether or not setgid() was applied (gid == runner's).
        assert effective_gid == expected_gid, (
            f"Effective gid mismatch for {app_name}: expected {expected_gid}, got {effective_gid}"
        )
        assert effective_uid != os.getuid(), (
            f"{app_name} is running as the test runner's own uid ({effective_uid}); sandbox "
            "identity was not actually applied"
        )

    # No requirement claim (launch_priority_support / scheduling_policy): skips in CI, see above.
    def test_launched_process_scheduling_matches_config_when_applied(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """With capabilities granted, the live app's `chrt` policy and priority equal the rendered
        sandbox values. Skips without the grant (the config is then downgraded to SCHED_OTHER)."""
        daemon_info = launch_manager_daemon
        if not daemon_info["sandbox_privileged"]:
            pytest.skip(
                "launch_manager was not granted cap_sys_nice in this environment; "
                f"scheduling policy cannot be applied. Reason: {daemon_info['sandbox_privileged_reason']}"
            )

        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"
        app_path = str(daemon_info["apps"][version])

        # The rendered config, not the source JSON, like the uid/gid test above.
        config = json.loads(daemon_info["runtime_config"].read_text(encoding="utf-8"))
        component_sandbox = config["components"][app_name].get("deployment_config", {}).get("sandbox")
        sandbox = component_sandbox or config["defaults"]["deployment_config"]["sandbox"]
        configured_policy = sandbox["scheduling_policy"]
        configured_priority = int(sandbox["scheduling_priority"])

        started = wait_until(lambda: is_running(app_path), timeout_s=8.0)
        assert started, f"{app_name} was not launched before scheduling verification"

        # Retry with a fresh pid in case the app restarted between pgrep and chrt.
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

    # No requirement claim: skips in CI, see above.
    def test_scheduling_policy_is_non_default_and_applied(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """With capabilities granted, the live app's `(policy, priority)` differs from
        launch_manager's own, so it was set by launch_manager rather than inherited. The config
        gives rust SCHED_RR/10 and cpp SCHED_FIFO/20; the daemon runs SCHED_OTHER/0. Skips
        without the grant."""
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
        partially_verifies=["feat_req__lifecycle__launch_support"],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
    )
    def test_launch_manager_and_apps_are_not_running_as_root(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """launch_manager itself runs with a non-root effective uid and still launches the app
        (the requirement: LM can be started as non-root). Also checks the app is non-root.

        Limitation: covers only a plain non-root start (optionally with file capabilities), not
        any other "security policy" mechanism.
        """
        daemon_info = launch_manager_daemon
        daemon = daemon_info["daemon"]
        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"
        app_path = str(daemon_info["apps"][version])

        assert daemon.is_running(), "Launch Manager daemon is not running"
        daemon_ids = self._proc_status_ids(str(daemon.pid()))
        assert daemon_ids is not None, f"Could not read /proc status for launch_manager pid={daemon.pid()}"
        assert daemon_ids[0] != 0, "launch_manager is running as root"

        started = wait_until(lambda: is_running(app_path), timeout_s=8.0)
        assert started, f"{app_name} was not launched before non-root verification"

        pid = first_pid(app_path)
        assert pid is not None, f"Could not resolve PID for {app_name}"
        proc_ids = self._proc_status_ids(pid)
        assert proc_ids is not None, f"Could not read /proc status uid/gid for {app_name} pid={pid}"
        effective_uid, _ = proc_ids
        assert effective_uid != 0, f"{app_name} is unexpectedly running as root"


class TestSupervisedAppRecovery:
    """Kill-and-recover against a dedicated daemon per `version`.

    Separate class so its daemon never overlaps the `launch_manager_daemon` fixture (fixed shm
    names; see daemon_helpers._live_daemons).
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
        """SIGKILL the running app; launch_manager must log its unexpected termination and bring
        it back (new pid) without restarting the other, healthy app or dying itself.

        The recovery that runs is the run target's `recovery_action` (switch to
        `fallback_run_target`, which contains both apps), not `ready_recovery_action.restart`,
        which only covers startup failures. Limitation: the test does not assert which recovery
        action ran, only that the app recovered. Does not claim `retries_configurable`
        (see test_retry_exhaustion.py).
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
            termination_logged = re.search(
                rf"unexpected termination of process\s+{re.escape(app_name)}\b", daemon.get_logs()
            )
            assert termination_logged, (
                f"launch_manager did not log the abnormal termination of {app_name}.\nDaemon logs:\n{daemon.get_logs()}"
            )

            assert daemon.is_running(), "Launch Manager daemon should still be running after recovery"

            other_new_pid = first_pid(other_app_path)
            assert other_new_pid == other_old_pid, (
                "The other, healthy supervised app was relaunched too; recovery should only relaunch the failed app"
            )
        finally:
            stop_launch_manager_daemon(daemon_info)


class TestParallelLaunch:
    """Parallel launch of independent components, with its own daemons rendered with
    `independent_apps=True`. `version` is unused (module-level parametrize), so the test runs
    twice with identical behaviour."""

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
        """With no `depends_on` between the apps and one of them stalled (runs, never reports
        Running), the other must be running within 4 s of the 1 s startup window. A serialized
        launcher would wait out `ready_timeout` (10 s) on the stalled app first. Both stall
        orders are tried, and the stalled stub must also be running (it was launched, not skipped).
        """
        ready_timeout_s = 10.0  # rendered over the base config's 2.0 s
        parallel_window_s = 4.0  # plus the 1 s startup window, still well under ready_timeout
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
                other_started = wait_until(lambda p=other_path: is_running(p), timeout_s=parallel_window_s)
                assert other_started, (
                    f"{other}_supervised_app did not start within {parallel_window_s}s while "
                    f"{stalled}_supervised_app was stalled (ready_timeout={ready_timeout_s}s), even "
                    "though neither depends on the other - launch is serialized, not parallel"
                )
                # Both in flight at once: rules out the stalled stub never being launched.
                assert is_running(stalled_path), f"stalled {stalled}_supervised_app stub was never launched"
            finally:
                stop_launch_manager_daemon(daemon_info)


class TestHealthMonitoringWithDaemon:
    """Alive-supervision (watchdog) detection, with its own daemon per `version`."""

    # No `smart_watchdog_config` claim: alive supervision is configured only in `defaults`, and
    # the test neither configures it per process nor varies it.
    @add_test_properties(
        partially_verifies=["feat_req__lifecycle__liveliness_detection"],
        test_type="requirements-based",
        derivation_technique="requirements-analysis",
    )
    def test_watchdog_detection(self, tmp_path_factory: pytest.TempPathFactory, version: str) -> None:
        """SIGSTOP the app so it stops reporting alive indications; launch_manager must log its
        Alive Supervision switching to FAILED or EXPIRED within 8 s.

        Limitation: checks detection only, not the reaction that follows. Uses its own daemon
        so the recovery triggered by one version's failure cannot affect the other's run.
        """
        daemon_info = start_launch_manager_daemon(tmp_path_factory)
        try:
            self._check_watchdog_detection(daemon_info, version)
        finally:
            stop_launch_manager_daemon(daemon_info)

    @staticmethod
    def _check_watchdog_detection(daemon_info: dict[str, Any], version: str) -> None:
        daemon = daemon_info["daemon"]
        app_name = "rust_supervised_app" if version == "rust" else "cpp_supervised_app"

        app_path = str(daemon_info["apps"][version])
        # start_launch_manager_daemon already waited for the app, so a missing process is a failure.
        pid = first_pid(app_path)
        assert pid is not None, f"{app_name} died before the watchdog check"

        sandbox_privileged = daemon_info["sandbox_privileged"]
        sent, reason = signal_process(pid, "-STOP", sandbox_privileged=sandbox_privileged)
        assert sent, f"Could not signal {app_name} (pid={pid}): {reason}"
        try:
            # Only alive-supervision verdicts count; a startup timeout or crash is not liveliness detection.
            liveliness_lost = rf"Alive Supervision \(\s*{re.escape(app_name)}\s*\) switched to (FAILED|EXPIRED)"
            # Poll rather than sleep: detection latency varies under CI load.
            detected = wait_until(lambda: re.search(liveliness_lost, daemon.get_logs()), timeout_s=8.0)
            assert detected, f"No Alive Supervision failure logged for {app_name}.\nDaemon logs:\n{daemon.get_logs()}"
        finally:
            signal_process(pid, "-CONT", sandbox_privileged=sandbox_privileged)
