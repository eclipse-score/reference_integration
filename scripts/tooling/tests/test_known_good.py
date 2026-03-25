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
from pathlib import Path

import pytest
from lib.known_good import KnownGood, Metadata, Module, load_known_good

# ---------------------------------------------------------------------------
# load_known_good – happy path
# ---------------------------------------------------------------------------


class TestLoadKnownGood:
    def test_returns_known_good_instance(self, minimal_json_file: Path):
        result = load_known_good(minimal_json_file)
        assert isinstance(result, KnownGood)

    def test_timestamp_is_string(self, minimal_json_file: Path):
        result = load_known_good(minimal_json_file)
        assert isinstance(result.timestamp, str)
        assert result.timestamp == "2026-01-01T00:00:00+00:00Z"

    def test_modules_is_dict_of_dicts(self, minimal_json_file: Path):
        result = load_known_good(minimal_json_file)
        assert isinstance(result.modules, dict)
        for group in result.modules.values():
            assert isinstance(group, dict)

    def test_module_values_are_module_instances(self, minimal_json_file: Path):
        result = load_known_good(minimal_json_file)
        module = result.modules["target_sw"]["score_baselibs"]
        assert isinstance(module, Module)

    def test_module_fields_are_typed(self, minimal_json_file: Path):
        m = load_known_good(minimal_json_file).modules["target_sw"]["score_baselibs"]
        assert isinstance(m.name, str)
        assert isinstance(m.hash, str)
        assert isinstance(m.repo, str)
        assert m.version is None
        assert m.bazel_patches is None
        assert isinstance(m.metadata, Metadata)
        assert isinstance(m.branch, str)
        assert isinstance(m.pin_version, bool)

    def test_module_field_values(self, minimal_json_file: Path):
        m = load_known_good(minimal_json_file).modules["target_sw"]["score_baselibs"]
        assert m.name == "score_baselibs"
        assert m.hash == "abc123"
        assert m.repo == "https://github.com/eclipse-score/baselibs.git"
        assert m.branch == "main"
        assert m.pin_version is False


# ---------------------------------------------------------------------------
# load_known_good – full file
# ---------------------------------------------------------------------------


class TestLoadKnownGoodFullFile:
    def test_loads_without_error(self, full_json_file: Path):
        load_known_good(full_json_file)

    def test_groups_present(self, full_json_file: Path):
        kg = load_known_good(full_json_file)
        assert "target_sw" in kg.modules
        assert "tooling" in kg.modules

    def test_score_baselibs_fields(self, full_json_file: Path):
        m = load_known_good(full_json_file).modules["target_sw"]["score_baselibs"]
        assert m.repo == "https://github.com/eclipse-score/baselibs.git"
        assert len(m.hash) == 40  # SHA-1
        assert m.bazel_patches is not None
        assert isinstance(m.metadata.extra_test_config, list)
        assert isinstance(m.metadata.exclude_test_targets, list)

    def test_tooling_module_no_metadata_defaults(self, full_json_file: Path):
        m = load_known_good(full_json_file).modules["tooling"]["score_crates"]
        assert isinstance(m.metadata, Metadata)

    def test_all_modules_have_repo(self, full_json_file: Path):
        kg = load_known_good(full_json_file)
        for group in kg.modules.values():
            for m in group.values():
                assert m.repo, f"Module {m.name} is missing a repo"

    def test_owner_repo_property(self, full_json_file: Path):
        m = load_known_good(full_json_file).modules["target_sw"]["score_baselibs"]
        assert m.owner_repo == "eclipse-score/baselibs"

    def test_metadata_extra_test_config(self, full_json_file: Path):
        known_good = load_known_good(full_json_file)
        baselibs = known_good.modules["target_sw"]["score_baselibs"]
        persistency = known_good.modules["target_sw"]["score_persistency"]
        assert baselibs.metadata.extra_test_config == [
            "//score/json:base_library=nlohmann",
            "//score/memory/shared/flags:use_typedshmd=False",
        ]
        assert persistency.metadata.extra_test_config == []

    def test_metadata_exclude_test_targets(self, full_json_file: Path):
        known_good = load_known_good(full_json_file)
        baselibs = known_good.modules["target_sw"]["score_baselibs"]
        persistency = known_good.modules["target_sw"]["score_persistency"]
        assert baselibs.metadata.exclude_test_targets == [
            "//score/language/safecpp/aborts_upon_exception:abortsuponexception_toolchain_test",
            "//score/containers:dynamic_array_test",
            "//score/mw/log/configuration:*",
            "//score/json/examples:*",
        ]
        assert persistency.metadata.exclude_test_targets == []

    def test_metadata_code_root_path(self, full_json_file: Path):
        known_good = load_known_good(full_json_file)
        baselibs = known_good.modules["target_sw"]["score_baselibs"]
        persistency = known_good.modules["target_sw"]["score_persistency"]
        assert baselibs.metadata.code_root_path == "//score/..."
        assert persistency.metadata.code_root_path == "//src/..."

    def test_metadata_langs(self, full_json_file: Path):
        known_good = load_known_good(full_json_file)
        baselibs = known_good.modules["target_sw"]["score_baselibs"]
        persistency = known_good.modules["target_sw"]["score_persistency"]
        assert baselibs.metadata.langs == ["cpp"]
        assert persistency.metadata.langs == ["cpp", "rust"]


# ---------------------------------------------------------------------------
# Metadata defaults
# ---------------------------------------------------------------------------


class TestMetadataDefaults:
    def test_defaults_when_metadata_key_absent(self, tmp_path: Path):
        data = {
            "modules": {"g": {"mod": {"repo": "https://github.com/a/b.git", "hash": "deadbeef"}}},
            "timestamp": "",
        }
        p = tmp_path / "kg.json"
        p.write_text(json.dumps(data))
        m = load_known_good(p).modules["g"]["mod"]
        assert m.metadata.code_root_path == "//score/..."
        assert m.metadata.extra_test_config == []
        assert m.metadata.exclude_test_targets == []
        assert m.metadata.langs == ["cpp", "rust"]

    def test_metadata_fields_typed(self, tmp_path: Path):
        data = {
            "modules": {
                "g": {
                    "mod": {
                        "repo": "https://github.com/a/b.git",
                        "hash": "deadbeef",
                        "metadata": {
                            "code_root_path": "//src/...",
                            "extra_test_config": ["//flag:val"],
                            "exclude_test_targets": ["//some:test"],
                            "langs": ["rust"],
                        },
                    }
                }
            },
            "timestamp": "",
        }
        p = tmp_path / "kg.json"
        p.write_text(json.dumps(data))
        meta = load_known_good(p).modules["g"]["mod"].metadata
        assert isinstance(meta.code_root_path, str)
        assert isinstance(meta.extra_test_config, list)
        assert isinstance(meta.exclude_test_targets, list)
        assert isinstance(meta.langs, list)
        assert meta.langs == ["rust"]


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestLoadKnownGoodErrors:
    def test_file_not_found(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_known_good(tmp_path / "nonexistent.json")

    def test_invalid_json_raises_value_error(self, tmp_path: Path):
        p = tmp_path / "bad.json"
        p.write_text("{invalid json,}")
        with pytest.raises(ValueError, match="Invalid JSON"):
            load_known_good(p)

    def test_missing_modules_key_raises_value_error(self, tmp_path: Path):
        p = tmp_path / "bad.json"
        p.write_text(json.dumps({"timestamp": "2026-01-01"}))
        with pytest.raises(ValueError, match="modules"):
            load_known_good(p)

    def test_hash_and_version_both_set_raises(self, tmp_path: Path):
        data = {
            "modules": {
                "g": {
                    "mod": {
                        "repo": "https://github.com/a/b.git",
                        "hash": "abc",
                        "version": "1.0.0",
                    }
                }
            },
            "timestamp": "",
        }
        p = tmp_path / "kg.json"
        p.write_text(json.dumps(data))
        with pytest.raises(ValueError, match="both 'hash' and 'version'"):
            load_known_good(p)

    def test_bazel_patches_are_list(self, minimal_json_file: Path):
        data = json.loads(minimal_json_file.read_text())
        data["modules"]["target_sw"]["score_baselibs"]["bazel_patches"] = ["//patch:foo.patch"]
        minimal_json_file.write_text(json.dumps(data))
        m = load_known_good(minimal_json_file).modules["target_sw"]["score_baselibs"]
        assert m.bazel_patches == ["//patch:foo.patch"]
