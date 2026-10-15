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

import contextlib
import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
import threading
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

_LAUNCH_MANAGER = "@score_lifecycle//score/launch_manager"
_LMCONTROL = "@score_lifecycle//examples/control_application:lmcontrol"
CONTROL_DAEMON = "@score_lifecycle//examples/control_application:control_daemon"
LIFECYCLE_PERSISTENCY_CONFIG = "//feature_integration_tests/configs:lifecycle_persistency_config.json"

_TARGET_ENV_MAP = {
    _LAUNCH_MANAGER: "FIT_LAUNCH_MANAGER_PATH",
    "@score_lifecycle//examples/rust_supervised_app": "FIT_RUST_SUPERVISED_APP_PATH",
    "@score_lifecycle//examples/cpp_supervised_app": "FIT_CPP_SUPERVISED_APP_PATH",
    _LMCONTROL: "FIT_LMCONTROL_PATH",
    CONTROL_DAEMON: "FIT_CONTROL_DAEMON_PATH",
    LIFECYCLE_PERSISTENCY_CONFIG: "FIT_LIFECYCLE_PERSISTENCY_CONFIG_PATH",
    "@score_lifecycle//scripts/config_mapping:lifecycle_config": "FIT_LIFECYCLE_CONFIG_TOOL_PATH",
    "@score_lifecycle//score/launch_manager/src/daemon/src/configuration/config_schema:launch_manager.schema.json": "FIT_LIFECYCLE_CONFIG_SCHEMA_PATH",
    "@score_lifecycle//score/launch_manager/src/daemon/src/configuration:lm_flatcfg_fbs": "FIT_LIFECYCLE_LM_SCHEMA_PATH",
    "@flatbuffers//:flatc": "FIT_FLATC_PATH",
}


def resolve_target_path(target: str) -> Path:
    """Resolve a Bazel label to its runfile via the env var the BUILD target sets.

    There is no `bazel build`/`cquery` fallback: nested bazel invocations fail
    inside the `bazel test` sandbox, so a missing env var or runfile is a BUILD
    wiring error and fails loudly.
    """
    env_var = _TARGET_ENV_MAP.get(target)
    if env_var is None:
        raise RuntimeError(f"No env var mapped for target {target}; add it to _TARGET_ENV_MAP.")

    raw_path = os.environ.get(env_var)
    if not raw_path:
        raise RuntimeError(f"{env_var} is not set; declare {target} in the test target's `data` and `env`.")

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

    raise RuntimeError(f"{env_var}={raw_path} does not exist under any of {search_roots}.")


def pgrep_cmdline_pattern(binary_path: str) -> str:
    """Build POSIX ERE pattern matching binary with optional arguments."""
    return rf"^{re.escape(binary_path)}([[:space:]]|$)"


def _pids(binary_path: str | Path) -> list[str]:
    result = subprocess.run(
        ["pgrep", "-f", pgrep_cmdline_pattern(str(binary_path))],
        capture_output=True,
        text=True,
        check=False,
    )
    return [line for line in result.stdout.splitlines() if line] if result.returncode == 0 else []


def is_running(binary_path: str | Path) -> bool:
    return bool(_pids(binary_path))


def wait_until(predicate, timeout_s: float, interval_s: float = 0.2) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(interval_s)
    return False


def _run_tool(cmd: list[str]) -> None:
    """Run a build tool, raising with its full output on failure."""
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed (rc={result.returncode}): {' '.join(cmd)}\n"
            f"stdout:\n{result.stdout.strip()}\nstderr:\n{result.stderr.strip()}"
        )


# cap_kill lets launch_manager terminate apps it started under another uid (run-target switches).
_SETCAP_CAPS = "cap_setuid,cap_setgid,cap_sys_nice,cap_kill+ep"
_KILL_CAPS = "cap_kill+ep"

# Sandbox uid used for `__FIT_SANDBOX_UID__` when capabilities are granted. Must differ from the
# runner's uid, else an applied identity cannot be told from an inherited one.
SANDBOX_UID = 65533

# Sandbox id placeholders in config templates. `__FIT_SANDBOX_UID__` becomes SANDBOX_UID when
# launch_manager may setuid() and the runner's uid otherwise; `__FIT_RUNNER_UID__` is always the
# runner's uid (for components the runner must reach, e.g. through a control socket). The gid is
# always the runner's, so the runner can read files the apps write.
_SANDBOX_UID_PLACEHOLDER = "__FIT_SANDBOX_UID__"
_RUNNER_UID_PLACEHOLDER = "__FIT_RUNNER_UID__"
_RUNNER_GID_PLACEHOLDER = "__FIT_RUNNER_GID__"


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


def _grant_capabilities(binary_path: Path, caps: str, required: tuple[str, ...]) -> tuple[bool, str]:
    """Best-effort grant of file capabilities `caps` to `binary_path`.

    Returns `(granted, reason)`: `granted` is a *verified* result (every name in
    `required` re-read via `getcap`, not just the setcap exit code); `reason` is a
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
    affects build actions).
    """
    if shutil.which("setcap") is None:
        return False, "setcap binary not found on PATH"

    attempts: list[tuple[list[str], str]] = [
        (["setcap", caps, str(binary_path)], "plain setcap (requires running as root)")
    ]
    if os.environ.get("FIT_ENABLE_SETCAP") == "1":
        if shutil.which("sudo") is None:
            attempts.append(([], "FIT_ENABLE_SETCAP=1 set but 'sudo' not found on PATH"))
        else:
            attempts.insert(0, (["sudo", "-n", "setcap", caps, str(binary_path)], "sudo -n setcap"))
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
            if not all(cap in verify.stdout for cap in required):
                nosuid_hint = " (path is on a 'nosuid' mount)" if _mount_nosuid(binary_path) else ""
                failures.append(
                    f"{label} reported success but getcap did not confirm the capabilities"
                    f"{nosuid_hint}: {verify.stdout.strip() or '<empty>'}"
                )
                continue

        return True, f"granted via {label}"

    return False, "; ".join(failures) if failures else "no grant attempt produced a result"


def _stage_privileged_kill(runtime_root: Path) -> tuple[Path | None, str]:
    """Stage an owner-only copy of `kill` carrying `cap_kill`.

    Supervised apps run as the configured sandbox uid once launch_manager holds
    `cap_setuid`, so the runner's own `kill` cannot signal them. The sudoers rule
    behind FIT_ENABLE_SETCAP only covers `setcap`, so `sudo -n kill` is not an
    option; the copy is granted through the same `setcap` path instead. It lives
    inside `runtime_root` and is deleted with it in `_teardown`.
    """
    system_kill = shutil.which("kill")
    if system_kill is None:
        return None, "'kill' binary not found on PATH"
    priv_dir = runtime_root / "priv"
    priv_dir.mkdir(mode=0o700)
    kill_copy = priv_dir / "kill"
    shutil.copy2(system_kill, kill_copy)
    kill_copy.chmod(0o700)
    granted, reason = _grant_capabilities(kill_copy, _KILL_CAPS, required=("cap_kill",))
    if not granted:
        kill_copy.unlink(missing_ok=True)
        return None, f"cap_kill grant for kill copy failed: {reason}"
    return kill_copy, reason


def signal_process(pid: str, sig: str, *, kill_binary: Path | None = None) -> tuple[bool, str]:
    """Send `sig` (e.g. "-9", "-STOP", "-CONT") to `pid`.

    Tries the runner's own `kill` first, then the staged `cap_kill` copy
    (`daemon_info["kill_binary"]`), which is set only when sandbox
    capabilities were granted and apps may run under another uid.
    """
    attempts: list[list[str]] = [["kill", sig, pid]]
    if kill_binary is not None:
        attempts.append([str(kill_binary), sig, pid])

    failures: list[str] = []
    for cmd in attempts:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return True, f"sent via {' '.join(cmd)}"
        failures.append(f"{' '.join(cmd)} failed (rc={result.returncode}): {result.stderr.strip() or '<no output>'}")

    return False, "; ".join(failures)


def find_descendant_pid(root_pid: int, process_name: str) -> int | None:
    """Return the PID of a descendant of `root_pid` whose command line contains `process_name`."""
    children_by_parent: dict[int, list[int]] = {}
    try:
        proc_entries = list(Path("/proc").iterdir())
    except OSError:
        return None
    for entry in proc_entries:
        if not entry.name.isdigit():
            continue
        try:
            status = (entry / "status").read_text()
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue  # Process disappeared or cannot be inspected.
        for line in status.splitlines():
            if line.startswith("PPid:"):
                children_by_parent.setdefault(int(line.split()[1]), []).append(int(entry.name))
                break

    pending = list(children_by_parent.get(root_pid, []))
    while pending:
        pid = pending.pop()
        pending.extend(children_by_parent.get(pid, []))
        try:
            # /proc/<pid>/cmdline is NUL-separated.
            command = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue  # Process terminated or is inaccessible.
        if process_name in command:
            return pid
    return None


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

    def _signal_group(self, sig: signal.Signals) -> None:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(os.getpgid(self.process.pid), sig)

    def stop(self) -> None:
        """Signal the daemon's process group and wait for the daemon to exit.

        Supervised apps `setpgid()` into their own groups, so this does not reach
        them; `_teardown` kills them separately before `close_output()`.
        """
        if not self.is_running():
            return
        self._signal_group(signal.SIGTERM)
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._signal_group(signal.SIGKILL)
            self.process.wait(timeout=5)

    def close_output(self) -> None:
        """Join the reader thread and close the pipe.

        Supervised apps inherit the daemon's stdout, so the reader only sees EOF
        once they are dead too; call this after they have been killed.
        """
        self._thread.join(timeout=2)
        if self.process.stdout is not None:
            self.process.stdout.close()

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


def _kill_apps(app_paths: Iterable[Path], kill_binary: Path | None) -> None:
    for app_path in app_paths:
        for pid in _pids(app_path):
            signal_process(pid, "-9", kill_binary=kill_binary)


def _teardown(
    daemon: ManagedDaemon | None,
    app_paths: Iterable[Path],
    runtime_root: Path,
    kill_binary: Path | None,
) -> None:
    """Stop daemon, kill apps, close output, remove runtime root; each step runs even if one raises."""
    try:
        if daemon is not None:
            daemon.stop()
    finally:
        try:
            _kill_apps(app_paths, kill_binary)
        finally:
            try:
                if daemon is not None:
                    daemon.close_output()
            finally:
                _cleanup_runtime_root(runtime_root)


def _generate_runtime_config(
    runtime_root: Path,
    etc_dir: Path,
    config_target: str,
    render: Callable[[dict[str, Any], Path], None] | None,
    *,
    sandbox_privileged: bool,
) -> Path:
    """Render and serialize an isolated launch-manager config for one daemon.

    Resolves the sandbox id placeholders (see `_SANDBOX_UID_PLACEHOLDER`). When
    `sandbox_privileged`, `runtime_root` is opened to the runner's group (0750)
    so apps running as `SANDBOX_UID` can reach `bin_dir`. Limitation: the gid
    is the runner's own, so a gid check cannot prove setgid() was applied.
    `render(config, runtime_root)` runs afterwards and may fill further
    runtime-specific values before the config is validated and serialized.
    """
    config = json.loads(resolve_target_path(config_target).read_text(encoding="utf-8"))
    config["defaults"]["deployment_config"]["bin_dir"] = str(runtime_root / "bin")
    ids = {
        _SANDBOX_UID_PLACEHOLDER: SANDBOX_UID if sandbox_privileged else os.getuid(),
        _RUNNER_UID_PLACEHOLDER: os.getuid(),
        _RUNNER_GID_PLACEHOLDER: os.getgid(),
    }
    sandboxes = [config["defaults"]["deployment_config"].get("sandbox")]
    sandboxes += [c.get("deployment_config", {}).get("sandbox") for c in config["components"].values()]
    for sandbox in filter(None, sandboxes):
        for field in ("uid", "gid"):
            if sandbox.get(field) in ids:
                sandbox[field] = ids[sandbox[field]]
    if sandbox_privileged:
        runtime_root.chmod(0o750)
    if render is not None:
        render(config, runtime_root)

    rendered_config = etc_dir / "lifecycle_config.json"
    rendered_config.write_text(json.dumps(config), encoding="utf-8")
    generated_dir = etc_dir / "generated"
    generated_dir.mkdir()
    config_tool = resolve_target_path("@score_lifecycle//scripts/config_mapping:lifecycle_config")
    config_schema = resolve_target_path(
        "@score_lifecycle//score/launch_manager/src/daemon/src/configuration/config_schema:launch_manager.schema.json"
    )
    _run_tool([str(config_tool), str(rendered_config), "--schema", str(config_schema), "-o", str(generated_dir)])

    flatc = resolve_target_path("@flatbuffers//:flatc")
    lm_schema = resolve_target_path(
        "@score_lifecycle//score/launch_manager/src/daemon/src/configuration:lm_flatcfg_fbs"
    )
    name = f"{rendered_config.stem}_gen"
    _run_tool(
        [
            str(flatc),
            "--binary",
            "--strict-json",
            "-o",
            str(etc_dir),
            str(lm_schema),
            str(generated_dir / f"{name}.json"),
        ]
    )
    return etc_dir / f"{name}.bin"


def _spawn_daemon(
    lm_binary: Path, config_path: Path, work_dir: Path, etc_dir: Path, log_config: Path | None
) -> ManagedDaemon:
    """Start launch_manager and wait briefly for startup.

    Stops its own daemon and closes its output if the startup wait is
    interrupted, since the caller only receives the handle on return. The
    caller's teardown kills the apps; the reader thread is joined with a
    timeout, so an app still holding the pipe cannot block here.
    """
    env = os.environ.copy()
    env.setdefault("ECUCFG_ENV_VAR_ROOTFOLDER", str(etc_dir))
    if log_config is not None:
        env["MW_LOG_CONFIG_FILE"] = str(log_config)

    lines: list[str] = []
    process = subprocess.Popen(
        [str(lm_binary), "-c", str(config_path)],
        cwd=work_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )

    def _collect_output() -> None:
        assert process.stdout is not None
        try:
            for line in process.stdout:
                line = line.rstrip("\n")
                if line:
                    lines.append(line)
        except ValueError:
            pass  # Pipe closed by close_output().

    thread = threading.Thread(target=_collect_output, daemon=True)
    thread.start()
    daemon = ManagedDaemon(process=process, _lines=lines, _thread=thread)

    try:
        time.sleep(1.0)
    except BaseException:
        try:
            daemon.stop()
        finally:
            daemon.close_output()
        raise
    return daemon


def start_launch_manager_daemon(
    tmp_path_factory: pytest.TempPathFactory,
    *,
    config_target: str,
    binaries: dict[str, Path],
    ready_apps: Iterable[str] | None = None,
    render: Callable[[dict[str, Any], Path], None] | None = None,
    log_level: str | None = None,
    control_client: bool = False,
) -> dict[str, Any]:
    """Start a real launch_manager process with generated flatbuffer config.

    Each invocation receives its own directory beneath `TEST_TMPDIR`. Any
    failure after allocation tears down everything started so far. A daemon
    that dies at startup fails the test: launch_manager is a declared Bazel
    `data` dependency, so there is no legitimate "unavailable" case to skip.

    `binaries` maps a `bin_dir` file name to its source; `ready_apps` names
    those that must be running after startup (default: all). `log_level`
    (e.g. "kDebug") writes an mw::log console config for launch_manager;
    without it only warnings are printed. `control_client` resolves `lmcontrol`
    into `lm_ctl_binary` (None otherwise), so only targets that drive the
    control interface need it in `data`.
    """
    runtime_root = Path(tempfile.mkdtemp(prefix="lifecycle_fit-", dir=_tmpdir_root()))
    bin_dir = runtime_root / "bin"
    apps = {name: bin_dir / name for name in binaries}
    daemon: ManagedDaemon | None = None
    kill_binary: Path | None = None
    try:
        work_dir = tmp_path_factory.mktemp("lm-daemon")
        etc_dir = work_dir / "etc"
        etc_dir.mkdir(parents=True, exist_ok=True)
        bin_dir.mkdir(parents=True, exist_ok=True)

        lm_dst = work_dir / "launch_manager"
        shutil.copy2(resolve_target_path(_LAUNCH_MANAGER), lm_dst)
        lm_dst.chmod(0o700)

        # Grant launch_manager its sandbox caps only if the cap_kill copy is in
        # place, so apps running under another uid can always be killed.
        kill_binary, sandbox_privileged_reason = _stage_privileged_kill(runtime_root)
        sandbox_privileged = False
        if kill_binary is not None:
            sandbox_privileged, sandbox_privileged_reason = _grant_capabilities(
                lm_dst, _SETCAP_CAPS, required=("cap_setuid", "cap_setgid", "cap_kill")
            )
            if not sandbox_privileged:
                kill_binary.unlink(missing_ok=True)
                kill_binary = None

        lm_ctl_binary = resolve_target_path(_LMCONTROL) if control_client else None

        for name, dst in apps.items():
            shutil.copy2(binaries[name], dst)
            dst.chmod(0o755)

        # sandbox_privileged implies the cap_kill copy is staged, so apps can always be killed.
        config_path = _generate_runtime_config(
            runtime_root, etc_dir, config_target, render, sandbox_privileged=sandbox_privileged
        )
        log_config = None
        if log_level is not None:
            log_config = etc_dir / "logging.json"
            log_config.write_text(
                json.dumps(
                    {"appId": "LM", "logMode": "kConsole", "logLevel": log_level, "logLevelThresholdConsole": log_level}
                ),
                encoding="utf-8",
            )
        daemon = _spawn_daemon(lm_dst, config_path, work_dir, etc_dir, log_config)

        if not daemon.is_running():
            pytest.fail(f"launch_manager exited during startup. Logs:\n{daemon.get_logs()}")

        ready = apps if ready_apps is None else {name: apps[name] for name in ready_apps}
        if not _wait_for_apps(ready):
            snapshot = subprocess.run(["ps", "-eo", "pid,args"], capture_output=True, text=True, check=False)
            pytest.fail(
                "Launch Manager did not bring supervised apps to running state within timeout.\n"
                f"Expected apps: {ready}\n"
                f"Daemon logs:\n{daemon.get_logs()}\n"
                f"Process snapshot:\n{snapshot.stdout}"
            )
    except BaseException:
        _teardown(daemon, apps.values(), runtime_root, kill_binary)
        raise

    return {
        "daemon": daemon,
        "work_dir": work_dir,
        "bin_dir": bin_dir,
        "apps": apps,
        "sandbox_privileged": sandbox_privileged,
        "sandbox_privileged_reason": sandbox_privileged_reason,
        "kill_binary": kill_binary,
        "runtime_root": runtime_root,
        "lm_ctl_binary": lm_ctl_binary,
    }


def stop_launch_manager_daemon(daemon_info: dict[str, Any]) -> None:
    """Tear down a daemon started by `start_launch_manager_daemon`."""
    _teardown(
        daemon_info["daemon"],
        daemon_info["apps"].values(),
        daemon_info["runtime_root"],
        daemon_info["kill_binary"],
    )
