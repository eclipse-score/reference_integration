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
Generate MISRA C/C++ compliance reports from CodeQL database results.

Parses CodeQL analysis output and generates structured MISRA violation reports
for CI/CD integration and dashboard display.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

_LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")


def parse_codeql_results(results_path: Path) -> list[dict]:
    """
    Parse CodeQL SARIF or JSON results for MISRA violations.

    Args:
        results_path: Path to CodeQL results file (.sarif or .json)

    Returns:
        List of violation dictionaries with rule, location, and message fields
    """
    if not results_path.exists():
        _LOG.error(f"Results file not found: {results_path}")
        return []

    try:
        with open(results_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        _LOG.error(f"Failed to parse JSON from {results_path}: {e}")
        return []

    violations = []

    # Handle SARIF format
    if results_path.suffix == ".sarif":
        for run in data.get("runs", []):
            tool_name = run.get("tool", {}).get("driver", {}).get("name", "")
            _LOG.info(f"Parsing CodeQL results from: {tool_name}")

            for result in run.get("results", []):
                rule_id = result.get("ruleId", "unknown")
                message = result.get("message", {}).get("text", "")

                # Extract location information
                locations = result.get("locations", [])
                if locations:
                    physical_loc = locations[0].get("physicalLocation", {})
                    artifact_location = physical_loc.get("artifactLocation", {})
                    file_path = artifact_location.get("uri", "unknown")

                    region = physical_loc.get("region", {})
                    line = region.get("startLine", 0)
                    column = region.get("startColumn", 0)

                    violations.append({
                        "rule": rule_id,
                        "file": file_path,
                        "line": line,
                        "column": column,
                        "message": message,
                        "level": result.get("level", "warning"),
                    })
    else:
        # Handle generic JSON format (CodeQL query results)
        if isinstance(data, list):
            for item in data:
                violations.append({
                    "rule": item.get("rule", "unknown"),
                    "file": item.get("file", "unknown"),
                    "line": item.get("line", 0),
                    "message": item.get("message", ""),
                })
        elif isinstance(data, dict):
            # Try common CodeQL result structures
            results = data.get("results", data.get("violations", []))
            for item in results:
                violations.append({
                    "rule": item.get("rule", "unknown"),
                    "file": item.get("file", "unknown"),
                    "line": item.get("line", 0),
                    "message": item.get("message", ""),
                })

    _LOG.info(f"Found {len(violations)} MISRA violations")
    return violations


def generate_summary_report(violations: list[dict], output_path: Path) -> None:
    """
    Generate a summary report grouped by MISRA rule.

    Args:
        violations: List of violation dictionaries
        output_path: Path to write the JSON summary report
    """
    # Group violations by rule
    rule_groups = {}
    for v in violations:
        rule = v.get("rule", "unknown")
        if rule not in rule_groups:
            rule_groups[rule] = {
                "rule": rule,
                "count": 0,
                "violations": [],
            }
        rule_groups[rule]["count"] += 1
        rule_groups[rule]["violations"].append({
            "file": v.get("file", ""),
            "line": v.get("line", 0),
            "message": v.get("message", ""),
        })

    # Sort by count (most violations first)
    sorted_rules = sorted(rule_groups.values(), key=lambda x: x["count"], reverse=True)

    report = {
        "total_violations": len(violations),
        "unique_rules": len(sorted_rules),
        "rules": sorted_rules,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    _LOG.info(f"Summary report written to {output_path}")


def generate_markdown_report(violations: list[dict], output_path: Path) -> None:
    """
    Generate a Markdown report for GitHub/CI display.

    Args:
        violations: List of violation dictionaries
        output_path: Path to write the Markdown report
    """
    # Group by rule
    rule_groups = {}
    for v in violations:
        rule = v.get("rule", "unknown")
        if rule not in rule_groups:
            rule_groups[rule] = []
        rule_groups[rule].append(v)

    lines = [
        "# MISRA Compliance Report",
        "",
        f"**Total Violations:** {len(violations)}",
        f"**Unique Rules:** {len(rule_groups)}",
        "",
        "## Summary by Rule",
        "",
        "| Rule | Count |",
        "|------|-------|",
    ]

    for rule, v_list in sorted(rule_groups.items(), key=lambda x: len(x[1]), reverse=True):
        lines.append(f"| {rule} | {len(v_list)} |")

    lines.extend(["", "## Violations by Rule", ""])

    for rule, v_list in sorted(rule_groups.items()):
        lines.extend([f"### {rule}", "", f"*{len(v_list)} violation(s)*", ""])
        for v in v_list:
            file_path = v.get("file", "")
            line_num = v.get("line", 0)
            message = v.get("message", "")
            lines.append(f"- **{file_path}:{line_num}**: {message}")
        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    _LOG.info(f"Markdown report written to {output_path}")


def main() -> int:
    """Main entry point for standalone execution."""
    parser = argparse.ArgumentParser(
        description="Generate MISRA compliance reports from CodeQL results"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to CodeQL SARIF or JSON results file",
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="./misra_reports",
        help="Output directory for generated reports (default: ./misra_reports)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "markdown", "all"],
        default="all",
        help="Report format to generate (default: all)",
    )

    args = parser.parse_args()

    results_path = Path(args.input)
    output_dir = Path(args.output_dir)

    # Parse violations from CodeQL results
    violations = parse_codeql_results(results_path)

    if not violations:
        _LOG.warning("No MISRA violations found in input file")
        return 0

    # Generate requested report formats
    if args.format in ("json", "all"):
        summary_path = output_dir / "misra_summary.json"
        generate_summary_report(violations, summary_path)

    if args.format in ("markdown", "all"):
        markdown_path = output_dir / "misra_report.md"
        generate_markdown_report(violations, markdown_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
