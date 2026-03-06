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
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .known_good import KnownGood

_TEMPLATE_DIR = Path(__file__).parent / "assets"
_ENV = Environment(
    loader=FileSystemLoader(_TEMPLATE_DIR),
    autoescape=select_autoescape(["html"]),
)


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
                }
            )
    return entries


def generate_report(known_good: KnownGood) -> str:
    """Return a self-contained HTML report string for *known_good*.

    The page embeds module data as JSON and uses client-side JavaScript to
    query the GitHub compare API, showing how many commits behind each module
    is relative to its target branch HEAD.  A GitHub personal access token
    (PAT) must be supplied via the token input in the header.  Without a token
    the grid is still rendered but each card shows an "unavailable / requires
    PAT" badge instead of live status.
    """
    entries = _collect_entries(known_good)
    tmpl = _ENV.get_template("report_template.html")
    return tmpl.render(
        modules_json=json.dumps(entries, indent=2),
        timestamp=known_good.timestamp,
    )


def write_report(
    known_good: KnownGood,
    output_path: Path,
) -> None:
    """Write the HTML report to *output_path*."""
    Path(output_path).write_text(generate_report(known_good), encoding="utf-8")
