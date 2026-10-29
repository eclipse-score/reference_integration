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

from math import isclose
from pathlib import Path
from typing import Any

import pytest
from fit_scenario import ResultCode
from persistency_scenario import (
    PersistencyScenario,
    create_kvs_defaults_file,
    read_kvs_snapshot,
    verify_kvs_snapshot_hash,
)
from test_properties import add_test_properties
from testing_utils import ScenarioResult

pytestmark = pytest.mark.parametrize("version", ["rust", "cpp"], scope="class")


# ---------------------------------------------------------------------------
# Scenario 1: Mixed value types in one snapshot, non-ASCII keys rejected
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
class TestAllTypesWithUtf8Keys(PersistencyScenario):
    """
    Verify that KVS can store multiple value types simultaneously under ASCII
    key names, that all of them are physically present in the single persisted
    snapshot file, and that keys with non-ASCII UTF-8 characters are rejected.

    KVS keys must be printable ASCII (the ASCII subset of UTF-8). The scenario
    fails if a non-ASCII key is accepted. This combines key-encoding with
    value-type coverage (i32, f64, bool, str, null) in one observable storage
    outcome.
    """

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "persistency.supported_datatypes.all_types_utf8"

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

    def test_value_types_persisted(self, results: ScenarioResult, temp_dir: Path) -> None:
        """
        Each key must carry the correct KVS type tag in the snapshot,
        confirming that value type information survives the flush cycle.
        """
        assert results.return_code == ResultCode.SUCCESS
        snapshot = read_kvs_snapshot(temp_dir, 1)

        assert snapshot["ascii_i32"]["t"] == "i32"
        assert snapshot["ascii_i32"]["v"] == -321

        assert snapshot["ascii_f64"]["t"] == "f64"
        assert isclose(snapshot["ascii_f64"]["v"], 3.14, abs_tol=1e-4)

        assert snapshot["ascii_bool"]["t"] == "bool"
        assert snapshot["ascii_bool"]["v"] is True

        assert snapshot["ascii_str"]["t"] == "str"
        assert snapshot["ascii_str"]["v"] == "hello"

        assert snapshot["ascii_null"]["t"] == "null"
        assert snapshot["ascii_null"]["v"] is None

    def test_non_ascii_keys_absent(self, results: ScenarioResult, temp_dir: Path) -> None:
        """Keys with non-ASCII UTF-8 characters are rejected and never reach the snapshot."""
        assert results.return_code == ResultCode.SUCCESS
        snapshot = read_kvs_snapshot(temp_dir, 1)

        assert "emoji_f64 🎯" not in snapshot
        assert "greek_bool αβγ" not in snapshot

    def test_snapshot_hash_matches_content(self, results: ScenarioResult, temp_dir: Path) -> None:
        """Verify the hash file matches the Adler-32 of the snapshot JSON after normalization."""
        assert results.return_code == ResultCode.SUCCESS
        verify_kvs_snapshot_hash(temp_dir, instance_id=1, snapshot_id=0)


# ---------------------------------------------------------------------------
# Scenario 2: Partial override — only explicitly written keys enter snapshot
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
class TestPartialOverrideSnapshot(PersistencyScenario):
    """
    Verify that when a KVS instance has default values for three keys but only
    one key is explicitly overridden, the snapshot contains ONLY the overridden
    key.  The two untouched keys remain as defaults and are absent from storage.

    This tests the boundary between default values (in-memory read-only) and
    persisted values (explicit flush), combining default_values,
    default_value_file, and store_data requirements.
    """

    _DEFAULT_VALUE = 50.0
    _OVERRIDE_VALUE = 999.0
    _KEYS = ["partial_key_0", "partial_key_1", "partial_key_2"]

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "persistency.default_values.partial_override"

    @pytest.fixture(scope="class")
    def defaults_file(self, temp_dir: Path) -> Path:
        """Create defaults for all three keys."""
        return create_kvs_defaults_file(
            temp_dir,
            1,
            {key: ("f64", self._DEFAULT_VALUE) for key in self._KEYS},
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
        assert isclose(snapshot["partial_key_1"]["v"], self._OVERRIDE_VALUE, abs_tol=1e-4)

        # Default-only keys must NOT appear in the snapshot.
        assert "partial_key_0" not in snapshot, "Default-only key partial_key_0 must be absent from snapshot"
        assert "partial_key_2" not in snapshot, "Default-only key partial_key_2 must be absent from snapshot"

    def test_snapshot_hash_matches_content(self, results: ScenarioResult, temp_dir: Path) -> None:
        """Verify the hash file matches the Adler-32 of the snapshot JSON after normalization."""
        assert results.return_code == ResultCode.SUCCESS
        verify_kvs_snapshot_hash(temp_dir, instance_id=1, snapshot_id=0)

    def test_default_values_accessible(self, results: ScenarioResult, logs_info_level: Any) -> None:
        """
        Verify that the default values for partial_key_0 and partial_key_2 are
        accessible via get_value even though they were never explicitly written.

        Checks structured log fields emitted by the scenario after flush.
        """
        assert results.return_code == ResultCode.SUCCESS
        log0 = logs_info_level.find_log("key", value="partial_key_0")
        assert log0 is not None, "Expected log entry for default partial_key_0"
        assert isclose(float(log0.value), self._DEFAULT_VALUE, abs_tol=1e-4), (
            f"Expected partial_key_0 default ≈ {self._DEFAULT_VALUE}, got {log0.value}"
        )
        log2 = logs_info_level.find_log("key", value="partial_key_2")
        assert log2 is not None, "Expected log entry for default partial_key_2"
        assert isclose(float(log2.value), self._DEFAULT_VALUE, abs_tol=1e-4), (
            f"Expected partial_key_2 default ≈ {self._DEFAULT_VALUE}, got {log2.value}"
        )


# ---------------------------------------------------------------------------
# Scenario 3: Non-ASCII UTF-8 keys in defaults file are rejected
# ---------------------------------------------------------------------------


@add_test_properties(
    partially_verifies=[
        "feat_req__persistency__support_datatype_keys",
        "feat_req__persistency__default_values",
        "feat_req__persistency__default_value_file",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestUtf8KeysWithDefaults(PersistencyScenario):
    """
    Verify that a defaults file with non-ASCII UTF-8 key names is rejected.

    KVS keys must be printable ASCII (the ASCII subset of UTF-8), and keys read
    from the defaults file are validated like keys passed to set_value. The
    defaults file contains one ASCII key and two non-ASCII keys (emoji, Greek
    script); the scenario fails unless opening it fails with InvalidKey. Python
    verifies the scenario succeeded and that nothing was persisted.

    This combines key-encoding (support_datatype_keys) with default value
    provisioning (default_values + default_value_file).
    """

    _KEY_ASCII = "utf8_ascii_key"
    _KEY_EMOJI = "utf8_emoji 🔑"
    _KEY_GREEK = "utf8_greek κλμ"
    _DEFAULT_VALUE = 42.0

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "persistency.utf8_defaults"

    @pytest.fixture(scope="class")
    def defaults_file(self, temp_dir: Path) -> Path:
        """Create defaults using non-ASCII UTF-8 key names."""
        return create_kvs_defaults_file(
            temp_dir,
            1,
            {
                self._KEY_ASCII: ("f64", self._DEFAULT_VALUE),
                self._KEY_EMOJI: ("f64", self._DEFAULT_VALUE),
                self._KEY_GREEK: ("f64", self._DEFAULT_VALUE),
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

    def test_non_ascii_defaults_rejected(self, results: ScenarioResult) -> None:
        """The scenario only succeeds if KVS refused to open the defaults file."""
        assert results.return_code == ResultCode.SUCCESS

    def test_no_snapshot_written(self, results: ScenarioResult, temp_dir: Path) -> None:
        """A rejected KVS must not persist anything."""
        assert results.return_code == ResultCode.SUCCESS
        assert not (temp_dir / "kvs_1_0.json").exists()


# ---------------------------------------------------------------------------
# Scenario 4: Punctuation key in defaults file + get_value without set_value
# ---------------------------------------------------------------------------


@add_test_properties(
    fully_verifies=["feat_req__persistency__default_value_get"],
    partially_verifies=["feat_req__persistency__support_datatype_keys"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestUtf8DefaultValueGet(PersistencyScenario):
    """
    Verify that get_value retrieves the correct default for a key made of
    printable ASCII punctuation and a space (the edges of the allowed key
    characters) that was provisioned in the defaults file but never explicitly set.

    The scenario reads the default via that key, writes the result to a plain
    probe key, and flushes. Python checks the probe key equals the expected
    default — combining feat_req__persistency__default_value_get with
    feat_req__persistency__support_datatype_keys in one storage outcome.
    """

    _GET_KEY = "probe ~!#$%"
    _GET_DEFAULT_VALUE = 42.0

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "persistency.utf8_default_value_get"

    @pytest.fixture(scope="class")
    def defaults_file(self, temp_dir: Path) -> Path:
        """Provision a default value behind a punctuation key."""
        return create_kvs_defaults_file(
            temp_dir,
            1,
            {self._GET_KEY: ("f64", self._GET_DEFAULT_VALUE)},
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
        The probe key written by the scenario must equal the punctuation key's
        default, confirming that get_value works with such default keys.
        """
        assert results.return_code == ResultCode.SUCCESS
        snapshot = read_kvs_snapshot(temp_dir, 1)
        assert "result_key" in snapshot, "Probe key 'result_key' must be present in snapshot"
        assert isclose(snapshot["result_key"]["v"], self._GET_DEFAULT_VALUE, abs_tol=1e-4), (
            f"Expected probe key value ≈ {self._GET_DEFAULT_VALUE}, got {snapshot['result_key']['v']}"
        )

    def test_snapshot_hash_matches_content(self, results: ScenarioResult, temp_dir: Path) -> None:
        """Verify the hash file matches the Adler-32 of the snapshot JSON after normalization."""
        assert results.return_code == ResultCode.SUCCESS
        verify_kvs_snapshot_hash(temp_dir, instance_id=1, snapshot_id=0)
