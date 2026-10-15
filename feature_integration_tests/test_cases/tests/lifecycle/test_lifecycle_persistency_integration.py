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
Cross-module FIT: Launch Manager run targets, recovery, control interface and
logging acting on KVS-owning processes.

Topology (`lifecycle_persistency_config.json`)
----------------------------------------------
- `control_daemon` (State_Manager) forwards `lmcontrol <run target>` requests
  to Launch Manager's control interface and prints the result.
- `kvs_primary`, `kvs_recovery_reset` and `kvs_secondary` are the FIT scenario
  binary (`persistency.restart_counter`) launched by Launch Manager as Native,
  self-terminating components. Each launch opens its KVS instance, increments
  a counter key, applies its configured writes/`reset_key` calls and flushes,
  so a counter equal to the launch count proves every relaunch reloaded the
  state its predecessor stored.
- `<version>_supervised_app` (`__FIT_SUPERVISED_APP__` in the template) is
  the crash target, so the rust and cpp parameters each crash their own
  language's supervised app; its unexpected termination switches to
  `fallback_run_target`, whose only KVS component is `kvs_recovery_reset`.
  That component resets key2 and reads every key back, so it shows what a
  recovery-launched process reloads.

Run targets: `Startup` (control_daemon), `Running` (+ supervised app,
kvs_primary), `Secondary` (+ kvs_secondary), `BothInstances` (+ kvs_primary,
kvs_secondary), `fallback_run_target` (+ kvs_recovery_reset).

Sandbox: control_daemon runs as the runner (lmcontrol must open its socket);
every other component runs as `__FIT_SANDBOX_UID__`, which is a distinct uid
only when launch_manager was granted `cap_setuid` (`FIT_ENABLE_SETCAP=1`).

Known limits
------------
- The upstream control client only offers `ActivateRunTarget`; no query
  command exists, so `feat_req__lifecycle__query_commands` stays uncovered.
- Logging is asserted on Launch Manager's mw::log console backend; DLT/remote
  routing is not exercised here.
"""

import functools
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

import pytest
from daemon_helpers import (
    CONTROL_DAEMON,
    LIFECYCLE_PERSISTENCY_CONFIG,
    find_descendant_pid,
    resolve_target_path,
    signal_process,
    start_launch_manager_daemon,
    stop_launch_manager_daemon,
    wait_until,
)
from persistency_scenario import (
    create_kvs_defaults_file,
    read_verified_kvs_values,
    restart_counter_logged_values,
)
from test_properties import add_test_properties
from testing_utils import BazelTools

pytestmark = [
    pytest.mark.parametrize("version", ["rust", "cpp"], scope="class"),
]

# control_daemon's control socket (see control.hpp in score_lifecycle).
_CONTROL_SOCKET = Path("/dev/shm/sm_control")
_KVS_DEFAULTS = {
    1: {"key1": 100.0, "key2": 200.0, "key3": 300.0},
    2: {"key1": 400.0, "key2": 500.0, "key3": 600.0},
}
_TIMEOUT_S = 10.0


def _remove_own_control_socket() -> None:
    """Remove a control socket left by an earlier daemon of this runner.

    The socket name is host-wide, which is one reason the lifecycle targets
    are `exclusive`. One owned by another user is not ours to delete.
    """
    if not _CONTROL_SOCKET.exists():
        return
    if _CONTROL_SOCKET.stat().st_uid != os.getuid():
        pytest.fail(f"{_CONTROL_SOCKET} belongs to another user; another launch_manager may be running.")
    _CONTROL_SOCKET.unlink()


def _supervised_app(version: str) -> str:
    return f"{version}_supervised_app"


def _render(config: dict[str, Any], runtime_root: Path, *, version: str) -> None:
    """Name the crash target after `version` and point the KVS components at a fresh directory.

    The KVS directory is group-writable: with sandbox capabilities the KVS
    components run as `SANDBOX_UID` with the runner's gid.
    """
    kvs_dir = runtime_root / "kvs"
    kvs_dir.mkdir()
    kvs_dir.chmod(0o770)
    for instance_id, defaults in _KVS_DEFAULTS.items():
        create_kvs_defaults_file(kvs_dir, instance_id, {key: ("f64", value) for key, value in defaults.items()})

    # The placeholder is a component name, binary name, env value and run-target dependency.
    rendered = json.loads(json.dumps(config).replace("__FIT_SUPERVISED_APP__", _supervised_app(version)))
    config.clear()
    config.update(rendered)

    for component in config["components"].values():
        args = component["component_properties"].get("process_arguments", [])
        component["component_properties"]["process_arguments"] = [
            arg.replace("__FIT_KVS_DIR__", str(kvs_dir)) for arg in args
        ]


def _rendered_config(daemon_info: dict[str, Any]) -> dict[str, Any]:
    """Return the config Launch Manager was started with (placeholders resolved)."""
    return json.loads((daemon_info["work_dir"] / "etc" / "lifecycle_config.json").read_text(encoding="utf-8"))


def _kvs_input(daemon_info: dict[str, Any], component: str) -> dict[str, Any]:
    """Return the scenario input Launch Manager passes to `component` (from the rendered config)."""
    args = _rendered_config(daemon_info)["components"][component]["component_properties"]["process_arguments"]
    return json.loads(args[args.index("--input") + 1])


def _instance_id(kvs_input: dict[str, Any]) -> int:
    return kvs_input["kvs_parameters_1"]["kvs_parameters"]["instance_id"]


def _process_ids(pid: int) -> tuple[int, int]:
    """Return the effective (uid, gid) of a live process from /proc/<pid>/status."""
    ids = {}
    for line in Path(f"/proc/{pid}/status").read_text().splitlines():
        name, _, values = line.partition(":")
        if name in ("Uid", "Gid"):
            ids[name] = int(values.split()[1])  # Fields: real, effective, saved, filesystem.
    return ids["Uid"], ids["Gid"]


def _written_values(kvs_input: dict[str, Any]) -> dict[str, float]:
    test = kvs_input["test"]
    return dict(zip(test.get("set_keys", []), test.get("set_values", []), strict=True))


def _activate(daemon_info: dict[str, Any], run_target: str) -> tuple[bool, str]:
    """Request `run_target` through lmcontrol -> control_daemon and wait for its reported result.

    Returns (succeeded, daemon log since the request). control_daemon reports
    only after Launch Manager completes or rejects the transition, so the
    self-terminating KVS components of the target have flushed by then.
    """
    daemon = daemon_info["daemon"]
    offset = daemon.get_log_offset()
    result = subprocess.run(
        [str(daemon_info["lm_ctl_binary"]), run_target], capture_output=True, text=True, timeout=5, check=False
    )
    assert result.returncode == 0, (
        f"lmcontrol {run_target} failed (rc={result.returncode}): {result.stdout}{result.stderr}"
    )
    outcome = re.compile(rf"Activating Run Target {re.escape(run_target)} (succeeded|failed)")
    reported = wait_until(lambda: outcome.search(daemon.get_logs_since(offset)) is not None, _TIMEOUT_S)
    logs = daemon.get_logs_since(offset)
    assert reported, f"control_daemon reported no result for {run_target} within {_TIMEOUT_S} s:\n{logs[-3000:]}"
    return outcome.search(logs).group(1) == "succeeded", logs


def _kill_supervised_app(daemon_info: dict[str, Any], app: str) -> int:
    daemon = daemon_info["daemon"]
    pid = find_descendant_pid(daemon.pid(), app)
    assert pid is not None, f"{app} is not running under the daemon:\n{daemon.get_logs()[-3000:]}"
    killed, reason = signal_process(str(pid), "-9", kill_binary=daemon_info["kill_binary"])
    assert killed, f"Failed to kill {app} {pid}: {reason}"
    return pid


def _wait_for_state(daemon: Any, offset: int, state: str) -> str:
    completed = re.compile(rf"Completed the request for PG\s+to State {re.escape(state)}\b")
    reached = wait_until(lambda: completed.search(daemon.get_logs_since(offset)) is not None, _TIMEOUT_S)
    logs = daemon.get_logs_since(offset)
    assert reached, f"Launch Manager did not complete the transition to {state}:\n{logs[-3000:]}"
    return logs


class TestLifecyclePersistencyIntegration:
    """Launch Manager drives KVS-owning components through run targets, recovery, control and shutdown."""

    @pytest.fixture
    def lp_daemon(
        self, tmp_path_factory: pytest.TempPathFactory, request: pytest.FixtureRequest, version: str
    ) -> dict[str, Any]:
        """One daemon per test: each test moves it through run targets and KVS state."""
        scenario_binary = BazelTools(option_prefix=version).select_target_path(request.config, expect_exists=True)
        _remove_own_control_socket()
        daemon_info = start_launch_manager_daemon(
            tmp_path_factory,
            config_target=LIFECYCLE_PERSISTENCY_CONFIG,
            binaries={
                "control_daemon": resolve_target_path(CONTROL_DAEMON),
                _supervised_app(version): resolve_target_path(f"@score_lifecycle//examples/{_supervised_app(version)}"),
                "kvs_scenario": scenario_binary,
            },
            ready_apps=("control_daemon",),
            render=functools.partial(_render, version=version),
            log_level="kDebug",
            control_client=True,
        )
        try:
            if not wait_until(_CONTROL_SOCKET.exists, _TIMEOUT_S):
                pytest.fail(f"control_daemon did not create {_CONTROL_SOCKET}:\n{daemon_info['daemon'].get_logs()}")
            # Upstream bug in score_lifecycle examples/control_application/control_daemon.cpp:38:
            # `sm_control_socket.create(control_socket_path, 600)` passes decimal 600
            # (= 0o1130, owner execute-only) as the shm_open() mode instead of 0600, so
            # lmcontrol's O_RDWR shm_open() fails with EACCES for anyone but root.
            # Restore the owner read/write it intends; drop this once fixed upstream.
            _CONTROL_SOCKET.chmod(0o600)
            daemon_info["kvs_dir"] = daemon_info["runtime_root"] / "kvs"
            daemon_info["supervised_app"] = _supervised_app(version)
            yield daemon_info
        finally:
            stop_launch_manager_daemon(daemon_info)
            _remove_own_control_socket()

    @add_test_properties(
        partially_verifies=[
            "feat_req__lifecycle__process_failure_react",
            "feat_req__lifecycle__monitor_abnormal_term",
            "feat_req__lifecycle__recovery_action_support",
            "feat_req__lifecycle__recov_run_target_switch",
            "feat_req__persistency__reset_to_default",
            "feat_req__persistency__store_data",
        ],
        test_type="integration",
        derivation_technique="architecture-based-testing",
    )
    def test_recovery_resets_kvs_key_and_relaunch_reloads_state(self, lp_daemon: dict[str, Any], version: str) -> None:
        """
        A crash runs the fallback target's reset component; relaunched writers reload the stored KVS state.

        1. `Running` launches kvs_primary (launch_count=1, key1..3 overridden).
        2. SIGKILL of `<version>_supervised_app`: Launch Manager logs the
           termination, stays alive and activates `fallback_run_target`, which
           launches kvs_recovery_reset — a component that exists only in the
           fallback target.
        3. kvs_recovery_reset opens the KVS fresh: it loads recovery_count=0,
           reads launch_count and key1/key3 back as kvs_primary stored them,
           and after its reset_key reads key2 back as its default with no
           stored value. The snapshot then lacks key2, keeps the other values,
           holds recovery_count=1, and the defaults file is unchanged.
        4. `Running` again relaunches the supervised app (new PID) and
           kvs_primary, which reads launch_count=1 back and stores 2 while
           recovery_count stays 1.

        Pass/fail
        ---------
        PASS  All KVS values and counters match after recovery and relaunch.
        FAIL  Recovery does not run the fallback component, the recovery
              component reloads wrong values, the reset touches other keys, or
              a relaunch starts from empty/reset storage.
        """
        daemon = lp_daemon["daemon"]
        kvs_dir = lp_daemon["kvs_dir"]
        app = lp_daemon["supervised_app"]
        primary = _kvs_input(lp_daemon, "kvs_primary")
        reset = _kvs_input(lp_daemon, "kvs_recovery_reset")
        instance_id = _instance_id(primary)
        assert _instance_id(reset) == instance_id, "Recovery reset must act on the primary KVS instance."
        launch_key = primary["test"]["counter_key"]
        recovery_key = reset["test"]["counter_key"]
        written = _written_values(primary)
        reset_keys = reset["test"]["reset_keys"]
        stored_before_crash = {launch_key: 1.0, **written}
        assert set(reset["test"]["read_keys"]) == set(stored_before_crash), (
            "kvs_recovery_reset must read back every key kvs_primary stores"
        )
        defaults_file = kvs_dir / f"kvs_{instance_id}_default.json"
        defaults_before = defaults_file.read_bytes()

        succeeded, logs = _activate(lp_daemon, "Running")
        assert succeeded, f"Activating Running failed:\n{logs[-3000:]}"
        assert read_verified_kvs_values(kvs_dir, instance_id) == stored_before_crash

        offset = daemon.get_log_offset()
        crashed_pid = _kill_supervised_app(lp_daemon, app)
        recovery_logs = _wait_for_state(daemon, offset, "fallback")
        assert f"unexpected termination of process {app}" in recovery_logs
        assert daemon.is_running(), "Launch Manager exited after the supervised app crashed"
        assert restart_counter_logged_values(recovery_logs, recovery_key) == [0.0], (
            f"kvs_recovery_reset did not run exactly once during recovery:\n{recovery_logs[-3000:]}"
        )
        for key, value in stored_before_crash.items():
            if key in reset_keys:
                continue
            assert restart_counter_logged_values(recovery_logs, key, source="read_back") == [value], (
                f"kvs_recovery_reset did not reload {key}={value} stored before the crash:\n{recovery_logs[-3000:]}"
            )
        for key in reset_keys:
            assert restart_counter_logged_values(recovery_logs, key, source="read_back") == [], (
                f"{key} still has a stored value after reset_key:\n{recovery_logs[-3000:]}"
            )
            assert restart_counter_logged_values(recovery_logs, key, source="read_back_default") == [
                _KVS_DEFAULTS[instance_id][key]
            ], f"{key} did not read back as its default after reset_key:\n{recovery_logs[-3000:]}"

        after_recovery = read_verified_kvs_values(kvs_dir, instance_id)
        assert after_recovery[recovery_key] == 1.0
        for key in reset_keys:
            assert key not in after_recovery, f"{key} was not reset to its default by the recovery component"
        kept = {key: value for key, value in written.items() if key not in reset_keys}
        assert {key: after_recovery[key] for key in kept} == kept, "Recovery reset changed keys it did not reset"
        assert after_recovery[launch_key] == 1.0, "State stored before the crash was lost during recovery"
        assert defaults_file.read_bytes() == defaults_before, "reset_key modified the defaults file"

        succeeded, relaunch_logs = _activate(lp_daemon, "Running")
        assert succeeded, f"Re-activating Running after recovery failed:\n{relaunch_logs[-3000:]}"
        relaunched_pid = find_descendant_pid(daemon.pid(), app)
        assert relaunched_pid not in (None, crashed_pid), f"{app} was not relaunched"
        assert restart_counter_logged_values(relaunch_logs, launch_key) == [1.0], (
            f"Relaunched kvs_primary did not reload the stored launch count:\n{relaunch_logs[-3000:]}"
        )

        after_relaunch = read_verified_kvs_values(kvs_dir, instance_id)
        assert after_relaunch[launch_key] == 2.0
        assert after_relaunch[recovery_key] == 1.0, "Relaunch lost state written during recovery"
        assert {key: after_relaunch[key] for key in written} == written

    @add_test_properties(
        partially_verifies=[
            "feat_req__lifecycle__control_commands",
            "feat_req__lifecycle__request_run_target_start",
            "feat_req__lifecycle__run_target_support",
            "feat_req__lifecycle__switch_run_targets",
            "feat_req__lifecycle__process_termination",
        ],
        test_type="integration",
        derivation_technique="architecture-based-testing",
    )
    def test_control_requests_switch_run_targets_of_kvs_components(
        self, lp_daemon: dict[str, Any], version: str
    ) -> None:
        """
        Control-interface requests start, switch and reject run targets that own KVS components.

        1. In `Startup` neither KVS component nor the supervised app has run.
        2. `Running` (via lmcontrol -> control_daemon -> Launch Manager) is
           reported as succeeded and kvs_primary has stored its values.
        3. `Secondary` is reported as succeeded: the supervised app is
           terminated, kvs_secondary stores instance 2, and instance 1 is
           byte-identical.
        4. An unknown run target is reported as failed and changes no process
           or KVS file.

        Pass/fail
        ---------
        PASS  Each request's reported result matches the observed processes and KVS files.
        FAIL  A request is not applied or reported, or touches unrelated KVS state.
        """
        daemon = lp_daemon["daemon"]
        kvs_dir = lp_daemon["kvs_dir"]
        app = lp_daemon["supervised_app"]
        primary = _kvs_input(lp_daemon, "kvs_primary")
        secondary = _kvs_input(lp_daemon, "kvs_secondary")
        primary_id, secondary_id = _instance_id(primary), _instance_id(secondary)

        assert not list(kvs_dir.glob("kvs_*_0.json")), "A KVS component ran outside its run target"
        assert find_descendant_pid(daemon.pid(), app) is None

        succeeded, logs = _activate(lp_daemon, "Running")
        assert succeeded, f"Activating Running failed:\n{logs[-3000:]}"
        app_pid = find_descendant_pid(daemon.pid(), app)
        assert app_pid is not None, f"Running did not launch {app}"
        primary_snapshot = read_verified_kvs_values(kvs_dir, primary_id)
        assert {key: primary_snapshot[key] for key in _written_values(primary)} == _written_values(primary)
        assert not (kvs_dir / f"kvs_{secondary_id}_0.json").exists(), "kvs_secondary ran outside Secondary"
        primary_bytes = (kvs_dir / f"kvs_{primary_id}_0.json").read_bytes()

        succeeded, logs = _activate(lp_daemon, "Secondary")
        assert succeeded, f"Activating Secondary failed:\n{logs[-3000:]}"
        assert re.search(rf"Requesting termination of process pid {app_pid}\b", logs), logs[-3000:]
        assert wait_until(lambda: find_descendant_pid(daemon.pid(), app) is None, _TIMEOUT_S), (
            f"{app} kept running after switching to Secondary"
        )
        secondary_snapshot = read_verified_kvs_values(kvs_dir, secondary_id)
        assert secondary_snapshot[secondary["test"]["counter_key"]] == 1.0
        assert {key: secondary_snapshot[key] for key in _written_values(secondary)} == _written_values(secondary)
        assert (kvs_dir / f"kvs_{primary_id}_0.json").read_bytes() == primary_bytes

        snapshots_before = {path.name: path.read_bytes() for path in kvs_dir.glob("kvs_*")}
        succeeded, logs = _activate(lp_daemon, "NoSuchRunTarget")
        assert not succeeded, f"An unknown run target was reported as activated:\n{logs[-3000:]}"
        assert daemon.is_running(), "Launch Manager exited after an invalid control request"
        assert {path.name: path.read_bytes() for path in kvs_dir.glob("kvs_*")} == snapshots_before
        assert find_descendant_pid(daemon.pid(), app) is None

    @add_test_properties(
        partially_verifies=[
            "feat_req__lifecycle__multi_instance_support",
            "feat_req__lifecycle__switch_run_targets",
            "feat_req__persistency__multiple_kvs",
        ],
        test_type="integration",
        derivation_technique="architecture-based-testing",
    )
    def test_kvs_instances_stay_isolated_across_run_target_switches(
        self, lp_daemon: dict[str, Any], version: str
    ) -> None:
        """
        Two instances of one executable keep separate KVS instances across run-target switches.

        1. `BothInstances` launches kvs_primary and kvs_secondary from the same
           executable; each stores only its own values in its own instance.
        2. `Startup` -> `Secondary` relaunches only kvs_secondary: instance 2
           reloads its counter (2) and instance 1 is byte-identical.
        3. `Running` relaunches only kvs_primary: instance 1 reloads its
           counter (2) and instance 2 is byte-identical.

        Pass/fail
        ---------
        PASS  Each relaunch changes only its own instance and continues its own counter.
        FAIL  Values leak between instances or a switch touches the other instance.
        """
        kvs_dir = lp_daemon["kvs_dir"]
        primary = _kvs_input(lp_daemon, "kvs_primary")
        secondary = _kvs_input(lp_daemon, "kvs_secondary")
        primary_id, secondary_id = _instance_id(primary), _instance_id(secondary)
        assert primary_id != secondary_id
        primary_counter = primary["test"]["counter_key"]
        secondary_counter = secondary["test"]["counter_key"]

        succeeded, logs = _activate(lp_daemon, "BothInstances")
        assert succeeded, f"Activating BothInstances failed:\n{logs[-3000:]}"
        executables = {
            component: re.search(rf"Starting process\s+\(\s*{component}\s*\)\s+from executable\s+(.+)", logs)
            for component in ("kvs_primary", "kvs_secondary")
        }
        assert all(executables.values()), f"Launch Manager did not start both KVS components:\n{logs[-3000:]}"
        assert executables["kvs_primary"].group(1) == executables["kvs_secondary"].group(1), (
            "The two KVS components were not launched from the same executable"
        )

        first = read_verified_kvs_values(kvs_dir, primary_id)
        second = read_verified_kvs_values(kvs_dir, secondary_id)
        assert first == {primary_counter: 1.0, **_written_values(primary)}
        assert second == {secondary_counter: 1.0, **_written_values(secondary)}

        primary_bytes = (kvs_dir / f"kvs_{primary_id}_0.json").read_bytes()
        for run_target in ("Startup", "Secondary"):
            succeeded, logs = _activate(lp_daemon, run_target)
            assert succeeded, f"Activating {run_target} failed:\n{logs[-3000:]}"
        assert read_verified_kvs_values(kvs_dir, secondary_id)[secondary_counter] == 2.0
        assert (kvs_dir / f"kvs_{primary_id}_0.json").read_bytes() == primary_bytes

        secondary_bytes = (kvs_dir / f"kvs_{secondary_id}_0.json").read_bytes()
        succeeded, logs = _activate(lp_daemon, "Running")
        assert succeeded, f"Activating Running failed:\n{logs[-3000:]}"
        assert read_verified_kvs_values(kvs_dir, primary_id) == {primary_counter: 2.0, **_written_values(primary)}
        assert (kvs_dir / f"kvs_{secondary_id}_0.json").read_bytes() == secondary_bytes

    @add_test_properties(
        partially_verifies=[
            "feat_req__lifecycle__logging_support",
        ],
        test_type="integration",
        derivation_technique="architecture-based-testing",
    )
    def test_launch_manager_logs_transitions_recovery_and_shutdown(
        self, lp_daemon: dict[str, Any], version: str
    ) -> None:
        """
        Launch Manager's own log records run-target transitions, KVS process exits, recovery and shutdown.

        Pass/fail
        ---------
        PASS  The log names the startup and requested transitions, the KVS
              component's start and exit status, the killed PID followed by the
              fallback recovery state, and an ordered SIGTERM shutdown through
              the Off state with exit code 0.
        FAIL  Any of these events is missing, names the wrong process, or is out of order.
        """
        daemon = lp_daemon["daemon"]
        app = lp_daemon["supervised_app"]
        startup_logs = daemon.get_logs()
        assert "Launch Manager Started" in startup_logs
        assert re.search(r"Completed the request for PG\s+to State Startup\b", startup_logs), startup_logs[-3000:]

        offset = daemon.get_log_offset()
        succeeded, _ = _activate(lp_daemon, "Running")
        assert succeeded
        logs = _wait_for_state(daemon, offset, "Running")
        assert re.search(r"got request kSetStateRequest.*re state Running", logs), logs[-3000:]
        assert re.search(r"Starting process\s+\(\s*kvs_primary\s*\)", logs), logs[-3000:]
        assert re.search(r"Process kvs_primary\s+\(\s*pid \d+\s*\)\s+terminated with exit code 0", logs), logs[-3000:]

        offset = daemon.get_log_offset()
        crashed_pid = _kill_supervised_app(lp_daemon, app)
        logs = _wait_for_state(daemon, offset, "fallback")
        termination = re.search(
            rf"unexpected termination of process {app}\s+\(\s*pid {crashed_pid}\s+exit code \d+\s*\)", logs
        )
        assert termination, f"Termination of PID {crashed_pid} was not logged:\n{logs[-3000:]}"
        recovery = re.search(r"activating recovery state:\s*fallback", logs[termination.end() :])
        assert recovery, f"No fallback recovery logged after the termination:\n{logs[-3000:]}"
        assert re.search(r"Process kvs_recovery_reset\s+\(\s*pid \d+\s*\)\s+terminated with exit code 0", logs)

        offset = daemon.get_log_offset()
        daemon.stop()
        assert daemon.process.returncode == 0, f"launch_manager exited with {daemon.process.returncode}"
        assert wait_until(lambda: "LCM run successfully" in daemon.get_logs_since(offset), 5.0)
        logs = daemon.get_logs_since(offset)
        markers = [
            r"received SIGTERM, exiting",
            r"Process control_daemon\s+\(\s*pid \d+\s*\)\s+terminated with exit code 0",
            r"Completed the request for PG\s+to State Off\b",
            r"LCM run successfully",
        ]
        positions = []
        for marker in markers:
            match = re.search(marker, logs)
            assert match, f"Shutdown log is missing {marker!r}:\n{logs[-3000:]}"
            positions.append(match.start())
        assert positions == sorted(positions), f"Shutdown log entries are out of order:\n{logs[-3000:]}"

    def test_components_run_with_configured_sandbox_identity(self, lp_daemon: dict[str, Any], version: str) -> None:
        """
        Launch Manager applies each component's configured sandbox uid/gid.

        Without `cap_setuid` the sandbox uid resolves to the runner's own, so an
        applied identity cannot be told from an inherited one and the test
        skips. It carries no requirement claim until CI grants the capability
        (`FIT_ENABLE_SETCAP=1`).

        1. The default sandbox uid differs from the runner's uid.
        2. After `Running`, the supervised app runs with the default sandbox
           uid/gid, and control_daemon with its own override (the runner's).
        3. kvs_primary's snapshot is owned by the sandbox uid, so the KVS
           component wrote it under that identity.

        Limitation: the sandbox gid is the runner's own, so the gid check is
        consistency-only and cannot prove setgid() ran.

        Pass/fail
        ---------
        PASS  Every observed process and file matches its configured identity.
        FAIL  A component inherits the runner's identity, or the override is ignored.
        """
        if not lp_daemon["sandbox_privileged"]:
            pytest.skip(f"Sandbox capabilities not granted: {lp_daemon['sandbox_privileged_reason']}")
        daemon = lp_daemon["daemon"]
        config = _rendered_config(lp_daemon)
        default_sandbox = config["defaults"]["deployment_config"]["sandbox"]
        control_sandbox = config["components"]["control_daemon"]["deployment_config"]["sandbox"]
        assert default_sandbox["uid"] != os.getuid(), "The sandbox uid must differ from the runner's"
        assert control_sandbox["uid"] == os.getuid()

        succeeded, logs = _activate(lp_daemon, "Running")
        assert succeeded, f"Activating Running failed:\n{logs[-3000:]}"
        app = lp_daemon["supervised_app"]
        expected = {
            app: (default_sandbox["uid"], default_sandbox["gid"]),
            "control_daemon": (control_sandbox["uid"], control_sandbox["gid"]),
        }
        for component, ids in expected.items():
            pid = find_descendant_pid(daemon.pid(), component)
            assert pid is not None, f"{component} is not running under the daemon"
            assert _process_ids(pid) == ids, f"{component} does not run with its configured sandbox identity"

        primary_id = _instance_id(_kvs_input(lp_daemon, "kvs_primary"))
        snapshot = lp_daemon["kvs_dir"] / f"kvs_{primary_id}_0.json"
        assert snapshot.stat().st_uid == default_sandbox["uid"], "kvs_primary did not write under the sandbox uid"
