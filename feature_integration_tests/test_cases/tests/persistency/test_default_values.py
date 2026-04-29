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
from fit_scenario import FitScenario, ResultCode, create_kvs_defaults_file, read_kvs_snapshot, temp_dir_common
from test_properties import add_test_properties
from testing_utils import ScenarioResult

pytestmark = pytest.mark.parametrize("version", ["rust", "cpp"], scope="class")

# Key and value constants shared across default-value tests.
_DEFAULT_KEY = "test_key"
_OVERRIDE_VALUE = 432.1

_PARITY_KEY = "test_number"
_PARITY_DEFAULT_VALUE = 123.4
_RESET_KEY_COUNT = 5
_RESET_DEFAULT_BASE = 10.0


def _reset_default_value(index: int) -> float:
    """
    Provide the default value for reset scenarios for a given index.
    """
    return _RESET_DEFAULT_BASE * (index + 1)


@add_test_properties(
    partially_verifies=["feat_req__persistency__default_values", "feat_req__persistency__default_value_get"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestDefaultValuesIgnored(FitScenario):
    """
    Verifies that with KvsDefaults::Ignored mode, default values are not loaded
    even if a defaults file exists. The explicitly set value is persisted to storage.
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

    def test_explicit_set_persisted(self, results: ScenarioResult, temp_dir: Path) -> None:
        """Verify that the explicitly set value is written to the KVS snapshot."""
        assert results.return_code == ResultCode.SUCCESS
        snapshot = read_kvs_snapshot(temp_dir, 1)
        assert _DEFAULT_KEY in snapshot, f"Expected key '{_DEFAULT_KEY}' in snapshot"
        assert isclose(snapshot[_DEFAULT_KEY]["v"], _OVERRIDE_VALUE, abs_tol=1e-5)


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


@pytest.mark.parametrize("defaults", ["optional", "required"], scope="class")
@add_test_properties(
    partially_verifies=["feat_req__persistency__default_values"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestDefaultValuesChecksum(DefaultValuesParityScenario):
    """
    Verify that the KVS snapshot checksum file matches the snapshot content.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "persistency.default_values.checksum"

    def test_checksum(self, results: ScenarioResult, temp_dir: Path) -> None:
        """
        Compare the snapshot bytes with the adler32 hash written by KVS.
        Both files are at the conventional paths derived from instance_id.
        """
        assert results.return_code == ResultCode.SUCCESS
        kvs_path = temp_dir / "kvs_1_0.json"
        hash_path = temp_dir / "kvs_1_0.hash"
        assert kvs_path.exists(), "KVS snapshot file must exist"
        assert hash_path.exists(), "KVS hash file must exist"
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
        return "required"

    @pytest.fixture(scope="class")
    def defaults_file(self, temp_dir: Path) -> Path | None:
        return None

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "persistency.default_values.checksum"

    def expect_command_failure(self) -> bool:
        return True

    def test_missing_defaults_file(self, results: ScenarioResult) -> None:
        """
        Ensure execution fails when defaults file is missing.
        """
        assert results.return_code != ResultCode.SUCCESS


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
        return "persistency.default_values.checksum"

    def expect_command_failure(self) -> bool:
        return True

    def capture_stderr(self) -> bool:
        return True

    def test_malformed_defaults_file(self, results: ScenarioResult) -> None:
        """
        Ensure execution fails with malformed defaults file.
        """
        assert results.return_code != ResultCode.SUCCESS
        assert results.stderr is not None
        assert re.search(r"(JsonParserError|KvsFileReadError|JSON parser error|KVS file read error)", results.stderr)


_GET_DEFAULT_KEY = "default_probe_key"
_GET_DEFAULT_EXPECTED = 123.456


@add_test_properties(
    fully_verifies=["feat_req__persistency__default_value_get"],
    partially_verifies=[
        "feat_req__persistency__default_values",
        "feat_req__persistency__default_value_file",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestGetDefaultValue(FitScenario):
    """
    Verify that get_value returns the default value for a key that was
    provisioned via the defaults file but never explicitly set.

    The scenario reads the default, writes it to a probe key, and flushes.
    Python checks the probe key equals the expected default — the first test
    in this suite that fully exercises feat_req__persistency__default_value_get.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "persistency.default_values.get_default_value"

    @pytest.fixture(scope="class")
    def temp_dir(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        version: str,
    ) -> Generator[Path, None, None]:
        yield from temp_dir_common(tmp_path_factory, self.__class__.__name__, version)

    @pytest.fixture(scope="class")
    def defaults_file(self, temp_dir: Path) -> Path:
        """Provision a default value for the probe key."""
        return create_kvs_defaults_file(
            temp_dir,
            1,
            {_GET_DEFAULT_KEY: ("f64", _GET_DEFAULT_EXPECTED)},
        )

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path, defaults_file: Path) -> dict[str, Any]:
        return {
            "kvs_parameters_1": {
                "kvs_parameters": {
                    "instance_id": 1,
                    "dir": str(temp_dir),
                    "defaults": "optional",
                },
            },
        }

    def test_default_value_readable(self, results: ScenarioResult, temp_dir: Path) -> None:
        """
        The probe key written by the scenario must equal the expected default.
        This confirms the KVS returned the correct default via get_value without
        any prior set_value call.
        """
        assert results.return_code == ResultCode.SUCCESS
        snapshot = read_kvs_snapshot(temp_dir, 1)
        assert "result_key" in snapshot, "Probe key 'result_key' must be present in snapshot"
        assert isclose(snapshot["result_key"]["v"], _GET_DEFAULT_EXPECTED, abs_tol=1e-4), (
            f"Expected probe key value ≈ {_GET_DEFAULT_EXPECTED}, got {snapshot['result_key']['v']}"
        )


_SEL_KEY_COUNT = 6
_SEL_DEFAULT_VALUE = 50.0


def _sel_override_value(index: int) -> float:
    """
    Return the override value used by the selective_reset scenario for a given index.
    Matches the value written by the scenario: 100.0 * (index + 1).
    """
    return 100.0 * (index + 1)


@add_test_properties(
    partially_verifies=[
        "feat_req__persistency__reset_to_default",
        "feat_req__persistency__default_values",
        "feat_req__persistency__default_value_file",
        "feat_req__persistency__store_data",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestSelectiveReset(FitScenario):
    """
    Verify selective reset_key: even-indexed keys revert to absent (default),
    odd-indexed keys keep their override values.

    Six keys (sel_key_0 .. sel_key_5) receive optional defaults and override
    values. reset_key is called on even-indexed keys (0, 2, 4). After the
    second flush, even-indexed keys must be absent from the snapshot while
    odd-indexed keys (1, 3, 5) must still hold their override values.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "persistency.default_values.selective_reset"

    @pytest.fixture(scope="class")
    def temp_dir(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        version: str,
    ) -> Generator[Path, None, None]:
        yield from temp_dir_common(tmp_path_factory, self.__class__.__name__, version)

    @pytest.fixture(scope="class")
    def defaults_file(self, temp_dir: Path) -> Path:
        """Provision optional defaults for all six sel_key_i keys."""
        return create_kvs_defaults_file(
            temp_dir,
            1,
            {f"sel_key_{i}": ("f64", _SEL_DEFAULT_VALUE) for i in range(_SEL_KEY_COUNT)},
        )

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path, defaults_file: Path) -> dict[str, Any]:
        return {
            "kvs_parameters_1": {
                "kvs_parameters": {
                    "instance_id": 1,
                    "dir": str(temp_dir),
                    "defaults": "optional",
                },
            },
        }

    def test_selective_reset_state(self, results: ScenarioResult, temp_dir: Path) -> None:
        """
        Even-indexed keys must be absent after reset_key; odd-indexed must retain
        their override values in the final flushed snapshot.
        """
        assert results.return_code == ResultCode.SUCCESS
        snapshot = read_kvs_snapshot(temp_dir, 1)
        for i in range(_SEL_KEY_COUNT):
            key = f"sel_key_{i}"
            if i % 2 == 0:
                assert key not in snapshot, f"Even key '{key}' must be absent after reset_key"
            else:
                assert key in snapshot, f"Odd key '{key}' must be present with override"
                assert isclose(snapshot[key]["v"], _sel_override_value(i), abs_tol=1e-4), (
                    f"Expected {key} ≈ {_sel_override_value(i)}, got {snapshot[key]['v']}"
                )


# ---------------------------------------------------------------------------
# Full reset: reset() clears all keys; subsequent writes persist correctly
# ---------------------------------------------------------------------------

_FR_KEY_COUNT = 4
_FR_NEW_KEYS = ("fr_new_0", "fr_new_1")
_FR_NEW_VALUES = (10.0, 20.0)


@add_test_properties(
    partially_verifies=[
        "feat_req__persistency__reset_to_default",
        "feat_req__persistency__default_values",
        "feat_req__persistency__default_value_file",
        "feat_req__persistency__store_data",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestFullReset(FitScenario):
    """
    Verify that reset() clears all previously written keys from storage
    and that keys written after reset() are correctly persisted.

    Four initial keys (fr_key_0..3) are written and flushed. reset() is then
    called to remove all of them. Two new keys (fr_new_0, fr_new_1) are written
    and flushed. Python verifies that all four initial keys are absent and both
    new keys are present with the expected values.

    This is the only FIT scenario exercising the "all keys" variant of
    feat_req__persistency__reset_to_default. TestSelectiveReset covers the
    single-key variant (reset_key). Together they give full coverage of the
    "individual key or all keys" phrase in the requirement.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "persistency.default_values.full_reset"

    @pytest.fixture(scope="class")
    def temp_dir(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        version: str,
    ) -> Generator[Path, None, None]:
        yield from temp_dir_common(tmp_path_factory, self.__class__.__name__, version)

    @pytest.fixture(scope="class")
    def defaults_file(self, temp_dir: Path) -> Path:
        """Provision optional defaults for all four initial keys."""
        return create_kvs_defaults_file(
            temp_dir,
            1,
            {f"fr_key_{i}": ("f64", 50.0) for i in range(_FR_KEY_COUNT)},
        )

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path, defaults_file: Path) -> dict[str, Any]:
        return {
            "kvs_parameters_1": {
                "kvs_parameters": {
                    "instance_id": 1,
                    "dir": str(temp_dir),
                    "defaults": "optional",
                },
            },
        }

    def test_full_reset_clears_initial_keys(self, results: ScenarioResult, temp_dir: Path) -> None:
        """
        All four initial fr_key_i keys must be absent after reset() — they were
        removed by the all-keys reset, not individually.
        """
        assert results.return_code == ResultCode.SUCCESS
        snapshot = read_kvs_snapshot(temp_dir, 1)
        for i in range(_FR_KEY_COUNT):
            key = f"fr_key_{i}"
            assert key not in snapshot, f"Initial key '{key}' must be absent after reset()"

    def test_full_reset_new_keys_present(self, results: ScenarioResult, temp_dir: Path) -> None:
        """
        Both keys written after reset() must be present in the snapshot with the
        correct values, proving that subsequent writes are unaffected by reset().
        """
        assert results.return_code == ResultCode.SUCCESS
        snapshot = read_kvs_snapshot(temp_dir, 1)
        for key, expected in zip(_FR_NEW_KEYS, _FR_NEW_VALUES):
            assert key in snapshot, f"Post-reset key '{key}' must be present in snapshot"
            assert isclose(snapshot[key]["v"], expected, abs_tol=1e-4), (
                f"Expected {key} ≈ {expected}, got {snapshot[key]['v']}"
            )


# ---------------------------------------------------------------------------
# Optional mode without defaults file: graceful degradation
# ---------------------------------------------------------------------------


@add_test_properties(
    partially_verifies=[
        "feat_req__persistency__default_values",
        "feat_req__persistency__default_value_file",
        "feat_req__persistency__store_data",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestOptionalModeWithoutDefaults(DefaultValuesParityScenario):
    """
    Verify that KVS starts and operates normally when defaults=optional but
    no defaults file is present (graceful degradation).

    Unlike TestDefaultValuesMissingDefaultsFile which proves required mode fails
    without a file, this test proves optional mode succeeds — the KVS initialises,
    the scenario writes a key, flush completes, and the scenario returns SUCCESS.
    This is a distinct code path from both ignored mode (no attempt to read the file)
    and required mode (hard failure when file is absent).
    """

    @pytest.fixture(scope="class")
    def defaults(self) -> str:
        # "without" maps to defaults=optional in KVS config with no file created.
        return "without"

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "persistency.default_values.checksum"

    def test_succeeds_without_defaults_file(self, results: ScenarioResult) -> None:
        """
        KVS must initialise and complete successfully even when configured with
        optional defaults and no defaults file exists on disk.
        """
        assert results.return_code == ResultCode.SUCCESS
