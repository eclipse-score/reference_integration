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
"""Check that a Stage-2 module really resolved to ref_int's dependency versions.

Compares the module's own post-MVS graph (``bazel mod graph --output=json``, run in the module
checkout after injection) against ref_int's ``resolved_versions.json``, turning DR-008's
"validated against the versions reference_integration resolved" into a check rather than an
assumption.

Not ``MODULE.bazel.lock``: its ``registryFileHashes`` lists every registry file Bazel consulted,
including versions it rejected, so presence there does not show what was selected. Modules pinned
by ``git_override`` carry a commit rather than a version and are counted separately as
unverifiable-by-version rather than as agreeing.

Usage:
  python3 scripts/known_good/verify_stage2_resolution.py \\
      --mod-graph _module_graph.json \\
      --resolved _resolved_deps/resolved_versions.json \\
      --module score_logging
"""

import argparse
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
try:
    from known_good.resolved_dependencies import _collect_resolved_versions, injected_override_names
except ImportError:
    if str(_HERE) not in sys.path:
        sys.path.insert(0, str(_HERE))
    from resolved_dependencies import _collect_resolved_versions, injected_override_names  # noqa: E402


def module_graph_versions(graph_path: Path) -> dict[str, str]:
    """Return {module_name: resolved_version} from a ``bazel mod graph --output=json`` dump."""
    acc: dict[str, str] = {}
    _collect_resolved_versions(json.loads(graph_path.read_text(encoding="utf-8")), acc)
    return acc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mod-graph", type=Path, required=True, help="bazel mod graph --output=json from the module")
    parser.add_argument("--resolved", type=Path, required=True, help="Stage-1 resolved_versions.json")
    parser.add_argument("--module", default="", help="Module under test (never overridden, so excluded)")
    parser.add_argument(
        "--module-bazel",
        type=Path,
        help="The module's MODULE.bazel, read AFTER injection. Splits mismatches by whether ref_int "
        "actually injected an override for the module: a mismatch there is an injection failure and "
        "fails the check, whereas one outside the injection block resolved on its own and only warns.",
    )
    args = parser.parse_args()

    # Every module ref_int injected an override for — its declared deps *and* its transitive
    # closure, since overwrite() emits a bazel_dep stub alongside the override for the latter.
    # A mismatch on any of them is ref_int's bug; anything else fell through to the module's
    # own MVS (a dev_dependency, or a dep ref_int pins with an unrepresentable override).
    injected: set[str] = set()
    if args.module_bazel and args.module_bazel.is_file():
        injected = injected_override_names(args.module_bazel.read_text(encoding="utf-8"))

    for path in (args.mod_graph, args.resolved):
        if not path.is_file():
            print(f"::error::verify_stage2_resolution: missing {path}")
            return 1

    actual = module_graph_versions(args.mod_graph)
    resolved = json.loads(args.resolved.read_text(encoding="utf-8"))
    resolved = resolved.get("modules", resolved)

    injected_mismatches: list[str] = []
    transitive_mismatches: list[str] = []
    absent: list[str] = []
    agreed = 0
    by_commit = 0

    for name, entry in sorted(resolved.items()):
        if name == args.module:
            continue
        want = entry.get("version")
        if want is None:
            by_commit += 1  # git_override'd: pinned by commit, not comparable by version
            continue
        if name not in actual:
            absent.append(name)  # not in this module's graph — unpinned transitively
            continue
        if actual[name] == want:
            agreed += 1
            continue
        detail = f"{name}: ref_int resolved {want}, module built {actual[name]}"
        (injected_mismatches if name in injected else transitive_mismatches).append(detail)

    print(
        f"verify_stage2_resolution: {agreed} agree, "
        f"{len(injected_mismatches)} MISMATCHED despite injection, "
        f"{len(transitive_mismatches)} mismatched transitively, "
        f"{len(absent)} not in module graph, {by_commit} pinned by commit"
    )

    # ref_int injected an override and the module still built something else — our bug.
    for line in injected_mismatches:
        print(f"::error::verify_stage2_resolution — override did not take effect: {line}")

    # Outside the injection block: ref_int never pinned it, so the module resolved it itself.
    # Expected for the module's dev_dependency deps (active only when it is the Bazel root, so
    # absent from ref_int's Stage 1 graph) and for deps ref_int pins with an override that
    # cannot be reproduced (archive_override / local_path_override) — warn, do not block.
    for line in transitive_mismatches:
        print(f"::warning::verify_stage2_resolution — not pinned by ref_int: {line}")

    if absent:
        print(f"::warning::verify_stage2_resolution: {len(absent)} resolved modules absent from the module's graph")

    # Only an override that failed to take effect fails the check; anything ref_int never pinned
    # warns above.
    return 1 if injected_mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
