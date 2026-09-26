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
"""Verify that a module disabled in known_good.json is really out of the build.

Setting ``"enabled": false`` removes a module's ``bazel_dep`` and ``git_override`` from
the generated Bazel fragments. That is *not* the same as removing it from the build:
if any other module declares its own ``bazel_dep`` on it, Bazel keeps it in the graph
and silently resolves it from the registry instead - at a released version rather than
the commit known_good.json used to pin. The result builds, and looks fine, against code
nobody chose.

This check makes that impossible. It asks Bazel for the resolved module graph and fails
if a disabled module is still in it, naming the modules that pull it back in.

It is free in the normal case: with nothing disabled it exits before ever invoking
Bazel.

Usage:
    python3 scripts/known_good/check_disabled_modules.py
    python3 scripts/known_good/check_disabled_modules.py --mod-graph graph.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# Importable both as a package module and runnable as a plain script from the repo
# root, which is how CI invokes it. Same fallback as update_module_from_known_good.py.
try:
    from known_good.models.known_good import load_known_good
except ImportError:
    _HERE = str(Path(__file__).resolve().parent)
    if _HERE not in sys.path:
        sys.path.insert(0, _HERE)
    from models.known_good import load_known_good  # noqa: E402


def module_name_of(key: str) -> str:
    """'score_logging@_' and 'score_logging@0.2.4' both name score_logging."""
    return key.split("@", 1)[0]


def collect_edges(root: dict[str, Any]) -> tuple[set[str], dict[str, set[str]]]:
    """Walk the 'bazel mod graph --output=json' tree.

    Returns every module name in the graph, plus a reverse index mapping a module to
    the modules that declare a dependency on it.

    Bazel prints a node's children only the first time it appears, so the reverse index
    is a lower bound - enough to name culprits, not to prove there are no others.
    """
    present: set[str] = set()
    consumers: dict[str, set[str]] = {}
    seen_keys: set[str] = set()

    def walk(node: dict[str, Any]) -> None:
        key = node.get("key", "")
        if key in seen_keys:
            return
        seen_keys.add(key)
        name = module_name_of(key)
        if not node.get("root"):
            present.add(name)
        for dep in node.get("dependencies", []) or []:
            dep_name = module_name_of(dep.get("key", ""))
            consumers.setdefault(dep_name, set()).add("<root>" if node.get("root") else name)
            walk(dep)

    walk(root)
    return present, consumers


def run_mod_graph(workspace: Path, bazel: str) -> dict[str, Any]:
    try:
        result = subprocess.run(
            [bazel, "mod", "graph", "--output=json"],
            cwd=workspace,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        raise SystemExit(
            f"ERROR: '{bazel}' not found. Pass --bazel, or --mod-graph with a precomputed\n"
            "'bazel mod graph --output=json' file."
        ) from None

    if result.returncode != 0:
        tail = "\n".join(result.stderr.strip().splitlines()[-15:])
        raise SystemExit(f"ERROR: 'bazel mod graph' failed (exit {result.returncode}):\n{tail}")

    return json.loads(result.stdout)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--known", default="known_good.json", help="Path to known_good.json")
    parser.add_argument("--bazel", default="bazel", help="Bazel binary to invoke (default: bazel)")
    parser.add_argument(
        "--mod-graph",
        type=Path,
        help=(
            "Use a precomputed 'bazel mod graph --output=json' file instead of invoking Bazel. "
            "It must come from an already-regenerated workspace, otherwise it still contains "
            "the entries the disabled module was supposed to lose."
        ),
    )
    args = parser.parse_args(argv)

    known_path = Path(args.known).resolve()
    if not known_path.is_file():
        raise SystemExit(f"ERROR: known_good.json not found at {known_path}")

    try:
        known_good = load_known_good(known_path)
    except ValueError as e:
        raise SystemExit(f"ERROR: {e}") from None

    disabled = known_good.disabled_modules

    if not disabled:
        print("No modules are disabled in known_good.json - nothing to check.")
        return 0

    print("Disabled modules to verify:")
    for name, module in sorted(disabled.items()):
        print(f"  - {name}: {module.disabled_reason}")

    if args.mod_graph:
        graph = json.loads(args.mod_graph.read_text(encoding="utf-8"))
    else:
        print("\nResolving the module graph ('bazel mod graph')...")
        graph = run_mod_graph(known_path.parent, args.bazel)

    present, consumers = collect_edges(graph)
    still_present = sorted(set(disabled) & present)

    if not still_present:
        print(f"\nOK: none of the {len(disabled)} disabled module(s) appear in the resolved module graph.")
        return 0

    # A disabled module the ROOT still depends on means the generated Bazel fragments are
    # stale, not that another module pulls it in. Saying so avoids sending the reader off
    # to hunt for a dependency that is not there.
    stale = [name for name in still_present if "<root>" in consumers.get(name, set())]
    if stale:
        print(
            "\nERROR: the generated Bazel fragments still declare disabled modules: "
            + ", ".join(stale)
            + "\nRun 'python3 scripts/known_good/update_module_from_known_good.py' and retry.",
            file=sys.stderr,
        )
        return 1

    print("\nERROR: disabled modules are still part of the resolved module graph.", file=sys.stderr)
    print(
        "Removing a module from known_good.json only drops this repository's bazel_dep and\n"
        "git_override. Another module still requires it, so Bazel resolves it from the\n"
        "registry instead - at a released version, not the commit that was pinned here.\n",
        file=sys.stderr,
    )
    for name in still_present:
        pullers = sorted(consumers.get(name, set()))
        print(f"  {name} is required by: {', '.join(pullers) or '(unknown)'}", file=sys.stderr)
    print(
        "\nEither re-enable these modules, or disable the modules that depend on them too.\n"
        "Run 'bazel mod explain <module>' to see the full path.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
