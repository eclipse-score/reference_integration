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

from math import isclose
from pathlib import Path
from typing import Any

import pytest
from fit_scenario import ResultCode
from persistency_scenario import PersistencyScenario, read_kvs_snapshot
from test_properties import add_test_properties
from testing_utils import ScenarioResult

pytestmark = pytest.mark.parametrize("version", ["rust", "cpp"], scope="class")


class SupportedDatatypesScenario(PersistencyScenario):
    """Common base for supported datatypes scenarios."""

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path) -> dict[str, Any]:
        return {
            "kvs_parameters_1": {
                "kvs_parameters": {
                    "instance_id": 1,
                    "dir": str(temp_dir),
                },
            },
        }


@add_test_properties(
    partially_verifies=[
        "feat_req__persistency__support_datatype_value",
        "feat_req__persistency__support_datatype_keys",
        "feat_req__persistency__store_data",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestAllValueTypes(SupportedDatatypesScenario):
    """
    Verify that all nine KVS value types coexist in a single flushed snapshot.

    All nine types (i32, u32, i64, u64, f64, bool, str, arr, obj) are written
    to one KVS instance and persisted in a single flush. Python verifies every
    key is present with the correct type tag and value, confirming that multiple
    value types do not interfere with each other in one atomic storage outcome.
    This verifies multi-type coexistence — exercising feat_req__persistency__support_datatype_value,
    feat_req__persistency__support_datatype_keys, and
    feat_req__persistency__store_data together.
    """

    _EXPECTED_ALL_TYPES: dict[str, dict[str, Any]] = {
        "i32_key": {"t": "i32", "v": -321},
        "u32_key": {"t": "u32", "v": 1234},
        "i64_key": {"t": "i64", "v": -123456789},
        "u64_key": {"t": "u64", "v": 123456789},
        "f64_key": {"t": "f64", "v": -5432.1},
        "bool_key": {"t": "bool", "v": True},
        "str_key": {"t": "str", "v": "example"},
        "arr_key": {
            "t": "arr",
            "v": [
                {"t": "f64", "v": 321.5},
                {"t": "bool", "v": False},
                {"t": "str", "v": "hello"},
                {"t": "null", "v": None},
                {"t": "arr", "v": []},
                {"t": "obj", "v": {"sub-number": {"t": "f64", "v": 789.0}}},
            ],
        },
        "obj_key": {"t": "obj", "v": {"sub-number": {"t": "f64", "v": 789.0}}},
    }

    @staticmethod
    def _assert_tagged_value(actual: dict[str, Any], expected: dict[str, Any]) -> None:
        """Recursively compare tagged KVS values with tolerance for f64 types."""
        assert actual["t"] == expected["t"]
        value_type = expected["t"]

        if value_type == "f64":
            assert isclose(actual["v"], expected["v"], abs_tol=1e-4)
            return

        if value_type == "arr":
            assert isinstance(actual["v"], list)
            assert len(actual["v"]) == len(expected["v"])
            for actual_item, expected_item in zip(actual["v"], expected["v"]):
                TestAllValueTypes._assert_tagged_value(actual_item, expected_item)
            return

        if value_type == "obj":
            assert isinstance(actual["v"], dict)
            assert set(actual["v"].keys()) == set(expected["v"].keys())
            for key, expected_item in expected["v"].items():
                TestAllValueTypes._assert_tagged_value(actual["v"][key], expected_item)
            return

        assert actual["v"] == expected["v"]

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "persistency.supported_datatypes.all_value_types"

    def test_all_types_in_snapshot(self, results: ScenarioResult, temp_dir: Path) -> None:
        """
        All nine type-tagged key-value pairs must be present in the snapshot
        with the correct type tags and values written by the scenario.
        """
        assert results.return_code == ResultCode.SUCCESS
        snapshot = read_kvs_snapshot(temp_dir, 1)

        for key, expected_tagged in self._EXPECTED_ALL_TYPES.items():
            assert key in snapshot, f"Expected key '{key}' in snapshot"
            self._assert_tagged_value(snapshot[key], expected_tagged)
