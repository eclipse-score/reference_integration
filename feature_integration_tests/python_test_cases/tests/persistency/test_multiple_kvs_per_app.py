# *******************************************************************************
# Copyright (c) 2025 Contributors to the Eclipse Foundation
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
from pathlib import Path
from typing import Any, Generator

import pytest
from fit_scenario import FitScenario, temp_dir_common
from test_properties import add_test_properties
from testing_utils import LogContainer


@add_test_properties(
    partially_verifies=["feat_req__persistency__multiple_kvs"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestMultipleInstanceIds(FitScenario):
    """
    Verifies that multiple KVS instances with different IDs store and retrieve independent values without interference.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "persistency.multiple_kvs_per_app"

    @pytest.fixture(scope="class")
    def kvs_key(self) -> str:
        return "number"

    @pytest.fixture(scope="class")
    def kvs_value_1(self) -> float:
        return 111.1

    @pytest.fixture(scope="class")
    def kvs_value_2(self) -> float:
        return 222.2

    @pytest.fixture(scope="class")
    def temp_dir(
        self,
        tmp_path_factory: pytest.TempPathFactory,
    ) -> Generator[Path, None, None]:
        yield from temp_dir_common(tmp_path_factory, self.__class__.__name__)

    @pytest.fixture(scope="class")
    def test_config(
        self,
        temp_dir: Path,
        kvs_key: str,
        kvs_value_1: float,
        kvs_value_2: float,
    ) -> dict[str, Any]:
        return {
            "kvs_parameters_1": {
                "kvs_parameters": {"instance_id": 1, "dir": str(temp_dir)},
            },
            "kvs_parameters_2": {
                "kvs_parameters": {"instance_id": 2, "dir": str(temp_dir)},
            },
            "test": {"key": kvs_key, "value_1": kvs_value_1, "value_2": kvs_value_2},
        }

    def test_logged_execution(
        self,
        kvs_key: str,
        kvs_value_1: float,
        kvs_value_2: float,
        logs_info_level: LogContainer,
    ):
        log1 = logs_info_level.find_log("instance", value="InstanceId(1)")
        assert log1 is not None
        assert log1.key == kvs_key
        assert log1.value == kvs_value_1

        log2 = logs_info_level.find_log("instance", value="InstanceId(2)")
        assert log2 is not None
        assert log2.key == kvs_key
        assert log2.value == kvs_value_2

    def test_kvs_write_results(
        self,
        temp_dir: Path,
        kvs_key: str,
        kvs_value_1: float,
        kvs_value_2: float,
    ):
        # Verify KVS Instance(1)
        kvs1_file = temp_dir / "kvs_1_0.json"
        data1 = json.loads(kvs1_file.read_text())
        assert data1["v"][kvs_key]["v"] == kvs_value_1

        # Verify KVS Instance(2)
        kvs2_file = temp_dir / "kvs_2_0.json"
        data2 = json.loads(kvs2_file.read_text())
        assert data2["v"][kvs_key]["v"] == kvs_value_2
