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

import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
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
    "@score_lifecycle_health//examples/control_application:lmcontrol": "FIT_LMCONTROL_PATH",
    "//feature_integration_tests/configs:lifecycle_daemon_config.json": "FIT_LIFECYCLE_DAEMON_CONFIG_PATH",
    "//feature_integration_tests/configs:lifecycle_daemon_parallel_launch_config.json": (
        "FIT_LIFECYCLE_PARALLEL_LAUNCH_CONFIG_PATH"
    ),
    "//feature_integration_tests/test_cases/support_apps/flaky_startup_app:flaky_startup_app": (
        "FIT_FLAKY_STARTUP_APP_PATH"
    ),
    "//feature_integration_tests/configs:lifecycle_daemon_retry_recovers_config.json": (
        "FIT_LIFECYCLE_RETRY_RECOVERS_CONFIG_PATH"
    ),
    "//feature_integration_tests/configs:lifecycle_daemon_retry_exhausts_config.json": (
        "FIT_LIFECYCLE_RETRY_EXHAUSTS_CONFIG_PATH"
    ),
    "@score_lifecycle_health//scripts/config_mapping:lifecycle_config": "FIT_LIFECYCLE_CONFIG_TOOL_PATH",
    "@score_lifecycle_health//score/launch_manager/src/daemon/src/configuration/config_schema:launch_manager.schema.json": "FIT_LIFECYCLE_CONFIG_SCHEMA_PATH",
    "@score_lifecycle_health//score/launch_manager/src/daemon/src/configuration/config_schema:lm_flatcfg.fbs": "FIT_LIFECYCLE_LM_SCHEMA_PATH",
    "@score_lifecycle_health//score/launch_manager/src/daemon/src/alive_monitor/config:hm_flatcfg.fbs": "FIT_LIFECYCLE_HM_SCHEMA_PATH",
    "@score_lifecycle_health//score/launch_manager/src/daemon/src/alive_monitor/config:hmcore_flatcfg.fbs": "FIT_LIFECYCLE_HMCORE_SCHEMA_PATH",
    "@flatbuffers//:flatc": "FIT_FLATC_PATH",
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


def signal_process(pid: str, sig: str, *, sandbox_privileged: bool) -> tuple[bool, str]:
    """Send `sig` (e.g. "-9", "-STOP", "-CONT") to `pid`, escalating via sudo if needed.

    Under sandbox capabilities, supervised apps run as the configured sandbox uid/gid,
    not the runner's own uid, so a plain `kill` fails. Falls back to `sudo -n kill` when
    `FIT_ENABLE_SETCAP=1` (same sudoers scope as `_grant_sandbox_capabilities`).
    """
    attempts: list[list[str]] = [["kill", sig, pid]]
    if sandbox_privileged and os.environ.get("FIT_ENABLE_SETCAP") == "1" and shutil.which("sudo") is not None:
        attempts.append(["sudo", "-n", "kill", sig, pid])

    failures: list[str] = []
    for cmd in attempts:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return True, f"sent via {' '.join(cmd)}"
        failures.append(f"{' '.join(cmd)} failed (rc={result.returncode}): {result.stderr.strip() or '<no output>'}")

    return False, "; ".join(failures)


def _wait_for_apps(apps: dict[str, Path], timeout_s: float = 8.0, interval_s: float = 0.2) -> bool:
    return wait_until(lambda: all(is_running(path) for path in apps.values()), timeout_s, interval_s)


def _tmpdir_root() -> Path:
    """Return the writable temp root for the current test invocation.

    Bazel sets `TEST_TMPDIR` to a fresh directory per test. Outside Bazel, fall
    back to the system temp dir; callers create unique children in either case.
    """
    value = os.environ.get("TEST_TMPDIR")
    if value:
        return Path(value)
    return Path(tempfile.gettempdir())


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

    def get_log_offset(self) -> int:
        """Return a cursor into the current log content, for use with `get_logs_since`."""
        return len(self._lines)

    def get_logs_since(self, offset: int) -> str:
        """Return only log content collected after a prior `get_log_offset()` call."""
        return "\n".join(self._lines[offset:])


def _cleanup_runtime_root(runtime_root: Path) -> None:
    """Remove a daemon's uniquely allocated runtime directory."""
    shutil.rmtree(runtime_root, ignore_errors=True)


def _generate_runtime_config(config_template: str, runtime_root: Path, etc_dir: Path) -> None:
    """Render and serialize an isolated launch-manager config for one daemon."""
    config = json.loads(_resolve_target_path(config_template).read_text(encoding="utf-8"))
    config["defaults"]["deployment_config"]["bin_dir"] = str(runtime_root / "bin")

    for component in config["components"].values():
        arguments = component["component_properties"].get("process_arguments", [])
        component["component_properties"]["process_arguments"] = [
            str(runtime_root / "flaky_startup_app.counter")
            if argument == "__FIT_RUNTIME_ROOT__/flaky_startup_app.counter"
            else argument
            for argument in arguments
        ]

    rendered_config = etc_dir / "lifecycle_config.json"
    rendered_config.write_text(json.dumps(config), encoding="utf-8")
    generated_dir = etc_dir / "generated"
    generated_dir.mkdir()
    config_tool = _resolve_target_path("@score_lifecycle_health//scripts/config_mapping:lifecycle_config")
    config_schema = _resolve_target_path(
        "@score_lifecycle_health//score/launch_manager/src/daemon/src/configuration/config_schema:launch_manager.schema.json"
    )
    subprocess.run(
        [str(config_tool), str(rendered_config), "--schema", str(config_schema), "-o", str(generated_dir)],
        capture_output=True,
        text=True,
        check=True,
    )

    flatc = _resolve_target_path("@flatbuffers//:flatc")
    buffers = (
        (
            "lm_demo",
            "@score_lifecycle_health//score/launch_manager/src/daemon/src/configuration/config_schema:lm_flatcfg.fbs",
        ),
        ("hm_demo", "@score_lifecycle_health//score/launch_manager/src/daemon/src/alive_monitor/config:hm_flatcfg.fbs"),
        (
            "hmcore",
            "@score_lifecycle_health//score/launch_manager/src/daemon/src/alive_monitor/config:hmcore_flatcfg.fbs",
        ),
    )
    for name, schema_target in buffers:
        subprocess.run(
            [
                str(flatc),
                "--binary",
                "--strict-json",
                "-o",
                str(etc_dir),
                str(_resolve_target_path(schema_target)),
                str(generated_dir / f"{name}.json"),
            ],
            capture_output=True,
            text=True,
            check=True,
        )


def start_launch_manager_daemon(
    tmp_path_factory: pytest.TempPathFactory,
    blocked_apps: frozenset[str] = frozenset(),
    wait_for_apps: bool = True,
    config_template: str = "//feature_integration_tests/configs:lifecycle_daemon_config.json",
) -> dict[str, Any]:
    """Start a real launch_manager process with generated flatbuffer config.

    `blocked_apps` names ("rust"/"cpp") are copied into place but left
    non-executable, so launch_manager cannot start them until the caller
    chmod's them back to 0o755. Used to exercise the dependency-gating
    negative path: assert the dependent app stays down while its
    dependency is withheld, then unblock and assert it starts - and, with
    an independent config (no depends_on between the two apps), the inverse:
    assert the other app starts anyway, proving it isn't gated at all.

    Each invocation receives its own directory beneath `TEST_TMPDIR`, so it can
    run concurrently with the class-scoped fixture or another Bazel test process.
    """

    runtime_root = Path(tempfile.mkdtemp(prefix="lifecycle_fit-", dir=_tmpdir_root()))
    try:
        work_dir = tmp_path_factory.mktemp("lm-daemon")
        etc_dir = work_dir / "etc"
        etc_dir.mkdir(parents=True, exist_ok=True)

        bin_dir = runtime_root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)

        launch_manager = _resolve_target_path("@score_lifecycle_health//score/launch_manager:launch_manager")
        rust_supervised = _resolve_target_path(
            "@score_lifecycle_health//examples/rust_supervised_app:rust_supervised_app"
        )
        cpp_supervised = _resolve_target_path("@score_lifecycle_health//examples/cpp_supervised_app:cpp_supervised_app")

        lm_dst = work_dir / "launch_manager"
        shutil.copy2(launch_manager, lm_dst)
        lm_dst.chmod(0o755)
        sandbox_privileged, sandbox_privileged_reason = _grant_sandbox_capabilities(lm_dst)

        try:
            lm_ctl_binary = _resolve_target_path("@score_lifecycle_health//examples/control_application:lmcontrol")
        except RuntimeError:
            lm_ctl_binary = None

        for key, src in (("rust", rust_supervised), ("cpp", cpp_supervised)):
            dst = bin_dir / src.name
            shutil.copy2(src, dst)
            dst.chmod(0o000 if key in blocked_apps else 0o755)

        _generate_runtime_config(config_template, runtime_root, etc_dir)

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
            pytest.skip(f"launch_manager failed to start in this environment. Logs:\n{logs}")

        apps = {
            "rust": bin_dir / "rust_supervised_app",
            "cpp": bin_dir / "cpp_supervised_app",
        }
        if wait_for_apps and not _wait_for_apps({k: v for k, v in apps.items() if k not in blocked_apps}):
            process_snapshot = _run(["ps", "-eo", "pid,args"])
            daemon.stop()
            _cleanup_runtime_root(runtime_root)
            pytest.fail(
                "Launch Manager did not bring supervised apps to running state within timeout.\n"
                f"Expected apps: {apps}\n"
                f"Daemon logs:\n{daemon.get_logs()}\n"
                f"Process snapshot:\n{process_snapshot}"
            )
    except BaseException:
        _cleanup_runtime_root(runtime_root)
        raise

    return {
        "daemon": daemon,
        "work_dir": work_dir,
        "bin_dir": bin_dir,
        "apps": apps,
        "sandbox_privileged": sandbox_privileged,
        "sandbox_privileged_reason": sandbox_privileged_reason,
        "runtime_root": runtime_root,
        "lm_ctl_binary": lm_ctl_binary,
    }


def start_flaky_retry_daemon(
    tmp_path_factory: pytest.TempPathFactory,
    config_template: str,
    crashes_before_success: int,
) -> dict[str, Any]:
    """Start launch_manager against a single-component retry config.

    Drives `flaky_startup_app` (see support_apps/flaky_startup_app/main.cpp), which
    aborts on its first `crashes_before_success` startup attempts and stays running
    from then on, so `ready_recovery_action.restart.number_of_attempts` can be
    exercised deterministically instead of relying on a real, racy startup failure.
    Does not wait for the app to reach Running: whether it ever does is exactly
    what the calling test is checking.
    """
    runtime_root = Path(tempfile.mkdtemp(prefix="lifecycle_fit_retries-", dir=_tmpdir_root()))
    try:
        work_dir = tmp_path_factory.mktemp("lm-retry-daemon")
        etc_dir = work_dir / "etc"
        etc_dir.mkdir(parents=True, exist_ok=True)

        bin_dir = runtime_root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)

        launch_manager = _resolve_target_path("@score_lifecycle_health//score/launch_manager:launch_manager")
        flaky_app = _resolve_target_path(
            "//feature_integration_tests/test_cases/support_apps/flaky_startup_app:flaky_startup_app"
        )
        lm_dst = work_dir / "launch_manager"
        shutil.copy2(launch_manager, lm_dst)
        lm_dst.chmod(0o755)

        app_dst = bin_dir / "flaky_startup_app"
        shutil.copy2(flaky_app, app_dst)
        app_dst.chmod(0o755)

        counter_path = runtime_root / "flaky_startup_app.counter"
        if counter_path.exists():
            counter_path.unlink()

        _generate_runtime_config(config_template, runtime_root, etc_dir)

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

        time.sleep(1.0)
        if not daemon.is_running():
            logs = daemon.get_logs()
            pytest.skip(f"launch_manager failed to start in this environment. Logs:\n{logs}")
    except BaseException:
        _cleanup_runtime_root(runtime_root)
        raise

    return {
        "daemon": daemon,
        "work_dir": work_dir,
        "bin_dir": bin_dir,
        "app_path": app_dst,
        "counter_path": counter_path,
        "crashes_before_success": crashes_before_success,
        "runtime_root": runtime_root,
    }


def stop_flaky_retry_daemon(daemon_info: dict[str, Any]) -> None:
    """Tear down a daemon started by `start_flaky_retry_daemon`."""
    daemon_info["daemon"].stop()
    subprocess.run(
        ["pkill", "-f", pgrep_cmdline_pattern(str(daemon_info["app_path"]))],
        capture_output=True,
        text=True,
        check=False,
    )
    _cleanup_runtime_root(daemon_info["runtime_root"])


def read_retry_attempt_count(counter_path: Path) -> int:
    """Read flaky_startup_app's persisted attempt counter; 0 if it hasn't run yet."""
    try:
        return int(counter_path.read_text().strip())
    except (FileNotFoundError, ValueError):
        return 0


def stop_launch_manager_daemon(daemon_info: dict[str, Any]) -> None:
    """Tear down a daemon started by `start_launch_manager_daemon`."""
    daemon_info["daemon"].stop()
    _cleanup_runtime_root(daemon_info["runtime_root"])


@pytest.fixture(scope="class")
def launch_manager_daemon(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    """Start a real launch_manager process with generated flatbuffer config."""
    daemon_info = start_launch_manager_daemon(tmp_path_factory)
    try:
        yield daemon_info
    finally:
        stop_launch_manager_daemon(daemon_info)
