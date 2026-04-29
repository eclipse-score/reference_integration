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

from collections.abc import Generator
from math import isclose
from pathlib import Path
from typing import Any

import pytest
from fit_scenario import FitScenario, ResultCode, create_kvs_defaults_file, read_kvs_snapshot, temp_dir_common
from test_properties import add_test_properties
from testing_utils import ScenarioResult

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
    Verifies that remove_key() resets a key to default by removing it from storage.
    After removing key2 and flushing: key1 and key3 remain in the snapshot with their
    override values, while key2 is absent (reverts to default lookup at runtime).
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

    def test_storage_state(self, results: ScenarioResult, temp_dir: Path) -> None:
        """
        Verify the KVS snapshot reflects the expected state after remove_key:
        - key2 (index 1) was removed and must be absent from the snapshot
        - key1 and key3 remain with their override values
        """
        assert results.return_code == ResultCode.SUCCESS
        snapshot = read_kvs_snapshot(temp_dir, 1)

        # key2 was removed — must be absent from snapshot
        assert _KEYS[1] not in snapshot, f"Reset key '{_KEYS[1]}' should be absent from snapshot after remove_key"

        # key1 and key3 remain with override values
        for i, key in enumerate(_KEYS):
            if i == 1:
                continue  # key2 already checked above
            assert key in snapshot, f"Key '{key}' should be present in snapshot"
            assert isclose(snapshot[key]["v"], _OVERRIDE_VALUES[i], abs_tol=1e-4), (
                f"Key '{key}': expected override {_OVERRIDE_VALUES[i]}, got {snapshot[key]['v']}"
            )
