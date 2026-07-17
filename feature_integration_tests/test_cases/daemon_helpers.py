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


def _pgrep_cmdline_pattern(binary_path: str) -> str:
    """Build POSIX ERE pattern matching binary with optional arguments."""
    return rf"^{re.escape(binary_path)}([[:space:]]|$)"


def _is_running(binary_path: Path) -> bool:
    result = subprocess.run(
        ["pgrep", "-f", _pgrep_cmdline_pattern(str(binary_path))],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def _wait_for_apps(apps: dict[str, Path], timeout_s: float = 8.0, interval_s: float = 0.2) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if all(_is_running(path) for path in apps.values()):
            return True
        time.sleep(interval_s)
    return False


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


@pytest.fixture(scope="class")
def launch_manager_daemon(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    """Start a real launch_manager process with generated flatbuffer config."""

    lock_file = Path("/tmp/lifecycle_fit.lock").open("w", encoding="utf-8")
    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)

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

    for src in (rust_supervised, cpp_supervised):
        dst = bin_dir / src.name
        shutil.copy2(src, dst)
        dst.chmod(0o755)

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
        pytest.skip(f"launch_manager failed to start in this environment. Logs:\n{logs}")

    apps = {
        "rust": bin_dir / "rust_supervised_app",
        "cpp": bin_dir / "cpp_supervised_app",
    }
    if not _wait_for_apps(apps):
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

    try:
        yield {
            "daemon": daemon,
            "work_dir": work_dir,
            "bin_dir": bin_dir,
            "apps": apps,
        }
    finally:
        daemon.stop()
        shutil.rmtree(runtime_root, ignore_errors=True)
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        lock_file.close()
