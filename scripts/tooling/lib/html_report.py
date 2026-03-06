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
"""HTML report generator for known_good.json status."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .github import fetch_compare
from .known_good import KnownGood

_LOG = logging.getLogger(__name__)


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


def _enrich_with_compare_data(
    entries: list[dict[str, Any]],
    token: str,
) -> None:
    """Fetch compare data for each GitHub module and store it in the entry."""
    for entry in entries:
        if not entry.get("owner_repo") or not entry.get("hash") or entry.get("version"):
            continue
        result = fetch_compare(entry["owner_repo"], entry["hash"], entry["branch"], token)
        if result:
            entry["current_hash"] = result.head_sha
            entry["behind_by"] = result.ahead_by
            entry["compare_status"] = result.status
        else:
            _LOG.warning(
                "Could not fetch compare data for %s@%s", entry["owner_repo"], entry["branch"]
            )


def generate_report(
    known_good: KnownGood,
    template_dir: Path,
    token: Optional[str] = None,
) -> str:
    """Return a self-contained HTML report string for *known_good*.

    Args:
        known_good: Parsed known_good.json data.
        template_dir: Directory containing ``report_template.html``.
        token: Optional GitHub PAT / ``GITHUB_TOKEN``.  When provided the
               compare API is called at generation time, embedding exact
               commit-behind counts and current HEAD hashes so the viewer
               needs no PAT.
    """
    entries = _collect_entries(known_good)
    if token:
        _enrich_with_compare_data(entries, token)
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html"]),
    )
    tmpl = env.get_template("report_template.html")
    return tmpl.render(
        modules_json=json.dumps(entries, indent=2),
        timestamp=known_good.timestamp,
    )


def write_report(
    known_good: KnownGood,
    output_path: Path,
    template_dir: Path,
    token: Optional[str] = None,
) -> None:
    """Write the HTML report to *output_path*."""
    Path(output_path).write_text(generate_report(known_good, template_dir, token), encoding="utf-8")
