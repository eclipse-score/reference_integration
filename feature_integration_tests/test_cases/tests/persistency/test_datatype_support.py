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
from abc import abstractmethod
from collections.abc import Generator
from math import isclose
from pathlib import Path
from typing import Any

import pytest
from fit_scenario import FitScenario, ResultCode, temp_dir_common
from test_properties import add_test_properties
from testing_utils import LogContainer, ScenarioResult

pytestmark = pytest.mark.parametrize("version", ["rust", "cpp"], scope="class")


def assert_tagged_value(actual: dict[str, Any], expected: dict[str, Any]) -> None:
    """Recursively compare tagged values with tolerance for f64 types."""
    assert actual["t"] == expected["t"]
    value_type = expected["t"]

    if value_type == "f64":
        assert isclose(actual["v"], expected["v"], abs_tol=1e-5)
        return

    if value_type == "arr":
        assert isinstance(actual["v"], list)
        assert len(actual["v"]) == len(expected["v"])
        for actual_item, expected_item in zip(actual["v"], expected["v"]):
            assert_tagged_value(actual_item, expected_item)
        return

    if value_type == "obj":
        assert isinstance(actual["v"], dict)
        assert set(actual["v"].keys()) == set(expected["v"].keys())
        for key, expected_item in expected["v"].items():
            assert_tagged_value(actual["v"][key], expected_item)
        return

    assert actual["v"] == expected["v"]


class SupportedDatatypesScenario(FitScenario):
    """Common base for supported datatypes scenarios."""

    @pytest.fixture(scope="class")
    def temp_dir(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        version: str,
    ) -> Generator[Path, None, None]:
        yield from temp_dir_common(tmp_path_factory, self.__class__.__name__, version)

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
        "feat_req__persistency__support_datatype_keys",
        "feat_req__persistency__support_datatype_value",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestSupportedDatatypesKeys(SupportedDatatypesScenario):
    """Verifies that KVS supports UTF-8 string keys for storing values."""

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "persistency.supported_datatypes.keys"

    def test_ok(self, results: ScenarioResult, logs_info_level: LogContainer) -> None:
        assert results.return_code == ResultCode.SUCCESS

        logs = logs_info_level.get_logs(field="key")
        actual_keys = {log.key for log in logs}
        expected_keys = {
            "example",
            "emoji ✅❗😀",
            "greek ημα",
        }
        assert actual_keys == expected_keys


@add_test_properties(
    partially_verifies=[
        "feat_req__persistency__support_datatype_keys",
        "feat_req__persistency__support_datatype_value",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestSupportedDatatypesValues(SupportedDatatypesScenario):
    """Verifies that KVS supports all documented value types."""

    @abstractmethod
    def exp_key(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def exp_value(self) -> Any:
        raise NotImplementedError

    def exp_tagged(self) -> dict[str, Any]:
        return {"t": self.exp_key(), "v": self.exp_value()}

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return f"persistency.supported_datatypes.values.{self.exp_key()}"

    def test_ok(self, results: ScenarioResult, logs_info_level: LogContainer) -> None:
        assert results.return_code == ResultCode.SUCCESS

        logs = logs_info_level.get_logs(field="key", value=self.exp_key())
        assert len(logs) == 1
        log = logs[0]

        actual_value = json.loads(log.value)
        assert_tagged_value(actual_value, self.exp_tagged())


class TestSupportedDatatypesValues_I32(TestSupportedDatatypesValues):
    def exp_key(self) -> str:
        return "i32"

    def exp_value(self) -> Any:
        return -321


class TestSupportedDatatypesValues_U32(TestSupportedDatatypesValues):
    def exp_key(self) -> str:
        return "u32"

    def exp_value(self) -> Any:
        return 1234


class TestSupportedDatatypesValues_I64(TestSupportedDatatypesValues):
    def exp_key(self) -> str:
        return "i64"

    def exp_value(self) -> Any:
        return -123456789


class TestSupportedDatatypesValues_U64(TestSupportedDatatypesValues):
    def exp_key(self) -> str:
        return "u64"

    def exp_value(self) -> Any:
        return 123456789


class TestSupportedDatatypesValues_F64(TestSupportedDatatypesValues):
    def exp_key(self) -> str:
        return "f64"

    def exp_value(self) -> Any:
        return -5432.1


class TestSupportedDatatypesValues_Bool(TestSupportedDatatypesValues):
    def exp_key(self) -> str:
        return "bool"

    def exp_value(self) -> Any:
        return True


class TestSupportedDatatypesValues_String(TestSupportedDatatypesValues):
    def exp_key(self) -> str:
        return "str"

    def exp_value(self) -> Any:
        return "example"


class TestSupportedDatatypesValues_Array(TestSupportedDatatypesValues):
    def exp_key(self) -> str:
        return "arr"

    def exp_value(self) -> Any:
        return [
            {"t": "f64", "v": 321.5},
            {"t": "bool", "v": False},
            {"t": "str", "v": "hello"},
            {"t": "null", "v": None},
            {"t": "arr", "v": []},
            {
                "t": "obj",
                "v": {
                    "sub-number": {
                        "t": "f64",
                        "v": 789,
                    },
                },
            },
        ]


class TestSupportedDatatypesValues_Object(TestSupportedDatatypesValues):
    def exp_key(self) -> str:
        return "obj"

    def exp_value(self) -> Any:
        return {"sub-number": {"t": "f64", "v": 789}}
