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
"""Unit tests for the build-setting label consistency guard, plus the live-tree check."""

import json
import sys
from pathlib import Path

import pytest

# Make scripts/ importable so known_good.* package resolves when run via plain pytest.
_SCRIPTS_DIR = Path(__file__).resolve().parents[2]
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from known_good.rc_label_consistency import (  # noqa: E402
    REF_INT_ROOT,
    collect_occurrences,
    find_conflicts,
    main,
)


def _tree(root: Path, bazelrc: str = "", module_rc: str = "", extra_test_config: list[str] | None = None) -> Path:
    (root / "ci" / "stage2").mkdir(parents=True)
    (root / ".bazelrc").write_text(bazelrc)
    (root / "ci" / "stage2" / "module.bazelrc").write_text(module_rc)
    (root / "known_good.json").write_text(
        json.dumps(
            {
                "modules": {
                    "target_sw": {
                        "score_persistency": {
                            "repo": "r",
                            "hash": "h",
                            "metadata": {"extra_test_config": extra_test_config or []},
                        }
                    }
                },
                "timestamp": "",
            }
        )
    )
    return root


class TestFindConflicts:
    def test_same_repo_two_paths_conflicts(self, tmp_path: Path):
        root = _tree(
            tmp_path,
            bazelrc="build --@score_baselibs//score/log_rust:safety_level=qm\n",
            module_rc="build --@score_baselibs//src/log:safety_level=qm\n",
        )
        conflicts = find_conflicts(collect_occurrences(root))
        assert set(conflicts) == {("@score_baselibs", "safety_level")}

    def test_conflict_reports_every_source(self, tmp_path: Path):
        root = _tree(
            tmp_path,
            bazelrc="build --@score_baselibs//score/log_rust:safety_level=qm\n",
            module_rc="build --@score_baselibs//src/log:safety_level=qm\n",
            extra_test_config=["@score_baselibs//score/log_rust:safety_level=qm"],
        )
        labels = find_conflicts(collect_occurrences(root))[("@score_baselibs", "safety_level")]
        assert labels["@score_baselibs//src/log:safety_level"] == ["ci/stage2/module.bazelrc:1"]
        assert len(labels["@score_baselibs//score/log_rust:safety_level"]) == 2

    def test_same_basename_different_repos_allowed(self, tmp_path: Path):
        # Both score_baselibs and score_logging genuinely define KRemote_Logging.
        root = _tree(
            tmp_path,
            bazelrc="build --@score_baselibs//score/mw/log/flags:KRemote_Logging=False\n",
            module_rc="build --@score_logging//score/mw/log/flags:KRemote_Logging=False\n",
        )
        assert find_conflicts(collect_occurrences(root)) == {}

    def test_consistent_tree_has_no_conflicts(self, tmp_path: Path):
        root = _tree(
            tmp_path,
            bazelrc="build --@score_baselibs//score/log_rust:safety_level=qm\n",
            module_rc="build --@score_baselibs//score/log_rust:safety_level=qm\n",
            extra_test_config=["@score_baselibs//score/log_rust:safety_level=qm"],
        )
        assert find_conflicts(collect_occurrences(root)) == {}

    def test_comments_are_not_scanned(self, tmp_path: Path):
        root = _tree(
            tmp_path,
            bazelrc="build --@score_baselibs//score/log_rust:safety_level=qm\n",
            module_rc="# was --@score_baselibs//src/log:safety_level=qm before the move\n",
        )
        assert find_conflicts(collect_occurrences(root)) == {}


class TestCollectOccurrences:
    def test_reads_all_three_sources(self, tmp_path: Path):
        root = _tree(
            tmp_path,
            bazelrc="build --@a//p:one=1\n",
            module_rc="build --@b//p:two=2\n",
            extra_test_config=["@c//p:three=3"],
        )
        assert {o.label for o in collect_occurrences(root)} == {"@a//p:one", "@b//p:two", "@c//p:three"}

    def test_repo_relative_label_kept(self, tmp_path: Path):
        root = _tree(tmp_path, bazelrc="common --//score/datarouter/flags:file_transfer=False\n")
        assert [o.label for o in collect_occurrences(root)] == ["//score/datarouter/flags:file_transfer"]


class TestLiveTree:
    def test_ref_int_own_configuration_is_consistent(self):
        """The check this guard exists for: ref_int's real tree must pass."""
        conflicts = find_conflicts(collect_occurrences(REF_INT_ROOT))
        assert conflicts == {}, f"stale build-setting labels in ref_int: {conflicts}"

    def test_main_exits_nonzero_on_conflict(self, tmp_path: Path, capsys: pytest.CaptureFixture):
        root = _tree(
            tmp_path,
            bazelrc="build --@score_baselibs//score/log_rust:safety_level=qm\n",
            module_rc="build --@score_baselibs//src/log:safety_level=qm\n",
        )
        assert main(["--root", str(root)]) == 1
        assert "safety_level" in capsys.readouterr().err
