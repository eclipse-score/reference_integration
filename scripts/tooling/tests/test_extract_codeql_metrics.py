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

import jsonschema
import pytest

from cli.workflow.extract_codeql_metrics import (
    SCHEMA_VERSION,
    build_metrics,
    extract_codeql_metrics,
    extract_findings,
    load_sarif_file,
)


# Path to the schema relative to the repo root (two levels up from tests/)
_SCHEMA_PATH = Path(__file__).parents[3] / "docs/schemas/codeql-metrics-schema.json"


@pytest.fixture(scope="session")
def codeql_schema() -> dict:
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

MINIMAL_SARIF = {
    "runs": [
        {
            "results": [
                {
                    "ruleId": "cpp/use-after-free",
                    "level": "error",
                    "message": {"text": "Use after free detected"},
                },
                {
                    "ruleId": "cpp/misleading-indentation",
                    "level": "warning",
                    "message": {"text": "Misleading indentation"},
                },
                {
                    "ruleId": "cpp/misleading-indentation",
                    "level": "warning",
                    "message": {"text": "Misleading indentation again"},
                },
                {
                    "ruleId": "cpp/info-note",
                    "level": "none",
                    "message": {"text": "Informational note"},
                },
            ]
        }
    ]
}


@pytest.fixture
def sarif_file(tmp_path: Path) -> Path:
    p = tmp_path / "cpp.sarif"
    p.write_text(json.dumps(MINIMAL_SARIF), encoding="utf-8")
    return p


@pytest.fixture
def output_file(tmp_path: Path) -> Path:
    return tmp_path / "codeql-metrics.json"


# ---------------------------------------------------------------------------
# load_sarif_file
# ---------------------------------------------------------------------------


class TestLoadSarifFile:
    def test_returns_none_for_missing_file(self, tmp_path):
        assert load_sarif_file(tmp_path / "nonexistent.sarif") is None

    def test_loads_valid_sarif(self, sarif_file):
        data = load_sarif_file(sarif_file)
        assert data is not None
        assert "runs" in data

    def test_returns_none_for_invalid_json(self, tmp_path):
        bad = tmp_path / "bad.sarif"
        bad.write_text("{ not valid json }", encoding="utf-8")
        assert load_sarif_file(bad) is None


# ---------------------------------------------------------------------------
# extract_findings
# ---------------------------------------------------------------------------


class TestExtractFindings:
    def test_empty_sarif_returns_empty_list(self):
        assert extract_findings({}) == []

    def test_no_results_returns_empty_list(self):
        assert extract_findings({"runs": [{"results": []}]}) == []

    def test_extracts_count(self):
        findings = extract_findings(MINIMAL_SARIF)
        assert len(findings) == 4

    def test_level_none_maps_to_note(self):
        findings = extract_findings(MINIMAL_SARIF)
        note_findings = [f for f in findings if f["ruleId"] == "cpp/info-note"]
        assert note_findings[0]["severity"] == "note"

    def test_error_severity_preserved(self):
        findings = extract_findings(MINIMAL_SARIF)
        errors = [f for f in findings if f["severity"] == "error"]
        assert len(errors) == 1
        assert errors[0]["ruleId"] == "cpp/use-after-free"

    def test_warning_severity_preserved(self):
        findings = extract_findings(MINIMAL_SARIF)
        warnings = [f for f in findings if f["severity"] == "warning"]
        assert len(warnings) == 2

    def test_default_severity_is_warning(self):
        # result with no 'level' key
        sarif = {"runs": [{"results": [{"ruleId": "cpp/foo", "message": {"text": "msg"}}]}]}
        findings = extract_findings(sarif)
        assert findings[0]["severity"] == "warning"

    def test_message_extracted_from_dict(self):
        findings = extract_findings(MINIMAL_SARIF)
        assert findings[0]["message"] == "Use after free detected"

    def test_rule_id_in_findings(self):
        findings = extract_findings(MINIMAL_SARIF)
        rule_ids = {f["ruleId"] for f in findings}
        assert "cpp/use-after-free" in rule_ids
        assert "cpp/misleading-indentation" in rule_ids

    def test_multiple_runs(self):
        sarif = {
            "runs": [
                {"results": [{"ruleId": "cpp/a", "level": "error", "message": {"text": "a"}}]},
                {"results": [{"ruleId": "cpp/b", "level": "warning", "message": {"text": "b"}}]},
            ]
        }
        assert len(extract_findings(sarif)) == 2


# ---------------------------------------------------------------------------
# build_metrics
# ---------------------------------------------------------------------------


class TestBuildMetrics:
    def test_empty_findings_produces_zero_counts(self):
        metrics = build_metrics([])
        assert metrics["overall_metrics"]["total_findings"] == 0
        assert metrics["overall_metrics"]["errors"] == 0
        assert metrics["overall_metrics"]["warnings"] == 0
        assert metrics["overall_metrics"]["notes"] == 0

    def test_empty_findings_zero_percentages(self):
        metrics = build_metrics([])
        for sev in ("error", "warning", "note"):
            assert metrics["metrics_by_severity"][sev]["percentage"] == 0

    def test_total_findings_count(self):
        findings = extract_findings(MINIMAL_SARIF)
        metrics = build_metrics(findings)
        assert metrics["overall_metrics"]["total_findings"] == 4

    def test_severity_counts(self):
        findings = extract_findings(MINIMAL_SARIF)
        metrics = build_metrics(findings)
        assert metrics["overall_metrics"]["errors"] == 1
        assert metrics["overall_metrics"]["warnings"] == 2
        assert metrics["overall_metrics"]["notes"] == 1

    def test_percentages_sum_to_100(self):
        findings = extract_findings(MINIMAL_SARIF)
        metrics = build_metrics(findings)
        total_pct = sum(
            v["percentage"] for v in metrics["metrics_by_severity"].values()
        )
        assert abs(total_pct - 100.0) < 0.1

    def test_rule_aggregation(self):
        findings = extract_findings(MINIMAL_SARIF)
        metrics = build_metrics(findings)
        assert metrics["metrics_by_rule"]["cpp/misleading-indentation"]["count"] == 2
        assert metrics["metrics_by_rule"]["cpp/use-after-free"]["count"] == 1

    def test_rules_sorted_by_count_descending(self):
        findings = extract_findings(MINIMAL_SARIF)
        metrics = build_metrics(findings)
        counts = [v["count"] for v in metrics["metrics_by_rule"].values()]
        assert counts == sorted(counts, reverse=True)

    def test_schema_version_present(self):
        metrics = build_metrics([])
        assert metrics["schema_version"] == SCHEMA_VERSION

    def test_generated_at_present(self):
        metrics = build_metrics([])
        assert "generated_at" in metrics
        assert metrics["generated_at"]  # non-empty string


# ---------------------------------------------------------------------------
# extract_codeql_metrics (integration)
# ---------------------------------------------------------------------------


class TestExtractCodeqlMetrics:
    def test_returns_true_on_success(self, sarif_file, output_file):
        assert extract_codeql_metrics(sarif_file, output_file) is True

    def test_writes_output_file(self, sarif_file, output_file):
        extract_codeql_metrics(sarif_file, output_file)
        assert output_file.exists()

    def test_output_is_valid_json(self, sarif_file, output_file):
        extract_codeql_metrics(sarif_file, output_file)
        data = json.loads(output_file.read_text(encoding="utf-8"))
        assert "overall_metrics" in data

    def test_creates_empty_metrics_when_sarif_missing(self, tmp_path, output_file):
        result = extract_codeql_metrics(tmp_path / "missing.sarif", output_file)
        assert result is True
        data = json.loads(output_file.read_text(encoding="utf-8"))
        assert data["overall_metrics"]["total_findings"] == 0

    def test_empty_metrics_output_file_created(self, tmp_path, output_file):
        extract_codeql_metrics(tmp_path / "missing.sarif", output_file)
        assert output_file.exists()

    def test_creates_parent_directories(self, sarif_file, tmp_path):
        nested_output = tmp_path / "a" / "b" / "metrics.json"
        result = extract_codeql_metrics(sarif_file, nested_output)
        assert result is True
        assert nested_output.exists()


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


class TestSchemaValidation:
    def test_build_metrics_with_findings_is_valid(self, codeql_schema):
        findings = extract_findings(MINIMAL_SARIF)
        metrics = build_metrics(findings)
        jsonschema.validate(instance=metrics, schema=codeql_schema)

    def test_build_metrics_empty_findings_is_valid(self, codeql_schema):
        metrics = build_metrics([])
        jsonschema.validate(instance=metrics, schema=codeql_schema)

    def test_extract_codeql_metrics_output_is_valid(self, sarif_file, output_file, codeql_schema):
        extract_codeql_metrics(sarif_file, output_file)
        data = json.loads(output_file.read_text(encoding="utf-8"))
        jsonschema.validate(instance=data, schema=codeql_schema)

    def test_empty_metrics_output_is_valid(self, tmp_path, output_file, codeql_schema):
        extract_codeql_metrics(tmp_path / "missing.sarif", output_file)
        data = json.loads(output_file.read_text(encoding="utf-8"))
        jsonschema.validate(instance=data, schema=codeql_schema)
