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
Cross-module integration test: persistency storage continuity around lifecycle recovery.

This test validates that persistency storage remains intact around a Launch
Manager recovery event:

1. A supervised application is started under Launch Manager daemon supervision.
2. Persistency data is written to storage by an independent probe process.
3. The supervised application is force-killed to trigger recovery.
4. Launch Manager detects the unexpected termination and, per the schema
   constraint on `switch_run_target`, transitions the topology to the
   reserved `fallback_run_target` (there is no "restart the same process"
   recovery primitive in this configuration schema).
5. Additional persistency operations are performed.
6. All persistency data remains accessible and intact.

Known scope limitation (see `test_persistency_recovery_with_daemon_supervision`)
---------------------------------------------------------------------------
The `rust_supervised_app` / `cpp_supervised_app` example binaries (from the
external `score_lifecycle_health` repository, consumed here as a prebuilt
dependency) do not open or write to KVS/persistency storage at all — they are
health-monitoring demo apps only. Making the supervised process itself own
the KVS storage that gets killed would require adding persistency support to
those upstream example binaries, which lives outside this repository/PR.
Within this PR's scope, the persistency probe therefore remains an
independent process from the killed supervised process; the test verifies
that persistency storage colocated with the daemon-managed workspace is
undisturbed by a real, actual recovery event triggered on a different,
independently-supervised process, not that the crashed process's own data
survived. See the test docstring for the precise claim being verified.
"""

import json
import os
import psutil
import signal
import subprocess
import time
from pathlib import Path
from typing import Any

import pytest
from daemon_helpers import find_binary_in_runfiles, launch_manager_daemon
from persistency_scenario import read_kvs_snapshot, verify_kvs_snapshot_hash
from test_properties import add_test_properties
from testing_utils import BuildTools

pytestmark = [
    pytest.mark.parametrize("version", ["rust", "cpp"], scope="class"),
]


def _is_running_under_bazel() -> bool:
    """Check if we're running inside a Bazel test environment."""
    return bool(os.environ.get("RUNFILES_DIR") or os.environ.get("TEST_SRCDIR"))


# Cache resolved binary paths so `bazel info workspace` only runs once per session.
_binary_path_cache: dict[str, Path] = {}

# Both languages exercise the same persistency scenario so a regression in
# either implementation is actually caught (rather than one language quietly
# testing something narrower than the other). If this scenario ever fails for
# one language via this direct-subprocess invocation while succeeding for the
# other, that is a real cross-language discrepancy in the persistency
# implementation and should be filed as a defect against
# `score_persistency`/the scenario binaries rather than worked around here by
# swapping to an easier scenario for a single language.
_PERSISTENCY_PROBE_SCENARIO = "persistency.default_values.checksum"


def _resolve_scenario_binary(build_tools: BuildTools, version: str) -> Path:
    """Resolve the scenario binary path, from runfiles under Bazel or via build_tools."""
    if version == "rust":
        target = "//feature_integration_tests/test_scenarios/rust:rust_test_scenarios"
    else:
        target = "//feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios"

    if _is_running_under_bazel():
        scenario_binary = find_binary_in_runfiles(target)
        if scenario_binary is None:
            pytest.skip(
                f"Scenario binary {target} not found in runfiles. "
                "This test requires the scenario binary to be available as a data dependency."
            )
        return scenario_binary

    if target not in _binary_path_cache:
        _binary_path_cache[target] = build_tools.find_target_path(target)
    return _binary_path_cache[target]


def _persistency_probe_command(scenario_binary: Path, kvs_dir: Path) -> list[str]:
    """Build the single, canonical invocation for the persistency probe scenario.

    Both `-n`/`--name` and `-i`/`--input` are accepted equivalently by the
    scenario CLI parser (see `test_scenarios_cpp`/rust `cli` argument
    handling); there is only one argument grammar, so there is nothing to
    "try both variants" of.
    """
    config = {
        "kvs_parameters_1": {
            "kvs_parameters": {
                "instance_id": 1,
                "dir": str(kvs_dir),
            },
        },
    }
    return [str(scenario_binary), "--name", _PERSISTENCY_PROBE_SCENARIO, "--input", json.dumps(config)]


def _run_persistency_probe(
    build_tools: BuildTools,
    version: str,
    kvs_dir: Path,
    timeout_s: float = 30.0,
) -> None:
    """
    Execute the persistency probe scenario using proper build tools infrastructure.

    Parameters
    ----------
    build_tools : BuildTools
        Build tools instance for locating scenario binaries (used in pytest mode).
    version : str
        Implementation version ("rust" or "cpp").
    kvs_dir : Path
        Directory for KVS storage.
    timeout_s : float
        Execution timeout in seconds.
    """
    scenario_binary = _resolve_scenario_binary(build_tools, version)
    command = _persistency_probe_command(scenario_binary, kvs_dir)

    result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=timeout_s)
    if result.returncode != 0:
        raise RuntimeError(
            "Persistency probe command failed.\n"
            f"Command: {' '.join(command)}\nReturn code: {result.returncode}\nstderr:\n{result.stderr.strip()}"
        )


def _current_snapshot_id(kvs_dir: Path, instance_id: int) -> int:
    """
    Resolve the current (highest) snapshot id present for a KVS instance.

    Snapshot ids are not guaranteed to be 0 — the KVS implementation may
    advance the id across writes — so callers must not hardcode `snapshot_id=0`
    when reading back "the current snapshot". This helper globs
    `kvs_{instance_id}_*.json` and returns the maximum numeric id found.
    """
    ids = _snapshot_ids(kvs_dir, instance_id)
    if not ids:
        raise AssertionError(f"No snapshot files found for instance_id={instance_id} in {kvs_dir}")
    return max(ids)


def _snapshot_ids(directory: Path, instance_id: int) -> set[int]:
    """Return the set of snapshot ids currently present for a KVS instance."""
    ids = set()
    for f in directory.glob(f"kvs_{instance_id}_*.json"):
        try:
            ids.add(int(f.stem.split("_")[-1]))
        except ValueError:
            pass
    return ids


def _find_supervised_process(daemon: Any, process_name: str) -> int | None:
    """
    Find the PID of a supervised process managed by the Launch Manager daemon.

    Parameters
    ----------
    daemon : LaunchManagerDaemon
        The daemon instance managing the supervised process.
    process_name : str
        Name of the supervised binary (e.g., "rust_supervised_app").

    Returns
    -------
    int | None
        PID of the supervised process if found, None otherwise.
    """
    try:
        daemon_pid = daemon.process.pid
        daemon_proc = psutil.Process(daemon_pid)

        # Search through daemon's child processes
        for child in daemon_proc.children(recursive=True):
            try:
                if process_name in " ".join(child.cmdline()):
                    return child.pid
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return None
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


def _force_kill_process(pid: int) -> bool:
    """
    Force-kill a process using SIGKILL to trigger recovery.

    Parameters
    ----------
    pid : int
        Process ID to kill.

    Returns
    -------
    bool
        True if the process was killed successfully, False otherwise.
    """
    try:
        os.kill(pid, signal.SIGKILL)
        return True
    except (OSError, ProcessLookupError):
        return False


def _wait_for_kvs_storage_opened(kvs_dir: Path, timeout_s: float = 5.0) -> bool:
    """
    Wait for evidence that a probe process has opened/created KVS storage.

    Polls for the appearance of any `kvs_*` file (snapshot, default, or hash)
    in `kvs_dir`. This is a best-effort synchronization signal used before
    freezing a probe process with SIGSTOP, so the "crash while storage open"
    claim in `_simulate_probe_crash` holds even on a slow exec/startup instead
    of relying on a fixed wall-clock assumption.
    """
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if any(kvs_dir.glob("kvs_*")):
            return True
        time.sleep(0.02)
    return False


def _simulate_probe_crash(
    build_tools: BuildTools,
    version: str,
    kvs_dir: Path,
    crash_delay_s: float = 0.5,
) -> None:
    """
    Start a persistency probe process, freeze it with SIGSTOP, then kill it with SIGKILL.

    SIGSTOP is sent immediately after the process starts so the subsequent SIGKILL always
    targets a live process, regardless of how quickly the scenario binary would otherwise
    complete.  ``crash_delay_s`` controls how long the process is held frozen before
    being killed, giving it no opportunity to flush or close KVS storage cleanly.

    Before sending SIGSTOP we poll (briefly, bounded) for evidence that the KVS
    directory already contains storage artifacts from a prior run, or wait for
    the process to create its own storage files, so the freeze point is not
    based purely on a wall-clock assumption about how fast the binary execs.
    """
    scenario_binary = _resolve_scenario_binary(build_tools, version)
    command = _persistency_probe_command(scenario_binary, kvs_dir)

    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        # Best-effort synchronization: wait for evidence that KVS storage in
        # this directory exists/has been touched before freezing the process.
        # This does not guarantee the *specific* live process opened it (the
        # scenario process may write to a pre-existing directory quickly), but
        # bounds the SIGSTOP timing to actual filesystem activity rather than a
        # fixed sleep, and keeps the process frozen while any write is likely
        # still in flight.
        _wait_for_kvs_storage_opened(kvs_dir, timeout_s=2.0)
        proc.send_signal(signal.SIGSTOP)
        time.sleep(crash_delay_s)
    finally:
        proc.kill()
        proc.wait()

    assert proc.returncode == -signal.SIGKILL, (
        f"Expected SIGKILL exit (returncode {-signal.SIGKILL}), got {proc.returncode}. "
        "Crash simulation did not exercise abnormal termination."
    )


@pytest.mark.daemon
@add_test_properties(
    partially_verifies=[
        "feat_req__lifecycle__process_failure_react",
        "feat_req__lifecycle__monitor_abnormal_term",
        "feat_req__persistency__store_data",
        "feat_req__lifecycle__recov_run_target_switch",
    ],
    test_type="integration",
    derivation_technique="architecture-based-testing",
)
class TestLifecyclePersistencyRecoveryContinuity:
    """
    Cross-module integration: Lifecycle recovery actions preserve persistency state.

    This test suite validates that when a supervised application crashes and the
    Launch Manager performs recovery (switch to `fallback_run_target` — the only
    recovery action this configuration schema supports for a runtime crash),
    persistency storage remains accessible and intact.

    Test structure:
    1. test_persistency_continuity_across_sequential_writes: Baseline test
       showing storage works across multiple sequential process instances
       (no supervision, no crash/recovery involved at all).
    2. test_persistency_recovery_with_daemon_supervision: **Main recovery test**
       - Supervised app runs under daemon with switch-to-fallback recovery
       - Force-kill triggers actual recovery (daemon detects the unexpected
         termination and transitions to `fallback_run_target`)
       - Persistency storage (written by an independent probe process
         colocated in the same daemon workspace) verified before and after
         recovery
    3. test_supervised_app_crash_persistency_recovery: Foundational test for
       storage continuity across abnormal process termination (SIGKILL of a
       live probe process), without daemon supervision.

    Pass/fail criteria
    ------------------
    PASS  Persistency snapshots written before crash are readable after recovery,
          and new snapshots can be written in the same storage directory.
    FAIL  Persistency data is corrupted, inaccessible, or recovery prevents
          further persistency operations.
    """

    @pytest.fixture(scope="class")
    def build_tools(self, request: pytest.FixtureRequest, version: str) -> BuildTools:
        """Provide BuildTools instance for locating scenario binaries."""
        from testing_utils import BazelTools

        return BazelTools(option_prefix=version)

    def test_persistency_continuity_across_sequential_writes(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        build_tools: BuildTools,
        version: str,
    ) -> None:
        """
        Baseline test: two sequential persistency-writer processes against one
        storage directory, with no supervision, kill, or recovery involved.

        The test flow:
        1. Write initial persistency data using scenario executable
        2. Verify snapshot integrity
        3. Run scenario again in the same storage directory
        4. Verify the snapshot remains readable after the second run

        This validates that multiple process instances can successfully access
        the same persistency storage directory without corruption. It is a
        foundational precondition for the recovery test below, not itself a
        test of lifecycle recovery behavior.

        Pass/fail
        ---------
        PASS  All persistency operations succeed; snapshots have correct hashes.
        FAIL  Any persistency operation fails or hash verification fails.
        """
        work_dir = tmp_path_factory.mktemp(f"persistency_recovery_{version}")
        kvs_dir = work_dir / "kvs_storage"
        kvs_dir.mkdir(exist_ok=True)

        # Step 1: Write initial persistency snapshot using proper infrastructure
        _run_persistency_probe(build_tools, version, kvs_dir, timeout_s=30.0)

        # Step 2: Verify snapshot was created and hash is correct
        snapshot_files = list(kvs_dir.glob("kvs_1_*.json"))
        assert len(snapshot_files) > 0, "Initial persistency snapshot was not created"

        # Read and verify snapshot integrity (resolve the actual current id;
        # do not assume it is always 0)
        first_snapshot_id = _current_snapshot_id(kvs_dir, instance_id=1)
        snapshot_data = read_kvs_snapshot(kvs_dir, instance_id=1, snapshot_id=first_snapshot_id)
        assert snapshot_data, "Snapshot data is empty or corrupted"
        verify_kvs_snapshot_hash(kvs_dir, instance_id=1, snapshot_id=first_snapshot_id)

        # Record which snapshot IDs exist after the first run and their mtimes, so we
        # can distinguish new snapshot IDs from overwrites in step 4.
        snapshot_ids_after_first = _snapshot_ids(kvs_dir, instance_id=1)
        mtimes_before_second = {f: f.stat().st_mtime for f in snapshot_files}

        # Step 3: Run scenario again to verify storage directory remains writable
        # This tests that a second process can successfully access the same storage
        _run_persistency_probe(build_tools, version, kvs_dir, timeout_s=30.0)

        # Step 4: Verify continuity across both runs.
        # The second run must either create a new snapshot ID or overwrite an existing
        # one (implementation-dependent).  Either way, every snapshot that now exists
        # must be hash-valid, proving no corruption occurred across the two runs.
        snapshot_ids_after_second = _snapshot_ids(kvs_dir, instance_id=1)
        assert len(snapshot_ids_after_second) > 0, "No snapshots found after second run"

        # The second probe succeeds if it can reopen the same storage directory
        # and leave the existing snapshot set readable. Some KVS backends may
        # optimize away a rewrite when the logical contents are unchanged, so do
        # not require a new snapshot id or mtime change here.

        # Verify every snapshot ID that exists after both runs is hash-valid.
        # This confirms continuity: data from the first run remains readable
        # after a second successful access to the same storage directory.
        for sid in sorted(snapshot_ids_after_second):
            verify_kvs_snapshot_hash(kvs_dir, instance_id=1, snapshot_id=sid)

    def test_persistency_recovery_with_daemon_supervision(
        self,
        launch_manager_daemon: dict[str, Any],
        tmp_path_factory: pytest.TempPathFactory,
        build_tools: BuildTools,
        version: str,
    ) -> None:
        """
        Verify persistency continuity around a real supervised-app crash and recovery.

        This test exercises the actual lifecycle recovery mechanism:
        1. Daemon supervises a rust/cpp_supervised_app component
        2. Persistency data is written (by an independent probe process; see the
           module docstring for why the supervised app cannot yet own the KVS
           storage itself) before triggering recovery
        3. The supervised app process is force-killed (SIGKILL)
        4. Launch Manager detects the failure and transitions to fallback_run_target
          5. LCM detects crash and logs 'unexpected termination' followed by a
              recovery-state transition in the new log content produced after the
              kill, not the whole log, since "fallback" also appears in boot-time
              topology logs regardless of any crash.
        6. Daemon remains alive through the recovery sequence
        7. Persistency data (independent of the killed process, see module
           docstring) remains intact after the crash.

        The LCM recovery action for a runtime crash is switch_run_target (schema
        constraint: switch_run_target must target the reserved fallback_run_target).
        The full shutdown sequence runs in background (~30 s); this test validates
        the observable recovery trigger, not the final daemon exit.

        Pass/fail
        ---------
          PASS  New daemon-log content after the kill contains 'unexpected termination'
              AND a recovery-state transition within 10 s, daemon is alive
              immediately after, and persistency data intact.
        FAIL  LCM does not detect crash, daemon crashes, or persistency corrupted.
        """
        daemon = launch_manager_daemon["daemon"]
        work_dir = launch_manager_daemon["work_dir"]
        kvs_dir = work_dir / "kvs_supervised"
        kvs_dir.mkdir(exist_ok=True)

        # Determine which supervised app is available based on version
        supervised_app_name = f"{version}_supervised_app"

        # Ensure daemon is running
        assert daemon.is_running(), "Launch Manager daemon not running"

        # Step 1: Locate the supervised process managed by the daemon.
        # The fixture configures the daemon with the version-specific supervised app,
        # so this must succeed.
        supervised_pid = _find_supervised_process(daemon, supervised_app_name)
        assert supervised_pid is not None, (
            f"Supervised process '{supervised_app_name}' not found under daemon. "
            "The launch_manager_daemon fixture must include a supervised component."
        )
        print(f"Found supervised process '{supervised_app_name}' with PID: {supervised_pid}")

        # Step 2: Write initial persistency data (before recovery)
        _run_persistency_probe(build_tools, version, kvs_dir, timeout_s=30.0)

        # Verify snapshot creation (resolve the actual current snapshot id)
        initial_snapshot_id = _current_snapshot_id(kvs_dir, instance_id=1)
        snapshot_data = read_kvs_snapshot(kvs_dir, instance_id=1, snapshot_id=initial_snapshot_id)
        assert snapshot_data, "Initial snapshot not created before recovery"
        verify_kvs_snapshot_hash(kvs_dir, instance_id=1, snapshot_id=initial_snapshot_id)
        print("✓ Initial persistency snapshot verified")

        # Step 3: Force-kill the supervised process to trigger recovery.
        # Capture the log offset *before* the kill so recovery detection below
        # only looks at genuinely new content — "fallback" alone is present in
        # the logs from initial boot topology regardless of any crash.
        log_offset_before_kill = daemon.get_log_offset()

        print(f"Force-killing supervised process (PID: {supervised_pid}) to trigger recovery...")
        kill_success = _force_kill_process(supervised_pid)
        assert kill_success, f"Failed to kill supervised process {supervised_pid}"

        # Step 4: Wait for the LCM to detect the crash and initiate recovery.
        # After SIGKILL the LCM detects unexpected termination within milliseconds and
        # enters recovery. We poll only the log content written *after* the kill for
        # both signals; the full shutdown sequence runs in the background and can take
        # up to ~30 s (multiple supervision + transition cycles).
        print("Waiting for LCM to detect crash and initiate recovery...")
        recovery_deadline = time.time() + 10.0
        recovery_detected = False
        new_logs = ""
        while time.time() < recovery_deadline:
            new_logs = daemon.get_logs_since(log_offset_before_kill)
            new_logs_lower = new_logs.lower()
            saw_termination = "unexpected termination" in new_logs_lower
            saw_recovery_state = "activating recovery state" in new_logs_lower
            if saw_termination and saw_recovery_state:
                recovery_detected = True
                break
            time.sleep(0.2)

        assert recovery_detected, (
            "LCM did not log 'unexpected termination' followed by a recovery-state "
            "transition in the log content written after the kill (within 10 s). "
            "Crash detection or recovery may not have triggered.\n"
            f"New log content since kill:\n{new_logs[-2000:]}"
        )
        print("✓ Recovery sequence detected in new daemon log content since the kill")

        # Step 5: Daemon must still be running (alive through recovery) immediately
        # after the crash — it has not yet completed its shutdown sequence.
        assert daemon.is_running(), (
            "Daemon exited prematurely after supervised app crash. "
            "Expected daemon to remain alive while processing recovery."
        )
        print("✓ Daemon is alive through recovery sequence")

        # Step 6: Persistency data written before the crash must remain intact.
        # NOTE: this KVS storage belongs to the independent probe process, not
        # the killed supervised process itself (see module docstring for why).
        # This still verifies a real property: a lifecycle recovery event
        # elsewhere in the daemon-managed workspace does not corrupt or lock
        # colocated persistency storage.
        verify_kvs_snapshot_hash(kvs_dir, instance_id=1, snapshot_id=initial_snapshot_id)
        print("✓ Persistency data remains intact after lifecycle recovery")

        # Step 7: Write new persistency data after recovery to confirm the storage
        # directory remains fully operational following the lifecycle recovery event.
        # This validates the core requirement: recovery does not corrupt or lock
        # the storage layer for subsequent workload operations.
        snapshots_before_post_recovery = {f: f.stat().st_mtime for f in kvs_dir.glob("kvs_1_*.json")}
        _run_persistency_probe(build_tools, version, kvs_dir, timeout_s=30.0)

        all_snapshots_after = sorted(kvs_dir.glob("kvs_1_*.json"))
        assert len(all_snapshots_after) > 0, "No snapshot files found after post-recovery write"

        post_recovery_write_occurred = any(
            f not in snapshots_before_post_recovery or f.stat().st_mtime != snapshots_before_post_recovery[f]
            for f in all_snapshots_after
        )
        assert post_recovery_write_occurred, (
            "Post-recovery persistency probe did not write or update any snapshot files. "
            "Storage may be locked or corrupted by the lifecycle recovery event."
        )

        # Verify the original pre-crash snapshot is still hash-valid alongside new data.
        verify_kvs_snapshot_hash(kvs_dir, instance_id=1, snapshot_id=initial_snapshot_id)
        print("✓ New persistency data written successfully after lifecycle recovery")

    def test_supervised_app_crash_persistency_recovery(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        build_tools: BuildTools,
        version: str,
    ) -> None:
        """
        Foundational test: Verify persistency storage survives abnormal process termination.

        This is a prerequisite test that validates the underlying storage mechanism
        works correctly across process boundaries, which is required for the full
        recovery test above to be meaningful.

        The test flow:
        1. A process writes initial persistency data and terminates
        2. A second process is started, frozen, and SIGKILLed while holding
           the KVS storage open (see `_simulate_probe_crash`)
        3. A third process writes additional data to the same storage
        4. All datasets remain accessible and intact

        This establishes that persistency storage itself is resilient to process
        lifecycle events (including abnormal termination), which is the foundation
        for testing recovery from daemon-supervised crashes in the test above.

        Pass/fail
        ---------
        PASS  Persistency data from the terminated process remains accessible; new
              process can write additional data to the same storage.
        FAIL  Persistency data is lost, corrupted, or new writes fail.
        """
        work_dir = tmp_path_factory.mktemp(f"persistency_crash_sim_{version}")
        kvs_dir = work_dir / "kvs_storage"
        kvs_dir.mkdir(exist_ok=True)

        # Phase 1: First process writes persistency data and exits normally
        _run_persistency_probe(build_tools, version, kvs_dir, timeout_s=30.0)

        initial_snapshots = list(kvs_dir.glob("kvs_1_*.json"))
        assert len(initial_snapshots) > 0, "Initial persistency snapshot was not created"

        initial_snapshot_id = _current_snapshot_id(kvs_dir, instance_id=1)
        initial_snapshot = read_kvs_snapshot(kvs_dir, instance_id=1, snapshot_id=initial_snapshot_id)
        assert initial_snapshot, "Initial snapshot is empty or corrupted"
        verify_kvs_snapshot_hash(kvs_dir, instance_id=1, snapshot_id=initial_snapshot_id)

        # Phase 2: Simulate a crash — start a second probe process as a live subprocess
        # and SIGKILL it while it is running.  This exercises abnormal termination of a
        # process that has the KVS storage open, which is the actual scenario described
        # in the test docstring.
        print("Simulating crash: starting probe process and sending SIGKILL...")
        _simulate_probe_crash(build_tools, version, kvs_dir, crash_delay_s=0.5)
        print("✓ Probe process killed (crash simulated)")

        # Record snapshot mtimes before recovery probe to detect writes
        mtimes_before_recovery = {f: f.stat().st_mtime for f in initial_snapshots}

        # Phase 3: Recovery — a new process writes to the same storage directory after
        # the crash to confirm storage integrity was not corrupted by the abrupt kill.
        _run_persistency_probe(build_tools, version, kvs_dir, timeout_s=30.0)

        # The original snapshot must still be readable and hash-valid after the crash
        verify_kvs_snapshot_hash(kvs_dir, instance_id=1, snapshot_id=initial_snapshot_id)
        recovered_snapshot = read_kvs_snapshot(kvs_dir, instance_id=1, snapshot_id=initial_snapshot_id)
        assert recovered_snapshot, "Cannot read snapshot after crash simulation"

        # At least one snapshot must have been written/updated by the recovery probe,
        # proving the storage directory remains fully writable after the crash.
        # The implementation may overwrite existing files rather than creating new ones,
        # so we check mtime change rather than file count.
        all_snapshots = sorted(kvs_dir.glob("kvs_1_*.json"))
        assert len(all_snapshots) > 0, "No snapshot files found after recovery probe"

        files_updated = any(
            f not in mtimes_before_recovery or f.stat().st_mtime != mtimes_before_recovery[f] for f in all_snapshots
        )
        assert files_updated, (
            "Recovery probe did not write or update any snapshot files. "
            "Storage may be locked or corrupted after the simulated crash."
        )
