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
"""Tests for the Stage-1 + Stage-2 report aggregation, focused on ownership attribution."""

import json
import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from aggregate_quality_report import (  # noqa: E402
    ATTRIBUTION_NAME,
    _classify,
    _extract_table_data_rows,
    _parse_ut_rows,
    _read_attributions,
)


def _report_dir(root: Path, module: str, rows: str, attribution: dict | None = None) -> Path:
    """Build one `stage2-report-<module>/` artifact directory as Stage 2 uploads it."""
    d = root / f"stage2-report-{module}"
    d.mkdir(parents=True)
    (d / "unit_test_summary.md").write_text(
        "# Unit Test Execution Summary\n\n| module | passed | failed | skipped | total |\n"
        "| --- | --- | --- | --- | --- |\n" + rows
    )
    if attribution is not None:
        (d / ATTRIBUTION_NAME).write_text(json.dumps(attribution))
    return d


class TestClassify:
    def test_passing_module_is_owned_by_nobody(self):
        assert _classify(total=248, failed=0) == ("✅ passed", "—")

    def test_failing_tests_are_the_module_team_s(self):
        verdict, owner = _classify(total=248, failed=3)
        assert "3 failing" in verdict
        assert "module team" in owner

    def test_zero_tests_with_no_attribution_stays_ref_int_s(self):
        # No attribution file: the conservative default is unchanged.
        _verdict, owner = _classify(total=0, failed=0)
        assert owner == "ref_int (harness defect)"

    def test_zero_tests_with_an_integration_conflict_is_not_a_harness_defect(self):
        # The regression: ownership was re-derived from total == 0, overwriting the verdict
        # quality_runners had already computed.
        verdict, owner = _classify(
            total=0, failed=0, attribution={"owner": "integration conflict", "conflicting": ["score_crates"]}
        )
        assert owner != "ref_int (harness defect)"
        assert "integration conflict" in owner
        assert "score_crates" in verdict or "score_crates" in owner

    def test_zero_tests_attributed_to_ref_int_is_still_ref_int_s(self):
        _verdict, owner = _classify(total=0, failed=0, attribution={"owner": "ref_int harness defect"})
        assert owner == "ref_int (harness defect)"

    def test_attribution_is_ignored_once_tests_actually_ran(self):
        # A stale attribution must never downgrade a real test failure.
        _verdict, owner = _classify(total=248, failed=1, attribution={"owner": "integration conflict"})
        assert "module team" in owner


class TestReadAttributions:
    def test_reads_the_sidecar(self, tmp_path: Path):
        d = _report_dir(
            tmp_path,
            "score_communication",
            "| score_communication | 0 | 0 | 0 | 0 |\n",
            {"score_communication": {"owner": "integration conflict", "conflicting": ["score_crates"]}},
        )
        assert _read_attributions(d) == {
            "score_communication": {"owner": "integration conflict", "conflicting": ["score_crates"]}
        }

    def test_absent_sidecar_is_empty_not_an_error(self, tmp_path: Path):
        d = _report_dir(tmp_path, "score_time", "| score_time | 314 | 0 | 0 | 314 |\n")
        assert _read_attributions(d) == {}

    def test_unparseable_sidecar_is_empty_not_an_error(self, tmp_path: Path):
        # A corrupt sidecar degrades to the count-based default rather than crashing the job.
        d = _report_dir(tmp_path, "score_time", "| score_time | 0 | 0 | 0 | 0 |\n")
        (d / ATTRIBUTION_NAME).write_text("{not json")
        assert _read_attributions(d) == {}


class TestTableParsing:
    def test_data_rows_skip_title_header_and_separator(self, tmp_path: Path):
        d = _report_dir(tmp_path, "score_time", "| score_time | 314 | 0 | 0 | 314 |\n")
        rows = _extract_table_data_rows(d / "unit_test_summary.md")
        assert rows == ["| score_time | 314 | 0 | 0 | 314 |"]

    def test_non_numeric_rows_are_skipped_not_fatal(self):
        assert _parse_ut_rows(["| score_time | n/a | 0 | 0 | 314 |"]) == []

    def test_parses_counts(self):
        assert _parse_ut_rows(["| score_time | 314 | 0 | 0 | 314 |"]) == [("score_time", 314, 0, 0, 314)]


class TestExitCode:
    """A module that executed no tests must never make the report exit 0 (Invariant I14)."""

    @pytest.mark.parametrize(
        "attribution",
        [None, {"owner": "integration conflict", "conflicting": ["score_crates"]}],
        ids=["unattributed", "integration-conflict"],
    )
    def test_zero_tests_is_a_failure_however_it_is_attributed(self, attribution):
        # Attribution changes who acts, never whether it passed.
        _verdict, owner = _classify(total=0, failed=0, attribution=attribution)
        assert owner != "—"
