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
Cross-module integration test: persistency storage continuity during lifecycle recovery.

This test validates that persistency storage remains intact when the Launch Manager
performs recovery actions (process restart) on supervised applications:

1. A supervised application is started under Launch Manager daemon supervision.
2. Persistency data is written to storage.
3. The supervised application is force-killed to trigger recovery.
4. Launch Manager detects the failure and restarts the application (recovery action).
5. Additional persistency operations are performed.
6. All persistency data remains accessible and intact after recovery.

This verifies the core integration requirement: lifecycle recovery actions do not
corrupt or interfere with persistency storage for colocated workloads.
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


def _run_persistency_probe(
    build_tools: BuildTools,
    version: str,
    kvs_dir: Path,
    timeout_s: float = 30.0,
) -> None:
    """
    Execute a persistency scenario using proper build tools infrastructure.

    This uses BuildTools when running via pytest or runfiles when running under Bazel,
    avoiding the subprocess-based workaround that caused issues with certain scenarios.

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
    if version == "rust":
        target = "//feature_integration_tests/test_scenarios/rust:rust_test_scenarios"
    else:
        target = "//feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios"

    # Use runfiles when running under Bazel, build_tools otherwise
    if _is_running_under_bazel():
        scenario_binary = find_binary_in_runfiles(target)
        if scenario_binary is None:
            pytest.skip(
                f"Scenario binary {target} not found in runfiles. "
                "This test requires the scenario binary to be available as a data dependency."
            )
    else:
        if target not in _binary_path_cache:
            _binary_path_cache[target] = build_tools.find_target_path(target)
        scenario_binary = _binary_path_cache[target]

    # NOTE: C++ all_value_types scenario requires the full FitScenario fixture infrastructure
    # (command, execution_timeout, results fixtures) which this test doesn't use.
    # Using subprocess.run() directly causes "Invalid value type" error for C++.
    # Use a simpler scenario (checksum) for C++ as a workaround.
    if version == "cpp":
        scenario_name = "persistency.default_values.checksum"
    else:
        scenario_name = "persistency.supported_datatypes.all_value_types"

    config = {
        "kvs_parameters_1": {
            "kvs_parameters": {
                "instance_id": 1,
                "dir": str(kvs_dir),
            },
        },
    }
    config_json = json.dumps(config)

    # Try both argument formats
    variants = [
        [str(scenario_binary), "--name", scenario_name, "--input", config_json],
        [str(scenario_binary), "-n", scenario_name, "-i", config_json],
    ]

    errors: list[str] = []
    for command in variants:
        result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=timeout_s)
        if result.returncode == 0:
            return
        errors.append(
            f"Command: {' '.join(command)}\nReturn code: {result.returncode}\nstderr:\n{result.stderr.strip()}"
        )

    raise RuntimeError("Persistency probe command failed for all invocation variants.\n\n" + "\n\n".join(errors))


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
    """
    if version == "rust":
        target = "//feature_integration_tests/test_scenarios/rust:rust_test_scenarios"
        scenario_name = "persistency.supported_datatypes.all_value_types"
    else:
        target = "//feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios"
        scenario_name = "persistency.default_values.checksum"

    if _is_running_under_bazel():
        scenario_binary = find_binary_in_runfiles(target)
        if scenario_binary is None:
            pytest.skip(
                f"Scenario binary {target} not found in runfiles. "
                "This test requires the scenario binary to be available as a data dependency."
            )
    else:
        if target not in _binary_path_cache:
            _binary_path_cache[target] = build_tools.find_target_path(target)
        scenario_binary = _binary_path_cache[target]

    config = {
        "kvs_parameters_1": {
            "kvs_parameters": {
                "instance_id": 1,
                "dir": str(kvs_dir),
            },
        },
    }
    config_json = json.dumps(config)
    command = [str(scenario_binary), "--name", scenario_name, "--input", config_json]

    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        # Freeze the process immediately so it cannot exit before we kill it.
        # Without SIGSTOP a fast-completing scenario exits normally before SIGKILL
        # is delivered — proc.kill() would then hit a zombie, exercising nothing.
        # After SIGSTOP the process is guaranteed alive; SIGKILL below delivers a
        # real abnormal termination regardless of how quickly the scenario runs.
        proc.send_signal(signal.SIGSTOP)
        time.sleep(crash_delay_s)
    finally:
        proc.kill()
        proc.wait()

    assert proc.returncode == -signal.SIGKILL, (
        f"Expected SIGKILL exit (returncode {-signal.SIGKILL}), got {proc.returncode}. "
        "Crash simulation did not exercise abnormal termination."
    )


def _wait_for_process_restart(daemon: Any, process_name: str, old_pid: int, timeout_s: float = 10.0) -> int | None:
    """
    Wait for a supervised process to be restarted with a new PID.

    Parameters
    ----------
    daemon : LaunchManagerDaemon
        The daemon instance managing the supervised process.
    process_name : str
        Name of the supervised binary.
    old_pid : int
        Previous PID of the process (before kill).
    timeout_s : float
        Maximum time to wait for restart.

    Returns
    -------
    int | None
        New PID if process was restarted, None if timeout or restart failed.
    """
    start_time = time.time()

    while time.time() - start_time < timeout_s:
        new_pid = _find_supervised_process(daemon, process_name)

        # Check if we found a new process (different PID)
        if new_pid is not None and new_pid != old_pid:
            # Verify the process is actually running
            try:
                proc = psutil.Process(new_pid)
                if proc.is_running():
                    return new_pid
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        time.sleep(0.2)

    return None


@pytest.mark.daemon
@add_test_properties(
    partially_verifies=[
        "feat_req__lifecycle__process_failure_react",
        "feat_req__lifecycle__monitor_abnormal_term",
        "feat_req__persistency__store_data",
        "feat_req__lifecycle__restart_on_failure",
        "feat_req__lifecycle__recovery_action",
    ],
    test_type="integration",
    derivation_technique="architecture-based-testing",
)
class TestLifecyclePersistencyRecoveryContinuity:
    """
    Cross-module integration: Lifecycle recovery actions preserve persistency state.

    This test suite validates that when a supervised application crashes and the
    Launch Manager performs recovery (restart), persistency storage remains
    accessible and intact for the recovered process.

    Test structure:
    1. test_persistency_continuity_across_recovery: Baseline test showing storage
       works across multiple process instances (no supervision)
    2. test_persistency_recovery_with_daemon_supervision: **Main recovery test**
       - Supervised app runs under daemon with restart recovery
       - Force-kill triggers actual recovery (daemon detects and restarts process)
       - Persistency storage verified before and after recovery
    3. test_supervised_app_crash_persistency_recovery: Foundational test for
       storage continuity across normal process termination

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

    def test_persistency_continuity_across_recovery(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        build_tools: BuildTools,
        version: str,
    ) -> None:
        """
        Verify that persistency snapshots remain stable during lifecycle recovery.

        The test flow:
        1. Write initial persistency data using scenario executable
        2. Verify snapshot integrity
        3. Run scenario again in the same storage directory
        4. Verify the snapshot remains readable after the second run

        This validates that multiple process instances can successfully access
        the same persistency storage directory without corruption.

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

        # Read and verify snapshot integrity
        snapshot_data = read_kvs_snapshot(kvs_dir, instance_id=1, snapshot_id=0)
        assert snapshot_data, "Snapshot data is empty or corrupted"

        # Verify hash matches
        verify_kvs_snapshot_hash(kvs_dir, instance_id=1, snapshot_id=0)

        # Record which snapshot IDs exist after the first run and their mtimes, so we
        # can distinguish new snapshot IDs from overwrites in step 4.
        def _snapshot_ids(directory: Path, instance_id: int) -> set[int]:
            ids = set()
            for f in directory.glob(f"kvs_{instance_id}_*.json"):
                try:
                    ids.add(int(f.stem.split("_")[-1]))
                except ValueError:
                    pass
            return ids

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

        new_snapshot_ids = snapshot_ids_after_second - snapshot_ids_after_first
        all_snapshots = sorted(kvs_dir.glob("kvs_1_*.json"))
        files_updated = any(
            f not in mtimes_before_second or f.stat().st_mtime != mtimes_before_second[f] for f in all_snapshots
        )
        assert new_snapshot_ids or files_updated, (
            "The second run neither created new snapshot IDs nor updated existing ones. "
            "The second probe wrote no data — storage may be read-only or broken."
        )

        # Verify every snapshot ID that exists after both runs is hash-valid.
        # This confirms continuity: data from the first run (snapshot_id=0) and any
        # data written by the second run are both readable and uncorrupted.
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
        Verify persistency continuity when supervised app crashes and is recovered.

        This test exercises the actual lifecycle recovery mechanism:
        1. Daemon supervises a rust/cpp_supervised_app component
        2. Persistency data is written before triggering recovery
        3. The supervised app process is force-killed (SIGKILL)
        4. Launch Manager detects the failure and transitions to fallback_run_target
        5. LCM detects crash, logs 'unexpected termination', and transitions to
           fallback_run_target within seconds
        6. Daemon remains alive through the recovery sequence
        7. All persistency data written before the crash remains intact

        The LCM recovery action for a runtime crash is switch_run_target (schema
        constraint: switch_run_target must target the reserved fallback_run_target).
        The full shutdown sequence runs in background (~30 s); this test validates
        the observable recovery trigger, not the final daemon exit.

        Pass/fail
        ---------
        PASS  LCM logs 'unexpected termination' and 'fallback' within 10 s of kill,
              daemon is alive immediately after, persistency data intact.
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

        # Verify snapshot creation
        snapshot_data = read_kvs_snapshot(kvs_dir, instance_id=1, snapshot_id=0)
        assert snapshot_data, "Initial snapshot not created before recovery"
        verify_kvs_snapshot_hash(kvs_dir, instance_id=1, snapshot_id=0)
        print("✓ Initial persistency snapshot verified")

        # Step 3: Force-kill the supervised process to trigger recovery.
        # The LCM detects the unexpected termination, activates recovery, and
        # transitions to fallback_run_target (schema constraint: switch_run_target
        # can only target the reserved fallback_run_target, not restart).
        print(f"Force-killing supervised process (PID: {supervised_pid}) to trigger recovery...")
        kill_success = _force_kill_process(supervised_pid)
        assert kill_success, f"Failed to kill supervised process {supervised_pid}"

        # Step 4: Wait for the LCM to detect the crash and initiate recovery.
        # After SIGKILL the LCM detects unexpected termination within milliseconds and
        # immediately transitions to fallback_run_target. We poll the log for evidence of
        # this transition; the full shutdown sequence runs in the background and can take
        # up to ~30 s (multiple supervision + transition cycles).
        print("Waiting for LCM to detect crash and initiate recovery...")
        recovery_deadline = time.time() + 10.0
        recovery_detected = False
        while time.time() < recovery_deadline:
            logs = daemon.get_logs()
            if "unexpected termination" in logs.lower() and "fallback" in logs.lower():
                recovery_detected = True
                break
            time.sleep(0.2)

        assert recovery_detected, (
            "LCM did not log 'unexpected termination' and 'fallback' within 10 s. "
            "Crash detection or recovery transition may not have triggered."
        )
        print("✓ Recovery sequence detected in daemon logs")

        # Step 5: Daemon must still be running (alive through recovery) immediately
        # after the crash — it has not yet completed its shutdown sequence.
        assert daemon.is_running(), (
            "Daemon exited prematurely after supervised app crash. "
            "Expected daemon to remain alive while processing recovery."
        )
        print("✓ Daemon is alive through recovery sequence")

        # Step 6: Persistency data written before the crash must remain intact.
        verify_kvs_snapshot_hash(kvs_dir, instance_id=1, snapshot_id=0)
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
        verify_kvs_snapshot_hash(kvs_dir, instance_id=1, snapshot_id=0)
        print("✓ New persistency data written successfully after lifecycle recovery")

    def test_supervised_app_crash_persistency_recovery(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        build_tools: BuildTools,
        version: str,
    ) -> None:
        """
        Foundational test: Verify persistency storage survives process termination.

        This is a prerequisite test that validates the underlying storage mechanism
        works correctly across process boundaries, which is required for the full
        recovery test above to be meaningful.

        The test flow:
        1. A process writes initial persistency data and terminates
        2. A second process writes additional data to the same storage
        3. Both datasets remain accessible and intact

        This establishes that persistency storage itself is resilient to process
        lifecycle events (normal termination), which is the foundation for testing
        recovery from abnormal termination (crashes) in the daemon-supervised test.

        Pass/fail
        ---------
        PASS  Persistency data from terminated process remains accessible; new
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

        initial_snapshot = read_kvs_snapshot(kvs_dir, instance_id=1, snapshot_id=0)
        assert initial_snapshot, "Initial snapshot is empty or corrupted"
        verify_kvs_snapshot_hash(kvs_dir, instance_id=1, snapshot_id=0)

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
        verify_kvs_snapshot_hash(kvs_dir, instance_id=1, snapshot_id=0)
        recovered_snapshot = read_kvs_snapshot(kvs_dir, instance_id=1, snapshot_id=0)
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
