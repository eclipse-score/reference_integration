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
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from fit_scenario import FitScenario, temp_dir_common


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
        "initial_run_target": "Startup",
        "fallback_run_target": {
            "description": "Fallback state",
            "depends_on": [],
            "transition_timeout": 1.5,
        },
    }
    config_path.write_text(json.dumps(config, indent=2))
    return config_path


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
