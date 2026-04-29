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
Creative FIT tests that mix and match persistency requirements.

Each test exercises multiple requirements together through a single observable
storage outcome rather than testing each requirement in isolation.
"""

from collections.abc import Generator
from math import isclose
from pathlib import Path
from typing import Any

import pytest
from fit_scenario import FitScenario, ResultCode, create_kvs_defaults_file, read_kvs_snapshot, temp_dir_common
from test_properties import add_test_properties
from testing_utils import ScenarioResult

pytestmark = pytest.mark.parametrize("version", ["rust", "cpp"], scope="class")


# ---------------------------------------------------------------------------
# Scenario 1: Mixed value types with UTF-8 keys in one snapshot
# ---------------------------------------------------------------------------


@add_test_properties(
    partially_verifies=[
        "feat_req__persistency__support_datatype_keys",
        "feat_req__persistency__support_datatype_value",
        "feat_req__persistency__store_data",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestAllTypesWithUtf8Keys(FitScenario):
    """
    Verify that KVS can store multiple value types simultaneously under both
    ASCII and UTF-8 encoded key names, and that all of them are physically
    present in the single persisted snapshot file.

    This combines key-encoding support (UTF-8) with value-type coverage
    (i32, f64, bool, str, null) in one observable storage outcome.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "persistency.supported_datatypes.all_types_utf8"

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

    def test_utf8_keys_present(self, results: ScenarioResult, temp_dir: Path) -> None:
        """
        All five key names — including UTF-8 emoji and Greek characters — must
        appear verbatim in the persisted KVS snapshot.
        """
        assert results.return_code == ResultCode.SUCCESS
        snapshot = read_kvs_snapshot(temp_dir, 1)

        expected_keys = {
            "ascii_i32",
            "emoji_f64 🎯",
            "greek_bool αβγ",
            "ascii_str",
            "ascii_null",
        }
        for key in expected_keys:
            assert key in snapshot, f"Expected UTF-8 key '{key}' in snapshot"

    def test_value_types_persisted(self, results: ScenarioResult, temp_dir: Path) -> None:
        """
        Each key must carry the correct KVS type tag in the snapshot,
        confirming that value type information survives the flush cycle.
        """
        assert results.return_code == ResultCode.SUCCESS
        snapshot = read_kvs_snapshot(temp_dir, 1)

        assert snapshot["ascii_i32"]["t"] == "i32"
        assert snapshot["ascii_i32"]["v"] == -321

        assert snapshot["emoji_f64 🎯"]["t"] == "f64"
        assert isclose(snapshot["emoji_f64 🎯"]["v"], 3.14, abs_tol=1e-4)

        assert snapshot["greek_bool αβγ"]["t"] == "bool"
        assert snapshot["greek_bool αβγ"]["v"]  # True or 1, both truthy

        assert snapshot["ascii_str"]["t"] == "str"
        assert snapshot["ascii_str"]["v"] == "hello"

        assert snapshot["ascii_null"]["t"] == "null"


# ---------------------------------------------------------------------------
# Scenario 2: Partial override — only explicitly written keys enter snapshot
# ---------------------------------------------------------------------------

_PARTIAL_DEFAULT_VALUE = 50.0
_PARTIAL_OVERRIDE_VALUE = 999.0
_PARTIAL_KEYS = ["partial_key_0", "partial_key_1", "partial_key_2"]


@add_test_properties(
    partially_verifies=[
        "feat_req__persistency__default_values",
        "feat_req__persistency__default_value_file",
        "feat_req__persistency__store_data",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestPartialOverrideSnapshot(FitScenario):
    """
    Verify that when a KVS instance has default values for three keys but only
    one key is explicitly overridden, the snapshot contains ONLY the overridden
    key.  The two untouched keys remain as defaults and are absent from storage.

    This tests the boundary between default values (in-memory read-only) and
    persisted values (explicit flush), combining default_values,
    default_value_file, and store_data requirements.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "persistency.default_values.partial_override"

    @pytest.fixture(scope="class")
    def temp_dir(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        version: str,
    ) -> Generator[Path, None, None]:
        yield from temp_dir_common(tmp_path_factory, self.__class__.__name__, version)

    @pytest.fixture(scope="class")
    def defaults_file(self, temp_dir: Path) -> Path:
        """Create defaults for all three keys."""
        return create_kvs_defaults_file(
            temp_dir,
            1,
            {key: ("f64", _PARTIAL_DEFAULT_VALUE) for key in _PARTIAL_KEYS},
        )

    @pytest.fixture(scope="class")
    def test_config(self, temp_dir: Path, defaults_file: Path) -> dict[str, Any]:
        # defaults_file dependency ensures the file is created before the scenario runs.
        return {
            "kvs_parameters_1": {
                "kvs_parameters": {
                    "instance_id": 1,
                    "dir": str(temp_dir),
                    "defaults": "optional",
                },
            },
        }

    def test_only_overridden_key_in_snapshot(self, results: ScenarioResult, temp_dir: Path) -> None:
        """
        The snapshot must contain exactly partial_key_1 (the explicitly set key).
        partial_key_0 and partial_key_2 were never written, so they must be absent.
        """
        assert results.return_code == ResultCode.SUCCESS
        snapshot = read_kvs_snapshot(temp_dir, 1)

        # Explicitly overridden key must be present with the override value.
        assert "partial_key_1" in snapshot, "Overridden key must be present in snapshot"
        assert isclose(snapshot["partial_key_1"]["v"], _PARTIAL_OVERRIDE_VALUE, abs_tol=1e-4)

        # Default-only keys must NOT appear in the snapshot.
        assert "partial_key_0" not in snapshot, "Default-only key partial_key_0 must be absent from snapshot"
        assert "partial_key_2" not in snapshot, "Default-only key partial_key_2 must be absent from snapshot"


# ---------------------------------------------------------------------------
# Scenario 3: UTF-8 keys in defaults file + selective override
# ---------------------------------------------------------------------------

_UTF8_KEY_ASCII = "utf8_ascii_key"
_UTF8_KEY_EMOJI = "utf8_emoji 🔑"
_UTF8_KEY_GREEK = "utf8_greek κλμ"
_UTF8_DEFAULT_VALUE = 42.0
_UTF8_OVERRIDE_VALUE = 777.0


@add_test_properties(
    partially_verifies=[
        "feat_req__persistency__support_datatype_keys",
        "feat_req__persistency__default_values",
        "feat_req__persistency__default_value_file",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestUtf8KeysWithDefaults(FitScenario):
    """
    Verify that UTF-8 encoded key names work correctly as keys in both the
    defaults file and the KVS snapshot.

    The defaults file contains three keys with UTF-8 names (ASCII, emoji,
    Greek script).  The scenario overrides only the emoji key.  Python verifies:
    - the emoji key appears in the snapshot with the override value
    - the ASCII and Greek default-only keys are absent from the snapshot

    This combines key-encoding (support_datatype_keys) with default value
    provisioning (default_values + default_value_file) in one storage outcome.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "persistency.utf8_defaults"

    @pytest.fixture(scope="class")
    def temp_dir(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        version: str,
    ) -> Generator[Path, None, None]:
        yield from temp_dir_common(tmp_path_factory, self.__class__.__name__, version)

    @pytest.fixture(scope="class")
    def defaults_file(self, temp_dir: Path) -> Path:
        """Create defaults using UTF-8 key names."""
        return create_kvs_defaults_file(
            temp_dir,
            1,
            {
                _UTF8_KEY_ASCII: ("f64", _UTF8_DEFAULT_VALUE),
                _UTF8_KEY_EMOJI: ("f64", _UTF8_DEFAULT_VALUE),
                _UTF8_KEY_GREEK: ("f64", _UTF8_DEFAULT_VALUE),
            },
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

    def test_emoji_override_persisted(self, results: ScenarioResult, temp_dir: Path) -> None:
        """
        The explicitly overridden UTF-8 emoji key must appear in the snapshot
        with the override value, confirming that UTF-8 key names survive the
        full round-trip through the defaults file and snapshot storage.
        """
        assert results.return_code == ResultCode.SUCCESS
        snapshot = read_kvs_snapshot(temp_dir, 1)

        assert _UTF8_KEY_EMOJI in snapshot, (
            f"Overridden UTF-8 emoji key '{_UTF8_KEY_EMOJI}' must be present in snapshot"
        )
        assert isclose(snapshot[_UTF8_KEY_EMOJI]["v"], _UTF8_OVERRIDE_VALUE, abs_tol=1e-4)

    def test_default_only_utf8_keys_absent(self, results: ScenarioResult, temp_dir: Path) -> None:
        """
        UTF-8 keys that were not explicitly overridden must remain absent from
        the snapshot, demonstrating that defaults do not pollute persisted storage.
        """
        assert results.return_code == ResultCode.SUCCESS
        snapshot = read_kvs_snapshot(temp_dir, 1)

        assert _UTF8_KEY_ASCII not in snapshot, (
            f"Default-only ASCII key '{_UTF8_KEY_ASCII}' must be absent from snapshot"
        )
        assert _UTF8_KEY_GREEK not in snapshot, (
            f"Default-only Greek key '{_UTF8_KEY_GREEK}' must be absent from snapshot"
        )


# ---------------------------------------------------------------------------
# Scenario 4: UTF-8 key in defaults file + get_value without set_value
# ---------------------------------------------------------------------------

_UTF8_GET_KEY = "probe 🔍"
_UTF8_GET_DEFAULT_VALUE = 42.0


@add_test_properties(
    fully_verifies=["feat_req__persistency__default_value_get"],
    partially_verifies=["feat_req__persistency__support_datatype_keys"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestUtf8DefaultValueGet(FitScenario):
    """
    Verify that get_value retrieves the correct default for a UTF-8 emoji key
    that was provisioned in the defaults file but never explicitly set.

    The scenario reads the default via the UTF-8 key, writes the result to an
    ASCII probe key, and flushes. Python checks the probe key equals the expected
    default — combining feat_req__persistency__default_value_get with
    feat_req__persistency__support_datatype_keys in one storage outcome.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "persistency.utf8_default_value_get"

    @pytest.fixture(scope="class")
    def temp_dir(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        version: str,
    ) -> Generator[Path, None, None]:
        yield from temp_dir_common(tmp_path_factory, self.__class__.__name__, version)

    @pytest.fixture(scope="class")
    def defaults_file(self, temp_dir: Path) -> Path:
        """Provision a default value behind a UTF-8 emoji key."""
        return create_kvs_defaults_file(
            temp_dir,
            1,
            {_UTF8_GET_KEY: ("f64", _UTF8_GET_DEFAULT_VALUE)},
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

    def test_utf8_default_value_readable(self, results: ScenarioResult, temp_dir: Path) -> None:
        """
        The ASCII probe key written by the scenario must equal the UTF-8 key's
        default, confirming that get_value works correctly with UTF-8 default keys.
        """
        assert results.return_code == ResultCode.SUCCESS
        snapshot = read_kvs_snapshot(temp_dir, 1)
        assert "result_key" in snapshot, "Probe key 'result_key' must be present in snapshot"
        assert isclose(snapshot["result_key"]["v"], _UTF8_GET_DEFAULT_VALUE, abs_tol=1e-4), (
            f"Expected probe key value ≈ {_UTF8_GET_DEFAULT_VALUE}, got {snapshot['result_key']['v']}"
        )
