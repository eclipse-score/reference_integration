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
"""Offline guard: ref_int must name one build setting by exactly one label.

ref_int sets the same build settings from three places (root ``.bazelrc``,
``ci/stage2/module.bazelrc``, ``metadata.extra_test_config``). When a setting relocates
upstream, a stale label fails at *option loading* — before any layered config can override
it — surfacing as an unrelated-looking Stage-2 failure.

Rule: within one repo, a setting's basename must resolve to a single package path. Two repos
may own a same-named setting (both score_baselibs and score_logging define
``KRemote_Logging``), so the repo is part of the key.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

REF_INT_ROOT = Path(__file__).resolve().parent.parent.parent

# Only sources ref_int owns; a module's own .bazelrc is fixed by a patch instead.
RC_FILES = (Path(".bazelrc"), Path("ci/stage2/module.bazelrc"))
# ref_int's dedicated per-module Stage-2 rc files. Globbed so a new one is covered automatically.
RC_GLOBS = (("ci/stage2", "*.bazelrc"),)
KNOWN_GOOD = Path("known_good.json")

# ``--@repo//pkg/path:setting=value`` or the repo-relative ``--//pkg:setting=value``.
_SETTING_RE = re.compile(r"--(?P<label>(?:@[A-Za-z0-9_.-]+)?//[A-Za-z0-9_/.+-]*:[A-Za-z0-9_.+-]+)=")


@dataclass(frozen=True)
class Occurrence:
    label: str
    source: str


def _scan_line(line: str, source: str, out: list[Occurrence]) -> None:
    if line.lstrip().startswith("#"):
        return
    for match in _SETTING_RE.finditer(line):
        out.append(Occurrence(label=match.group("label"), source=source))


def collect_occurrences(root: Path = REF_INT_ROOT) -> list[Occurrence]:
    """Gather every build-setting label ref_int sets, tagged with where it was found."""
    found: list[Occurrence] = []

    globbed = sorted(rc.relative_to(root) for directory, pattern in RC_GLOBS for rc in (root / directory).glob(pattern))
    for rc in list(RC_FILES) + [rc for rc in globbed if rc not in RC_FILES]:
        path = root / rc
        if not path.is_file():
            continue
        for number, line in enumerate(path.read_text().splitlines(), start=1):
            _scan_line(line, f"{rc}:{number}", found)

    known_good = root / KNOWN_GOOD
    if known_good.is_file():
        data = json.loads(known_good.read_text())
        for group, modules in (data.get("modules") or {}).items():
            for name, module in (modules or {}).items():
                metadata = module.get("metadata") or {}
                for setting in metadata.get("extra_test_config") or []:
                    source = f"{KNOWN_GOOD}: {group}/{name} extra_test_config"
                    _scan_line(f"--{setting}=", source, found)

    return found


def find_conflicts(occurrences: list[Occurrence]) -> dict[tuple[str, str], dict[str, list[str]]]:
    """Group by (repo, setting basename); return only keys carrying more than one label.

    Result maps ``(repo, basename)`` to ``{label: [sources...]}``.
    """
    grouped: dict[tuple[str, str], dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for occurrence in occurrences:
        repo, _, path = occurrence.label.partition("//")
        basename = path.rsplit(":", 1)[1]
        grouped[(repo or "//", basename)][occurrence.label].append(occurrence.source)
    return {key: dict(labels) for key, labels in grouped.items() if len(labels) > 1}


def format_conflicts(conflicts: dict[tuple[str, str], dict[str, list[str]]]) -> str:
    lines: list[str] = []
    for (repo, basename), labels in sorted(conflicts.items()):
        lines.append(f"{repo} defines setting '{basename}' at {len(labels)} different paths:")
        for label, sources in sorted(labels.items()):
            lines.append(f"  {label}")
            for source in sources:
                lines.append(f"      {source}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REF_INT_ROOT, help="ref_int workspace root to scan")
    args = parser.parse_args(argv)

    conflicts = find_conflicts(collect_occurrences(args.root.resolve()))
    if conflicts:
        print("Inconsistent build-setting labels in ref_int's own configuration:\n", file=sys.stderr)
        print(format_conflicts(conflicts), file=sys.stderr)
        print(
            "\nA stale label fails at option loading, before any layered config can override it. "
            "Point every occurrence at the setting's current package.",
            file=sys.stderr,
        )
        return 1

    print("Build-setting labels are consistent across .bazelrc, ci/stage2/module.bazelrc and known_good.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
