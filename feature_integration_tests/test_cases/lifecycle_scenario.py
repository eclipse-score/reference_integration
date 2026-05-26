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
Helpers and base scenario class for lifecycle feature integration tests.

``LifecycleScenario`` is a :class:`FitScenario` subclass that supplies the
shared ``temp_dir`` fixture so individual test classes do not have to duplicate it.
"""

import json
import shutil
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from fit_scenario import FitScenario, temp_dir_common
from testing_utils import BazelTools


def read_launch_manager_config(config_path: Path) -> dict[str, Any]:
    """
    Read and parse the launch manager configuration JSON file.

    Parameters
    ----------
    config_path : Path
        Path to the launch manager configuration file.

    Returns
    -------
    dict
        Parsed launch manager configuration.
    """
    return json.loads(config_path.read_text())


def create_launch_manager_config(config_path: Path, components: dict[str, Any], run_targets: dict[str, Any]) -> Path:
    """
    Create a launch manager configuration JSON file.

    Parameters
    ----------
    config_path : Path
        Path where the configuration file should be created.
    components : dict
        Component definitions for the launch manager.
    run_targets : dict
        Run target definitions.

    Returns
    -------
    Path
        Path to the created configuration file.
    """
    config = {
        "schema_version": 1,
        "defaults": {
            "deployment_config": {
                "bin_dir": "/tmp/lifecycle_test/bin/",
                "ready_recovery_action": {"restart": {"number_of_attempts": 1, "delay_before_restart": 0.5}},
                "sandbox": {
                    "uid": 0,
                    "gid": 0,
                    "supplementary_group_ids": [],
                    "scheduling_policy": "SCHED_OTHER",
                    "scheduling_priority": 1,
                },
            },
            "component_properties": {
                "application_profile": {
                    "application_type": "Reporting",
                    "is_self_terminating": False,
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
        "components": components,
        "run_targets": run_targets,
        "initial_run_target": "startup",
        "fallback_run_target": {
            "description": "Fallback state",
            "depends_on": [],
            "transition_timeout": 1.5,
        },
    }
    config_path.write_text(json.dumps(config, indent=2))
    return config_path


def create_daemon_integrated_config(
    config_path: Path,
    bin_dir: Path,
    components: dict[str, Any],
    run_targets: dict[str, Any] | None = None,
    enable_health_monitoring: bool = True,
) -> Path:
    """
    Create a Launch Manager configuration for daemon integration tests.

    Parameters
    ----------
    config_path : Path
        Path where the configuration file should be created.
    bin_dir : Path
        Directory containing application binaries.
    components : dict
        Component definitions with supervised applications.
    run_targets : dict, optional
        Run target definitions. If None, uses default startup/running/fallback.
    enable_health_monitoring : bool
        Whether to enable alive supervision for components.

    Returns
    -------
    Path
        Path to the created configuration file.
    """
    if run_targets is None:
        run_targets = {
            "startup": {"description": "System startup", "depends_on": []},
            "running": {"description": "Normal operation", "depends_on": []},
            "fallback": {"description": "Fallback mode", "depends_on": [], "transition_timeout": 5},
        }

    alive_supervision = {}
    if enable_health_monitoring:
        alive_supervision = {
            "alive_supervision": {
                "reporting_cycle": 0.1,
                "min_indications": 1,
                "max_indications": 3,
                "failed_cycles_tolerance": 2,
            }
        }

    config = {
        "schema_version": 1,
        "defaults": {
            "deployment_config": {
                "bin_dir": str(bin_dir) + "/",
                "ready_recovery_action": {"restart": {"number_of_attempts": 3, "delay_before_restart": 0.5}},
                "sandbox": {
                    "uid": 0,
                    "gid": 0,
                    "supplementary_group_ids": [],
                    "scheduling_policy": "SCHED_OTHER",
                    "scheduling_priority": 1,
                },
            },
            "component_properties": {
                "application_profile": {
                    "application_type": "Reporting",
                    "is_self_terminating": False,
                    **alive_supervision,
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
        "components": components,
        "run_targets": run_targets,
        "initial_run_target": "startup",
        "fallback_run_target": {"description": "Fallback state", "depends_on": [], "transition_timeout": 1.5},
    }
    config_path.write_text(json.dumps(config, indent=2))
    return config_path


def add_supervised_component(
    component_name: str,
    binary_name: str,
    app_type: str = "Reporting",
    depends_on: list[str] | None = None,
    process_args: list[str] | None = None,
    env_vars: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Create a component configuration for a supervised application.

    Parameters
    ----------
    component_name : str
        Unique component identifier.
    binary_name : str
        Name of the binary to execute.
    app_type : str
        Application type (Reporting, State_Manager, Reporting_And_Supervised, etc.).
    depends_on : list[str], optional
        List of component names this component depends on.
    process_args : list[str], optional
        Command-line arguments for the process.
    env_vars : dict[str, str], optional
        Environment variables to set.

    Returns
    -------
    dict
        Component configuration suitable for Launch Manager config.
    """
    component = {
        "description": f"{component_name} supervised application",
        "component_properties": {
            "binary_name": binary_name,
            "application_profile": {"application_type": app_type},
            "depends_on": depends_on or [],
            "process_arguments": process_args or [],
        },
    }

    if env_vars:
        component["deployment_config"] = {"environmental_variables": env_vars}

    return component


def copy_test_app_to_daemon_workspace(daemon_info: dict[str, Any], app_name: str, version: str = "rust") -> Path:
    """
    Copy a test application binary to the daemon workspace.

    Parameters
    ----------
    daemon_info : dict
        Daemon information from launch_manager_daemon fixture.
    app_name : str
        Name of the test application (e.g., "supervised_test_app").
    version : str
        Implementation version: "rust" or "cpp".

    Returns
    -------
    Path
        Path to the copied binary in daemon workspace.
    """
    # Build the test application
    tools = BazelTools(option_prefix=version)
    target_suffix = "_rust" if version == "rust" else "_cpp"
    target = f"//feature_integration_tests/test_apps:{app_name}{target_suffix}"
    tools.build(target)
    source_path = tools.find_target_path(target)

    # Copy to daemon bin directory
    dest_path = daemon_info["bin_dir"] / (app_name if version == "rust" else f"{app_name}_cpp")
    shutil.copy2(source_path, dest_path)
    dest_path.chmod(0o755)

    return dest_path


class LifecycleScenario(FitScenario):
    """
    Base class for lifecycle feature integration tests.

    Provides the ``temp_dir`` fixture shared by all lifecycle test classes,
    avoiding fixture duplication across subclasses.
    """

    @pytest.fixture(scope="class")
    def temp_dir(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        version: str,
    ) -> Generator[Path, None, None]:
        """
        Provide a temporary working directory for the lifecycle tests.

        The directory is named after the test class and parametrized version,
        and is automatically removed after the test class completes.

        Parameters
        ----------
        tmp_path_factory : pytest.TempPathFactory
            Built-in pytest factory for temporary directories.
        version : str
            Parametrized scenario version (``"rust"`` or ``"cpp"``).
        """
        yield from temp_dir_common(tmp_path_factory, self.__class__.__name__, version)
