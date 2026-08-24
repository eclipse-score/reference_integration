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
"""Emit the modules of a known_good.json group as a JSON array.

Builds the Stage-2 module matrix in test_and_docs.yml so it is always sourced from
known_good.json and never hardcoded. Each entry is
  {"name": <bazel module name>, "repo": <git url>, "slug": <owner/name>,
   "commit": <hash>, "branch": <branch>}
where "slug" is what actions/checkout expects as `repository:`, derived from the git URL because
the repo name often differs from the bazel module name (score_lifecycle_health ->
eclipse-score/lifecycle).

Usage:
  python scripts/known_good/list_modules.py --group target_sw
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def repo_slug(repo_url: str) -> str:
    """Derive the 'owner/name' slug actions/checkout expects from a git URL."""
    match = re.search(r"[:/]([^/:]+/[^/:]+?)(?:\.git)?/?$", repo_url or "")
    return match.group(1) if match else ""


_HERE = Path(__file__).resolve().parent
try:
    from known_good.models.known_good import load_known_good
except ImportError:
    if str(_HERE) not in sys.path:
        sys.path.insert(0, str(_HERE))
    from models.known_good import load_known_good  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="List known_good.json modules of a group as JSON (for CI matrices).")
    parser.add_argument(
        "--known-good-path",
        type=Path,
        default=_HERE.parents[1] / "known_good.json",
        help="Path to known_good.json (default: repo-root known_good.json).",
    )
    parser.add_argument("--group", default="target_sw", help="Module group to list (default: target_sw).")
    args = parser.parse_args()

    kg = load_known_good(args.known_good_path.resolve())
    if args.group not in kg.modules:
        raise SystemExit(f"Group '{args.group}' not found in {args.known_good_path}. Groups: {sorted(kg.modules)}")

    modules = [kg.modules[args.group][name] for name in sorted(kg.modules[args.group])]

    print(
        json.dumps(
            [
                {
                    "name": m.name,
                    "repo": m.repo,
                    "slug": repo_slug(m.repo),
                    "commit": m.hash,
                    "branch": m.branch,
                }
                for m in modules
            ]
        )
    )


if __name__ == "__main__":
    main()
