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
import shutil
from pathlib import Path
from typing import Generator
from zlib import adler32

import pytest
from testing_utils import (
    BazelTools,
    BuildTools,
    LogContainer,
    Scenario,
    ScenarioResult,
)


class ResultCode:
    """
    Test scenario exit codes.
    """

    SUCCESS = 0
    PANIC = 101
    SIGKILL = -9
    SIGABRT = -6


def temp_dir_common(
    tmp_path_factory: pytest.TempPathFactory, base_name: str, *args: str
) -> Generator[Path, None, None]:
    """
    Create temporary directory and remove it after test.
    Common implementation to be reused by fixtures.

    Returns generator providing numbered path to temporary directory.
    E.g., '<TMP_PATH>/<BASE_NAME>-<ARG1>-<ARG2><NUMBER>/'.

    Parameters
    ----------
    tmp_path_factory : pytest.TempPathFactory
        Factory for temporary directories.
    base_name : str
        Base directory name.
        'self.__class__.__name__' use is recommended.
    *args : Any
        Other parameters to be included in directory name.
    """
    parts = [base_name, *args]
    dir_name = "-".join(parts)
    dir_path = tmp_path_factory.mktemp(dir_name, numbered=True)
    yield dir_path
    shutil.rmtree(dir_path)


def create_kvs_defaults_file(dir_path: Path, instance_id: int, values: dict) -> Path:
    """
    Create a KVS defaults JSON file and matching hash file at conventional paths.

    KVS expects defaults at: {dir}/kvs_{instance_id}_default.json
    and the hash at:         {dir}/kvs_{instance_id}_default.hash

    The JSON format is: {"key": {"t": "type_tag", "v": value}, ...}
    The hash is adler32 of the JSON string, written as 4 big-endian bytes.

    Parameters
    ----------
    dir_path : Path
        Working directory for the KVS instance.
    instance_id : int
        KVS instance identifier.
    values : dict
        Mapping of key -> (type_tag, value), e.g. {"my_key": ("f64", 1.0)}.

    Returns
    -------
    Path
        Path to the created JSON defaults file.
    """
    json_path = dir_path / f"kvs_{instance_id}_default.json"
    hash_path = dir_path / f"kvs_{instance_id}_default.hash"

    data = {key: {"t": type_tag, "v": val} for key, (type_tag, val) in values.items()}
    json_str = json.dumps(data)

    json_path.write_text(json_str)
    hash_path.write_bytes(adler32(json_str.encode()).to_bytes(length=4, byteorder="big"))
    return json_path


class FitScenario(Scenario):
    """
    CIT test scenario definition.
    """

    @pytest.fixture(scope="class")
    def build_tools(self, request: pytest.FixtureRequest) -> BuildTools:
        # Use test parametrization when available; default to rust for non-parametrized tests.
        if "version" in request.fixturenames:
            return BazelTools(option_prefix=request.getfixturevalue("version"))
        return BazelTools(option_prefix="rust")

    def expect_command_failure(self, *args, **kwargs) -> bool:
        """
        Expect command failure (e.g., non-zero return code or hang).
        """
        return False

    @pytest.fixture(scope="class")
    def results(
        self,
        command: list[str],
        execution_timeout: float,
        *args,
        **kwargs,
    ) -> ScenarioResult:
        result = self._run_command(command, execution_timeout, args, kwargs)
        success = result.return_code == ResultCode.SUCCESS and not result.hang
        if self.expect_command_failure() and success:
            raise RuntimeError(f"Command execution succeeded unexpectedly: {result=}")
        if not self.expect_command_failure() and not success:
            raise RuntimeError(f"Command execution failed unexpectedly: {result=}")
        return result

    @pytest.fixture(scope="class")
    def logs_target(self, target_path: Path, logs: LogContainer) -> LogContainer:
        """
        Logs with messages generated strictly by the tested code.

        Parameters
        ----------
        target_path : Path
            Path to test scenario executable.
        logs : LogContainer
            Unfiltered logs.
        """
        return logs.get_logs(field="target", pattern=f"{target_path.name}.*")

    @pytest.fixture(scope="class")
    def logs_info_level(self, logs_target: LogContainer) -> LogContainer:
        """
        Logs with messages with INFO level.

        Parameters
        ----------
        logs_target : LogContainer
            Logs with messages generated strictly by the tested code.
        """
        return logs_target.get_logs(field="level", value="INFO")

    @pytest.fixture(autouse=True)
    def print_to_report(
        self,
        request: pytest.FixtureRequest,
        logs: LogContainer,
        logs_target: LogContainer,
    ) -> None:
        """
        Print traces to stdout.

        Allowed "--traces" values:
        - "none" - show no traces.
        - "target" - show traces generated by test code.
        - "all" - show all traces.

        Parameters
        ----------
        request : FixtureRequest
            Test request built-in fixture.
        logs : LogContainer
            Test scenario execution logs.
        logs_target : LogContainer
            Logs with messages generated strictly by the tested code.
        """
        traces_param = request.config.getoption("--traces")
        match traces_param:
            case "all":
                traces = logs
            case "target":
                traces = logs_target
            case "none":
                traces = LogContainer()
            case _:
                raise RuntimeError(f'Invalid "--traces" value: {traces_param}')

        for trace in traces:
            print(trace)
