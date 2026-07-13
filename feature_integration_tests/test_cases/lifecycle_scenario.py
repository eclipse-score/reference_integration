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

from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from fit_scenario import FitScenario, temp_dir_common


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
