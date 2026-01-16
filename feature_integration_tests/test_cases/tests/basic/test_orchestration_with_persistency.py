import json
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from fit_scenario import FitScenario, temp_dir_common
from test_properties import add_test_properties
from testing_utils import LogContainer


@add_test_properties(
    partially_verifies=["feat_req__persistency__persistency"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestOrchWithPersistency(FitScenario):
    """
    Tests orchestration with persistency scenario.
    Scenario uses Orchestration and Kyron to run program `run_count` times.
    Each run increments counter stored by KVS in `tmp_dir`.
    After all runs, test verifies that counter value equals `run_count`.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "basic.orchestration_with_persistency"

    @pytest.fixture(scope="class", params=[1, 5])
    def run_count(self, request) -> int:
        return request.param

    @pytest.fixture(scope="class")
    def temp_dir(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        run_count: int,  # run_count is required to ensure proper order of fixture calls
    ) -> Generator[Path, None, None]:
        yield from temp_dir_common(tmp_path_factory, self.__class__.__name__)

    @pytest.fixture(scope="class")
    def test_config(self, run_count: int, temp_dir: Path) -> dict[str, Any]:
        return {
            "runtime": {"task_queue_size": 2, "workers": 4},
            "test": {"run_count": run_count, "kvs_path": str(temp_dir)},
        }

    def test_kvs_logged_execution(self, run_count: int, logs_info_level: LogContainer):
        """Verify that all runs have been logged."""
        logs = logs_info_level.get_logs(field="run_cycle_number")
        logged_cycles = [log.run_cycle_number for log in logs]
        expected_cycles = list(range(1, run_count + 1))
        assert logged_cycles == expected_cycles

    def test_kvs_write_results(self, temp_dir: Path, run_count: int):
        """Verify that KVS file contains correct final run count."""
        kvs_file = temp_dir / "kvs_1_0.json"
        data = json.loads(kvs_file.read_text())
        assert data["v"]["run_cycle_number"]["v"] == run_count


@add_test_properties(
    partially_verifies=["feat_req__persistency__multiple_kvs"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestConcurrentKVS(FitScenario):
    """
    Tests persistency running in orchestration scenario using multiple KVS files concurrently.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "basic.concurrent_kvs"

    @pytest.fixture(scope="class", params=[1, 5])
    def run_count(self, request) -> int:
        return request.param

    @pytest.fixture(scope="class")
    def temp_dir(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        run_count: int,  # run_count is required to ensure proper order of fixture calls
    ) -> Generator[Path, None, None]:
        yield from temp_dir_common(tmp_path_factory, self.__class__.__name__)

    @pytest.fixture(scope="class")
    def test_config(self, run_count: int, temp_dir: Path) -> dict[str, Any]:
        return {
            "runtime": {"task_queue_size": 2, "workers": 4},
            "test": {"run_count": run_count, "kvs_path": str(temp_dir)},
        }

    def test_kvs_logged_execution(self, run_count: int, logs_info_level: LogContainer):
        """Verify that all runs have been logged."""
        logs = logs_info_level.get_logs(field="run_cycle_number")
        for log_group in logs.group_by("kvs_instance_id").values():
            logged_cycles = [log.run_cycle_number for log in log_group]
            expected_cycles = list(range(1, run_count + 1))
            assert logged_cycles == expected_cycles

    def test_kvs_write_results(self, temp_dir: Path, run_count: int):
        """Verify that each KVS file contains correct final run count."""
        # Verify KVS Instance(1)
        kvs1_file = temp_dir / "kvs_1_0.json"
        data1 = json.loads(kvs1_file.read_text())
        assert data1["v"]["run_cycle_number"]["v"] == run_count

        # Verify KVS Instance(2)
        kvs2_file = temp_dir / "kvs_2_0.json"
        data2 = json.loads(kvs2_file.read_text())
        assert data2["v"]["run_cycle_number"]["v"] == run_count

        # Verify KVS Instance(3)
        kvs3_file = temp_dir / "kvs_3_0.json"
        data3 = json.loads(kvs3_file.read_text())
        assert data3["v"]["run_cycle_number"]["v"] == run_count


@add_test_properties(
    partially_verifies=[
        "feat_req__persistency__multiple_kvs",
        "feat_req__persistency__support_datatype_value",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestMultipleKVS(FitScenario):
    """
    Tests persistency running in orchestration scenario using multiple KVS instances.
    Validates all basic data types stored in KVS.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "basic.multiple_kvs"

    @pytest.fixture(scope="class")
    def run_count(self) -> int:
        return 1

    @pytest.fixture(scope="class")
    def temp_dir(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        run_count: int,  # run_count is required to ensure proper order of fixture calls
    ) -> Generator[Path, None, None]:
        yield from temp_dir_common(tmp_path_factory, self.__class__.__name__)

    @pytest.fixture(scope="class")
    def test_config(self, run_count: int, temp_dir: Path) -> dict[str, Any]:
        return {
            "runtime": {"task_queue_size": 256, "workers": 4},
            "test": {"run_count": run_count, "kvs_path": str(temp_dir)},
        }

    def test_kvs_cycle_write_results(self, temp_dir: Path, run_count: int):
        """Verify that KVS file contains correct final run count."""
        # Verify KVS Instance(1)
        kvs1_file = temp_dir / "kvs_1_0.json"
        data1 = json.loads(kvs1_file.read_text())
        assert data1["v"]["run_cycle_number"]["v"] == run_count

    def test_kvs_write_i32_max(self, temp_dir: Path):
        """Verify that KVS file contains correct value."""
        # Verify KVS Instance(2)
        kvs2_file = temp_dir / "kvs_2_0.json"
        data2 = json.loads(kvs2_file.read_text())
        assert data2["v"]["key_i32_max"]["v"] == 2147483647
        assert data2["v"]["key_i32_max"]["t"] == "i32"

    def test_kvs_write_i32_min(self, temp_dir: Path):
        """Verify that KVS file contains correct value."""
        # Verify KVS Instance(2)
        kvs2_file = temp_dir / "kvs_2_0.json"
        data2 = json.loads(kvs2_file.read_text())
        assert data2["v"]["key_i32_min"]["v"] == -2147483648
        assert data2["v"]["key_i32_min"]["t"] == "i32"

    def test_kvs_write_u32_max(self, temp_dir: Path):
        """Verify that KVS file contains correct value."""
        # Verify KVS Instance(2)
        kvs2_file = temp_dir / "kvs_2_0.json"
        data2 = json.loads(kvs2_file.read_text())
        assert data2["v"]["key_u32_max"]["v"] == 4294967295
        assert data2["v"]["key_u32_max"]["t"] == "u32"

    def test_kvs_write_u32_min(self, temp_dir: Path):
        """Verify that KVS file contains correct value."""
        # Verify KVS Instance(2)
        kvs2_file = temp_dir / "kvs_2_0.json"
        data2 = json.loads(kvs2_file.read_text())
        assert data2["v"]["key_u32_min"]["v"] == 0
        assert data2["v"]["key_u32_min"]["t"] == "u32"

    @pytest.mark.xfail(reason="https://github.com/eclipse-score/persistency/issues/204")
    def test_kvs_write_i64_max(self, temp_dir: Path):
        """Verify that KVS file contains correct value."""
        # Verify KVS Instance(2)
        kvs2_file = temp_dir / "kvs_2_0.json"
        data2 = json.loads(kvs2_file.read_text())
        assert data2["v"]["key_i64_max"]["v"] == 9223372036854775807
        assert data2["v"]["key_i64_max"]["t"] == "i64"

    @pytest.mark.xfail(reason="https://github.com/eclipse-score/persistency/issues/204")
    def test_kvs_write_i64_min(self, temp_dir: Path):
        """Verify that KVS file contains correct value."""
        # Verify KVS Instance(2)
        kvs2_file = temp_dir / "kvs_2_0.json"
        data2 = json.loads(kvs2_file.read_text())
        assert data2["v"]["key_i64_min"]["v"] == -9223372036854775808
        assert data2["v"]["key_i64_min"]["t"] == "i64"

    @pytest.mark.xfail(reason="https://github.com/eclipse-score/persistency/issues/204")
    def test_kvs_write_u64_max(self, temp_dir: Path):
        """Verify that KVS file contains correct value."""
        # Verify KVS Instance(2)
        kvs2_file = temp_dir / "kvs_2_0.json"
        data2 = json.loads(kvs2_file.read_text())
        assert data2["v"]["key_u64_max"]["v"] == 18446744073709551615
        assert data2["v"]["key_u64_max"]["t"] == "u64"

    def test_kvs_write_u64_min(self, temp_dir: Path):
        """Verify that KVS file contains correct value."""
        # Verify KVS Instance(2)
        kvs2_file = temp_dir / "kvs_2_0.json"
        data2 = json.loads(kvs2_file.read_text())
        assert data2["v"]["key_u64_min"]["v"] == 0
        assert data2["v"]["key_u64_min"]["t"] == "u64"

    def test_kvs_write_f64(self, temp_dir: Path):
        """Verify that KVS file contains correct value."""
        # Verify KVS Instance(2)
        kvs2_file = temp_dir / "kvs_2_0.json"
        data2 = json.loads(kvs2_file.read_text())
        assert data2["v"]["key_f64"]["v"] == 1.2345
        assert data2["v"]["key_f64"]["t"] == "f64"

    def test_kvs_write_bool(self, temp_dir: Path):
        """Verify that KVS file contains correct value."""
        # Verify KVS Instance(2)
        kvs2_file = temp_dir / "kvs_2_0.json"
        data2 = json.loads(kvs2_file.read_text())
        assert data2["v"]["key_bool"]["v"] == True  # noqa: E712
        assert data2["v"]["key_bool"]["t"] == "bool"

    def test_kvs_write_string(self, temp_dir: Path):
        """Verify that KVS file contains correct value."""
        # Verify KVS Instance(2)
        kvs2_file = temp_dir / "kvs_2_0.json"
        data2 = json.loads(kvs2_file.read_text())
        assert data2["v"]["key_String"]["v"] == "TestString"
        assert data2["v"]["key_String"]["t"] == "str"

    def test_kvs_write_null(self, temp_dir: Path):
        """Verify that KVS file contains correct value."""
        # Verify KVS Instance(2)
        kvs2_file = temp_dir / "kvs_2_0.json"
        data2 = json.loads(kvs2_file.read_text())
        assert data2["v"]["key_Null"]["v"] is None
        assert data2["v"]["key_Null"]["t"] == "null"

    def test_kvs_write_array(self, temp_dir: Path):
        """Verify that KVS file contains correct values."""
        # Verify KVS Instance(2)
        kvs2_file = temp_dir / "kvs_2_0.json"
        data2 = json.loads(kvs2_file.read_text())
        assert data2["v"]["key_Array"]["v"] == [
            {"t": "i32", "v": 1},
            {"t": "i32", "v": 2},
            {"t": "i32", "v": 3},
        ]
        assert data2["v"]["key_Array"]["t"] == "arr"

    def test_kvs_write_map(self, temp_dir: Path):
        """Verify that KVS file contains correct values."""
        # Verify KVS Instance(2)
        kvs2_file = temp_dir / "kvs_2_0.json"
        data2 = json.loads(kvs2_file.read_text())
        assert data2["v"]["key_Map"]["v"] == {
            "inner_key": {"t": "i32", "v": 1},
        }
        assert data2["v"]["key_Map"]["t"] == "obj"
