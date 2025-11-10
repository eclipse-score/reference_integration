import json
from pathlib import Path
from typing import Any, Generator

import pytest
from fit_scenario import FitScenario, temp_dir_common
from testing_utils import LogContainer


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
