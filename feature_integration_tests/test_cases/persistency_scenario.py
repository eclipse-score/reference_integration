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
Helpers and base scenario class for persistency feature integration tests.

``create_kvs_defaults_file`` and ``read_kvs_snapshot`` provide the file-system
operations that test methods use to set up and inspect KVS state.
``PersistencyScenario`` is a :class:`FitScenario` subclass that supplies the
shared ``temp_dir`` fixture so individual test classes do not have to duplicate it.
"""

import json
from collections.abc import Generator
from pathlib import Path
from zlib import adler32

import pytest
from fit_scenario import FitScenario, temp_dir_common


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


def read_kvs_snapshot(dir_path: Path, instance_id: int, snapshot_id: int = 0) -> dict:
    """
    Read and parse the KVS snapshot JSON for a given instance.

    Supports both the Rust/normalized envelope format {"t":"obj","v":{...}}
    and the raw C++ format {key: {...}}. Returns the inner key -> tagged-value mapping.

    Parameters
    ----------
    dir_path : Path
        Working directory containing the KVS snapshot files.
    instance_id : int
        KVS instance identifier used in the filename convention.
    snapshot_id : int, optional
        Snapshot sequence number (default 0).

    Returns
    -------
    dict
        Mapping of key -> tagged-value dict, e.g. {"mykey": {"t": "f64", "v": 1.0}}.
    """
    path = dir_path / f"kvs_{instance_id}_{snapshot_id}.json"
    data = json.loads(path.read_text())
    if isinstance(data, dict) and data.get("t") == "obj" and "v" in data:
        return data["v"]
    return data


class PersistencyScenario(FitScenario):
    """
    Base class for persistency feature integration tests.

    Provides the ``temp_dir`` fixture shared by all persistency test classes,
    avoiding fixture duplication across subclasses.
    """

    @pytest.fixture(scope="class")
    def temp_dir(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        version: str,
    ) -> Generator[Path, None, None]:
        """
        Provide a temporary working directory for the KVS instance.

        The directory is named after the test class and parametrized version,
        and is automatically removed after the test class completes.

        Parameters
        ----------
        tmp_path_factory : pytest.TempPathFactory
            Built-in pytest factory for temporary directories.
        version : str
            Parametrized scenario version (``"rust"`` or ``"cpp"``).
        """
        yield from temp_dir_common(tmp_path_factory, self.__class__.__name__, version)
