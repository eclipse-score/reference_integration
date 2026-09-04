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
"""Aggregate Stage 1 and Stage 2 quality reports into a single consolidated report.

The upstream aggregation step of DR-008 Option 4. ``--stage2-dir`` holds one
``stage2-report-<module>/`` per module, each with the ``unit_test_summary.md`` and
``coverage_summary.md`` quality_runners.py produced.

Usage:
  python3 scripts/aggregate_quality_report.py \\
      --stage1-result success \\
      --stage2-result success \\
      --stage2-dir _stage2_reports/ \\
      >> "$GITHUB_STEP_SUMMARY"
"""

import argparse
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
try:
    from known_good.resolved_dependencies import workspace_path
except ImportError:
    if str(_HERE) not in sys.path:
        sys.path.insert(0, str(_HERE))
    from known_good.resolved_dependencies import workspace_path  # noqa: E402

_STATUS_MAP = {
    "success": "✅ Success",
    "failure": "❌ Failure",
    "cancelled": "⚪ Cancelled",
    "skipped": "⚪ Skipped",
    "": "⚪ Unknown",
}

# Printed when an exclusion carries no recorded reason, so the gap is visible in the report
# rather than papered over with a generic justification.
_NO_EXCLUSION_REASON = "⚠️ no reason recorded"

# Written by quality_runners.py into the same report directory; keep in sync with the constant of
# the same name there. Carries the owner of a failure, which the count columns cannot: zero tests
# looks identical for a harness defect and an integration conflict.
ATTRIBUTION_NAME = "failure_attribution.json"

_OWNER_REF_INT = "ref_int (harness defect)"
_OWNER_MODULE = "module team (integration finding)"
_OWNER_JOINT = "integration conflict (ref_int pin ↔ module sources)"


def _format_status(result: str) -> str:
    return _STATUS_MAP.get(result.lower().strip(), "⚪ Unknown")


def _read_attributions(artifact_dir: Path) -> dict[str, dict]:
    """Return ``{module: {"owner", "conflicting"}}`` from one report directory.

    Missing or unparseable is ``{}``, so :func:`_classify` falls back to its count-based default
    rather than the report failing on a corrupt sidecar.
    """
    path = artifact_dir / ATTRIBUTION_NAME
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


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


def _parse_ut_rows(rows: list[str]) -> list[tuple[str, int, int, int, int]]:
    """Parse ``| module | passed | failed | skipped | total |`` rows into typed tuples.

    Rows whose numeric cells do not parse are skipped rather than crashing the report.
    """
    parsed: list[tuple[str, int, int, int, int]] = []
    for row in rows:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        try:
            parsed.append((cells[0], int(cells[1]), int(cells[2]), int(cells[3]), int(cells[4])))
        except ValueError:
            continue
    return parsed


def _classify(total: int, failed: int, attribution: dict | None = None) -> tuple[str, str]:
    """Return (verdict, owner) for one module's unit-test result.

    Zero tests validated nothing and always fails, but *who must act* does not follow from the
    count: only ``quality_runners.classify_gate_failure`` sees which repositories the failure
    named, and ``attribution`` is that verdict carried through :data:`ATTRIBUTION_NAME`.

    Tests that ran and failed are the module team's regardless of any earlier attribution; an
    absent attribution keeps ref_int as the conservative default.
    """
    if total == 0:
        owner = (attribution or {}).get("owner", "")
        conflicting = (attribution or {}).get("conflicting") or []
        if owner == "integration conflict":
            over = f" over {', '.join(conflicting)}" if conflicting else ""
            return f"❌ no tests executed — integration conflict{over}", _OWNER_JOINT
        return "❌ no tests executed", _OWNER_REF_INT
    if failed > 0:
        return f"❌ {failed} failing", _OWNER_MODULE
    return "✅ passed", "—"


def _excluded_test_targets(known_good_path: Path) -> list[tuple[str, list[tuple[str, str]]]]:
    """Return [(module, [(excluded target, reason)])] for target_sw modules in known_good.json.

    These targets never run in Stage 2 and so are absent from the counts above; they remain
    covered by each module's own CI. Surfacing them keeps the report honest about completeness.

    The reason is printed rather than inferred. Stage 2 runs each module as the Bazel *root*, so
    the old blanket explanation -- "depends on dev_dependency-only deps invisible from the
    resolved graph" -- describes a build scope that no longer exists: a root module's dev edges
    are active. An exclusion that survives that change has a specific, scope-independent reason
    (a benchmark, a sanitizer or miri target), and it belongs in ``metadata.exclude_test_target_reasons``
    next to the label. An entry with no recorded reason is flagged here instead of being dressed
    up in a justification nobody checked.
    """
    if not known_good_path.exists():
        return []

    data = json.loads(known_good_path.read_text(encoding="utf-8"))
    target_sw = data.get("modules", {}).get("target_sw", {})

    excluded: list[tuple[str, list[tuple[str, str]]]] = []
    for name in sorted(target_sw):
        metadata = target_sw[name].get("metadata", {})
        targets = metadata.get("exclude_test_targets", [])
        reasons = metadata.get("exclude_test_target_reasons", {})
        if targets:
            excluded.append((name, [(t, reasons.get(t, _NO_EXCLUSION_REASON)) for t in targets]))
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
    # Under 'bazel run' the cwd is the runfiles tree, so relative paths need anchoring.
    args.stage2_dir = workspace_path(args.stage2_dir)
    args.known_good_path = workspace_path(args.known_good_path)

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
    attributions: dict[str, dict] = {}

    if stage2_dir.exists():
        for artifact_dir in sorted(stage2_dir.iterdir()):
            if not artifact_dir.is_dir():
                continue
            if not artifact_dir.name.startswith("stage2-report-"):
                continue
            ut_rows.extend(_extract_table_data_rows(artifact_dir / "unit_test_summary.md"))
            cov_rows.extend(_extract_table_data_rows(artifact_dir / "coverage_summary.md"))
            attributions.update(_read_attributions(artifact_dir))
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

    # Failure ownership — a Stage-2 job that ran no tests validated nothing and always fails, but
    # the owner comes from the attribution Stage 2 recorded, never from the count (see _classify).
    parsed = _parse_ut_rows(ut_rows)
    no_tests = [name for name, _p, _f, _s, total in parsed if total == 0]
    if parsed:
        out.write("### Failure Ownership\n\n")
        out.write("| module | tests run | verdict | owner |\n")
        out.write("|--------|-----------|---------|-------|\n")
        for name, _passed, failed, _skipped, total in parsed:
            verdict, owner = _classify(total, failed, attributions.get(name))
            out.write(f"| {name} | {total} | {verdict} | {owner} |\n")
        out.write("\n")

    if cov_rows:
        out.write("### Coverage Summary\n\n")
        out.write("| module | lines | functions | branches |\n")
        out.write("|--------|-------|-----------|----------|\n")
        for row in cov_rows:
            out.write(f"{row}\n")
        out.write("\n")

    # score_communication has known-broken rust coverage extraction (mostly proc_macro) and is
    # excluded from the *_rust rows above in both modes — see DISABLED_RUST_COVERAGE in
    # quality_runners.py. Stated explicitly so its absent row reads as "not measured for this
    # module", not "not measured at all".
    out.write(
        "> Rust coverage is not measured for `score_communication` "
        "(known extraction issues, mostly proc_macro). Rust *tests* do run for it; every "
        "other Rust module's coverage is measured in Stage 2 the same as in the old workflow.\n\n"
    )

    # ------------------------------------------------------------------
    # Excluded test targets — completeness disclosure (DR-008 Q4)
    # ------------------------------------------------------------------
    excluded = _excluded_test_targets(args.known_good_path)
    if excluded:
        out.write("### Test Targets Excluded from Stage 2\n\n")
        out.write(
            "These targets do not run in Stage 2, so they are not counted above. They are still "
            "validated by each module's own CI. Stage 2 runs each module as the Bazel root, so an "
            "exclusion has to justify itself on its own terms — the reason is recorded per target "
            "in `known_good.json`.\n\n"
        )
        out.write("| module | excluded test target | reason |\n")
        out.write("|--------|----------------------|--------|\n")
        for module_name, targets in excluded:
            for target, reason in targets:
                out.write(f"| {module_name} | `{target}` | {reason} |\n")
        out.write("\n")

    # ------------------------------------------------------------------
    # Overall status
    # ------------------------------------------------------------------
    out.write("## Overall Status\n\n")
    stage1_ok = args.stage1_result == "success"
    stage2_ok = args.stage2_result in ("success", "skipped")
    # A module that configured but executed no tests is a failure: Stage 2's purpose is to
    # run the module's tests against the resolved set, and zero tests validates nothing.
    tests_ran = not no_tests

    if stage1_ok and stage2_ok and tests_ran:
        out.write("✅ All quality checks passed.\n")
    else:
        out.write("❌ One or more quality checks failed — see details above.\n\n")
        out.write("| Stage | Result |\n")
        out.write("|-------|--------|\n")
        out.write(f"| Stage 1 (integration) | {_format_status(args.stage1_result)} |\n")
        out.write(f"| Stage 2 (module validation) | {_format_status(args.stage2_result)} |\n")
        # Both are failures, but they go to different people, so they cannot share one heading.
        conflicts = [n for n in no_tests if (attributions.get(n) or {}).get("owner") == "integration conflict"]
        harness = [n for n in no_tests if n not in conflicts]
        if harness:
            out.write(
                f"\n**ref_int harness defect** — no tests executed for: "
                f"{', '.join(f'`{n}`' for n in harness)}. "
                "These did not validate the resolved dependency set.\n"
            )
        for name in conflicts:
            over = ", ".join(f"`{c}`" for c in (attributions.get(name) or {}).get("conflicting") or [])
            out.write(
                f"\n**Integration conflict** — `{name}` did not run: ref_int's resolved set and the "
                f"module's sources are each self-consistent but mutually incompatible"
                f"{f' over {over}' if over else ''}. "
                "Resolve by moving ref_int's pin or the module's `known_good` commit — not by "
                "changing the harness.\n"
            )

    return 0 if (stage1_ok and stage2_ok and tests_ran) else 1


if __name__ == "__main__":
    sys.exit(main())
