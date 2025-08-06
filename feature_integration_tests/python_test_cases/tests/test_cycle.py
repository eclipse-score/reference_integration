import json
import logging
from typing import Any, Dict

import pytest
from docker.models.containers import Container


class FitTest:
    kvs_current_file = "/app/test_data/kvs_0_0.json"
    kvs_previous_file = "/app/test_data/kvs_0_1.json"

    def exec_binary(
        self,
        docker: Container,
        scenario_name: str,
        scenario_input: str,
        input_type: str = "arg",
    ):
        binary = "/app/target/debug/rust_test_scenarios"
        command = f"{binary} --name {scenario_name} --input-type {input_type} --input '{scenario_input}'"
        logging.debug(f"Executing binary in docker container: {command}")
        docker.exec_run(command)

    def read_json_file(self, docker: Container, file_path: str) -> Dict[str, Any]:
        result = docker.exec_run(f"cat {file_path}")
        if result.exit_code != 0:
            logging.error(f"Failed to read file {file_path}: {result.output.decode()}")
            return {}
        output = result.output.decode()
        logging.debug(f"Reading JSON file from {file_path}: {output}")
        return json.loads(output)


@pytest.mark.PartiallyVerifies(
    [
        "feat_req__persistency__default_values",
        "feat_req__persistency__persistency",
        "feat_req__persistency__cpp_rust_interop",
    ]
)
@pytest.mark.FullyVerifies([])
@pytest.mark.Description(
    "Simple cycle tests to verify that the cycle counter increments correctly"
)
@pytest.mark.TestType("requirement-based")
@pytest.mark.DerivationTechnique("requirement-based")
class TestCycle(FitTest):
    @pytest.fixture(scope="class", autouse=True)
    def scenario_name(self):
        return "basic.cycle_counter"

    @pytest.fixture(scope="class", autouse=True)
    def test_input(self):
        return json.dumps({"runtime": {"task_queue_size": 256, "workers": 2}})

    def test_docker_is_clean(self, docker: Container):
        result = docker.exec_run("ls /app/test_data")
        output = result.output.decode()
        assert "kvs_0_0.json" not in output, (
            "Container is not clean, test_data directory exists"
        )

    def test_first_cycle(self, docker: Container, scenario_name: str, test_input: str):
        self.exec_binary(
            docker,
            scenario_name=scenario_name,
            scenario_input=test_input,
        )
        data = self.read_json_file(docker, self.kvs_current_file)
        assert {"cycle_counter": 1} == data

    def test_second_cycle(self, docker: Container, scenario_name: str, test_input: str):
        self.exec_binary(docker, scenario_name=scenario_name, scenario_input=test_input)
        data_current = self.read_json_file(docker, self.kvs_current_file)
        assert {"cycle_counter": 2} == data_current
        data_previous = self.read_json_file(docker, self.kvs_previous_file)
        assert {"cycle_counter": 1} == data_previous

    def test_cycling(self, docker: Container, scenario_name: str, test_input: str):
        for _ in range(10):
            data_before_exec = self.read_json_file(docker, self.kvs_current_file)
            cycle_before_exec = data_before_exec["cycle_counter"]
            self.exec_binary(
                docker, scenario_name=scenario_name, scenario_input=test_input
            )
            data_after_exec = self.read_json_file(docker, self.kvs_current_file)
            cycle_after_exec = data_after_exec["cycle_counter"]
            assert cycle_after_exec == cycle_before_exec + 1, (
                f"Cycle counter did not increment: {cycle_before_exec} -> {cycle_after_exec}"
            )
