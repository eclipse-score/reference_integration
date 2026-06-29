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
Helpers for running tests with the Launch Manager daemon.

Provides fixtures and utilities for integration tests that require
a running Launch Manager daemon instance.
"""

import json
import os
import shutil
import signal
import subprocess
import time
from collections.abc import Generator
from pathlib import Path
from typing import Any, TextIO

import pytest


def find_binary_in_runfiles(target_path: str) -> Path | None:
    """
    Find a binary in Bazel runfiles when running under Bazel.

    Parameters
    ----------
    target_path : str
        Bazel target path (e.g., "@score_lifecycle_health//src/launch_manager_daemon:launch_manager")

    Returns
    -------
    Path | None
        Path to the binary if found in runfiles, None otherwise.
    """
    # Check if running under Bazel by looking for runfiles
    runfiles_dir = os.environ.get("RUNFILES_DIR")
    if not runfiles_dir:
        # Try to find runfiles relative to current file
        test_srcdir = os.environ.get("TEST_SRCDIR")
        if test_srcdir:
            runfiles_dir = test_srcdir

    if not runfiles_dir:
        # Try to find runfiles from the current working directory
        cwd = Path.cwd()
        if ".runfiles" in str(cwd):
            # We're inside a runfiles directory
            runfiles_parts = str(cwd).split(".runfiles")
            if len(runfiles_parts) > 1:
                runfiles_dir = runfiles_parts[0] + ".runfiles/_main"

    if not runfiles_dir:
        return None

    # Convert Bazel target to runfiles path
    # @score_lifecycle_health//src/launch_manager_daemon:launch_manager
    # -> score_lifecycle_health/src/launch_manager_daemon/launch_manager
    if target_path.startswith("@"):
        # Remove @ and split by //
        parts = target_path[1:].split("//")
        if len(parts) == 2:
            # Handle bzlmod repository names with + suffix
            repo_name = parts[0]
            # Try both with and without + suffix
            repo_variants = [
                repo_name,
                repo_name.rstrip("+"),
                repo_name + "+",
                repo_name.replace("+", "~"),
            ]

            package_and_target = parts[1].split(":")
            if len(package_and_target) == 2:
                package = package_and_target[0]
                target = package_and_target[1]

                # Try different runfiles path patterns
                candidates = []
                for repo in repo_variants:
                    candidates.extend(
                        [
                            Path(runfiles_dir) / repo / package / target,
                            Path(runfiles_dir) / f"{repo}~" / package / target,
                            Path(runfiles_dir) / "_main" / "external" / repo / package / target,
                            Path(runfiles_dir) / "external" / repo / package / target,
                        ]
                    )

                for candidate in candidates:
                    if candidate.exists() and candidate.is_file():
                        return candidate

    return None


def get_binary_path(target: str, version: str = "rust") -> Path:
    """
    Get path to a binary, either from runfiles or by building it.

    Parameters
    ----------
    target : str
        Bazel target path.
    version : str
        Build version ("rust" or "cpp").

    Returns
    -------
    Path
        Path to the binary.
    """
    # First try to find in runfiles (when running under Bazel)
    binary_path = find_binary_in_runfiles(target)
    if binary_path:
        return binary_path

    # Fall back to a config-aware Bazel build (when running pytest directly).
    # Local plain `bazel build` can fail for this target due to missing default flags.
    bazel_config = os.environ.get("FIT_BAZEL_CONFIG", "linux-x86_64")
    build_cmd = ["bazel", "build", f"--config={bazel_config}", target]
    build_res = subprocess.run(build_cmd, capture_output=True, text=True, check=False)
    if build_res.returncode != 0:
        stderr_tail = "\n".join(build_res.stderr.strip().splitlines()[-20:])
        raise RuntimeError(
            f"Failed to build target {target!r} with --config={bazel_config}.\nstderr (last lines):\n{stderr_tail}"
        )

    ws_info_res = subprocess.run(["bazel", "info", "workspace"], capture_output=True, text=True, check=False)
    if ws_info_res.returncode != 0:
        raise RuntimeError(f"Failed to resolve Bazel workspace path.\nstderr:\n{ws_info_res.stderr.strip()}")

    cquery_cmd = [
        "bazel",
        "cquery",
        f"--config={bazel_config}",
        "--output=starlark",
        "--starlark:expr=target.files_to_run.executable.path",
        target,
    ]
    cquery_res = subprocess.run(cquery_cmd, capture_output=True, text=True, check=False)
    if cquery_res.returncode != 0:
        raise RuntimeError(
            f"Failed to locate built executable with Bazel cquery.\nstderr:\n{cquery_res.stderr.strip()}"
        )

    ws_path = Path(ws_info_res.stdout.strip())
    # cquery may return multiple lines (e.g. target + exec configuration).
    # Filter out exec-configuration paths and use the first remaining line.
    cquery_lines = [line for line in cquery_res.stdout.strip().splitlines() if line and "-exec-" not in line]
    if not cquery_lines:
        cquery_lines = cquery_res.stdout.strip().splitlines()
    binary_path = ws_path / cquery_lines[0]
    if not binary_path.is_file():
        raise RuntimeError(f"Executable not found after build: {binary_path}")

    return binary_path


def copy_flatbuffer_daemon_configs(etc_dir: Path, *, include_lm_config: bool = True) -> None:
    """
    Populate `etc_dir` with Launch Manager flatbuffer config binaries.

    The current Launch Manager daemon startup path expects flatbuffer files
    (e.g., lm_demo.bin) in `etc/` relative to its working directory.

    Parameters
    ----------
    etc_dir : Path
        Destination directory where flatbuffer binaries are copied.
    include_lm_config : bool
        Whether to copy `lm_demo.bin` (the main Launch Manager config). Set to
        False when tests need to force JSON config usage for dynamic sandbox
        identity values (uid/gid).
    """
    bazel_config = os.environ.get("FIT_BAZEL_CONFIG", "linux-x86_64")
    config_target = "//feature_integration_tests/test_cases:daemon_lifecycle_configs"

    build_cmd = ["bazel", "build", f"--config={bazel_config}", config_target]
    build_res = subprocess.run(build_cmd, capture_output=True, text=True, check=False)
    if build_res.returncode != 0:
        stderr_tail = "\n".join(build_res.stderr.strip().splitlines()[-20:])
        raise RuntimeError(
            "Failed to build lifecycle flatbuffer configs "
            f"from {config_target!r} with --config={bazel_config}.\n"
            f"stderr (last lines):\n{stderr_tail}"
        )

    ws_info_res = subprocess.run(["bazel", "info", "workspace"], capture_output=True, text=True, check=False)
    if ws_info_res.returncode != 0:
        raise RuntimeError(
            "Failed to resolve Bazel workspace path while locating flatbuffer configs.\n"
            f"stderr:\n{ws_info_res.stderr.strip()}"
        )

    cquery_cmd = [
        "bazel",
        "cquery",
        f"--config={bazel_config}",
        "--output=starlark",
        "--starlark:expr=target.files.to_list()[0].path",
        config_target,
    ]
    cquery_res = subprocess.run(cquery_cmd, capture_output=True, text=True, check=False)
    if cquery_res.returncode != 0:
        raise RuntimeError(
            "Failed to locate generated flatbuffer config directory with Bazel cquery.\n"
            f"stderr:\n{cquery_res.stderr.strip()}"
        )

    flatbuffer_dir = Path(ws_info_res.stdout.strip()) / cquery_res.stdout.strip().strip('"')
    if not flatbuffer_dir.is_dir():
        raise RuntimeError(f"Generated flatbuffer config directory not found: {flatbuffer_dir}")

    for flatbuffer_file in flatbuffer_dir.glob("*.bin"):
        if not include_lm_config and flatbuffer_file.name == "lm_demo.bin":
            continue
        shutil.copy2(flatbuffer_file, etc_dir / flatbuffer_file.name)


def _find_prebuilt_flatbuffers_in_runfiles() -> Path | None:
    """
    Locate the pre-built daemon flatbuffer config directory in Bazel runfiles.

    The `launch_manager_config` rule (used by `:daemon_lifecycle_configs`)
    outputs flatbuffer files to a `flatbuffer_out/` subdirectory within the
    package.  Returns that directory, or None if not found.
    """
    for env_var in ("TEST_SRCDIR", "RUNFILES_DIR"):
        base = os.environ.get(env_var)
        if not base:
            continue
        # Under bzlmod the workspace files are nested under _main/
        for prefix in (Path(base) / "_main", Path(base)):
            candidate = prefix / "feature_integration_tests" / "test_cases" / "flatbuffer_out"
            if candidate.is_dir() and any(candidate.glob("*.bin")):
                return candidate
    return None


def copy_dynamic_flatbuffer_daemon_configs(
    etc_dir: Path,
    work_dir: Path,
    *,
    uid: int,
    gid: int,
    input_config: dict | None = None,
) -> None:
    """
    Generate and copy daemon flatbuffer configs with runtime sandbox identity.

    This mirrors the Bazel `launch_manager_config` generation pipeline used by
    `daemon_lifecycle_configs`, but injects UID/GID dynamically so local runs can
    align sandbox identity with the current user.

    Parameters
    ----------
    input_config : dict | None
        If provided, use this config dict instead of the template JSON file.
        UID/GID are still injected/overwritten into the sandbox section.
    """
    if input_config is not None:
        dynamic_config = json.loads(json.dumps(input_config))  # deep copy via JSON round-trip
    else:
        template_config_path = Path(__file__).resolve().parent / "configs" / "daemon_launch_manager_config.json"
        dynamic_config = json.loads(template_config_path.read_text())

    # Remove state_manager from any run_target depends_on — control_daemon requires
    # setuid/setgid capabilities which are unavailable in standard test environments.
    for rt in dynamic_config.get("run_targets", {}).values():
        deps = rt.get("depends_on", [])
        if "state_manager" in deps:
            deps.remove("state_manager")

    sandbox = dynamic_config.setdefault("defaults", {}).setdefault("deployment_config", {}).setdefault("sandbox", {})
    sandbox["uid"] = uid
    sandbox["gid"] = gid

    input_json = work_dir / "daemon_launch_manager_config.dynamic.json"
    input_json.write_text(json.dumps(dynamic_config, indent=2))

    json_out_dir = work_dir / "json_out"
    flatbuffer_out_dir = work_dir / "flatbuffer_out"
    json_out_dir.mkdir(exist_ok=True)
    flatbuffer_out_dir.mkdir(exist_ok=True)

    # When running inside a Bazel test sandbox, `bazel build/info` commands fail
    # because the sandbox has no MODULE.bazel workspace file.
    _under_bazel = bool(os.environ.get("TEST_SRCDIR") or os.environ.get("RUNFILES_DIR"))
    if _under_bazel:
        prebuilt_dir = _find_prebuilt_flatbuffers_in_runfiles()
        if prebuilt_dir is None:
            raise RuntimeError(
                "Cannot find pre-built daemon flatbuffers in Bazel runfiles. "
                "Ensure ':daemon_lifecycle_configs' is listed as a data dependency."
            )

        # Copy all pre-built flatbuffers (lm_demo.bin is needed for SWCL/config-manager
        # startup; hm_demo.bin + hmproc_*.bin are needed for the health monitor).
        for flatbuffer_file in prebuilt_dir.glob("*.bin"):
            shutil.copy2(flatbuffer_file, etc_dir / flatbuffer_file.name)
        return

    else:
        bazel_config = os.environ.get("FIT_BAZEL_CONFIG", "linux-x86_64")
        materialize_cmd = [
            "bazel",
            "build",
            f"--config={bazel_config}",
            "//feature_integration_tests/test_cases:daemon_lifecycle_configs",
        ]
        materialize_res = subprocess.run(materialize_cmd, capture_output=True, text=True, check=False)
        if materialize_res.returncode != 0:
            raise RuntimeError(
                f"Failed to materialize daemon config toolchain artifacts.\nstderr:\n{materialize_res.stderr.strip()}"
            )

        output_base_res = subprocess.run(["bazel", "info", "output_base"], capture_output=True, text=True, check=False)
        if output_base_res.returncode != 0:
            raise RuntimeError(
                "Failed to resolve Bazel output base for dynamic flatbuffer generation.\n"
                f"stderr:\n{output_base_res.stderr.strip()}"
            )
        output_base = Path(output_base_res.stdout.strip())
        external_root = output_base / "external" / "score_lifecycle_health+"

    lifecycle_config_bin = get_binary_path("@score_lifecycle_health//scripts/config_mapping:lifecycle_config")
    launch_manager_schema = external_root / "src/launch_manager_daemon/config/config_schema/launch_manager.schema.json"
    if not launch_manager_schema.is_file():
        raise RuntimeError(f"Launch Manager schema not found: {launch_manager_schema}")

    gen_cmd = [
        str(lifecycle_config_bin),
        str(input_json),
        "--schema",
        str(launch_manager_schema),
        "-o",
        str(json_out_dir),
    ]
    gen_res = subprocess.run(gen_cmd, capture_output=True, text=True, check=False)
    if gen_res.returncode != 0:
        raise RuntimeError(
            f"Failed to generate intermediate lifecycle JSON configs.\nstderr:\n{gen_res.stderr.strip()}"
        )

    flatc_bin = get_binary_path("@flatbuffers//:flatc")
    lm_schema = external_root / "src/launch_manager_daemon/config/lm_flatcfg.fbs"
    hm_schema = external_root / "src/launch_manager_daemon/health_monitor_lib/config/hm_flatcfg.fbs"
    hmcore_schema = external_root / "src/launch_manager_daemon/health_monitor_lib/config/hmcore_flatcfg.fbs"

    for json_cfg in json_out_dir.glob("*"):
        if not json_cfg.is_file():
            continue

        filename = json_cfg.name
        if filename.startswith("lm_"):
            schema = lm_schema
        elif filename.startswith("hmcore"):
            schema = hmcore_schema
        elif filename.startswith("hm_") or filename.startswith("hmproc_"):
            schema = hm_schema
        else:
            continue

        compile_res = subprocess.run(
            [str(flatc_bin), "-b", "-o", str(flatbuffer_out_dir), str(schema), str(json_cfg)],
            capture_output=True,
            text=True,
            check=False,
        )
        if compile_res.returncode != 0:
            raise RuntimeError(
                f"Failed to compile dynamic flatbuffer config for {filename}.\nstderr:\n{compile_res.stderr.strip()}"
            )

    for flatbuffer_file in flatbuffer_out_dir.glob("*.bin"):
        shutil.copy2(flatbuffer_file, etc_dir / flatbuffer_file.name)


def ensure_path_traversable_for_sandbox(path: Path) -> None:
    """
    Ensure path and its ancestors are traversable by non-owner sandbox users.

    Launch Manager may execute supervised processes under a different uid/gid.
    For those processes to chdir into the pytest workspace, all parent
    directories must have execute permission for others.
    """
    for candidate in [path, *path.parents]:
        if candidate == Path("/"):
            break
        try:
            mode = candidate.stat().st_mode & 0o777
            desired_mode = mode | 0o055
            if desired_mode != mode:
                candidate.chmod(desired_mode)
        except OSError:
            # Best effort: permission tweaks are environment-dependent.
            continue


class LaunchManagerDaemon:
    """
    Context manager for Launch Manager daemon lifecycle.

    Starts and stops a Launch Manager daemon instance for testing purposes.

    Parameters
    ----------
    daemon_binary : Path
        Path to the launch_manager executable.
    config_file : Path
        Path to the launch manager configuration JSON file.
    working_dir : Path
        Working directory for the daemon process.
    """

    def __init__(self, daemon_binary: Path, config_file: Path, working_dir: Path):
        self.daemon_binary = daemon_binary
        self.config_file = config_file
        self.working_dir = working_dir
        self.process: subprocess.Popen | None = None
        self.log_file: Path | None = None
        self._log_fd: TextIO | None = None

    def start(self, startup_timeout: float = 2.0) -> None:
        """
        Start the Launch Manager daemon.

        Parameters
        ----------
        startup_timeout : float
            Time to wait after starting the daemon (seconds).
        """
        # If a stale process reference exists from a previous run, clear it.
        if self.process is not None and self.process.poll() is not None:
            self.process = None

        if self.process is not None:
            raise RuntimeError("Daemon already started")

        # Create log file
        self.log_file = self.working_dir / "launch_manager.log"
        self._log_fd = open(self.log_file, "w", encoding="utf-8")

        # Start daemon process
        cmd = [str(self.daemon_binary), str(self.config_file)]
        self.process = subprocess.Popen(
            cmd,
            cwd=self.working_dir,
            stdout=self._log_fd,
            stderr=subprocess.STDOUT,
            text=True,
        )

        # Wait for daemon to initialize
        time.sleep(startup_timeout)

        # Check if daemon is still running
        if self.process.poll() is not None:
            return_code = self.process.returncode
            log_content = self.log_file.read_text() if self.log_file.exists() else "No logs available"
            self._close_log_fd()
            self.process = None
            raise RuntimeError(f"Launch Manager daemon failed to start. Exit code: {return_code}\nLogs:\n{log_content}")

    def stop(self, shutdown_timeout: float = 5.0) -> None:
        """
        Stop the Launch Manager daemon gracefully.

        Parameters
        ----------
        shutdown_timeout : float
            Maximum time to wait for graceful shutdown (seconds).
        """
        if self.process is None:
            self._close_log_fd()
            return

        try:
            # Send SIGTERM for graceful shutdown if still running.
            if self.process.poll() is None:
                try:
                    self.process.send_signal(signal.SIGTERM)
                except ProcessLookupError:
                    pass

            try:
                self.process.wait(timeout=shutdown_timeout)
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown fails.
                self.process.kill()
                self.process.wait()
        finally:
            self.process = None
            self._close_log_fd()

    def _close_log_fd(self) -> None:
        """Close daemon log file descriptor if it is open."""
        if self._log_fd is None:
            return

        try:
            self._log_fd.close()
        finally:
            self._log_fd = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False

    def is_running(self) -> bool:
        """Check if the daemon process is still running."""
        return self.process is not None and self.process.poll() is None

    def get_logs(self) -> str:
        """Get the daemon log contents."""
        if self.log_file and self.log_file.exists():
            return self.log_file.read_text()
        return ""


@pytest.fixture(scope="class")
def launch_manager_daemon(
    tmp_path_factory: pytest.TempPathFactory, version: str
) -> Generator[dict[str, Any], None, None]:
    """
    Fixture that provides a running Launch Manager daemon instance.

    The fixture sets up a complete daemon environment including:
    - Building the launch_manager binary
    - Creating a temporary workspace with bin/ and etc/ directories
    - Starting the daemon with a minimal configuration
    - Cleaning up on teardown

    Parameters
    ----------
    tmp_path_factory : pytest.TempPathFactory
        Pytest temporary path factory.
    version : str
        Parametrized version ("rust" or "cpp").

    Yields
    ------
    dict
        Daemon information containing:
        - daemon: LaunchManagerDaemon instance
        - bin_dir: Path to bin directory for test applications
        - etc_dir: Path to etc directory for configurations
        - work_dir: Path to workspace root
        - config_file: Path to launch manager config

    Examples
    --------
    >>> def test_with_daemon(launch_manager_daemon):
    ...     daemon_info = launch_manager_daemon
    ...     assert daemon_info["daemon"].is_running()
    ...     # Copy test app to daemon_info["bin_dir"]
    ...     # Run your integration test
    """
    # Create workspace structure
    work_dir = tmp_path_factory.mktemp(f"daemon_workspace_{version}")
    bin_dir = work_dir / "bin"
    etc_dir = work_dir / "etc"
    bin_dir.mkdir(exist_ok=True)
    etc_dir.mkdir(exist_ok=True)

    # Supervised processes may run as a different uid from the test user.
    # Make the pytest temp path traversable to avoid chdir permission failures.
    ensure_path_traversable_for_sandbox(work_dir)
    ensure_path_traversable_for_sandbox(bin_dir)
    ensure_path_traversable_for_sandbox(etc_dir)

    # Get launch_manager daemon binary (from runfiles or build it)
    daemon_target = "@score_lifecycle_health//src/launch_manager_daemon:launch_manager"
    daemon_binary = get_binary_path(daemon_target, version)

    # Copy daemon to bin directory
    daemon_path = bin_dir / "launch_manager"
    shutil.copy2(daemon_binary, daemon_path)
    daemon_path.chmod(0o755)

    # Optional capability setup for environments that explicitly enable it.
    # Set FIT_ENABLE_SETCAP=1 to prompt for sudo password and apply setcap.
    if os.environ.get("FIT_ENABLE_SETCAP", "0") == "1":
        try:
            # In setuid mode, supervised processes may run as a uid different
            # from the test user and still need to traverse Bazel output paths.
            ensure_path_traversable_for_sandbox(Path.home())
            ensure_path_traversable_for_sandbox(Path.home() / ".cache" / "bazel")

            if os.geteuid() != 0:
                subprocess.run(["sudo", "-v"], check=True, timeout=30)
                subprocess.run(
                    ["sudo", "setcap", "cap_setuid,cap_setgid=ep", str(daemon_path)],
                    check=True,
                    timeout=30,
                )
            else:
                subprocess.run(
                    ["setcap", "cap_setuid,cap_setgid=ep", str(daemon_path)],
                    check=True,
                    timeout=30,
                )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            # If capability setup fails (e.g., sudo denied, setcap missing),
            # tests will xfail gracefully due to uid/gid permission guards.
            pass

    # Preload binaries referenced by the generated daemon config run target.
    for app_target, app_name in [
        ("@score_lifecycle_health//examples/rust_supervised_app:rust_supervised_app", "rust_supervised_app"),
        ("@score_lifecycle_health//examples/cpp_supervised_app:cpp_supervised_app", "cpp_supervised_app"),
        ("@score_lifecycle_health//examples/control_application:control_daemon", "control_daemon"),
    ]:
        app_binary = get_binary_path(app_target, version)
        app_dest = bin_dir / app_name
        if app_dest.exists() or app_dest.is_symlink():
            app_dest.unlink()
        app_dest.symlink_to(app_binary.resolve())

    # Create launch manager configuration with the version-specific supervised app.
    # Use current user's UID/GID for sandbox to avoid setuid/setgid permission errors
    # when running in non-root environments.
    current_uid = os.getuid()
    current_gid = os.getgid()

    # The supervised app's HM config (hmproc flatbuffer) will be generated and placed
    # in etc_dir by copy_dynamic_flatbuffer_daemon_configs.  We pre-compute the path
    # so it can be embedded in the config before generation runs.
    supervised_app_name = f"{version}_supervised_app"
    hmproc_config_path = str(etc_dir / f"hmproc_{supervised_app_name}.bin")

    if version == "cpp":
        process_args = ["-d50"]
    else:
        process_args = ["--delay", "100"]

    config = {
        "schema_version": 1,
        "defaults": {
            "deployment_config": {
                "bin_dir": str(bin_dir) + "/",
                "ready_recovery_action": {"restart": {"number_of_attempts": 3, "delay_before_restart": 0.5}},
                "sandbox": {
                    "uid": current_uid,
                    "gid": current_gid,
                    "supplementary_group_ids": [],
                    "scheduling_policy": "SCHED_OTHER",
                    "scheduling_priority": 1,
                },
            },
            "component_properties": {
                "application_profile": {
                    "application_type": "Reporting",
                    "is_self_terminating": False,
                    "alive_supervision": {
                        "reporting_cycle": 0.1,
                        "min_indications": 1,
                        "max_indications": 3,
                        "failed_cycles_tolerance": 2,
                    },
                },
                "depends_on": [],
                "process_arguments": [],
                "ready_condition": {"process_state": "Running"},
            },
            "run_target": {
                "transition_timeout": 5,
                "recovery_action": {"switch_run_target": {"run_target": "fallback_run_target"}},
            },
        },
        "components": {
            supervised_app_name: {
                "description": f"Supervised application under test ({version})",
                "component_properties": {
                    "binary_name": supervised_app_name,
                    "application_profile": {
                        "application_type": "Reporting_And_Supervised",
                    },
                    "depends_on": [],
                    "process_arguments": process_args,
                },
                "deployment_config": {
                    "environmental_variables": {
                        "IDENTIFIER": supervised_app_name,
                        "PROCESSIDENTIFIER": supervised_app_name,
                        "CONFIG_PATH": hmproc_config_path,
                    },
                    "recovery_action": {
                        "switch_run_target": {"run_target": "fallback_run_target"},
                    },
                },
            },
        },
        "run_targets": {
            "Startup": {"description": "System startup", "depends_on": [supervised_app_name]},
        },
        "initial_run_target": "Startup",
        "fallback_run_target": {"description": "Fallback state", "depends_on": [], "transition_timeout": 1.5},
    }

    config_file = etc_dir / "launch_manager_config.json"
    config_file.write_text(json.dumps(config, indent=2))

    # Generate flatbuffer configs (lm_demo.bin, hmproc_*.bin, etc.) from our custom
    # config so the Launch Manager reads the correct topology including the supervised app.
    copy_dynamic_flatbuffer_daemon_configs(etc_dir, work_dir, uid=current_uid, gid=current_gid, input_config=config)

    # Start the daemon
    daemon = LaunchManagerDaemon(daemon_path, config_file, work_dir)
    try:
        daemon.start(startup_timeout=2.0)
    except RuntimeError as e:
        # If daemon fails to start due to ACL/setcap issues (which happen when
        # FIT_ENABLE_SETCAP fails in sandboxed environments), skip tests gracefully.
        if "Could not set ACL" in str(e) or "Could not create Monitor interface IPC" in str(e):
            pytest.skip(f"Daemon startup requires setcap capabilities: {str(e)[:100]}")
        raise

    try:
        # Verify daemon is running
        if not daemon.is_running():
            raise RuntimeError("Launch Manager daemon failed to stay running")

        print(f"Launch Manager daemon started successfully (PID: {daemon.process.pid})")

        yield {
            "daemon": daemon,
            "bin_dir": bin_dir,
            "etc_dir": etc_dir,
            "work_dir": work_dir,
            "config_file": config_file,
        }
    finally:
        # Cleanup
        print("\nStopping Launch Manager daemon...")
        daemon.stop()
        print(f"Daemon logs:\n{daemon.get_logs()}")
