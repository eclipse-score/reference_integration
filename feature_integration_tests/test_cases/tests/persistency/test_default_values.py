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
import re
from collections.abc import Generator
from math import isclose
from pathlib import Path
from typing import Any
from zlib import adler32

import pytest
from fit_scenario import FitScenario, ResultCode, create_kvs_defaults_file, temp_dir_common
from test_properties import add_test_properties
from testing_utils import LogContainer

pytestmark = pytest.mark.parametrize("version", ["rust", "cpp"], scope="class")

# KVS default value type tag and value pair used across tests.
# Using f64 to match KVS type-tagged JSON format.
_DEFAULT_KEY = "test_key"
_OVERRIDE_VALUE = 432.1

_PARITY_KEY = "test_number"
_PARITY_DEFAULT_VALUE = 123.4
_PARITY_OVERRIDE_VALUE = 432.1
_RESET_KEY_COUNT = 5
_RESET_DEFAULT_BASE = 10.0


def _format_f64(value: float) -> str:
    """
    Format a float with one decimal place to match KVS debug output.
    """
    return f"{value:.1f}"


def _reset_default_value(index: int) -> float:
    """
    Provide the default value for reset scenarios for a given index.
    """
    return _RESET_DEFAULT_BASE * (index + 1)


def _reset_override_value(index: int) -> float:
    """
    Provide the override value for reset scenarios for a given index.
    """
    return 123.4 * index


@add_test_properties(
    partially_verifies=["feat_req__persistency__default_values", "feat_req__persistency__default_value_get"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestDefaultValuesIgnored(FitScenario):
    """
    Verifies that with KvsDefaults::Ignored mode, default values are not loaded
    even if a defaults file exists in the working directory.
    Explicit set/get still works normally.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "persistency.default_values_ignored"

    @pytest.fixture(scope="class")
    def temp_dir(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        version: str,
    ) -> Generator[Path, None, None]:
        """
        Provide a temporary working directory for parity scenarios.
        """
        yield from temp_dir_common(tmp_path_factory, self.__class__.__name__, version)

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path) -> dict[str, Any]:
        return {
            "kvs_parameters_1": {
                "kvs_parameters": {
                    "instance_id": 1,
                    "dir": str(temp_dir),
                    "defaults": "ignored",
                },
            },
            "test": {
                "key": _DEFAULT_KEY,
                "override_value": _OVERRIDE_VALUE,
            },
        }

    def test_defaults_not_loaded(self, logs_info_level: LogContainer):
        """Verify that default values are not loaded with Ignored mode."""
        log = logs_info_level.find_log("mode", value="ignored")
        assert log is not None
        assert log.defaults_loaded == "false"

    def test_explicit_set_works(self, logs_info_level: LogContainer):
        """Verify that explicitly set values work even with Ignored mode."""
        log = logs_info_level.find_log("operation", value="set_and_get")
        assert log is not None
        assert abs(log.value - _OVERRIDE_VALUE) < 1e-5


class DefaultValuesParityScenario(FitScenario):
    """
    Common fixtures for default value parity scenarios.
    """

    @pytest.fixture(scope="class")
    def temp_dir(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        version: str,
        defaults: str,
    ) -> Generator[Path, None, None]:
        yield from temp_dir_common(tmp_path_factory, self.__class__.__name__, version, defaults)

    @pytest.fixture(scope="class")
    def defaults(self, request: pytest.FixtureRequest) -> str:
        """
        Provide defaults mode for parity scenarios.
        """
        return getattr(request, "param", "optional")

    @pytest.fixture(scope="class")
    def defaults_values(self) -> dict[str, tuple[str, float]]:
        """
        Provide default values for parity scenarios.
        """

        values: dict[str, tuple[str, float]] = {
            _PARITY_KEY: ("f64", _PARITY_DEFAULT_VALUE),
        }
        for idx in range(_RESET_KEY_COUNT):
            values[f"{_PARITY_KEY}_{idx}"] = ("f64", _reset_default_value(idx))
        return values

    @pytest.fixture(scope="class")
    def defaults_file(
        self,
        temp_dir: Path,
        defaults_values: dict[str, tuple[str, float]],
        defaults: str,
    ) -> Path | None:
        """
        Create defaults file for parity scenarios unless overridden.
        """
        if defaults == "without":
            return None
        return create_kvs_defaults_file(temp_dir, 1, defaults_values)

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path, defaults: str, defaults_file: Path | None) -> dict[str, Any]:
        """
        Provide the test configuration for parity scenarios.
        """

        kvs_parameters: dict[str, Any] = {
            "instance_id": 1,
            "dir": str(temp_dir),
        }
        if defaults is not None:
            kvs_parameters["defaults"] = "optional" if defaults == "without" else defaults
        return {
            "kvs_parameters_1": {
                "kvs_parameters": kvs_parameters,
            },
        }


@pytest.mark.parametrize("defaults", ["optional", "required", "without"], scope="class")
@add_test_properties(
    partially_verifies=[
        "feat_req__persistency__default_values",
        "feat_req__persistency__default_value_file",
        "feat_req__persistency__default_value_get",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestDefaultValues(DefaultValuesParityScenario):
    """
    Verify default value reads and overrides are reflected in logs.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        """
        Provide the scenario name for default value parity.
        """
        return "persistency.default_values.default_values"

    def test_values(self, defaults_file: Path | None, logs_info_level: LogContainer) -> None:
        """
        Check value_is_default, default_value, and current_value sequences.
        """

        logs = logs_info_level.get_logs(field="key", value=_PARITY_KEY)
        assert len(logs) == 2

        expected_default = f"Ok(F64({_format_f64(_PARITY_DEFAULT_VALUE)}))"
        expected_override = f"Ok(F64({_format_f64(_PARITY_OVERRIDE_VALUE)}))"

        if defaults_file is None:
            assert logs[0].value_is_default == "Err(KeyNotFound)"
            assert logs[0].default_value == "Err(KeyNotFound)"
            assert logs[0].current_value == "Err(KeyNotFound)"

            assert logs[1].value_is_default == "Ok(false)"
            assert logs[1].default_value == "Err(KeyNotFound)"
            assert logs[1].current_value == expected_override
            return

        assert logs[0].value_is_default == "Ok(true)"
        assert logs[0].default_value == expected_default
        assert logs[0].current_value == expected_default

        assert logs[1].value_is_default == "Ok(false)"
        assert logs[1].default_value == expected_default
        assert logs[1].current_value == expected_override


@pytest.mark.parametrize("defaults", ["optional", "required", "without"], scope="class")
@add_test_properties(
    partially_verifies=[
        "feat_req__persistency__default_values",
        "feat_req__persistency__default_value_file",
        "feat_req__persistency__default_value_get",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestDefaultValuesRemoveKey(DefaultValuesParityScenario):
    """
    Verify remove_key restores the default value.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        """
        Provide the scenario name for remove_key parity.
        """
        return "persistency.default_values.remove_key"

    def test_values(self, defaults_file: Path | None, logs_info_level: LogContainer) -> None:
        """
        Check logs for default, override, and remove phases.
        """

        logs = logs_info_level.get_logs(field="key", value=_PARITY_KEY)
        assert len(logs) == 3

        expected_default = f"Ok(F64({_format_f64(_PARITY_DEFAULT_VALUE)}))"
        expected_override = f"Ok(F64({_format_f64(_PARITY_OVERRIDE_VALUE)}))"

        if defaults_file is None:
            assert logs[0].value_is_default == "Err(KeyNotFound)"
            assert logs[0].default_value == "Err(KeyNotFound)"
            assert logs[0].current_value == "Err(KeyNotFound)"

            assert logs[1].value_is_default == "Ok(false)"
            assert logs[1].default_value == "Err(KeyNotFound)"
            assert logs[1].current_value == expected_override

            assert logs[2].value_is_default == "Err(KeyNotFound)"
            assert logs[2].default_value == "Err(KeyNotFound)"
            assert logs[2].current_value == "Err(KeyNotFound)"
            return

        assert logs[0].value_is_default == "Ok(true)"
        assert logs[0].default_value == expected_default
        assert logs[0].current_value == expected_default

        assert logs[1].value_is_default == "Ok(false)"
        assert logs[1].default_value == expected_default
        assert logs[1].current_value == expected_override

        assert logs[2].value_is_default == "Ok(true)"
        assert logs[2].default_value == expected_default
        assert logs[2].current_value == expected_default


@pytest.mark.parametrize("defaults", ["optional", "required"], scope="class")
@add_test_properties(
    fully_verifies=["feat_req__persistency__reset_to_default"],
    partially_verifies=[
        "feat_req__persistency__default_values",
        "feat_req__persistency__default_value_file",
        "feat_req__persistency__default_value_get",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestDefaultValuesResetAllKeys(DefaultValuesParityScenario):
    """
    Verify reset() restores defaults for all keys.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        """
        Provide the scenario name for reset_all_keys parity.
        """
        return "persistency.default_values.reset_all_keys"

    def test_values(self, logs_info_level: LogContainer) -> None:
        """
        Validate before/after reset values for each key.
        """

        for idx in range(_RESET_KEY_COUNT):
            key = f"{_PARITY_KEY}_{idx}"
            logs = logs_info_level.get_logs(field="key", value=key)
            assert len(logs) == 3

            default_value = _reset_default_value(idx)
            override_value = _reset_override_value(idx)

            assert logs[0].value_is_default
            assert isclose(logs[0].current_value, default_value, abs_tol=1e-5)

            assert not logs[1].value_is_default
            assert isclose(logs[1].current_value, override_value, abs_tol=1e-5)

            assert logs[2].value_is_default
            assert isclose(logs[2].current_value, default_value, abs_tol=1e-5)


@pytest.mark.parametrize("defaults", ["optional", "required"], scope="class")
@add_test_properties(
    partially_verifies=[
        "feat_req__persistency__default_values",
        "feat_req__persistency__default_value_file",
        "feat_req__persistency__default_value_get",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestDefaultValuesResetSingleKey(DefaultValuesParityScenario):
    """
    Verify reset_key restores the default value for a single key.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        """
        Provide the scenario name for reset_single_key parity.
        """
        return "persistency.default_values.reset_single_key"

    def test_values(self, logs_info_level: LogContainer) -> None:
        """
        Validate before/after reset values for each key.
        """

        reset_index = 2
        for idx in range(_RESET_KEY_COUNT):
            key = f"{_PARITY_KEY}_{idx}"
            logs = logs_info_level.get_logs(field="key", value=key)
            assert len(logs) == 3

            default_value = _reset_default_value(idx)
            override_value = _reset_override_value(idx)
            expect_reset_default = idx == reset_index

            assert logs[0].value_is_default
            assert isclose(logs[0].current_value, default_value, abs_tol=1e-5)

            assert not logs[1].value_is_default
            assert isclose(logs[1].current_value, override_value, abs_tol=1e-5)

            assert logs[2].value_is_default == expect_reset_default
            expected_value = default_value if expect_reset_default else override_value
            assert isclose(logs[2].current_value, expected_value, abs_tol=1e-5)


@pytest.mark.parametrize("defaults", ["optional", "required"], scope="class")
@add_test_properties(
    partially_verifies=["feat_req__persistency__default_values"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestDefaultValuesChecksum(DefaultValuesParityScenario):
    """
    Verify snapshot checksum matches the persisted data.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        """
        Provide the scenario name for checksum parity.
        """
        return "persistency.default_values.checksum"

    def test_checksum(self, logs_info_level: LogContainer) -> None:
        """
        Compare the snapshot hash with the adler32 checksum.
        """

        log = logs_info_level.find_log("kvs_path")
        assert log is not None

        kvs_path = Path(log.kvs_path)
        hash_path = Path(log.hash_path)
        assert kvs_path.exists()
        assert hash_path.exists()

        expected = adler32(kvs_path.read_bytes()).to_bytes(length=4, byteorder="big")
        assert hash_path.read_bytes() == expected


@add_test_properties(
    partially_verifies=[
        "feat_req__persistency__default_values",
        "feat_req__persistency__default_value_file",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestDefaultValuesMissingDefaultsFile(DefaultValuesParityScenario):
    """
    Verify required defaults mode fails when defaults file is missing.
    """

    @pytest.fixture(scope="class")
    def defaults(self) -> str:
        """
        Require defaults for this scenario.
        """

        return "required"

    @pytest.fixture(scope="class")
    def defaults_file(self, temp_dir: Path) -> Path | None:
        """
        Skip defaults file creation for this scenario.
        """

        return None

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        """
        Provide the scenario name for missing defaults (required).
        """
        return "persistency.default_values.default_values"

    def expect_command_failure(self) -> bool:
        """
        Expect scenario execution to fail for missing defaults.
        """

        return True

    def test_missing_defaults_file(self, results) -> None:
        """
        Ensure execution fails with PANIC when defaults file is missing.
        """

        assert results.return_code == ResultCode.PANIC


@pytest.mark.parametrize("defaults", ["optional", "required"], scope="class")
@add_test_properties(
    partially_verifies=[
        "feat_req__persistency__default_values",
        "feat_req__persistency__default_value_file",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestDefaultValuesMalformedDefaultsFile(DefaultValuesParityScenario):
    """
    Verify required defaults mode fails with malformed defaults file.
    """

    @pytest.fixture(scope="class")
    def defaults_file(self, temp_dir: Path) -> Path | None:
        """
        Create a malformed defaults file (truncated JSON) to trigger parsing errors.
        """

        json_path = temp_dir / "kvs_1_default.json"
        hash_path = temp_dir / "kvs_1_default.hash"
        json_str = json.dumps({"test_number": {"t": "f64", "v": 123.4}})[:-2]
        json_path.write_text(json_str)
        hash_path.write_bytes(adler32(json_str.encode()).to_bytes(length=4, byteorder="big"))
        return json_path

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        """
        Provide the scenario name for malformed defaults.
        """
        return "persistency.default_values.default_values"

    def expect_command_failure(self) -> bool:
        """
        Expect scenario execution to fail for malformed defaults.
        """

        return True

    def capture_stderr(self) -> bool:
        """
        Capture stderr to inspect the failure reason.
        """

        return True

    def test_malformed_defaults_file(self, results) -> None:
        """
        Ensure execution fails with malformed defaults file.
        """

        assert results.return_code == ResultCode.PANIC
        assert results.stderr is not None
        assert re.search(r"(JsonParserError|KvsFileReadError)", results.stderr)
