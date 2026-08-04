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
"""Daemon helpers for lifecycle behavior tests against real Launch Manager."""

from __future__ import annotations

import fcntl
import os
import re
import shutil
import signal
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest


_TARGET_ENV_MAP = {
    "@score_lifecycle_health//score/launch_manager:launch_manager": "FIT_LAUNCH_MANAGER_PATH",
    "@score_lifecycle_health//examples/rust_supervised_app:rust_supervised_app": "FIT_RUST_SUPERVISED_APP_PATH",
    "@score_lifecycle_health//examples/cpp_supervised_app:cpp_supervised_app": "FIT_CPP_SUPERVISED_APP_PATH",
    "//feature_integration_tests/configs:lifecycle_daemon_config": "FIT_LIFECYCLE_DAEMON_CONFIG_PATH",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _run(cmd: list[str]) -> str:
    completed = subprocess.run(
        cmd,
        cwd=_repo_root(),
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()


def _resolve_from_env(target: str) -> Path | None:
    """Resolve a target path from Bazel-provided runfile environment variables."""
    env_var = _TARGET_ENV_MAP.get(target)
    if env_var is None:
        return None

    raw_path = os.environ.get(env_var)
    if not raw_path:
        return None

    candidate = Path(raw_path)
    search_roots = [Path.cwd()]

    test_srcdir = os.environ.get("TEST_SRCDIR")
    test_workspace = os.environ.get("TEST_WORKSPACE")
    if test_srcdir and test_workspace:
        search_roots.append(Path(test_srcdir) / test_workspace)
    if test_srcdir:
        search_roots.append(Path(test_srcdir))

    for root in search_roots:
        resolved = candidate if candidate.is_absolute() else (root / candidate)
        if resolved.exists():
            return resolved.resolve()

    return None


def _resolve_target_path(target: str) -> Path:
    """Resolve an executable/file path from a bazel target label."""
    env_resolved = _resolve_from_env(target)
    if env_resolved is not None:
        return env_resolved

    _run(["bazel", "build", target])
    output = _run(["bazel", "cquery", "--output=files", target])
    candidates = [line.strip() for line in output.splitlines() if line.strip()]
    if not candidates:
        raise RuntimeError(f"No files produced by target: {target}")

    execution_root = Path(_run(["bazel", "info", "execution_root"]))
    for item in candidates:
        candidate = Path(item)
        if not candidate.is_absolute():
            candidate = execution_root / candidate
        if candidate.exists():
            return candidate

    raise RuntimeError(f"No existing artifact found for target: {target}. Candidates: {candidates!r}")


def get_binary_path(target: str) -> Path:
    """Compatibility helper used by daemon tests for bazel labels."""
    return _resolve_target_path(target)


def pgrep_cmdline_pattern(binary_path: str) -> str:
    """Build POSIX ERE pattern matching binary with optional arguments."""
    return rf"^{re.escape(binary_path)}([[:space:]]|$)"


def is_running(binary_path: str | Path) -> bool:
    result = subprocess.run(
        ["pgrep", "-f", pgrep_cmdline_pattern(str(binary_path))],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def first_pid(binary_path: str | Path) -> str | None:
    result = subprocess.run(
        ["pgrep", "-f", pgrep_cmdline_pattern(str(binary_path))],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    lines = [line for line in result.stdout.splitlines() if line]
    return lines[0] if lines else None


def wait_until(predicate, timeout_s: float, interval_s: float = 0.2) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(interval_s)
    return False


_SETCAP_CAPS = "cap_setuid,cap_setgid,cap_sys_nice+ep"


def _mount_nosuid(path: Path) -> bool:
    """Best-effort check whether `path` lives on a filesystem mounted `nosuid`.

    A `nosuid` mount silently strips file capabilities at exec time even when `setcap`
    itself reports success, which otherwise looks identical to "grant never happened"
    from the caller's point of view.
    """
    try:
        findmnt = shutil.which("findmnt")
        if findmnt is None:
            return False
        result = subprocess.run(
            [findmnt, "-n", "-o", "OPTIONS", "-T", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0 and "nosuid" in result.stdout
    except OSError:
        return False


def _grant_sandbox_capabilities(binary_path: Path) -> tuple[bool, str]:
    """Best-effort grant of the capabilities launch_manager needs to apply sandbox uid/gid
    and scheduling policy without running as root. Returns `(granted, reason)`: `granted`
    is a *verified* result (re-read via `getcap`, not just the setcap exit code) so tests
    can key off a real, established precondition instead of assuming root; `reason` is a
    human-readable diagnostic that is safe to surface directly in a pytest.skip() message.

    Requires CAP_SETFCAP to write the capability xattr, which a non-root test runner does not
    have by default. Set FIT_ENABLE_SETCAP=1 to opt into a `sudo -n setcap` attempt, backed by
    a passwordless sudoers rule scoped to the setcap binary (e.g. `<user> ALL=(root) NOPASSWD:
    /usr/sbin/setcap`, with NO trailing arguments pinned — the target path is a fresh tmp_path
    on every test run, so a rule that also pins the argument list will never match). Without
    the flag, only a plain (non-sudo) setcap is tried, which only succeeds if the runner is
    already root.

    Under `bazel test`, undeclared env vars (like FIT_ENABLE_SETCAP) do not reach the test
    process unless passed via `--test_env=FIT_ENABLE_SETCAP=1` (NOT `--action_env`, which only
    affects build actions). `bazel run` inherits the invoking shell's environment directly, so
    `--action_env` is a no-op for this variable there; it is only needed to force a rebuild
    when it affects action inputs, which it does not here.
    """
    if shutil.which("setcap") is None:
        return False, "setcap binary not found on PATH"

    setcap_enabled = os.environ.get("FIT_ENABLE_SETCAP") == "1"
    attempts: list[tuple[list[str], str]] = [
        (["setcap", _SETCAP_CAPS, str(binary_path)], "plain setcap (requires running as root)")
    ]
    if setcap_enabled:
        if shutil.which("sudo") is None:
            attempts.append(([], "FIT_ENABLE_SETCAP=1 set but 'sudo' not found on PATH"))
        else:
            attempts.insert(
                0,
                (["sudo", "-n", "setcap", _SETCAP_CAPS, str(binary_path)], "sudo -n setcap"),
            )
    else:
        attempts.append(([], "FIT_ENABLE_SETCAP not set to '1'; skipping sudo setcap attempt"))

    failures: list[str] = []
    for cmd, label in attempts:
        if not cmd:
            failures.append(label)
            continue
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            failures.append(
                f"{label} failed (rc={result.returncode}): "
                f"{result.stderr.strip() or result.stdout.strip() or '<no output>'}"
            )
            continue

        # setcap can report success while the kernel still drops the capability at exec
        # time (e.g. the binary lives on a filesystem mounted `nosuid`). Verify by reading
        # the xattr back instead of trusting the exit code.
        getcap = shutil.which("getcap")
        if getcap is not None:
            verify = subprocess.run([getcap, str(binary_path)], capture_output=True, text=True, check=False)
            if "cap_setuid" not in verify.stdout or "cap_setgid" not in verify.stdout:
                nosuid_hint = " (path is on a 'nosuid' mount)" if _mount_nosuid(binary_path) else ""
                failures.append(
                    f"{label} reported success but getcap did not confirm the capabilities"
                    f"{nosuid_hint}: {verify.stdout.strip() or '<empty>'}"
                )
                continue

        return True, f"granted via {label}"

    return False, "; ".join(failures) if failures else "no grant attempt produced a result"


def _wait_for_apps(apps: dict[str, Path], timeout_s: float = 8.0, interval_s: float = 0.2) -> bool:
    return wait_until(lambda: all(is_running(path) for path in apps.values()), timeout_s, interval_s)


_RUNTIME_ROOT_LOCK_PATH = Path("/tmp/lifecycle_fit.lock")
_RUNTIME_ROOT_LOCK_TIMEOUT_S = 120.0


def _acquire_runtime_root_lock(timeout_s: float = _RUNTIME_ROOT_LOCK_TIMEOUT_S):
    """Acquire the exclusive lock guarding the shared /tmp/lifecycle_fit runtime_root.

    Polls with a non-blocking flock instead of blocking indefinitely: an unbounded
    `LOCK_EX` would hang forever (and silently eat the whole CI job's timeout budget)
    if the lock is ever legitimately held longer than expected, giving no diagnostic
    signal about what's actually stuck. No lifecycle test suite should need this lock
    for anywhere near `timeout_s`, so failing loudly here is strictly more useful than
    an indefinite wait.
    """
    lock_file = _RUNTIME_ROOT_LOCK_PATH.open("w", encoding="utf-8")
    deadline = time.time() + timeout_s
    while True:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return lock_file
        except OSError:
            if time.time() >= deadline:
                lock_file.close()
                raise RuntimeError(
                    f"Could not acquire {_RUNTIME_ROOT_LOCK_PATH} within {timeout_s}s; "
                    "another lifecycle daemon run appears to be holding it. If no other "
                    "lifecycle test is genuinely running, a stale process may be stuck "
                    "holding this lock."
                ) from None
            time.sleep(0.5)


@dataclass
class ManagedDaemon:
    """A subprocess wrapper with line-buffered output collection."""

    process: subprocess.Popen[str]
    _lines: list[str]
    _thread: threading.Thread

    def is_running(self) -> bool:
        return self.process.poll() is None

    def pid(self) -> int:
        return self.process.pid

    def stop(self) -> None:
        if self.is_running():
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            deadline = time.time() + 5.0
            while self.is_running() and time.time() < deadline:
                time.sleep(0.1)
            if self.is_running():
                os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                self.process.wait(timeout=5)
        self._thread.join(timeout=1)

    def get_logs(self) -> str:
        return "\n".join(self._lines)


def start_launch_manager_daemon(
    tmp_path_factory: pytest.TempPathFactory,
    blocked_apps: frozenset[str] = frozenset(),
    wait_for_apps: bool = True,
) -> dict[str, Any]:
    """Start a real launch_manager process with generated flatbuffer config.

    `blocked_apps` names ("rust"/"cpp") are copied into place but left
    non-executable, so launch_manager cannot start them until the caller
    chmod's them back to 0o755. Used to exercise the dependency-gating
    negative path: assert the dependent app stays down while its
    dependency is withheld, then unblock and assert it starts.

    Relies on tags = ["exclusive"] on the bazel test targets that use this:
    only one lifecycle daemon (sharing the runtime_root/lock below) may run
    on the machine at a time, so it is safe for a test to manage its own
    instance here rather than the shared `launch_manager_daemon` fixture.
    """

    lock_file = _acquire_runtime_root_lock()

    work_dir = tmp_path_factory.mktemp("lm-daemon")
    etc_dir = work_dir / "etc"
    etc_dir.mkdir(parents=True, exist_ok=True)

    runtime_root = Path("/tmp/lifecycle_fit")
    if runtime_root.exists():
        shutil.rmtree(runtime_root)
    bin_dir = runtime_root / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    launch_manager = _resolve_target_path("@score_lifecycle_health//score/launch_manager:launch_manager")
    rust_supervised = _resolve_target_path("@score_lifecycle_health//examples/rust_supervised_app:rust_supervised_app")
    cpp_supervised = _resolve_target_path("@score_lifecycle_health//examples/cpp_supervised_app:cpp_supervised_app")

    config_artifact = _resolve_target_path("//feature_integration_tests/configs:lifecycle_daemon_config")

    lm_dst = work_dir / "launch_manager"
    shutil.copy2(launch_manager, lm_dst)
    lm_dst.chmod(0o755)
    sandbox_privileged, sandbox_privileged_reason = _grant_sandbox_capabilities(lm_dst)

    for key, src in (("rust", rust_supervised), ("cpp", cpp_supervised)):
        dst = bin_dir / src.name
        shutil.copy2(src, dst)
        dst.chmod(0o000 if key in blocked_apps else 0o755)

    if config_artifact.is_dir():
        for item in config_artifact.iterdir():
            if item.is_file():
                shutil.copy2(item, etc_dir / item.name)
    else:
        if config_artifact.name.endswith(".bin"):
            shutil.copy2(config_artifact, etc_dir / "lm_demo.bin")
        else:
            raise RuntimeError(f"Unexpected lifecycle daemon config artifact: {config_artifact}")

    env = os.environ.copy()
    env.setdefault("ECUCFG_ENV_VAR_ROOTFOLDER", str(etc_dir))

    lines: list[str] = []
    process = subprocess.Popen(
        [str(lm_dst)],
        cwd=work_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )

    def _collect_output() -> None:
        assert process.stdout is not None
        for line in process.stdout:
            line = line.rstrip("\n")
            if line:
                lines.append(line)

    thread = threading.Thread(target=_collect_output, daemon=True)
    thread.start()

    daemon = ManagedDaemon(process=process, _lines=lines, _thread=thread)

    # Give startup a chance to complete and fail early if config is broken.
    time.sleep(1.0)
    if not daemon.is_running():
        logs = daemon.get_logs()
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        lock_file.close()
        pytest.skip(f"launch_manager failed to start in this environment. Logs:\n{logs}")

    apps = {
        "rust": bin_dir / "rust_supervised_app",
        "cpp": bin_dir / "cpp_supervised_app",
    }
    if wait_for_apps and not _wait_for_apps({k: v for k, v in apps.items() if k not in blocked_apps}):
        process_snapshot = _run(["ps", "-eo", "pid,args"])
        daemon.stop()
        shutil.rmtree(runtime_root, ignore_errors=True)
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        lock_file.close()
        pytest.fail(
            "Launch Manager did not bring supervised apps to running state within timeout.\n"
            f"Expected apps: {apps}\n"
            f"Daemon logs:\n{daemon.get_logs()}\n"
            f"Process snapshot:\n{process_snapshot}"
        )

    return {
        "daemon": daemon,
        "work_dir": work_dir,
        "bin_dir": bin_dir,
        "apps": apps,
        "sandbox_privileged": sandbox_privileged,
        "sandbox_privileged_reason": sandbox_privileged_reason,
        "runtime_root": runtime_root,
        "lock_file": lock_file,
    }


def stop_launch_manager_daemon(daemon_info: dict[str, Any]) -> None:
    """Tear down a daemon started by `start_launch_manager_daemon`."""
    daemon_info["daemon"].stop()
    shutil.rmtree(daemon_info["runtime_root"], ignore_errors=True)
    lock_file = daemon_info["lock_file"]
    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
    lock_file.close()


@pytest.fixture(scope="class")
def launch_manager_daemon(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    """Start a real launch_manager process with generated flatbuffer config."""
    daemon_info = start_launch_manager_daemon(tmp_path_factory)
    try:
        yield daemon_info
    finally:
        stop_launch_manager_daemon(daemon_info)
