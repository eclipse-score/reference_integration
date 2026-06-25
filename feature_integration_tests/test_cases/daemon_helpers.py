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


def find_flatbuffer_configs_in_runfiles() -> Path | None:
    """
    Locate the daemon flatbuffer config directory inside Bazel runfiles.

    Returns the first directory that contains *.bin files, or None when not
    running under Bazel or when the configs are not present as data deps.
    """
    runfiles_root = None
    if os.environ.get("RUNFILES_DIR"):
        runfiles_root = Path(os.environ["RUNFILES_DIR"])
    elif os.environ.get("TEST_SRCDIR"):
        runfiles_root = Path(os.environ["TEST_SRCDIR"])

    if runfiles_root is None:
        return None

    # Known candidate paths matching the daemon_lifecycle_configs output dir.
    candidates = [
        runfiles_root / "_main" / "feature_integration_tests" / "test_cases" / "daemon_lifecycle_configs",
        runfiles_root / "feature_integration_tests" / "test_cases" / "daemon_lifecycle_configs",
    ]
    for candidate in candidates:
        if candidate.is_dir() and any(candidate.glob("*.bin")):
            return candidate

    # Fallback: search the runfiles tree for any lm_*.bin file and return its
    # parent directory (handles non-standard output paths from the rule).
    for bin_file in runfiles_root.rglob("lm_*.bin"):
        return bin_file.parent

    return None


def find_binary_in_runfiles(target_path: str) -> Path | None:
    """
    Find a binary in Bazel runfiles when running under Bazel.

    Parameters
    ----------
    target_path : str
        Bazel target path (e.g., "@score_lifecycle_health//src/launch_manager_daemon:launch_manager"
        or "//feature_integration_tests/test_scenarios/rust:rust_test_scenarios")

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
    # //feature_integration_tests/test_scenarios/rust:rust_test_scenarios
    # -> _main/feature_integration_tests/test_scenarios/rust/rust_test_scenarios

    if target_path.startswith("//"):
        # Local target - relative to main workspace
        parts = target_path[2:].split(":")
        if len(parts) == 2:
            package = parts[0]
            target = parts[1]

            # Try different runfiles path patterns for local targets
            candidates = [
                Path(runfiles_dir) / "_main" / package / target,
                Path(runfiles_dir) / package / target,
            ]

            for candidate in candidates:
                if candidate.exists() and candidate.is_file():
                    return candidate

    elif target_path.startswith("@"):
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
    binary_path = ws_path / cquery_res.stdout.strip()
    if not binary_path.is_file():
        raise RuntimeError(f"Executable not found after build: {binary_path}")

    return binary_path


def copy_flatbuffer_daemon_configs(etc_dir: Path, *, include_lm_config: bool = True) -> None:
    """
    Populate `etc_dir` with flatbuffer daemon config binaries from build outputs.

    All ``*.bin`` files from the ``daemon_lifecycle_configs`` target are copied,
    with the following exceptions:

    - ``hmproc_state_manager.bin`` is always excluded because the test fixture
      provides a minimal JSON config with a dynamically-managed state_manager
      component; copying this static process-level config would create conflicts.
    - ``lm_demo.bin`` is excluded when ``include_lm_config=False`` (the default
      for integration tests where a JSON config is passed directly as a CLI
      argument instead of using the static flatbuffer LM config).

    Parameters
    ----------
    etc_dir : Path
        Destination directory where flatbuffer binaries are copied.
    include_lm_config : bool
        Whether to copy ``lm_demo.bin``.  Set to ``False`` (the default for
        integration tests) when a JSON config file is passed to the daemon
        directly as a CLI argument.
    """
    # Exclude only configs that conflict with dynamically-provided components
    # or those not needed when using JSON config mode.
    _EXCLUDED_IN_JSON_MODE = {"hmproc_state_manager.bin"}

    def _should_skip(name: str) -> bool:
        if name in _EXCLUDED_IN_JSON_MODE:
            return True
        if not include_lm_config and name == "lm_demo.bin":
            return True
        return False

    # Under Bazel, the daemon_lifecycle_configs target is provided as a data dep
    # and its output files are accessible via runfiles — no subprocess build needed.
    runfiles_flatbuffer_dir = find_flatbuffer_configs_in_runfiles()
    if runfiles_flatbuffer_dir is not None:
        for flatbuffer_file in runfiles_flatbuffer_dir.glob("*.bin"):
            if _should_skip(flatbuffer_file.name):
                continue
            shutil.copy2(flatbuffer_file, etc_dir / flatbuffer_file.name)
        return

    # Fall back to a subprocess Bazel build (direct pytest invocation outside Bazel).
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
        if _should_skip(flatbuffer_file.name):
            continue
        shutil.copy2(flatbuffer_file, etc_dir / flatbuffer_file.name)


def copy_dynamic_flatbuffer_daemon_configs(
    etc_dir: Path, work_dir: Path, bin_dir: Path, config_file: Path, *, uid: int, gid: int
) -> None:
    """
    Generate and copy daemon flatbuffer configs with runtime sandbox identity.

    This mirrors the Bazel `launch_manager_config` generation pipeline used by
    `daemon_lifecycle_configs`, but injects UID/GID and bin_dir dynamically so
    local runs can align sandbox identity with the current user.
    """
    template_config_path = Path(__file__).resolve().parent / "configs" / "daemon_launch_manager_config.json"
    dynamic_config = json.loads(template_config_path.read_text())

    deployment_config = dynamic_config.setdefault("defaults", {}).setdefault("deployment_config", {})
    # Inject absolute bin_dir path for setcap mode (without trailing slash to avoid bin//binary_name)
    deployment_config["bin_dir"] = str(bin_dir)

    sandbox = deployment_config.setdefault("sandbox", {})
    sandbox["uid"] = uid
    sandbox["gid"] = gid

    # Remove state_manager from run target dependencies as it requires control channel setup
    # which isn't configured in test mode
    if "run_targets" in dynamic_config:
        for rt_name, rt_config in dynamic_config["run_targets"].items():
            if "depends_on" in rt_config and "state_manager" in rt_config["depends_on"]:
                rt_config["depends_on"].remove("state_manager")

    # Remove state_manager from fallback_run_target dependencies
    if "fallback_run_target" in dynamic_config:
        fallback_rt = dynamic_config["fallback_run_target"]
        if "depends_on" in fallback_rt and "state_manager" in fallback_rt["depends_on"]:
            fallback_rt["depends_on"].remove("state_manager")

    # Remove state_manager component entirely to avoid control channel issues
    if "components" in dynamic_config and "state_manager" in dynamic_config["components"]:
        del dynamic_config["components"]["state_manager"]

    # Write the modified config to the config_file path so the daemon uses it
    config_file.write_text(json.dumps(dynamic_config, indent=2))

    input_json = work_dir / "daemon_launch_manager_config.dynamic.json"
    input_json.write_text(json.dumps(dynamic_config, indent=2))

    json_out_dir = work_dir / "json_out"
    flatbuffer_out_dir = work_dir / "flatbuffer_out"
    json_out_dir.mkdir(exist_ok=True)
    flatbuffer_out_dir.mkdir(exist_ok=True)

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

    ws_info_res = subprocess.run(["bazel", "info", "execution_root"], capture_output=True, text=True, check=False)
    if ws_info_res.returncode != 0:
        raise RuntimeError(
            "Failed to resolve Bazel execution root for dynamic flatbuffer generation.\n"
            f"stderr:\n{ws_info_res.stderr.strip()}"
        )
    exec_root = Path(ws_info_res.stdout.strip())

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

    # When using JSON config mode, exclude only process-level configs.
    # Core topology files are required for daemon initialization.
    _EXCLUDED_IN_JSON_MODE = {"hmproc_state_manager.bin"}

    for flatbuffer_file in flatbuffer_out_dir.glob("*.bin"):
        if flatbuffer_file.name in _EXCLUDED_IN_JSON_MODE:
            continue
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
        self._log_fd = open(self.log_file, "w")

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
            # NOTE: Supervised processes may run as a uid different from the test user.
            # If Bazel outputs are under your home directory and it lacks o+x permissions,
            # those processes will fail to traverse paths. To avoid modifying your home
            # directory permissions automatically, ensure it is already traversable (o+x)
            # or configure Bazel to use an output directory outside your home.
            # Test workspace directories are made traversable below.

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

    # Create minimal launch manager configuration
    # Use current user's UID/GID for sandbox to avoid setuid/setgid permission errors
    # when running in non-root environments.
    current_uid = os.getuid()
    current_gid = os.getgid()

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
                "transition_timeout": 10,
                "recovery_action": {"switch_run_target": {"run_target": "fallback"}},
            },
        },
        "components": {
            "state_manager": {
                "description": "State Manager application (minimal control daemon)",
                "component_properties": {
                    "binary_name": "control_daemon",
                    "application_profile": {"application_type": "Native"},
                    "depends_on": [],
                },
            }
        },
        "run_targets": {
            "Startup": {"description": "System startup", "depends_on": []},
            "fallback": {"description": "Fallback state", "depends_on": [], "transition_timeout": 1.5},
        },
        "initial_run_target": "Startup",
        "fallback_run_target": {"description": "Fallback state", "depends_on": [], "transition_timeout": 1.5},
    }

    config_file = etc_dir / "launch_manager_config.json"

    # Launch Manager daemon consumes flatbuffer config binaries from `etc/`.
    # In setcap mode, generate them dynamically with current UID/GID so
    # sandbox identity aligns with the active runtime user.
    if os.environ.get("FIT_ENABLE_SETCAP", "0") == "1":
        # Dynamic config generation writes to config_file directly
        copy_dynamic_flatbuffer_daemon_configs(
            etc_dir, work_dir, bin_dir, config_file, uid=current_uid, gid=current_gid
        )
    else:
        # Write programmatic config for non-setcap mode
        config_file.write_text(json.dumps(config, indent=2))
        copy_flatbuffer_daemon_configs(etc_dir, include_lm_config=True)

    # Start the daemon
    daemon = LaunchManagerDaemon(daemon_path, config_file, work_dir)
    daemon.start(startup_timeout=2.0)

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
