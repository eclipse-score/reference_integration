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
"""Resolved dependency versions from the reference_integration root.

Provides :class:`ResolvedDependencies`, which holds the resolved version/commit per
dependency (sourced from ref_int's root — either ``known_good.json`` for local runs,
or the Stage-1 ``stage1-resolved-deps`` artifact for CI runs), and exposes an interface
to **scan** an individual module's ``MODULE.bazel`` and **overwrite** the declared
dependency versions to match the resolved set by appending the matching
``git_override`` / ``single_version_override`` directives.

The injection operates on the CI checkout of the module — it is never committed back
to the module's released sources.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

_HERE = Path(__file__).resolve().parent

from known_good.models.known_good import load_known_good
from known_good.models.module import Module
from known_good.update_module_from_known_good import generate_override_directive

# Marker delimiting the block we append, so injection is idempotent / detectable.
INJECTION_BEGIN = "# --- BEGIN ref_int resolved-deps injection ---"
INJECTION_END = "# --- END ref_int resolved-deps injection ---"

# The single file that carries the resolved set from Stage 1 (resolve) to Stage 2
# (per-module validation). It is the only handoff needed: first-party commits +
# third-party resolved versions, merged. The lock travels alongside only as evidence.
MANIFEST_NAME = "resolved_versions.json"

# Built-in / non-registry modules that must not be given a single_version_override.
_SKIP_MODULES = {"bazel_tools"}

# Capture the module name from any ``bazel_dep(name = "...")`` call (name is the first arg).
_BAZEL_DEP_RE = re.compile(r'bazel_dep\(\s*name\s*=\s*"([^"]+)"')
# Parsers for reconstructing the resolved set from generated score_modules_*.MODULE.bazel.
_GIT_OVERRIDE_BLOCK_RE = re.compile(r"git_override\((?P<body>.*?)\)", re.S)
_SINGLE_VERSION_BLOCK_RE = re.compile(r"single_version_override\((?P<body>.*?)\)", re.S)
_FIELD_RE = lambda field: re.compile(rf'{field}\s*=\s*"([^"]+)"')  # noqa: E731


class ResolvedDependencies:
    """Resolved dependency versions from the reference_integration root.

    Holds a ``name -> Module`` map of the dependencies ref_int pins, and provides an
    interface to scan + overwrite a module's ``MODULE.bazel`` to those versions.
    """

    def __init__(self, resolved: Dict[str, Module]):
        self._resolved = resolved

    # -- construction: "resolved deps versions from ref_int root" --------------------

    @classmethod
    def from_known_good(cls, known_good_path: Path) -> "ResolvedDependencies":
        """Build from ``known_good.json`` (local / dev source of the resolved pins)."""
        kg = load_known_good(Path(known_good_path).resolve())
        resolved: Dict[str, Module] = {}
        for group in kg.modules.values():
            for module in group.values():
                resolved[module.name] = module
        return cls(resolved)

    @classmethod
    def from_resolved_artifact(cls, artifact_dir: Path) -> "ResolvedDependencies":
        """Build from the Stage-1 ``stage1-resolved-deps`` artifact.

        The handoff is the single ``resolved_versions.json`` manifest (see
        :meth:`from_mod_graph` / :meth:`to_file`). For backward compatibility, if the
        manifest is absent the older format is parsed: the generated
        ``score_modules_*.MODULE.bazel`` override files, gated on the presence of
        ``MODULE.bazel.lock`` as evidence of full resolution.
        """
        artifact_dir = Path(artifact_dir)

        manifest = artifact_dir / MANIFEST_NAME
        if manifest.is_file():
            return cls.from_file(manifest)

        # Legacy fallback: reconstruct from the generated override files.
        lock = artifact_dir / "MODULE.bazel.lock"
        if not lock.is_file():
            raise FileNotFoundError(
                f"Neither {MANIFEST_NAME} nor MODULE.bazel.lock found in resolved-deps artifact "
                f"{artifact_dir}; Stage 2 must consume the Stage-1 resolved dependency set."
            )

        module_files = sorted(artifact_dir.glob("score_modules_*.MODULE.bazel"))
        if not module_files:
            raise FileNotFoundError(f"No score_modules_*.MODULE.bazel files in resolved-deps artifact {artifact_dir}.")

        resolved: Dict[str, Module] = {}
        for mf in module_files:
            for module in cls._parse_override_file(mf.read_text()):
                resolved[module.name] = module
        return cls(resolved)

    @classmethod
    def from_mod_graph(cls, mod_graph_json: Path, override_files: List[Path]) -> "ResolvedDependencies":
        """Build the *complete* resolved set by merging two sources.

        * The override directives ref_int actually declares — parsed from its root
          ``MODULE.bazel`` and the ``bazel_common/*.MODULE.bazel`` files it ``include()``s.
          This carries every module ref_int pins by a non-registry source as its real
          directive: ``git_override(commit, remote)`` for ``score_*`` plus third-party like
          ``trlc`` / ``flatbuffers`` / ``rules_oci``, and ``single_version_override`` where
          ref_int pins a registry version. The graph cannot supply these — it reports
          overridden modules as version ``0.0.0``.
        * ``bazel mod graph --output=json`` — the post-MVS resolved version of every other
          (registry) module (protobuf, abseil, rules_rust, ...), emitted as
          ``single_version_override`` so each module under test is forced to the exact
          version ref_int resolved (MVS is graph-global, so a module's own subgraph could
          otherwise select a different version).

        ``archive_override`` / ``local_path_override`` targets (e.g. ``rules_boost``) cannot
        be represented and are logged as not carried.
        """
        resolved: Dict[str, Module] = {}
        unrepresentable: List[str] = []
        for f in override_files:
            # Drop comment-only lines first: hand-written MODULE.bazel files contain
            # commented-out overrides (e.g. "# git_override(... rules_rpm ...)") that must
            # not be captured. Inline trailing comments (after a value) are left intact.
            text = "\n".join(ln for ln in Path(f).read_text().splitlines() if not ln.lstrip().startswith("#"))
            for module in cls._parse_override_file(text):  # git_override + single_version_override
                resolved[module.name] = module
            for m in re.finditer(r'(archive_override|local_path_override)\(\s*module_name\s*=\s*"([^"]+)"', text):
                unrepresentable.append(f"{m.group(2)} ({m.group(1)})")

        graph = json.loads(Path(mod_graph_json).read_text())
        versions: Dict[str, str] = {}
        _collect_resolved_versions(graph, versions)
        skipped: List[str] = []
        for name, version in versions.items():
            if name in resolved or name in _SKIP_MODULES:
                continue  # already carried by an override directive, or non-overridable
            if not version or version == "0.0.0":
                # Non-registry version: ref_int pins it via an override we did not capture
                # (e.g. archive_override). single_version_override cannot reproduce it.
                skipped.append(name)
                continue
            resolved[name] = Module(name=name, hash="", repo="", version=version)

        if unrepresentable:
            logging.warning(
                "Overrides not carried into manifest (need manual handling): %s", ", ".join(unrepresentable)
            )
        if skipped:
            logging.warning(
                "Graph modules at version 0.0.0 with no carried override, skipped: %s", ", ".join(sorted(skipped))
            )
        return cls(resolved)

    def to_file(self, path: Path) -> None:
        """Serialize the resolved set to the JSON manifest (Stage 1 -> Stage 2 handoff).

        Only the fields needed to regenerate the override directive are stored
        (``version`` for single_version_override; ``repo`` + ``hash`` for git_override).
        Metadata is intentionally omitted — the manifest carries dependency pins, not the
        module-under-test's test configuration (that comes from known_good.json).
        """
        modules = {}
        for name in sorted(self._resolved):
            m = self._resolved[name]
            entry: Dict[str, object] = {"version": m.version} if m.version else {"repo": m.repo, "hash": m.hash}
            if m.bazel_patches:
                entry["bazel_patches"] = m.bazel_patches
            modules[name] = entry
        Path(path).write_text(json.dumps({"modules": modules}, indent=2) + "\n")

    @classmethod
    def from_file(cls, path: Path) -> "ResolvedDependencies":
        """Load a resolved set previously written by :meth:`to_file`."""
        data = json.loads(Path(path).read_text())
        resolved = {name: Module.from_dict(name, md) for name, md in data.get("modules", {}).items()}
        return cls(resolved)

    @staticmethod
    def _parse_override_file(text: str) -> List[Module]:
        """Reconstruct Module objects from generated git/single_version override blocks."""
        modules: List[Module] = []

        for match in _GIT_OVERRIDE_BLOCK_RE.finditer(text):
            body = match.group("body")
            name = _field(body, "module_name")
            commit = _field(body, "commit")
            remote = _field(body, "remote")
            if name and commit and remote:
                modules.append(Module(name=name, hash=commit, repo=remote))

        for match in _SINGLE_VERSION_BLOCK_RE.finditer(text):
            body = match.group("body")
            name = _field(body, "module_name")
            version = _field(body, "version")
            if name and version:
                modules.append(Module(name=name, hash="", repo="", version=version))

        return modules

    # -- interface: scan + overwrite a module's MODULE.bazel -------------------------

    @property
    def names(self) -> set[str]:
        return set(self._resolved)

    def get(self, name: str) -> Optional[Module]:
        return self._resolved.get(name)

    def scan(self, module_bazel: Path) -> List[str]:
        """Return the names of dependencies a module declares via ``bazel_dep``."""
        text = Path(module_bazel).read_text()
        # Ignore anything inside a previous injection block so re-scans are stable.
        text = self._strip_injection(text)
        return _BAZEL_DEP_RE.findall(text)

    def overwrite(self, module_bazel: Path, *, module_under_test: Optional[str] = None, write: bool = True) -> str:
        """Overwrite a module's declared dependency versions with the resolved set.

        Appends a ``git_override`` / ``single_version_override`` directive for every
        dependency the module declares that we have a resolved version for, so the
        module (and all its transitive deps) build against ref_int's resolved versions.

        * Skips the module under test itself (the root is never overridden).
        * Skips dependencies that already carry an override in the file.
        * Re-running is idempotent: a prior injection block is replaced.
        """
        module_bazel = Path(module_bazel)
        original = self._strip_injection(module_bazel.read_text())

        declared = set(_BAZEL_DEP_RE.findall(original))

        from dataclasses import replace as _replace

        directives: List[str] = []
        # Inject overrides only for deps the module actually declares (intersected with the
        # resolved set). Bazel fails with "root module specifies overrides on nonexistent
        # module(s)" if an override targets a module that is not in this module's dependency
        # graph, so the full resolved set cannot be injected wholesale — a declared bazel_dep
        # is by definition in the graph, which makes its override safe.
        # ref_int always decides the version — any existing module-level override is replaced.
        for name in sorted(declared):
            if name == module_under_test:
                continue  # the module under test is the root; never override it
            module = self._resolved.get(name)
            if module is None:
                continue  # dep ref_int does not pin; resolves normally
            # Strip bazel_patches: they reference //patches/... labels in ref_int's
            # workspace which do not exist inside another module's checkout.
            module = _replace(module, bazel_patches=None)
            directive = generate_override_directive(module)
            if directive is None:
                continue
            directives.append(directive)

        if not directives:
            patched = original
        else:
            body = "\n".join(directives)
            patched = f"{original.rstrip()}\n\n{INJECTION_BEGIN}\n{body}\n{INJECTION_END}\n"

        if write:
            module_bazel.write_text(patched)
        return patched

    @staticmethod
    def _strip_injection(text: str) -> str:
        """Remove a previously appended injection block, if present."""
        pattern = re.compile(
            re.escape(INJECTION_BEGIN) + r".*?" + re.escape(INJECTION_END) + r"\n?",
            re.S,
        )
        return pattern.sub("", text).rstrip() + "\n" if pattern.search(text) else text


def _field(body: str, field: str) -> str:
    match = _FIELD_RE(field).search(body)
    return match.group(1) if match else ""


def _collect_resolved_versions(node: dict, acc: Dict[str, str]) -> None:
    """Walk a ``bazel mod graph --output=json`` tree, recording name -> resolved version.

    Each node carries the post-MVS ``name`` and ``version``; a module can appear many
    times in the graph but always at the single resolved version, so deduping by name is
    safe. The ``<root>`` node has an empty version and is skipped implicitly.
    """
    for dep in node.get("dependencies", []):
        name, version = dep.get("name"), dep.get("version")
        if name and version:
            acc[name] = version
        _collect_resolved_versions(dep, acc)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve (Stage 1) or inject (Stage 2) ref_int's resolved dependency set (DR-008 Option 4)."
    )
    parser.add_argument(
        "module_bazel",
        type=Path,
        nargs="?",
        default=None,
        help="Inject mode: path to the module's MODULE.bazel to overwrite. Omit when using --export.",
    )
    parser.add_argument(
        "--known-good-path",
        type=Path,
        default=_HERE.parents[1] / "known_good.json",
        help="Resolved set source: known_good.json (default; first-party commit pins).",
    )
    parser.add_argument(
        "--resolved-deps",
        type=Path,
        default=None,
        help="Inject mode: Stage-1 stage1-resolved-deps artifact dir (overrides --known-good-path).",
    )
    parser.add_argument(
        "--mod-graph",
        type=Path,
        default=None,
        help="Export mode: 'bazel mod graph --output=json' output, merged with known_good.json.",
    )
    parser.add_argument(
        "--export",
        type=Path,
        default=None,
        help=f"Export mode: write the merged resolved set to this {MANIFEST_NAME} manifest and exit.",
    )
    parser.add_argument(
        "--module-under-test",
        default=None,
        help="Name of the module under test (never overridden as it is the root).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print patched content instead of writing.")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    # Export mode (Stage 1): build the manifest by merging the override directives ref_int
    # declares (root MODULE.bazel + bazel_common/*.MODULE.bazel) with the resolved registry
    # versions from 'bazel mod graph'.
    if args.export is not None:
        if args.mod_graph is None:
            raise SystemExit("--export requires --mod-graph (output of 'bazel mod graph --output=json')")
        repo_root = _HERE.parents[1]
        override_files = [repo_root / "MODULE.bazel", *sorted((repo_root / "bazel_common").glob("*.MODULE.bazel"))]
        override_files = [f for f in override_files if f.is_file()]
        resolved = ResolvedDependencies.from_mod_graph(args.mod_graph, override_files)
        Path(args.export).parent.mkdir(parents=True, exist_ok=True)
        resolved.to_file(args.export)
        print(f"Wrote resolved dependency manifest ({len(resolved.names)} modules) to {args.export}")
        return

    # Inject mode (Stage 2): overwrite a module's MODULE.bazel with the resolved set.
    if args.module_bazel is None:
        raise SystemExit("module_bazel is required unless --export is given")

    if args.resolved_deps:
        resolved = ResolvedDependencies.from_resolved_artifact(args.resolved_deps)
    else:
        resolved = ResolvedDependencies.from_known_good(args.known_good_path)

    patched = resolved.overwrite(
        args.module_bazel,
        module_under_test=args.module_under_test,
        write=not args.dry_run,
    )
    if args.dry_run:
        print(patched)
    else:
        print(f"Injected resolved-deps overrides into {args.module_bazel}")


if __name__ == "__main__":
    main()
