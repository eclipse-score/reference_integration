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
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from scripts.tooling.lib.github import fetch_compare
from scripts.tooling.lib.known_good import KnownGood, load_known_good

_LOG = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent / "assets"


def _find_repo_root() -> Path:
    candidate = Path(__file__).resolve()
    for parent in candidate.parents:
        if (parent / "known_good.json").exists():
            return parent
    return Path.cwd()


def _resolve_path_from_bazel(path: Path) -> Path:
    if not path.is_absolute():
        build_working_dir = os.environ.get("BUILD_WORKING_DIRECTORY")
        if build_working_dir:
            return (Path(build_working_dir) / path).resolve()
    return path.resolve()


def _collect_entries(known_good: KnownGood) -> list[dict[str, Any]]:
    entries = []
    for group_name, group_modules in known_good.modules.items():
        for module in group_modules.values():
            try:
                owner_repo = module.owner_repo
            except ValueError:
                owner_repo = None
            entries.append(
                {
                    "name": module.name,
                    "group": group_name,
                    "repo": module.repo,
                    "owner_repo": owner_repo,
                    "hash": module.hash,
                    "version": module.version,
                    "branch": module.branch,
                    "current_hash": None,
                    "behind_by": None,
                    "compare_status": None,
                }
            )
    return entries


def _enrich_with_compare_data(entries: list[dict[str, Any]], token: str) -> None:
    for entry in entries:
        if not entry.get("owner_repo") or not entry.get("hash") or entry.get("version"):
            continue
        result = fetch_compare(entry["owner_repo"], entry["hash"], entry["branch"], token)
        if result:
            entry["current_hash"] = result.head_sha
            entry["behind_by"] = result.ahead_by
            entry["compare_status"] = result.status
        else:
            _LOG.warning("Could not fetch compare data for %s@%s", entry["owner_repo"], entry["branch"])


def generate_report(known_good: KnownGood, token: Optional[str] = None) -> str:
    entries = _collect_entries(known_good)
    if token:
        _enrich_with_compare_data(entries, token)
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html"]),
    )
    tmpl = env.get_template("report_template.html")
    return tmpl.render(
        modules_json=json.dumps(entries, indent=2),
        timestamp=known_good.timestamp,
    )


def write_report(known_good: KnownGood, output_path: Path, token: Optional[str] = None) -> None:
    Path(output_path).write_text(generate_report(known_good, token), encoding="utf-8")


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("html_report", help="Generate an HTML status report from known_good.json")
    parser.add_argument(
        "--known_good",
        metavar="PATH",
        default=str(_find_repo_root()),
        help="Directory containing known_good.json (default: repo root)",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default="report.html",
        help="Output HTML file path (default: report.html)",
    )
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    known_good_path = Path(args.known_good) / "known_good.json"
    try:
        known_good = load_known_good(known_good_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    token = os.environ.get("GITHUB_TOKEN")
    output = _resolve_path_from_bazel(Path(args.output))
    write_report(known_good, output, token=token)
    if token:
        print(f"Report written to {output} (current hashes fetched from GitHub)")
    else:
        print(f"Report written to {output} (set GITHUB_TOKEN to embed current hashes)")
    return 0
