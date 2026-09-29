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
    "@score_lifecycle//score/launch_manager:launch_manager": "FIT_LAUNCH_MANAGER_PATH",
    "@score_lifecycle//examples/rust_supervised_app:rust_supervised_app": "FIT_RUST_SUPERVISED_APP_PATH",
    "@score_lifecycle//examples/cpp_supervised_app:cpp_supervised_app": "FIT_CPP_SUPERVISED_APP_PATH",
    "//feature_integration_tests/configs:lifecycle_daemon_config.json": "FIT_LIFECYCLE_DAEMON_CONFIG_PATH",
    "//feature_integration_tests/test_cases/support_apps/flaky_startup_app:flaky_startup_app": (
        "FIT_FLAKY_STARTUP_APP_PATH"
    ),
    "//feature_integration_tests/configs:lifecycle_daemon_retry_config.json": "FIT_LIFECYCLE_RETRY_CONFIG_PATH",
    "@score_lifecycle//scripts/config_mapping:lifecycle_config": "FIT_LIFECYCLE_CONFIG_TOOL_PATH",
    "@score_lifecycle//score/launch_manager/src/daemon/src/configuration/config_schema:launch_manager.schema.json": "FIT_LIFECYCLE_CONFIG_SCHEMA_PATH",
    "@score_lifecycle//score/launch_manager/src/daemon/src/configuration:lm_flatcfg_fbs": "FIT_LIFECYCLE_LM_SCHEMA_PATH",
    "@flatbuffers//:flatc": "FIT_FLATC_PATH",
}


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
    """Resolve an executable/file path from a bazel target label via its runfile env var."""
    env_resolved = _resolve_from_env(target)
    if env_resolved is not None:
        return env_resolved

    env_var = _TARGET_ENV_MAP.get(target)
    raise RuntimeError(
        f"Could not resolve target {target!r}: environment variable "
        f"{env_var!r} is not set or does not point to an existing file. "
        "Ensure the corresponding data dependency is declared on the test target."
    )


def pgrep_cmdline_pattern(binary_path: str) -> str:
    """Build POSIX ERE pattern matching binary with optional arguments."""
    return rf"^{re.escape(binary_path)}([[:space:]]|$)"


def is_running(binary_path: str | Path) -> bool:
    """True if some process's cmdline starts with `binary_path` (pgrep). This is process
    existence only, not launch_manager's reported Running state."""
    result = subprocess.run(
        ["pgrep", "-f", pgrep_cmdline_pattern(str(binary_path))],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def first_pid(binary_path: str | Path) -> str | None:
    """First pgrep match for `binary_path` (see `is_running`), or None."""
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
    """Poll `predicate` until it is truthy (True) or `timeout_s` elapses (False)."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(interval_s)
    return False


# cap_setuid/cap_setgid: apply sandbox uid/gid; cap_sys_nice: apply non-SCHED_OTHER policies;
# cap_kill: launch_manager (runner uid) must signal children running as `_SANDBOX_UID`.
_SETCAP_CAPS = "cap_setuid,cap_setgid,cap_sys_nice,cap_kill+ep"

# Sandbox uid substituted when capabilities are granted. Must differ from the runner's uid, else
# the uid test cannot tell an applied identity from an inherited one (config's 1001 is commonly
# the runner's own uid). The gid is NOT remapped to a distinct value: see `_generate_runtime_config`.
_SANDBOX_UID = 65533

# Capability-granted copies of `kill` (cap_kill) and `cat` (cap_sys_ptrace, cap_dac_read_search),
# staged per daemon by `_spawn_daemon` and deleted by `_teardown`. They let the runner signal apps
# running as `_SANDBOX_UID` and read their /proc/<pid>/environ with only the setcap sudoers rule.
_privileged_kill: Path | None = None
_privileged_cat: Path | None = None


def _mount_nosuid(path: Path) -> bool:
    """Best-effort check (via `findmnt`) whether `path` is on a `nosuid` mount, which drops
    file capabilities at exec time. Used only to enrich a failed-grant diagnostic."""
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


def _grant_sandbox_capabilities(
    binary_path: Path,
    caps: str = _SETCAP_CAPS,
    required: tuple[str, ...] = ("cap_setuid", "cap_setgid"),
) -> tuple[bool, str]:
    """Best-effort `setcap caps binary_path`. Never raises.

    Returns `(granted, reason)`. `granted` is True only if `getcap` reads back every cap in
    `required` (when `getcap` is available); `reason` is a diagnostic suitable for a skip message.

    Tries `sudo -n setcap` first when FIT_ENABLE_SETCAP=1 (needs a passwordless sudoers rule for
    the setcap binary with no pinned arguments), then plain `setcap` (succeeds only as root).
    Under `bazel test` the variable must be passed with `--test_env`, and the grant is inert
    inside linux-sandbox (PR_SET_NO_NEW_PRIVS) even when setcap succeeds.

    Limitation: only `required` is verified; the other caps in `caps` are assumed granted with it.
    """
    if shutil.which("setcap") is None:
        return False, "setcap binary not found on PATH"

    setcap_enabled = os.environ.get("FIT_ENABLE_SETCAP") == "1"
    attempts: list[tuple[list[str], str]] = [
        (["setcap", caps, str(binary_path)], "plain setcap (requires running as root)")
    ]
    if setcap_enabled:
        if shutil.which("sudo") is None:
            attempts.append(([], "FIT_ENABLE_SETCAP=1 set but 'sudo' not found on PATH"))
        else:
            attempts.insert(
                0,
                (["sudo", "-n", "setcap", caps, str(binary_path)], "sudo -n setcap"),
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
            if any(cap not in verify.stdout for cap in required):
                nosuid_hint = " (path is on a 'nosuid' mount)" if _mount_nosuid(binary_path) else ""
                failures.append(
                    f"{label} reported success but getcap did not confirm the capabilities"
                    f"{nosuid_hint}: {verify.stdout.strip() or '<empty>'}"
                )
                continue

        return True, f"granted via {label}"

    return False, "; ".join(failures) if failures else "no grant attempt produced a result"


def signal_process(pid: str, sig: str, *, sandbox_privileged: bool) -> tuple[bool, str]:
    """Send `sig` (e.g. "-9", "-STOP", "-CONT") to `pid`. Returns `(sent, reason)`; never raises.

    Tries plain `kill`, then (if `sandbox_privileged`) the staged cap_kill copy, then
    `sudo -n kill` when FIT_ENABLE_SETCAP=1. The sudo fallback only works with a sudoers rule
    for `kill`, which the documented setup does not provide.
    """
    attempts: list[list[str]] = [["kill", sig, pid]]
    if sandbox_privileged and _privileged_kill is not None:
        attempts.append([str(_privileged_kill), sig, pid])
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
    """A launch_manager subprocess plus the stdout/stderr lines its reader thread collected."""

    process: subprocess.Popen[str]
    _lines: list[str]
    _thread: threading.Thread

    def is_running(self) -> bool:
        return self.process.poll() is None

    def pid(self) -> int:
        return self.process.pid

    def stop(self) -> None:
        """SIGTERM the daemon's process group, SIGKILL after 5 s. Does not reach supervised
        apps, which launch_manager moves into their own process groups (see `_teardown`)."""
        if self.is_running():
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            deadline = time.time() + 5.0
            while self.is_running() and time.time() < deadline:
                time.sleep(0.1)
            if self.is_running():
                os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                self.process.wait(timeout=5)

    def close_output(self) -> None:
        """Join the stdout reader (1 s) and close the pipe.

        Call only after the supervised apps are dead: they inherit the pipe, so the reader sees
        EOF only then. If the reader is still alive the pipe is left open (leaked) rather than
        closed under it, which would deadlock.
        """
        self._thread.join(timeout=1)
        if self.process.stdout is not None and not self._thread.is_alive():
            self.process.stdout.close()

    def get_logs(self) -> str:
        return "\n".join(self._lines)


def _cleanup_runtime_root(runtime_root: Path) -> None:
    """Remove a daemon's uniquely allocated runtime directory."""
    shutil.rmtree(runtime_root, ignore_errors=True)


def _generate_runtime_config(
    config_template: str,
    runtime_root: Path,
    etc_dir: Path,
    sandbox_privileged: bool = True,
    *,
    remap_sandbox_uid: bool = False,
    independent_apps: bool = False,
    ready_timeout_s: float | None = None,
    crashes_before_success: int | None = None,
) -> None:
    """Render `config_template` for one daemon and serialize it to `etc_dir`.

    Writes the rendered JSON to `etc_dir/lifecycle_config.json` (tests read expected values from
    it) and the flatbuffer to `etc_dir/launch_manager_config.bin` via the upstream config mapper
    and `flatc`. Raises RuntimeError with the tool's output if either step fails.

    Rendering always sets `bin_dir` to `runtime_root/bin` and the flaky-app counter path; optional
    variants (rendered, not kept as copied config files, so they cannot drift):
    - `independent_apps`: drop every component's `depends_on`.
    - `ready_timeout_s`: override `defaults.deployment_config.ready_timeout`.
    - `crashes_before_success`: fill the `__FIT_CRASHES_BEFORE_SUCCESS__` argument.
    - `remap_sandbox_uid`: set every sandbox uid to `_SANDBOX_UID` and gid to the runner's gid,
      and chmod `runtime_root` 0750. Limitation: the gid then equals the runner's, so a gid
      check cannot prove setgid() was applied.
    - `sandbox_privileged=False`: downgrade non-`SCHED_OTHER` policies to `SCHED_OTHER`/0.
      launch_manager treats a failed sched_setscheduler() as fatal for the component, so without
      CAP_SYS_NICE every such component would crash-loop.
    """
    config = json.loads(_resolve_target_path(config_template).read_text(encoding="utf-8"))
    config["defaults"]["deployment_config"]["bin_dir"] = str(runtime_root / "bin")
    if ready_timeout_s is not None:
        config["defaults"]["deployment_config"]["ready_timeout"] = ready_timeout_s
    if independent_apps:
        for component in config["components"].values():
            component["component_properties"].pop("depends_on", None)

    sandboxes = [config["defaults"]["deployment_config"].get("sandbox")]
    sandboxes += [component.get("deployment_config", {}).get("sandbox") for component in config["components"].values()]
    if remap_sandbox_uid:
        for sandbox in filter(None, sandboxes):
            sandbox["uid"] = _SANDBOX_UID
            sandbox["gid"] = os.getgid()
        runtime_root.chmod(0o750)
    if not sandbox_privileged:
        for sandbox in sandboxes:
            if sandbox and sandbox.get("scheduling_policy") not in (None, "SCHED_OTHER"):
                sandbox["scheduling_policy"] = "SCHED_OTHER"
                sandbox["scheduling_priority"] = 0

    placeholders = {"__FIT_RUNTIME_ROOT__/flaky_startup_app.counter": str(runtime_root / "flaky_startup_app.counter")}
    if crashes_before_success is not None:
        placeholders["__FIT_CRASHES_BEFORE_SUCCESS__"] = str(crashes_before_success)
    for component in config["components"].values():
        arguments = component["component_properties"].get("process_arguments", [])
        component["component_properties"]["process_arguments"] = [placeholders.get(a, a) for a in arguments]

    rendered_config = etc_dir / "lifecycle_config.json"
    rendered_config.write_text(json.dumps(config), encoding="utf-8")
    generated_dir = etc_dir / "generated"
    generated_dir.mkdir()
    config_tool = _resolve_target_path("@score_lifecycle//scripts/config_mapping:lifecycle_config")
    config_schema = _resolve_target_path(
        "@score_lifecycle//score/launch_manager/src/daemon/src/configuration/config_schema:launch_manager.schema.json"
    )
    config_mapping_result = subprocess.run(
        [str(config_tool), str(rendered_config), "--schema", str(config_schema), "-o", str(generated_dir)],
        capture_output=True,
        text=True,
        check=False,
    )
    if config_mapping_result.returncode != 0:
        raise RuntimeError(
            f"Command failed (rc={config_mapping_result.returncode}): {config_tool} {rendered_config} "
            f"--schema {config_schema} -o {generated_dir}\n"
            f"stdout:\n{config_mapping_result.stdout}\nstderr:\n{config_mapping_result.stderr}"
        )

    flatc = _resolve_target_path("@flatbuffers//:flatc")
    lm_schema = _resolve_target_path(
        "@score_lifecycle//score/launch_manager/src/daemon/src/configuration:lm_flatcfg_fbs"
    )
    generated_config = generated_dir / f"{rendered_config.stem}_gen.json"
    # launch_manager defaults to loading "etc/launch_manager_config.bin", and flatc names its
    # output after the input file's stem, so the input must be named to match.
    flatc_input = generated_dir / "launch_manager_config.json"
    shutil.copy2(generated_config, flatc_input)
    flatc_cmd = [
        str(flatc),
        "--binary",
        "--strict-json",
        "-o",
        str(etc_dir),
        str(lm_schema),
        str(flatc_input),
    ]
    flatc_result = subprocess.run(
        flatc_cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    if flatc_result.returncode != 0:
        raise RuntimeError(
            f"Command failed (rc={flatc_result.returncode}): {' '.join(flatc_cmd)}\n"
            f"stdout:\n{flatc_result.stdout}\nstderr:\n{flatc_result.stderr}"
        )


# launch_manager creates POSIX shm objects with fixed names ("/ipc_shared_mem<N>", "/_nudge~._.~me_")
# using O_CREAT|O_EXCL on the host-wide /dev/shm (not isolated by `unshare -i`). A second daemon
# started before the first has unlinked them gets EEXIST and silently launches nothing. So daemon
# lifetimes must not overlap: this registry enforces it within one pytest process; across Bazel
# test processes the lifecycle targets are tagged "exclusive".
_live_daemons: list[ManagedDaemon] = []


def _assert_no_live_daemon() -> None:
    """Fail the test if a daemon started by this process is still running."""
    _live_daemons[:] = [d for d in _live_daemons if d.is_running()]
    if _live_daemons:
        pytest.fail(
            f"Another launch_manager (pid={_live_daemons[0].pid()}) is still running; overlapping "
            "daemon lifetimes collide on launch_manager's fixed POSIX shm names. Don't start a "
            "daemon from a test that also holds the class-scoped `launch_manager_daemon` fixture."
        )


def _spawn_daemon(
    work_dir: Path,
    etc_dir: Path,
    runtime_root: Path,
    config_template: str,
    staged_binaries: list[tuple[Path, Path, int]],
    grant_sandbox_capabilities: bool = False,
    **config_options: Any,
) -> tuple[ManagedDaemon, bool, str]:
    """Copy launch_manager (0700) and `staged_binaries` (src, dst, mode) into place, render the
    config (`config_options` go to `_generate_runtime_config`), and start launch_manager in its
    own session with stdout+stderr collected by a reader thread.

    With `grant_sandbox_capabilities`, tries to setcap launch_manager; if that succeeds it also
    stages the privileged `kill`/`cat` copies, and only when both are staged remaps the sandbox
    uid. Returns `(daemon, sandbox_privileged, sandbox_privileged_reason)`.

    `pytest.fail`s if another daemon from this process is alive or if launch_manager exits within
    the 1 s startup window; in the latter case (or any exception after Popen) it tears down the
    daemon itself, since the caller never receives it.
    """
    _assert_no_live_daemon()
    launch_manager = _resolve_target_path("@score_lifecycle//score/launch_manager:launch_manager")
    lm_dst = work_dir / "launch_manager"
    shutil.copy2(launch_manager, lm_dst)
    # 0700: once granted cap_setuid it must not be executable by other local users.
    lm_dst.chmod(0o700)

    global _privileged_kill, _privileged_cat
    _privileged_kill = _privileged_cat = None
    if grant_sandbox_capabilities:
        sandbox_privileged, sandbox_privileged_reason = _grant_sandbox_capabilities(lm_dst)
    else:
        sandbox_privileged, sandbox_privileged_reason = False, "not requested"
    if sandbox_privileged:
        # Remap the uid only if the runner can still signal the apps and read their environ.
        kill_tool, kill_reason = _stage_privileged_tool(work_dir, "kill", ("cap_kill",))
        cat_tool, cat_reason = _stage_privileged_tool(work_dir, "cat", ("cap_sys_ptrace", "cap_dac_read_search"))
        if kill_tool is not None and cat_tool is not None:
            _privileged_kill, _privileged_cat = kill_tool, cat_tool
        else:
            for tool in (kill_tool, cat_tool):
                if tool is not None:
                    tool.unlink()
            sandbox_privileged_reason += f"; sandbox uid not remapped: {kill_reason}; {cat_reason}"

    for src, dst, mode in staged_binaries:
        shutil.copy2(src, dst)
        dst.chmod(mode)

    _generate_runtime_config(
        config_template,
        runtime_root,
        etc_dir,
        sandbox_privileged=sandbox_privileged,
        remap_sandbox_uid=_privileged_kill is not None,
        **config_options,
    )

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
    _live_daemons.append(daemon)

    # The caller never receives `daemon` if this raises, so tear it down here; otherwise a
    # detached launch_manager keeps running and blocks every later start via _live_daemons.
    try:
        # Startup window: a broken config makes launch_manager exit within it.
        time.sleep(1.0)
        if not daemon.is_running():
            pytest.fail(f"launch_manager failed to start. Logs:\n{daemon.get_logs()}")
    except BaseException:
        _teardown(daemon, [dst for _, dst, _ in staged_binaries], runtime_root)
        raise

    return daemon, sandbox_privileged, sandbox_privileged_reason


def start_launch_manager_daemon(
    tmp_path_factory: pytest.TempPathFactory,
    blocked_apps: frozenset[str] = frozenset(),
    stalled_apps: frozenset[str] = frozenset(),
    wait_for_apps: bool = True,
    independent_apps: bool = False,
    ready_timeout_s: float | None = None,
) -> dict[str, Any]:
    """Start launch_manager on lifecycle_daemon_config.json with rust_ and cpp_supervised_app.

    Always attempts the sandbox capability grant (see `_spawn_daemon`); check the returned
    `sandbox_privileged` before asserting on uid/gid/scheduling.
    - `blocked_apps` ("rust"/"cpp"): staged with mode 0000, so exec fails until the caller
      chmods them 0755. Used to withhold a dependency.
    - `stalled_apps`: replaced by a stub that runs but never reports Running, so launch_manager
      waits out `ready_timeout` on it.
    - `independent_apps`, `ready_timeout_s`: rendered into the config (`_generate_runtime_config`).
    - `wait_for_apps`: `pytest.fail` unless every non-blocked app is running within 8 s.
      Limitation: "running" means a matching process exists (pgrep), not launch_manager's Running state.

    Uses a fresh runtime root under `TEST_TMPDIR`; must not overlap another live daemon.
    Returns the daemon info dict consumed by `stop_launch_manager_daemon`.
    """

    runtime_root = Path(tempfile.mkdtemp(prefix="lifecycle_fit-", dir=_tmpdir_root()))
    bin_dir = runtime_root / "bin"
    apps = {
        "rust": bin_dir / "rust_supervised_app",
        "cpp": bin_dir / "cpp_supervised_app",
    }
    daemon = None
    try:
        work_dir = tmp_path_factory.mktemp("lm-daemon")
        etc_dir = work_dir / "etc"
        etc_dir.mkdir(parents=True, exist_ok=True)

        bin_dir.mkdir(parents=True, exist_ok=True)

        rust_supervised = _resolve_target_path("@score_lifecycle//examples/rust_supervised_app:rust_supervised_app")
        cpp_supervised = _resolve_target_path("@score_lifecycle//examples/cpp_supervised_app:cpp_supervised_app")
        stall_stub = work_dir / "stall_stub.sh"
        # `exec -a "$0"` keeps the staged app path as argv[0], so the anchored pgrep/pkill pattern
        # matches the stub, and it stays a single process that dies on SIGTERM.
        stall_stub.write_text('#!/bin/bash\nexec -a "$0" sleep infinity\n', encoding="utf-8")
        staged_binaries = [
            (
                stall_stub if key in stalled_apps else src,
                bin_dir / src.name,
                0o000 if key in blocked_apps else 0o755,
            )
            for key, src in (("rust", rust_supervised), ("cpp", cpp_supervised))
        ]

        daemon, sandbox_privileged, sandbox_privileged_reason = _spawn_daemon(
            work_dir,
            etc_dir,
            runtime_root,
            "//feature_integration_tests/configs:lifecycle_daemon_config.json",
            staged_binaries,
            grant_sandbox_capabilities=True,
            independent_apps=independent_apps,
            ready_timeout_s=ready_timeout_s,
        )

        if wait_for_apps and not _wait_for_apps({k: v for k, v in apps.items() if k not in blocked_apps}):
            process_snapshot = subprocess.run(
                ["ps", "-eo", "pid,args"],
                capture_output=True,
                text=True,
                check=False,
            )
            pytest.fail(
                "Launch Manager did not bring supervised apps to running state within timeout.\n"
                f"Expected apps: {apps}\n"
                f"Daemon logs:\n{daemon.get_logs()}\n"
                f"Process snapshot (rc={process_snapshot.returncode}):\n"
                f"{process_snapshot.stdout}{process_snapshot.stderr}"
            )
    except BaseException:
        # Kill apps too: any that already started outlive the daemon (own process group).
        _teardown(daemon, list(apps.values()), runtime_root)
        raise

    return {
        "daemon": daemon,
        "work_dir": work_dir,
        "bin_dir": bin_dir,
        "apps": apps,
        "sandbox_privileged": sandbox_privileged,
        "sandbox_privileged_reason": sandbox_privileged_reason,
        "runtime_root": runtime_root,
        "runtime_config": etc_dir / "lifecycle_config.json",
    }


def start_flaky_retry_daemon(
    tmp_path_factory: pytest.TempPathFactory,
    crashes_before_success: int,
) -> dict[str, Any]:
    """Start launch_manager on lifecycle_daemon_retry_config.json with only `flaky_startup_app`.

    The app aborts on its first `crashes_before_success` launches and then stays up, counting
    every launch in `counter_path`, so tests can observe `number_of_attempts` deterministically.
    No capability grant is requested. Does not wait for the app: whether it ever runs is what
    the caller checks. Returns the daemon info dict consumed by `stop_flaky_retry_daemon`.
    """
    runtime_root = Path(tempfile.mkdtemp(prefix="lifecycle_fit_retries-", dir=_tmpdir_root()))
    bin_dir = runtime_root / "bin"
    app_dst = bin_dir / "flaky_startup_app"
    daemon = None
    try:
        work_dir = tmp_path_factory.mktemp("lm-retry-daemon")
        etc_dir = work_dir / "etc"
        etc_dir.mkdir(parents=True, exist_ok=True)

        bin_dir.mkdir(parents=True, exist_ok=True)

        flaky_app = _resolve_target_path(
            "//feature_integration_tests/test_cases/support_apps/flaky_startup_app:flaky_startup_app"
        )
        staged_binaries = [(flaky_app, app_dst, 0o755)]

        # runtime_root is a fresh mkdtemp, so the counter starts at 0.
        counter_path = runtime_root / "flaky_startup_app.counter"

        daemon, _, _ = _spawn_daemon(
            work_dir,
            etc_dir,
            runtime_root,
            "//feature_integration_tests/configs:lifecycle_daemon_retry_config.json",
            staged_binaries,
            crashes_before_success=crashes_before_success,
        )
    except BaseException:
        _teardown(daemon, [app_dst], runtime_root)
        raise

    return {
        "daemon": daemon,
        "work_dir": work_dir,
        "bin_dir": bin_dir,
        "app_path": app_dst,
        "counter_path": counter_path,
        "crashes_before_success": crashes_before_success,
        "runtime_root": runtime_root,
        "runtime_config": etc_dir / "lifecycle_config.json",
    }


def _teardown(daemon: ManagedDaemon | None, app_paths: list[Path], runtime_root: Path) -> None:
    """Stop `daemon` (if any), SIGKILL each of `app_paths` by cmdline, close the daemon's output,
    delete the privileged tool copies and remove `runtime_root`. Each step runs even if an
    earlier one raises.

    Apps are killed explicitly because they run in their own process groups, which `stop()`
    does not reach.
    """
    try:
        if daemon is not None:
            daemon.stop()
    finally:
        try:
            for app_path in app_paths:
                _kill_app(app_path)
            if daemon is not None:
                daemon.close_output()
        finally:
            _drop_privileged_tools()
            _cleanup_runtime_root(runtime_root)


def _drop_privileged_tools() -> None:
    """Delete the capability-granted `kill`/`cat` copies. `work_dir` is not removed (pytest keeps
    recent basetemps), so they would otherwise stay on disk."""
    global _privileged_kill, _privileged_cat
    for tool in (_privileged_kill, _privileged_cat):
        if tool is not None:
            tool.unlink(missing_ok=True)
    _privileged_kill = _privileged_cat = None


def _stage_privileged_tool(work_dir: Path, name: str, caps: tuple[str, ...]) -> tuple[Path | None, str]:
    """Copy the `name` binary from PATH to `work_dir/privileged/name` (mode 0700, runner only) and
    grant it `caps` via `_grant_sandbox_capabilities`. Returns `(path, reason)`; `path` is None
    if the grant was not verified (the copy is then left for the caller to delete).

    The basename is kept because procps `kill` dispatches on argv[0].
    """
    src = shutil.which(name)
    if src is None:
        return None, f"{name} binary not found on PATH"
    dst = work_dir / "privileged" / name
    dst.parent.mkdir(exist_ok=True)
    shutil.copy2(Path(src).resolve(), dst)
    dst.chmod(0o700)
    granted, reason = _grant_sandbox_capabilities(dst, ",".join(caps) + "+ep", caps)
    return (dst if granted else None), f"{'/'.join(caps)} on {name}: {reason}"


def read_proc_file(pid: str, name: str) -> bytes:
    """Read `/proc/<pid>/<name>`, via the privileged `cat` copy when one is staged.

    Needed for files like `environ`: once the app runs as `_SANDBOX_UID` it is non-dumpable and
    the runner lacks ptrace access to it. Raises RuntimeError (with stderr) if `cat` fails.
    """
    path = f"/proc/{pid}/{name}"
    if _privileged_cat is None:
        return Path(path).read_bytes()
    result = subprocess.run([str(_privileged_cat), path], capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed (rc={result.returncode}): {_privileged_cat} {path}\n"
            f"stderr:\n{result.stderr.decode(errors='replace')}"
        )
    return result.stdout


def _kill_app(app_path: Path) -> None:
    """SIGKILL every process whose cmdline starts with `app_path`. Uses the cap_kill `kill` copy
    when staged, since a plain pkill gets EPERM for apps running as `_SANDBOX_UID`. Best effort."""
    if _privileged_kill is None:
        subprocess.run(
            ["pkill", "-9", "-f", pgrep_cmdline_pattern(str(app_path))], capture_output=True, text=True, check=False
        )
        return
    pids = subprocess.run(
        ["pgrep", "-f", pgrep_cmdline_pattern(str(app_path))], capture_output=True, text=True, check=False
    ).stdout.split()
    if pids:
        subprocess.run([str(_privileged_kill), "-9", *pids], capture_output=True, text=True, check=False)


def _stop_daemon(daemon_info: dict[str, Any], app_paths: list[Path]) -> None:
    """Tear down a started daemon, its `app_paths`, and its runtime root."""
    _teardown(daemon_info["daemon"], app_paths, daemon_info["runtime_root"])


def stop_flaky_retry_daemon(daemon_info: dict[str, Any]) -> None:
    """Tear down a daemon started by `start_flaky_retry_daemon`."""
    _stop_daemon(daemon_info, [daemon_info["app_path"]])


def read_retry_attempt_count(counter_path: Path) -> int:
    """Read flaky_startup_app's persisted attempt counter; 0 if it hasn't run yet."""
    try:
        return int(counter_path.read_text().strip())
    except (FileNotFoundError, ValueError):
        return 0


def stop_launch_manager_daemon(daemon_info: dict[str, Any]) -> None:
    """Tear down a daemon started by `start_launch_manager_daemon`."""
    _stop_daemon(daemon_info, list(daemon_info["apps"].values()))
