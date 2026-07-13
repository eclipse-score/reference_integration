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
Feature integration tests for configuration file management.

Tests verify that the Launch Manager supports modular configuration files
including OCI runtime configuration compatibility and validation.
"""

from pathlib import Path
from typing import Any

import pytest
from fit_scenario import ResultCode
from lifecycle_scenario import LifecycleScenario
from test_properties import add_test_properties
from testing_utils import LogContainer, ScenarioResult

pytestmark = pytest.mark.parametrize("version", ["rust", "cpp"], scope="class")


@add_test_properties(
    partially_verifies=[
        "feat_req__lifecycle__modular_config_support",
        "feat_req__lifecycle__runtime_config_compat",
        "feat_req__lifecycle__session_extension",
        "feat_req__lifecycle__clustering_modules_supp",
        "feat_req__lifecycle__central_default_defines",
        "feat_req__lifecycle__lazy_check",
        "feat_req__lifecycle__deps_visualization",
        "feat_req__lifecycle__offline_config_valid",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestConfigurationManagement(LifecycleScenario):
    """
    Verify configuration file management support.

    This test confirms that the Launch Manager supports modular
    configuration files with proper validation and extension.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.configuration_management"

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path) -> dict[str, Any]:
        return {
            "test": {
                "test_duration_ms": 200,
                "config_modules": ["base", "extended", "runtime"],
                "use_oci_config": True,
            }
        }

    def test_modular_config_support(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that modular configuration is supported.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            for module in ["base", "extended", "runtime"]:
                assert f"Configuration module loaded: {module}" in results.stdout, (
                    f"Configuration module {module} not loaded"
                )
        else:
            for module in ["base", "extended", "runtime"]:
                config_logs = logs_info_level.get_logs(
                    field="message", pattern=f"Configuration module loaded: {module}"
                )
                assert len(config_logs) > 0, f"Configuration module {module} not loaded"

    def test_oci_compatibility(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that OCI runtime configuration is compatible.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "OCI runtime config compatible" in results.stdout, "OCI compatibility failed"
        else:
            oci_logs = logs_info_level.get_logs(field="message", value="OCI runtime config compatible")
            assert len(oci_logs) > 0, "OCI compatibility failed"

    def test_session_extension(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that session can be extended with new configuration.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Session extended with new configuration" in results.stdout, "Session extension failed"
        else:
            extension_logs = logs_info_level.get_logs(field="message", value="Session extended with new configuration")
            assert len(extension_logs) > 0, "Session extension failed"

    def test_module_clustering(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that components can be clustered as modules.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Components clustered in modules" in results.stdout, "Module clustering failed"
        else:
            cluster_logs = logs_info_level.get_logs(field="message", value="Components clustered in modules")
            assert len(cluster_logs) > 0, "Module clustering failed"

    def test_default_properties(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that central default properties are defined.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Default properties applied" in results.stdout, "Default properties not applied"
        else:
            defaults_logs = logs_info_level.get_logs(field="message", value="Default properties applied")
            assert len(defaults_logs) > 0, "Default properties not applied"

    def test_lazy_executable_check(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that executable availability is checked lazily.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Lazy executable check enabled" in results.stdout, "Lazy check not enabled"
        else:
            lazy_logs = logs_info_level.get_logs(field="message", value="Lazy executable check enabled")
            assert len(lazy_logs) > 0, "Lazy check not enabled"

    def test_config_validation(self, results: ScenarioResult, logs_info_level: LogContainer, version: str) -> None:
        """
        Verify that configuration validation works.
        """
        assert results.return_code == ResultCode.SUCCESS

        if version == "cpp":
            assert "Configuration validated successfully" in results.stdout, "Configuration validation failed"
        else:
            validation_logs = logs_info_level.get_logs(field="message", value="Configuration validated successfully")
            assert len(validation_logs) > 0, "Configuration validation failed"
