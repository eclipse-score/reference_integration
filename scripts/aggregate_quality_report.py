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
Aggregate Stage 1 and Stage 2 quality reports into a single consolidated report.

Implements the upstream aggregation step of DR-008 Option 4: reads per-module
unit_test_summary.md and coverage_summary.md from downloaded stage2-report-*
artifacts and combines them with the Stage 1 integration result.

Usage:
  python3 scripts/aggregate_quality_report.py \\
      --stage1-result success \\
      --stage2-result success \\
      --stage2-dir _stage2_reports/ \\
      >> "$GITHUB_STEP_SUMMARY"

The --stage2-dir is expected to contain subdirectories named
stage2-report-<module>, each holding unit_test_summary.md and
coverage_summary.md produced by quality_runners.py.
"""

import argparse
import json
import sys
from pathlib import Path

_STATUS_MAP = {
    "success": "✅ Success",
    "failure": "❌ Failure",
    "cancelled": "⚪ Cancelled",
    "skipped": "⚪ Skipped",
    "": "⚪ Unknown",
}


def _format_status(result: str) -> str:
    return _STATUS_MAP.get(result.lower().strip(), "⚪ Unknown")


def _extract_table_data_rows(md_path: Path) -> list[str]:
    """Return the data rows of the first markdown table found in md_path.

    Skips the title line (starts with #), the header row, and the separator
    row (contains ---), then collects all remaining pipe-delimited lines.
    """
    if not md_path.exists():
        return []

    lines = md_path.read_text(encoding="utf-8").splitlines()
    data_rows: list[str] = []
    header_seen = False
    separator_seen = False

    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if not header_seen:
            header_seen = True
            continue
        if not separator_seen:
            separator_seen = True
            continue
        if stripped:
            data_rows.append(stripped)

    return data_rows


def _excluded_test_targets(known_good_path: Path) -> list[tuple[str, list[str]]]:
    """Return [(module, [excluded targets])] for target_sw modules in known_good.json.

    These targets are excluded from Stage 2 (e.g. they depend on dev_dependency-only
    deps) and so are absent from the consolidated report — they are still covered by
    each module's own CI. Surfacing them keeps the report honest about completeness.
    """
    if not known_good_path.exists():
        return []

    data = json.loads(known_good_path.read_text(encoding="utf-8"))
    target_sw = data.get("modules", {}).get("target_sw", {})

    excluded: list[tuple[str, list[str]]] = []
    for name in sorted(target_sw):
        targets = target_sw[name].get("metadata", {}).get("exclude_test_targets", [])
        if targets:
            excluded.append((name, targets))
    return excluded


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Aggregate Stage 1 + Stage 2 quality reports (DR-008 Option 4).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 scripts/aggregate_quality_report.py \\\n"
            "    --stage1-result success \\\n"
            "    --stage2-result failure \\\n"
            "    --stage2-dir _stage2_reports/ \\\n"
            "    >> $GITHUB_STEP_SUMMARY\n"
        ),
    )
    parser.add_argument(
        "--stage1-result",
        default="",
        help="GitHub Actions result of the stage1_integration job (success/failure/cancelled/skipped).",
    )
    parser.add_argument(
        "--stage2-result",
        default="",
        help="GitHub Actions result of the stage2_module_validation job.",
    )
    parser.add_argument(
        "--stage2-dir",
        type=Path,
        default=Path("_stage2_reports"),
        help="Directory containing downloaded stage2-report-* artifact subdirectories.",
    )
    parser.add_argument(
        "--known-good-path",
        type=Path,
        default=Path("known_good.json"),
        help="Path to known_good.json (used to list test targets excluded from Stage 2).",
    )
    args = parser.parse_args()

    out = sys.stdout

    out.write("# S-CORE Quality Report — DR-008 Option 4\n\n")

    # ------------------------------------------------------------------
    # Stage 1 summary
    # ------------------------------------------------------------------
    out.write("## Stage 1 — Integration Results\n\n")
    out.write("| Check | Status |\n")
    out.write("|-------|--------|\n")
    out.write(f"| Platform Build + Feature Integration Tests (linux-x86_64) | {_format_status(args.stage1_result)} |\n")
    out.write("\n")

    # ------------------------------------------------------------------
    # Stage 2 summary — read per-module reports
    # ------------------------------------------------------------------
    out.write("## Stage 2 — Module Validation Results\n\n")

    stage2_dir: Path = args.stage2_dir
    ut_rows: list[str] = []
    cov_rows: list[str] = []

    if stage2_dir.exists():
        for artifact_dir in sorted(stage2_dir.iterdir()):
            if not artifact_dir.is_dir():
                continue
            if not artifact_dir.name.startswith("stage2-report-"):
                continue
            ut_rows.extend(_extract_table_data_rows(artifact_dir / "unit_test_summary.md"))
            cov_rows.extend(_extract_table_data_rows(artifact_dir / "coverage_summary.md"))
    else:
        out.write(f"*Stage 2 reports directory not found: `{stage2_dir}`*\n\n")

    if ut_rows:
        out.write("### Unit Test Summary\n\n")
        out.write("| module | passed | failed | skipped | total |\n")
        out.write("|--------|--------|--------|---------|-------|\n")
        for row in ut_rows:
            out.write(f"{row}\n")
        out.write("\n")
    else:
        out.write("*No Stage 2 unit test reports found.*\n\n")

    if cov_rows:
        out.write("### Coverage Summary\n\n")
        out.write("| module | lines | functions | branches |\n")
        out.write("|--------|-------|-----------|----------|\n")
        for row in cov_rows:
            out.write(f"{row}\n")
        out.write("\n")

    # ------------------------------------------------------------------
    # Excluded test targets — completeness disclosure (DR-008 Q4)
    # ------------------------------------------------------------------
    excluded = _excluded_test_targets(args.known_good_path)
    if excluded:
        out.write("### Test Targets Excluded from Stage 2\n\n")
        out.write(
            "These targets are excluded from central Stage 2 execution (typically because "
            "they depend on `dev_dependency`-only deps that are not visible from the resolved "
            "graph). They are still validated by each module's own CI.\n\n"
        )
        out.write("| module | excluded test target |\n")
        out.write("|--------|----------------------|\n")
        for module_name, targets in excluded:
            for target in targets:
                out.write(f"| {module_name} | `{target}` |\n")
        out.write("\n")

    # ------------------------------------------------------------------
    # Overall status
    # ------------------------------------------------------------------
    out.write("## Overall Status\n\n")
    stage1_ok = args.stage1_result == "success"
    stage2_ok = args.stage2_result in ("success", "skipped")

    if stage1_ok and stage2_ok:
        out.write("✅ All quality checks passed.\n")
    else:
        out.write("❌ One or more quality checks failed — see details above.\n\n")
        out.write("| Stage | Result |\n")
        out.write("|-------|--------|\n")
        out.write(f"| Stage 1 (integration) | {_format_status(args.stage1_result)} |\n")
        out.write(f"| Stage 2 (module validation) | {_format_status(args.stage2_result)} |\n")

    return 0 if (stage1_ok and stage2_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
