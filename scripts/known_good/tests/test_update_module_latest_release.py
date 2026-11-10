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
"""Unit tests for the pre-release version selection, report and known_good.json update."""

import datetime as dt
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[2]
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from known_good import update_module_latest_release  # noqa: E402
from known_good.update_module_latest_release import (  # noqa: E402
    Release,
    apply_versions,
    latest_version,
    render,
    tag_at,
)

TODAY = dt.date(2026, 11, 9)


def test_latest_version_semver_with_prerelease():
    assert latest_version({"versions": ["1.0.5", "1.0.6-rc1", "1.0.10", "1.0.9"]}) == "1.0.10"
    assert latest_version({"versions": ["1.0.5", "1.0.6-rc1"]}) == "1.0.6-rc1"
    assert latest_version({"versions": ["1.0.6-rc1", "1.0.6"]}) == "1.0.6"


def test_latest_version_skips_yanked():
    assert latest_version({"versions": ["0.2.0", "0.3.0"], "yanked_versions": {"0.3.0": "broken"}}) == "0.2.0"
    assert latest_version({"versions": []}) is None


def test_render_head_column_bold_from_threshold():
    ok = Release("score_a", "target_sw", "o/a", "main", "abc", "1.0.0", "v1.0.0", TODAY, 9)
    bad = Release("score_b", "tooling", "o/b", "main", "def", "2.0.0", "v2.0.0", TODAY, 10)
    report = render([ok, bad], TODAY)
    assert report.count("| Module |") == 1
    assert "| Now | Head | OK/NOK |" in report
    assert "| [9](https://github.com/o/a/compare/v1.0.0...main) | |" in report
    assert "| [**10**](https://github.com/o/b/compare/v2.0.0...main) | |" in report


def test_render_versions_table_shows_dates_before_and_now():
    ok = Release("score_a", "target_sw", "o/a", "main", "abc", "1.0.0", "v1.0.0", TODAY, 0)
    ok.current_date = dt.date(2026, 10, 1)
    report = render([ok], TODAY)
    assert "| Before | Now |" in report
    assert "| `abc` (2026-10-01) | [1.0.0](https://github.com/o/a/releases/tag/v1.0.0) (2026-11-09) |" in report


def test_render_before_shows_release_of_tagged_commit():
    entry = Release("score_a", "target_sw", "o/a", "main", "0.9.0", "1.0.0", "v1.0.0", TODAY, 0)
    entry.current_tag, entry.current_date = "v0.9.0", dt.date(2026, 10, 1)
    assert "| [0.9.0](https://github.com/o/a/releases/tag/v0.9.0) (2026-10-01) |" in render([entry], TODAY)


def test_tag_at_picks_highest_tag_on_commit_across_pages():
    pages = {
        1: [{"name": "v1.0.0", "commit": {"sha": "aaa111"}}, {"name": "v0.9.0", "commit": {"sha": "bbb222"}}],
        2: [{"name": "v0.10.0-rc1", "commit": {"sha": "bbb222"}}],
    }
    original = update_module_latest_release.http_json
    update_module_latest_release.http_json = lambda url, **_: pages.get(int(url.rsplit("page=", 1)[1]), [])
    try:
        assert tag_at("o/a", "bbb222") == "v0.10.0-rc1"
        assert tag_at("o/a", "ccc333") is None
    finally:
        update_module_latest_release.http_json = original


def test_apply_versions_touches_only_version_and_timestamp(tmp_path):
    path = tmp_path / "known_good.json"
    path.write_text(
        '{\n    "modules": {\n        "target_sw": {\n'
        '            "score_a": {\n                "repo": "r",\n                "hash": "abc",\n'
        '                "metadata": {\n                    "langs": [\n                        "cpp"\n'
        "                    ]\n                }\n            },\n"
        '            "score_b": {\n                "version": "0.1.0"\n            },\n'
        '            "score_c": {\n                "hash": "def"\n            }\n'
        '        }\n    },\n    "timestamp": "2026-01-01T00:00:00Z"\n}'
    )
    releases = [
        Release("score_a", "target_sw", "o/a", "main", "abc", "1.0.0"),
        Release("score_b", "target_sw", "o/b", "main", "0.1.0", "0.2.0"),
        Release("score_c", "target_sw", "o/c", "main", "def"),
    ]
    apply_versions(path, releases)
    text = path.read_text()
    assert '"repo": "r",\n                "version": "1.0.0",\n                "metadata"' in text
    assert '"version": "0.2.0"' in text
    assert '"hash": "def"' in text
    assert "rust_coverage_config" not in text
    assert not text.endswith("\n")
