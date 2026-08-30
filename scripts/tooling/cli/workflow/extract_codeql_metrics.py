#!/usr/bin/env python3
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
Extract CodeQL metrics from SARIF results.

Parses recategorized SARIF output from CodeQL analysis and produces a JSON file
containing aggregated metrics grouped by severity and rule, following the
codeql-metrics-schema.json specification.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

_LOG = logging.getLogger(__name__)

SARIF_FILE = "sarif-results/cpp.sarif"
OUTPUT_FILE = "codeql-metrics.json"
SCHEMA_VERSION = "1"


def load_sarif_file(sarif_path: Path) -> Optional[dict]:
    """Load and validate SARIF file exists and is valid JSON."""
    if not sarif_path.exists():
        _LOG.warning("SARIF file not found at %s", sarif_path)
        return None

    try:
        with open(sarif_path, "r", encoding="utf-8") as f:
            sarif_data = json.load(f)
        _LOG.info("Loaded SARIF file: %s", sarif_path)
        return sarif_data
    except (json.JSONDecodeError, IOError) as e:
        _LOG.error("Failed to load SARIF file: %s", e)
        return None


def extract_findings(sarif_data: dict) -> list[dict]:
    """
    Extract all findings from SARIF data.

    Returns list of findings with normalized structure:
    {
        "ruleId": "cpp/some-rule",
        "severity": "error|warning|note",
        "message": "...",
        "ruleName": "..."
    }
    """
    findings = []

    if "runs" not in sarif_data:
        _LOG.warning("No runs found in SARIF data")
        return findings

    for run in sarif_data.get("runs", []):
        for result in run.get("results", []):
            # Extract severity (default to 'warning' if not specified)
            level = result.get("level", "warning")
            # SARIF level can be: "none", "note", "warning", "error"
            if level == "none":
                severity = "note"
            else:
                severity = level

            # Extract rule ID
            rule_ref = result.get("ruleId", "unknown")
            rule_name = None

            # Try to get rule name from rule object if available
            if "rule" in result:
                rule_name = result["rule"].get("id", rule_ref)

            # Try to get from ruleIndex and rules array
            if not rule_name and "ruleIndex" in result and "rules" in run:
                rule_idx = result.get("ruleIndex", -1)
                if 0 <= rule_idx < len(run["rules"]):
                    rule_name = run["rules"][rule_idx].get("id", rule_ref)

            # Extract message
            message = "No message"
            if "message" in result:
                if isinstance(result["message"], dict):
                    message = result["message"].get("text", message)
                else:
                    message = str(result["message"])

            findings.append(
                {
                    "ruleId": rule_ref,
                    "severity": severity,
                    "message": message,
                    "ruleName": rule_name or rule_ref,
                }
            )

    _LOG.info("Extracted %d findings from SARIF", len(findings))
    return findings


def build_metrics(findings: list[dict]) -> dict:
    """
    Aggregate findings into metrics matching codeql-metrics-schema.json.

    Returns metrics dict with overall_metrics, metrics_by_severity, metrics_by_rule.
    """
    severity_counts = {"error": 0, "warning": 0, "note": 0}
    rule_metrics = {}

    # Aggregate by severity and rule
    for finding in findings:
        severity = finding["severity"]
        rule_id = finding["ruleId"]

        # Count by severity
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Aggregate by rule
        if rule_id not in rule_metrics:
            rule_metrics[rule_id] = {
                "count": 0,
                "severity": severity,
                "rule_name": finding.get("ruleName", rule_id),
            }
        rule_metrics[rule_id]["count"] += 1

    total_findings = len(findings)

    # Calculate percentages
    metrics_by_severity = {}
    for severity, count in severity_counts.items():
        percentage = (count / total_findings * 100) if total_findings > 0 else 0
        metrics_by_severity[severity] = {
            "count": count,
            "percentage": round(percentage, 2),
        }

    # Sort rules by count descending
    sorted_rules = dict(
        sorted(rule_metrics.items(), key=lambda x: x[1]["count"], reverse=True)
    )

    metrics = {
        "schema_version": SCHEMA_VERSION,
        "generated_by": "extract_codeql_metrics.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall_metrics": {
            "total_findings": total_findings,
            "errors": severity_counts["error"],
            "warnings": severity_counts["warning"],
            "notes": severity_counts["note"],
        },
        "metrics_by_severity": metrics_by_severity,
        "metrics_by_rule": sorted_rules,
    }

    return metrics


def extract_codeql_metrics(
    sarif_path: Path = Path(SARIF_FILE), output_path: Path = Path(OUTPUT_FILE)
) -> bool:
    """
    Main workflow: load SARIF, extract metrics, write output.

    Returns True on success, False on failure.
    """
    sarif_data = load_sarif_file(sarif_path)

    # If SARIF doesn't exist, output empty metrics
    if sarif_data is None:
        _LOG.info("Creating empty metrics file (no SARIF available)")
        empty_metrics = {
            "schema_version": SCHEMA_VERSION,
            "generated_by": "extract_codeql_metrics.py",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "overall_metrics": {
                "total_findings": 0,
                "errors": 0,
                "warnings": 0,
                "notes": 0,
            },
            "metrics_by_severity": {
                "error": {"count": 0, "percentage": 0},
                "warning": {"count": 0, "percentage": 0},
                "note": {"count": 0, "percentage": 0},
            },
            "metrics_by_rule": {},
        }
        output_path.write_text(json.dumps(empty_metrics, indent=2), encoding="utf-8")
        _LOG.info("Wrote empty metrics to %s", output_path)
        return True

    try:
        findings = extract_findings(sarif_data)
        metrics = build_metrics(findings)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        _LOG.info("Wrote metrics to %s", output_path)

        # Print summary
        print(f"CodeQL Metrics Summary:")
        print(f"  Total findings: {metrics['overall_metrics']['total_findings']}")
        print(f"  Errors: {metrics['overall_metrics']['errors']}")
        print(f"  Warnings: {metrics['overall_metrics']['warnings']}")
        print(f"  Notes: {metrics['overall_metrics']['notes']}")
        print(f"  Unique rules: {len(metrics['metrics_by_rule'])}")

        return True

    except Exception as e:
        _LOG.error("Failed to extract metrics: %s", e)
        return False


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register CLI command for extracting CodeQL metrics."""
    parser = subparsers.add_parser(
        "extract_codeql_metrics", help="Extract code quality metrics from CodeQL SARIF results"
    )
    parser.add_argument(
        "--sarif",
        metavar="PATH",
        default=SARIF_FILE,
        help=f"Path to SARIF file (default: {SARIF_FILE})",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default=OUTPUT_FILE,
        help=f"Output metrics JSON file (default: {OUTPUT_FILE})",
    )
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    """CLI entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    success = extract_codeql_metrics(
        sarif_path=Path(args.sarif),
        output_path=Path(args.output),
    )
    return 0 if success else 1


if __name__ == "__main__":
    # Can be run standalone for testing
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    success = extract_codeql_metrics()
    sys.exit(0 if success else 1)
