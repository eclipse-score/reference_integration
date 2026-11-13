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
"""Unit tests for update_module_latest.py (grouped known_good.json handling)."""

import json
import re
import sys
from pathlib import Path

# update_module_latest.py imports `models.known_good` relative to its own directory.
_KNOWN_GOOD_DIR = Path(__file__).resolve().parents[1]
if str(_KNOWN_GOOD_DIR) not in sys.path:
    sys.path.insert(0, str(_KNOWN_GOOD_DIR))

import update_module_latest  # noqa: E402

OLD = "0" * 40
NEW = "f" * 40


def _write_known_good(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "modules": {
                    "target_sw": {
                        "score_a": {"repo": "https://github.com/example/a.git", "hash": OLD},
                        "score_pinned": {
                            "repo": "https://github.com/example/pinned.git",
                            "hash": OLD,
                            "pin_version": True,
                        },
                    },
                    "tooling": {
                        "score_b": {"repo": "https://github.com/example/b.git", "hash": OLD},
                    },
                },
                "sbom": {"tracked_modules": ["score_a"]},
            }
        )
    )


def test_updates_modules_in_every_group_and_skips_pinned(tmp_path, monkeypatch):
    known_good = tmp_path / "known_good.json"
    output = tmp_path / "known_good.updated.json"
    _write_known_good(known_good)

    fetched = []

    def fake_fetch(owner_repo, branch):
        fetched.append((owner_repo, branch))
        return NEW

    monkeypatch.setattr(update_module_latest.shutil, "which", lambda _name: "/usr/bin/gh")
    monkeypatch.setattr(update_module_latest, "fetch_latest_commit_gh", fake_fetch)

    rc = update_module_latest.main(["--known-good", str(known_good), "--output", str(output)])

    assert rc == 0
    modules = json.loads(output.read_text())["modules"]
    assert modules["target_sw"]["score_a"]["hash"] == NEW
    assert modules["tooling"]["score_b"]["hash"] == NEW
    assert modules["target_sw"]["score_pinned"]["hash"] == OLD
    assert sorted(fetched) == [("example/a", "main"), ("example/b", "main")]


def test_written_timestamp_is_utc_with_a_single_z(tmp_path, monkeypatch):
    known_good = tmp_path / "known_good.json"
    output = tmp_path / "known_good.updated.json"
    _write_known_good(known_good)
    monkeypatch.setattr(update_module_latest.shutil, "which", lambda _name: "/usr/bin/gh")
    monkeypatch.setattr(update_module_latest, "fetch_latest_commit_gh", lambda _repo, _branch: NEW)

    update_module_latest.main(["--known-good", str(known_good), "--output", str(output)])

    timestamp = json.loads(output.read_text())["timestamp"]
    # e.g. 2026-09-28T05:39:55Z — not the old "...+00:00Z"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", timestamp), timestamp
