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

import json
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from fit_scenario import FitScenario, create_kvs_defaults_file, temp_dir_common
from test_properties import add_test_properties
from testing_utils import LogContainer

pytestmark = pytest.mark.parametrize("version", ["rust", "cpp"], scope="class")

# Test constants — f64 to match KVS defaults type-tagged format.
_KEYS = ["key1", "key2", "key3"]
_DEFAULT_VALUES = [100.0, 200.0, 300.0]
_OVERRIDE_VALUES = [111.0, 222.0, 333.0]


@add_test_properties(
    partially_verifies=["feat_req__persistency__reset_to_default"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestResetToDefault(FitScenario):
    """
    Verifies that keys can be reset to their default values using remove_key() API.
    When a key is removed from KVS with defaults enabled, it should revert to the
    default value if one exists.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "persistency.reset_to_default"

    @pytest.fixture(scope="class")
    def temp_dir(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        version: str,
    ) -> Generator[Path, None, None]:
        yield from temp_dir_common(tmp_path_factory, self.__class__.__name__, version)

    @pytest.fixture(scope="class")
    def defaults_file(self, temp_dir: Path) -> Path:
        """
        Create KVS defaults JSON and hash files at the conventional paths.
        KVS finds defaults automatically by convention: kvs_{instance_id}_default.json
        """
        return create_kvs_defaults_file(
            temp_dir,
            1,
            {key: ("f64", val) for key, val in zip(_KEYS, _DEFAULT_VALUES)},
        )

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path, defaults_file: Path) -> dict[str, Any]:
        # defaults_file fixture must run first to create the file before KVS initializes
        return {
            "kvs_parameters_1": {
                "kvs_parameters": {
                    "instance_id": 1,
                    "dir": str(temp_dir),
                    "defaults": "optional",
                },
            },
            "test": {
                "keys": _KEYS,
                "override_values": _OVERRIDE_VALUES,
                "default_values": _DEFAULT_VALUES,
            },
        }

    def test_reset_single_key(self, logs_info_level: LogContainer):
        """Verify that a single key can be reset to its default value."""
        log_override = logs_info_level.find_log("operation", value="override_key2")
        assert log_override is not None
        assert abs(log_override.value - _OVERRIDE_VALUES[1]) < 1e-5
        if hasattr(log_override, "is_default") and log_override.is_default != "unknown":
            assert log_override.is_default == "false"

        log_reset = logs_info_level.find_log("operation", value="after_reset_key2")
        assert log_reset is not None
        assert abs(log_reset.value - _DEFAULT_VALUES[1]) < 1e-5
        if hasattr(log_reset, "is_default") and log_reset.is_default != "unknown":
            assert log_reset.is_default == "true"

    def test_other_keys_unchanged(self, logs_info_level: LogContainer):
        """Verify that resetting one key doesn't affect other keys."""
        log_key1 = logs_info_level.find_log("operation", value="check_key1_after_reset")
        assert log_key1 is not None
        assert abs(log_key1.value - _OVERRIDE_VALUES[0]) < 1e-5
        if hasattr(log_key1, "is_default") and log_key1.is_default != "unknown":
            assert log_key1.is_default == "false"

        log_key3 = logs_info_level.find_log("operation", value="check_key3_after_reset")
        assert log_key3 is not None
        assert abs(log_key3.value - _OVERRIDE_VALUES[2]) < 1e-5
        if hasattr(log_key3, "is_default") and log_key3.is_default != "unknown":
            assert log_key3.is_default == "false"

    def test_reset_persisted(self, temp_dir: Path):
        """Verify that the KVS snapshot file exists after reset."""
        kvs_file = temp_dir / "kvs_1_0.json"
        assert kvs_file.exists()
        data = json.loads(kvs_file.read_text())
        assert "v" in data
