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
import os
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def repo_root() -> Path:
    """ref_int's workspace root.

    Prefers the environment Bazel sets for ``bazel run`` targets so paths passed on the
    command line resolve against the user's workspace rather than the runfiles tree (and
    so ``graph.json`` need not be declared in ``data = [...]``). Falls back to walking up
    from this file for direct ``python3 scripts/...`` invocations.
    """
    for var in ("BUILD_WORKSPACE_DIRECTORY", "BUILD_WORKING_DIRECTORY"):
        value = os.environ.get(var)
        if value:
            return Path(value)
    return _HERE.parents[1]


def workspace_path(path: Path) -> Path:
    """Anchor a relative command-line path at :func:`repo_root`.

    ``bazel run`` executes the binary with the runfiles tree as its working directory, so a
    relative path would be read from — or, worse, written into — runfiles instead of the
    user's workspace. Absolute paths are taken as given.
    """
    return path if path.is_absolute() else repo_root() / path


try:
    from known_good.models.known_good import load_known_good
    from known_good.models.module import Module
    from known_good.module_patches import patch_relpath
except ImportError:
    if str(_HERE) not in sys.path:
        sys.path.insert(0, str(_HERE))
    from models.known_good import load_known_good  # noqa: E402
    from models.module import Module  # noqa: E402
    from module_patches import patch_relpath  # noqa: E402

# Marker delimiting the block we append, so injection is idempotent / detectable.
INJECTION_BEGIN = "# --- BEGIN ref_int resolved-deps injection ---"
INJECTION_END = "# --- END ref_int resolved-deps injection ---"


def generate_override_directive(module: Module, repo_commit_dict: dict[str, str] | None = None) -> str | None:
    """Return the override directive (single_version_override / git_override) for a module.

    Returns just the override call without a preceding ``bazel_dep(...)`` line, since
    :meth:`ResolvedDependencies.overwrite` injects into a module's own MODULE.bazel where the
    ``bazel_dep`` is already declared, and adds one itself only for a closure member that is not.

    Returns ``None`` when the module has neither a usable version nor a valid repo+commit.

    ``repo_commit_dict`` lets a caller pin a specific repo to a different commit than
    known_good.json records, backing update_module_from_known_good.py's --repo-override.
    """
    repo_commit_dict = repo_commit_dict or {}
    commit = repo_commit_dict.get(module.repo, module.hash)

    patches_lines = ""
    if module.bazel_patches:
        patches_lines = "    patches = [\n"
        for patch in module.bazel_patches:
            patches_lines += f'        "{patch}",\n'
        patches_lines += "    ],\n"
    patch_strip_line = "    patch_strip = 1,\n" if patches_lines else ""

    if module.version:
        return (
            "single_version_override(\n"
            f'    module_name = "{module.name}",\n'
            f"{patch_strip_line}"
            f"{patches_lines}"
            f'    version = "{module.version}",\n'
            ")\n"
        )

    if not module.repo or not commit:
        logging.warning(
            "Skipping module %s with missing repo or commit: repo=%s, commit=%s",
            module.name,
            module.repo,
            commit,
        )
        return None

    if not re.match(r"^[a-fA-F0-9]{7,40}$", commit):
        logging.warning("Skipping module %s with invalid commit hash: %s", module.name, commit)
        return None

    return (
        "git_override(\n"
        f'    module_name = "{module.name}",\n'
        f'    commit = "{commit}",\n'
        f"{patch_strip_line}"
        f"{patches_lines}"
        f'    remote = "{module.repo}",\n'
        ")\n"
    )


# The file Stage 1 stores alongside the manifest so Stage 2 can determine, for a given
# module, which *transitive* dependencies need an override (see DependencyGraph).
GRAPH_NAME = "graph.json"

# The patch files themselves, beside the manifest: Stage 2 can name a dependency's patches
# from the manifest alone, but not apply them.
PATCHES_DIRNAME = "patches"

# overwrite() re-hosts them here inside the checkout; ref_int's own //patches/... labels do
# not resolve in another module's root.
INJECTED_PATCHES_PKG = "ref_int_patches"


class DependencyGraph:
    """The ``bazel mod graph --output=json`` tree, queryable per module.

    :meth:`closure` returns a module's full transitive set, which is what
    :meth:`ResolvedDependencies.overwrite` pins. For ``score_communication`` that is 149 modules
    against 32 declared -- it never declares ``flatbuffers``, which arrives via ``score_baselibs``.

    The graph is *not* a plain tree. A module that appears more than once is emitted once
    with its ``dependencies`` and thereafter as an ``unexpanded`` stub carrying no
    children (864 of ref_int's 1022 nodes). Walking the subtree naively would therefore miss
    most of the closure, so nodes are indexed by name on load and unexpanded references are
    resolved through that index.
    """

    def __init__(self, root: dict):
        self._index: dict[str, dict] = {}
        self._build_index(root)

    def _build_index(self, node: dict, seen: set[int] | None = None) -> None:
        seen = set() if seen is None else seen
        if id(node) in seen:
            return
        seen.add(id(node))
        name = node.get("name")
        # Only expanded nodes carry children; the first occurrence is the authoritative one.
        if name and not node.get("unexpanded") and "dependencies" in node:
            self._index.setdefault(name, node)
        for dep in node.get("dependencies") or []:
            self._build_index(dep, seen)

    @classmethod
    def from_file(cls, path: Path) -> DependencyGraph:
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(
                f"Dependency graph {path} not found. Stage 1 must produce it with "
                f"'bazel mod graph --output=json' and store it as {GRAPH_NAME} in the "
                f"stage1-resolved-deps artifact."
            )
        return cls(json.loads(path.read_text()))

    @property
    def names(self) -> set[str]:
        return set(self._index)

    def closure(self, module_name: str) -> set[str]:
        """Every module reachable from ``module_name``, excluding itself.

        ``unexpanded`` stubs are resolved via the name index; ``visited`` terminates the walk,
        since the graph is a DAG with diamonds. Correct only for a graph produced without
        ``--depth`` -- both callers omit it, so every edge is a ``dependencies`` entry.
        """
        visited: set[str] = set()
        stack = [module_name]
        while stack:
            node = self._index.get(stack.pop())
            if node is None:
                continue  # unexpanded-only or absent: nothing further to walk
            for dep in node.get("dependencies") or []:
                name = dep.get("name")
                if name and name not in visited:
                    visited.add(name)
                    stack.append(name)
        visited.discard(module_name)
        return visited


# The single file that carries the resolved set from Stage 1 (resolve) to Stage 2
# (per-module validation). It is the only handoff needed: first-party commits +
# third-party resolved versions, merged. The lock travels alongside only as evidence.
MANIFEST_NAME = "resolved_versions.json"

# Sidecar beside the manifest: what a human needs to judge the pins, kept out of the manifest so
# that stays a lean Stage-2 input.
REPORT_NAME = "resolved_pins_report.json"

# Stated in the report so a reader does not have to infer why the export is this broad.
POLICY = "ref_int's pins are authoritative and are forced onto every module under test."

# Built-in / non-registry modules that must not be given a single_version_override.
_SKIP_MODULES = {"bazel_tools"}

# The whole ``bazel_dep(...)`` argument list. ``[^)]*`` is sufficient: bazel_dep takes only
# scalar keyword arguments, never a nested call.
_BAZEL_DEP_CALL_RE = re.compile(r"bazel_dep\((?P<body>[^)]*)\)", re.S)
# The two override kinds ref_int declares, each mapping onto a single Module.
# multiple_version_override is unsupported: ref_int declares none. archive_override /
# local_path_override cannot be reproduced at all and are reported instead.
_GIT_OVERRIDE_BLOCK_RE = re.compile(r"git_override\((?P<body>.*?)\)", re.S)
_SINGLE_VERSION_BLOCK_RE = re.compile(r"single_version_override\((?P<body>.*?)\)", re.S)
_FIELD_RE = lambda field: re.compile(rf'{field}\s*=\s*"([^"]+)"')  # noqa: E731
# ``patches = [...]``, whose entries are the only list-valued field the manifest carries.
_PATCHES_FIELD_RE = re.compile(r"patches\s*=\s*\[(?P<items>[^\]]*)\]", re.S)
_QUOTED_RE = re.compile(r'"([^"]+)"')

# Every override directive Bazel accepts from a root module.
_OVERRIDE_KINDS = (
    "git_override",
    "single_version_override",
    "archive_override",
    "local_path_override",
    "multiple_version_override",
)
# Any override block. ``[^)]*`` suffices: override arguments are scalars and lists, never a call.
_ANY_OVERRIDE_BLOCK_RE = re.compile(r"(?P<kind>" + "|".join(_OVERRIDE_KINDS) + r")\((?P<body>[^)]*)\)", re.S)

_UNCARRIED_CONSEQUENCE = "ref_int imposes nothing for this module; each module under test resolves its own version"

# Fetched outside bzlmod, so MVS never sees them and no override reaches them.
_NON_BZLMOD_FETCH_RULES = (
    "http_archive",
    "http_file",
    "git_repository",
    "new_git_repository",
    "local_repository",
)
_NON_BZLMOD_FETCH_RE = re.compile(r"^\s*(?:\w+\s*=\s*)?(?P<rule>" + "|".join(_NON_BZLMOD_FETCH_RULES) + r")\s*\(", re.M)


def module_resolution_hazards(text: str) -> list[str]:
    """Ways ``text`` resolves a dependency that ref_int's injected pins cannot reach.

    Reported, not rejected: several are legitimate. Without them a dependency that silently
    ignored ref_int's pin reads as a defect in the module under test.
    """
    hazards: list[str] = []
    scannable = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))
    for match in _ANY_OVERRIDE_BLOCK_RE.finditer(scannable):
        name = _field(match.group("body"), "module_name")
        if not name:
            continue
        patches = _patch_labels(match.group("body"))
        detail = f" with {len(patches)} patch(es)" if patches else ""
        hazards.append(f"{match.group('kind')} for {name}{detail}")
    for match in _NON_BZLMOD_FETCH_RE.finditer(scannable):
        hazards.append(f"{match.group('rule')} (fetched outside bzlmod; no override applies)")
    return sorted(set(hazards))


def _declared_overrides(text: str, source: str) -> dict[str, dict[str, str]]:
    """Every module ref_int declares an override for, with its kind and why it might not carry.

    The completeness half of the manifest guard: ``_parse_override_file`` says what can become a
    Module, this says what ref_int actually wrote, and the difference is a pin ref_int believes it
    imposes but does not. That gap hid ``rules_oci`` -- a ``git_override`` with ``tag`` instead of
    ``commit``, rejected by the parser and missed by a warning that only matched archive/local_path,
    so it produced no output at all. Enumerated from :data:`_OVERRIDE_KINDS` rather than a list of
    known-bad cases, so an unforeseen kind cannot vanish quietly either.
    """
    declared: dict[str, dict[str, str]] = {}
    for match in _ANY_OVERRIDE_BLOCK_RE.finditer(text):
        kind, body = match.group("kind"), match.group("body")
        name = _field(body, "module_name")
        if not name:
            continue
        declared[name] = {
            "module": name,
            "kind": kind,
            "file": source,
            "reason": _uncarried_reason(kind, body),
            "consequence": _UNCARRIED_CONSEQUENCE,
        }
    return declared


def _patch_labels(body: str) -> list[str]:
    """The ``patches = [...]`` entries of one override block, in declaration order."""
    match = _PATCHES_FIELD_RE.search(body)
    return _QUOTED_RE.findall(match.group("items")) if match else []


def _uncarried_reason(kind: str, body: str) -> str:
    """Why an override ref_int declares cannot become a manifest entry."""
    if kind == "git_override":
        ref = _field(body, "tag") or _field(body, "branch")
        if ref:
            return (
                f"git_override pins the mutable ref {ref!r} rather than a commit; the manifest "
                f"carries immutable commits only"
            )
        if not _field(body, "commit"):
            return "git_override declares no commit"
        return "git_override declares no remote"
    if kind == "single_version_override":
        return "single_version_override declares no version"
    if kind == "multiple_version_override":
        return "multiple_version_override cannot be expressed as a single pin"
    return f"{kind} cannot be expressed as a manifest directive"


# ``dev_dependency = True`` is a bare token, not a quoted value, so _FIELD_RE cannot match it.
_DEV_DEPENDENCY_RE = re.compile(r"dev_dependency\s*=\s*True")


def _declared_dep_specs(text: str) -> dict[str, dict[str, object]]:
    """Every ``bazel_dep`` in ``text``, with the version it asks for and whether it is dev-scoped.

    Kept separate from :func:`_declared_deps` so ``overwrite()`` keeps its narrower contract.
    ``dev_dependency`` is recorded for Stage 2, which needs it to attribute a conflict on a dev
    edge; Stage 1 does not filter on it.
    """
    specs: dict[str, dict[str, object]] = {}
    for call in _BAZEL_DEP_CALL_RE.finditer(text):
        body = call.group("body")
        name = _FIELD_RE("name").search(body)
        if name is None:
            continue
        version = _FIELD_RE("version").search(body)
        specs[name.group(1)] = {
            "version": version.group(1) if version else None,
            "dev_dependency": bool(_DEV_DEPENDENCY_RE.search(body)),
        }
    return specs


def _internal_drift(resolved: dict[str, Module], declared: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    """Where ref_int's own declared ``bazel_dep`` version is not the one it ends up imposing.

    ref_int disagreeing with itself, invisible in review because ``bazel_dep(version = ...)`` reads
    like a decision while MVS treats it as a floor and raises it silently.
    """
    drift: list[dict[str, object]] = []
    for name, spec in sorted(declared.items()):
        wanted, module = spec.get("version"), resolved.get(name)
        if not wanted or module is None or not module.version or module.version == wanted:
            continue
        drift.append(
            {
                "module": name,
                "declared": wanted,
                "resolved": module.version,
                "file": spec.get("file"),
                "dev_dependency": spec.get("dev_dependency", False),
            }
        )
    return drift


def _declared_deps(text: str) -> set[str]:
    """Every dependency a module declares via ``bazel_dep``, dev-declared ones included.

    The ``dev_dependency`` flag is deliberately not reported -- policy, not omission: ref_int's pins
    are authoritative, so presence in its resolved set decides a pin, not how the module scopes its
    own declaration. See :func:`_declared_dep_specs` where the version and dev flag are needed.
    """
    declared: set[str] = set()
    for call in _BAZEL_DEP_CALL_RE.finditer(text):
        name = _FIELD_RE("name").search(call.group("body"))
        if name is not None:
            declared.add(name.group(1))
    return declared


def generate_bazel_dep(module: Module | None, name: str) -> str:
    """Return the ``bazel_dep`` line that brings ``name`` into the root module's graph.

    Required alongside an injected override: without it Bazel rejects "the root module specifies
    overrides on nonexistent module(s)". A registry module repeats its resolved version so
    ``--check_direct_dependencies`` stays quiet; a git-overridden one omits the version, since the
    override supplies the source and any literal would only produce a spurious mismatch warning.
    """
    if module is not None and module.version:
        return f'bazel_dep(name = "{name}", version = "{module.version}")\n'
    return f'bazel_dep(name = "{name}")\n'


class ResolvedDependencies:
    """Resolved dependency versions from the reference_integration root.

    Holds a ``name -> Module`` map of the dependencies ref_int pins, and provides the
    :meth:`overwrite` interface that pins a module's ``MODULE.bazel`` to those versions.
    """

    def __init__(self, resolved: dict[str, Module], report: dict | None = None):
        self._resolved = resolved
        # Only from_mod_graph sees both what ref_int declared and what Bazel resolved, so only it can
        # populate the report. A manifest read back has the pins but not the evidence.
        self._report = report if report is not None else _empty_report()

    # -- construction: "resolved deps versions from ref_int root" --------------------

    @classmethod
    def from_known_good(cls, known_good_path: Path) -> ResolvedDependencies:
        """Build from ``known_good.json`` — first-party pins only. Tests and local inspection.

        Not an injection source, and ``main()`` rejects it as one: it carries no transitive
        registry versions and no graph, so the closure cannot be pinned from it.
        """
        kg = load_known_good(Path(known_good_path).resolve())
        resolved: dict[str, Module] = {}
        for group in kg.modules.values():
            for module in group.values():
                resolved[module.name] = module
        return cls(resolved)

    @classmethod
    def from_resolved_artifact(cls, artifact_dir: Path) -> ResolvedDependencies:
        """Build from the Stage-1 ``stage1-resolved-deps`` artifact.

        The handoff is the ``resolved_versions.json`` manifest :meth:`to_file` writes.
        ``graph.json`` sits beside it, loaded separately by :class:`DependencyGraph`;
        ``MODULE.bazel.lock`` travels along as evidence and is not read. A missing manifest is
        fatal -- Stage 2 cannot pin anything without the versions MVS selected.
        """
        artifact_dir = Path(artifact_dir)

        manifest = artifact_dir / MANIFEST_NAME
        if not manifest.is_file():
            raise FileNotFoundError(
                f"No {MANIFEST_NAME} in resolved-deps artifact {artifact_dir}; Stage 2 must consume "
                f"the Stage-1 resolved dependency set, which Stage 1 writes with "
                f"'resolved_dependencies.py --mod-graph <graph> --export <manifest>'."
            )
        return cls.from_file(manifest)

    @classmethod
    def from_mod_graph(cls, mod_graph_json: Path, override_files: list[Path]) -> ResolvedDependencies:
        """Build the resolved set by merging two sources.

        A module keeps its own version only where ref_int has no representable pin, and each such
        gap lands in the report's ``uncarried`` list rather than staying implicit.

        * The override directives ref_int declares — parsed from its root ``MODULE.bazel`` and the
          ``bazel_common/*.MODULE.bazel`` files it ``include()``s. The graph cannot supply these: it
          reports an overridden module at an empty version, or at whatever the overridden source
          declares for itself, never at the version ref_int meant to impose.
        * ``bazel mod graph --output=json`` — the post-MVS resolved version of every other
          (registry) module, emitted as ``single_version_override`` so each module under test is
          forced to the exact version ref_int resolved (MVS is graph-global, so a module's own
          subgraph could otherwise select a different version).

        Produce the graph with ``--verbose`` to populate ``originalVersion``, without which every
        report verdict is ``unknown``. The export succeeds either way.
        """
        resolved: dict[str, Module] = {}
        provenance: dict[str, str] = {}
        declared_overrides: dict[str, dict[str, str]] = {}
        declared_deps: dict[str, dict[str, object]] = {}
        for f in override_files:
            # Drop comment-only lines first: hand-written MODULE.bazel files contain
            # commented-out overrides (e.g. "# git_override(... rules_rpm ...)") that must
            # not be captured. Inline trailing comments (after a value) are left intact.
            text = "\n".join(ln for ln in Path(f).read_text().splitlines() if not ln.lstrip().startswith("#"))
            for module in cls._parse_override_file(text):  # git_override + single_version_override
                resolved[module.name] = module
                provenance[module.name] = "asserted"
            declared_overrides.update(_declared_overrides(text, Path(f).name))
            for name, spec in _declared_dep_specs(text).items():
                declared_deps[name] = {**spec, "file": Path(f).name}

        graph = json.loads(Path(mod_graph_json).read_text())
        versions: dict[str, str] = {}
        _collect_resolved_versions(graph, versions)
        declared_by: dict[str, set[str]] = {}
        _collect_declared_versions(graph, declared_by)
        for name, version in versions.items():
            if name in resolved or name in _SKIP_MODULES:
                continue  # already carried by an override directive, or non-overridable
            # Defensive: a module declaring 0.0.0 itself that ref_int does not override has no
            # version worth imposing. Every 0.0.0 module in ref_int's graph today (trlc,
            # score_tooling, the score_* target modules) is already carried by an override above.
            if version == "0.0.0":
                declared_overrides.setdefault(
                    name,
                    {
                        "module": name,
                        "kind": "none",
                        "file": str(mod_graph_json),
                        "reason": "resolves to 0.0.0 in the graph and ref_int declares no override for it",
                        "consequence": _UNCARRIED_CONSEQUENCE,
                    },
                )
                continue
            resolved[name] = Module(name=name, hash="", repo="", version=version)
            provenance[name] = "incidental"

        # The completeness guard: every override ref_int declared that did not become a manifest entry.
        uncarried = [entry for name, entry in sorted(declared_overrides.items()) if name not in resolved]
        report = _build_report(resolved, provenance, uncarried, declared_by, _internal_drift(resolved, declared_deps))
        _warn_report(report)
        return cls(resolved, report)

    def to_file(self, path: Path) -> None:
        """Serialize the resolved set to the JSON manifest (Stage 1 -> Stage 2 handoff).

        Only the fields needed to regenerate the override directive are stored
        (``version`` for single_version_override; ``repo`` + ``hash`` for git_override).
        Metadata is intentionally omitted — the manifest carries dependency pins, not the
        module-under-test's test configuration (that comes from known_good.json).
        """
        modules: dict[str, dict[str, object]] = {}
        for name in sorted(self._resolved):
            m = self._resolved[name]
            entry: dict[str, object] = {"version": m.version} if m.version else {"repo": m.repo, "hash": m.hash}
            if m.bazel_patches:
                entry["bazel_patches"] = m.bazel_patches
            modules[name] = entry
        Path(path).write_text(json.dumps({"modules": dict(sorted(modules.items()))}, indent=2) + "\n")

    @property
    def report(self) -> dict:
        """Pin provenance, consumer version differences and uncarried overrides. Empty unless built by
        :meth:`from_mod_graph`."""
        return self._report

    def write_report(self, path: Path) -> None:
        """Write the sidecar beside the manifest (see :data:`REPORT_NAME`)."""
        Path(path).write_text(json.dumps(self._report, indent=2, sort_keys=False) + "\n")

    @classmethod
    def from_file(cls, path: Path) -> ResolvedDependencies:
        """Load a resolved set previously written by :meth:`to_file`."""
        data = json.loads(Path(path).read_text())
        entries = data.get("modules", {})
        return cls({name: Module.from_dict(name, md) for name, md in entries.items()})

    @staticmethod
    def _parse_override_file(text: str) -> list[Module]:
        """Reconstruct Module objects from ref_int's own git/single_version override blocks.

        ``patches`` travels with the pin: the same commit built patched and unpatched is not
        the same dependency.
        """
        modules: list[Module] = []

        for match in _GIT_OVERRIDE_BLOCK_RE.finditer(text):
            body = match.group("body")
            name = _field(body, "module_name")
            commit = _field(body, "commit")
            remote = _field(body, "remote")
            if name and commit and remote:
                modules.append(Module(name=name, hash=commit, repo=remote, bazel_patches=_patch_labels(body)))

        for match in _SINGLE_VERSION_BLOCK_RE.finditer(text):
            body = match.group("body")
            name = _field(body, "module_name")
            version = _field(body, "version")
            if name and version:
                modules.append(Module(name=name, hash="", repo="", version=version, bazel_patches=_patch_labels(body)))

        return modules

    def export_patches(self, dest_root: Path, ref_int_root: Path) -> list[str]:
        """Copy every patch the resolved set references into ``dest_root``, workspace-relative.

        The manifest names them; Stage 2 needs the bytes to apply them.
        """
        copied: list[str] = []
        for module in sorted(self._resolved.values(), key=lambda m: m.name):
            for entry in module.bazel_patches or ():
                relative = patch_relpath(entry)
                source = Path(ref_int_root) / relative
                if not source.is_file():
                    logging.warning("%s declares patch %s, missing at %s", module.name, entry, source)
                    continue
                destination = Path(dest_root) / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(source.read_bytes())
                copied.append(relative.as_posix())
        return copied

    # -- interface: overwrite a module's MODULE.bazel ---------------------------------

    @property
    def names(self) -> set[str]:
        return set(self._resolved)

    @property
    def modules(self) -> dict[str, Module]:
        return dict(self._resolved)

    def get(self, name: str) -> Module | None:
        return self._resolved.get(name)

    def overwrite(
        self,
        module_bazel: Path,
        graph: DependencyGraph,
        *,
        module_under_test: str | None = None,
        patch_source: Path | None = None,
        write: bool = True,
    ) -> str:
        """Overwrite a module's dependency versions with ref_int's resolved set.

        ref_int's version wins wherever ref_int has one -- never raised to the module's own, never
        fallen back to it. The rule is *presence in the resolved set*, not how the module declares
        a dependency:

        * ref_int resolved a version or commit for it -> pin it, whether the module declares it
          ``dev_dependency`` or not. ref_int has an answer, so it imposes it.
        * ref_int resolved nothing for it -> leave the module's own declaration untouched and log
          it. There is nothing to impose.

        ``dev_dependency`` is not the discriminator and is never read: it does not predict whether
        ref_int resolved a dependency. ``score_baselibs`` at 0.2.9 declares 13 dev-only deps that
        ref_int *has* resolved and therefore pins (``score_tooling``, ``score_docs_as_code``,
        ``toolchains_llvm``, ...). A dependency is absent from the resolved set for an unrelated
        reason: nothing in ref_int's own graph reaches it, or ref_int pins it with an override the
        manifest cannot express (``rules_boost``, an ``archive_override``).

        Scope is the module's declared deps plus ``closure()`` of the module and of each declared
        dep. The closure is what makes the rule above safe rather than merely permissive: pinning
        ``score_tooling`` without ``lobster``/``trlc`` aborts with ``module lobster@0.0.0 not found
        in registries``, since those are non-registry and resolvable only via a root override.
        ``graph`` is therefore required -- a caller that cannot supply the closure must not pin.

        Each closure member the module does not declare gets a ``bazel_dep`` alongside its
        override, without which Bazel rejects it as an override on a nonexistent module.

        ``patch_source`` is the ``patches/`` tree Stage 1 shipped beside the manifest; without
        one a pinned dependency's patches are dropped and it is reported as unpatched.

        * Skips the module under test itself (the root is never overridden).
        * Always overwrites an existing override; re-running replaces a prior block.
        """
        module_bazel = Path(module_bazel)
        original = self._strip_injection(module_bazel.read_text())

        declared = _declared_deps(original)
        module_under_test = module_under_test or _module_name_of(original)

        from dataclasses import replace as _replace

        # The module's own closure, plus each declared dep's closure. The second is what reaches
        # deps of a dev-declared module: Stage 1 has the modules as nodes but not the edge, since
        # a dev edge is inactive unless its declaring module is root.
        in_scope = set(declared) | graph.closure(module_under_test)
        for dep in declared:
            in_scope |= graph.closure(dep)

        directives: list[str] = []
        injected_names: list[str] = []
        unresolved: list[str] = []
        unpatched: list[str] = []
        workspace = module_bazel.parent
        for name in sorted(in_scope):
            if name == module_under_test or name in _SKIP_MODULES:
                continue  # the module under test is the root; never override it
            module = self._resolved.get(name)
            if module is None:
                unresolved.append(name)
                continue
            labels = self._stage_patches(module, workspace, patch_source)
            if module.bazel_patches and not labels:
                unpatched.append(f"{name} ({len(module.bazel_patches)})")
            module = _replace(module, bazel_patches=labels or None)
            directive = generate_override_directive(module)
            if directive is None:
                continue
            # Only closure members the module does not declare need the bazel_dep line;
            # emitting a second one for a declared dep would be a duplicate declaration.
            if name not in declared:
                directives.append(generate_bazel_dep(module, name))
            directives.append(directive)
            injected_names.append(name)

        if unpatched:
            logging.warning(
                "%s: pinned %s WITHOUT ref_int's patches (count in brackets); Stage 1 builds them "
                "patched. Pass patch_source to transport them.",
                module_bazel,
                ", ".join(unpatched),
            )

        if unresolved:
            logging.warning(
                "%s: ref_int resolved no version for %s; left as the module declares them. Expected "
                "when nothing in ref_int's own graph reaches a dependency, or when ref_int pins it "
                "with an archive_override/local_path_override the manifest cannot express.",
                module_bazel,
                ", ".join(unresolved),
            )

        # ref_int's injected override must be the ONLY override for each dep. A module that
        # pins a dep with its own git_override/single_version_override (e.g. score_platform)
        # would otherwise trip Bazel's "multiple overrides for dep <x> found". Remove the
        # module's own override for every dep we inject so ref_int's resolved version wins.
        original = _strip_existing_overrides(original, injected_names)

        # After the module's competing overrides are stripped and before ref_int's are appended,
        # what is left is the module's own resolution that survives injection.
        hazards = module_resolution_hazards(original)
        if hazards:
            logging.warning(
                "%s resolves dependencies in ways ref_int's pins cannot reach: %s. These win over "
                "the resolved set; a version or patch difference here is not a defect in ref_int.",
                module_under_test,
                "; ".join(hazards),
            )

        if not directives:
            patched = original
        else:
            body = "\n".join(directives)
            patched = f"{original.rstrip()}\n\n{INJECTION_BEGIN}\n{body}\n{INJECTION_END}\n"

        if write:
            module_bazel.write_text(patched)
        return patched

    @staticmethod
    def _stage_patches(module: Module, workspace: Path, patch_source: Path | None) -> list[str]:
        """Copy one dependency's ref_int patches into the checkout; return their new labels.

        All or nothing: patches are cumulative, so a partial set builds something nobody
        validated. A missing file drops the whole set, which the caller reports.
        """
        if not module.bazel_patches or patch_source is None:
            return []

        staged: list[tuple[Path, bytes]] = []
        labels: list[str] = []
        for entry in module.bazel_patches:
            relative = patch_relpath(entry)
            source = Path(patch_source) / relative
            if not source.is_file():
                return []
            staged.append((workspace / INJECTED_PATCHES_PKG / relative, source.read_bytes()))
            labels.append(f"//{INJECTED_PATCHES_PKG}:{relative.as_posix()}")

        for destination, payload in staged:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(payload)
        # One package for the whole tree: subdirectories stay plain directories, so each patch is
        # addressable as //<pkg>:<relative path> without a BUILD file of its own.
        build_file = workspace / INJECTED_PATCHES_PKG / "BUILD"
        if not build_file.is_file():
            build_file.write_text('exports_files(glob(["**/*.patch"]))\n')
        return labels

    @staticmethod
    def _strip_injection(text: str) -> str:
        """Remove a previously appended injection block, if present."""
        pattern = re.compile(
            re.escape(INJECTION_BEGIN) + r".*?" + re.escape(INJECTION_END) + r"\n?",
            re.S,
        )
        return pattern.sub("", text).rstrip() + "\n" if pattern.search(text) else text


def _strip_existing_overrides(text: str, names: list[str]) -> str:
    """Remove any ``*_override(module_name = "<name>", ...)`` the module declares itself.

    ref_int re-injects its own resolved override for each of ``names``; Bazel forbids two
    overrides for the same module, so a module's pre-existing override must be removed first.
    Only for ``names``; an override for a dep ref_int does not inject is left alone.

    Both layouts must be matched -- a surviving one makes ref_int's the *second* override and
    Bazel aborts with "multiple overrides for dep <x> found". Two patterns rather than one, since
    each layout has an unambiguous terminator and a pattern covering both would also swallow a
    neighbouring override.
    """
    if not names:
        return text
    kinds = "|".join(_OVERRIDE_KINDS)
    for name in names:
        head = r"(?:" + kinds + r")\s*\(\s*module_name\s*=\s*\"" + re.escape(name) + r"\""
        exploded = re.compile(head + r".*?\n\)\n?", re.S)
        single_line = re.compile(head + r"[^)\n]*\)[ \t]*\n?")
        text = single_line.sub("", exploded.sub("", text))
    return text.rstrip() + "\n"


def _field(body: str, field: str) -> str:
    match = _FIELD_RE(field).search(body)
    return match.group(1) if match else ""


# A module declares its own name in the module(...) call at the top of its MODULE.bazel.
_MODULE_DECL_RE = re.compile(r"module\(\s*name\s*=\s*\"([^\"]+)\"", re.S)


def injected_override_names(module_bazel_text: str) -> set[str]:
    """Module names ref_int injected an override for, read back from a patched MODULE.bazel.

    The authoritative answer to "did ref_int pin this?" — it distinguishes an override that failed
    to take effect (ref_int's bug) from a dependency that was never pinned at all (the module
    resolved it on its own).

    Consumed by ``scripts/known_good/verify_stage2_resolution.py``, which lands with the Stage-2
    workflow; it has no caller inside Stage 1, where the manifest itself is the source of truth.
    """
    if INJECTION_BEGIN not in module_bazel_text:
        return set()
    block = module_bazel_text.split(INJECTION_BEGIN, 1)[1].split(INJECTION_END, 1)[0]
    return set(re.findall(r'_override\(\s*module_name\s*=\s*"([^"]+)"', block))


def _module_name_of(module_bazel_text: str) -> str:
    """The module's own name, from the ``module(name = "...")`` call in its MODULE.bazel.

    Lets Stage 2 identify the module under test from the file itself, so the caller need
    not also pass ``--module-under-test``.
    """
    match = _MODULE_DECL_RE.search(module_bazel_text)
    return match.group(1) if match else ""


def _collect_resolved_versions(node: dict, acc: dict[str, str]) -> None:
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


def _collect_declared_versions(node: dict, acc: dict[str, set[str]]) -> None:
    """Walk the graph recording name -> the versions consumers asked for.

    ``--verbose`` adds ``originalVersion`` to an edge whenever MVS moved a module off the version its
    dependent declared; without it, nothing is recorded. Incomplete by construction, since a non-root
    ``dev_dependency`` edge is never loaded: ``score_crates`` and ``score_rules_imagefs`` are visible
    but ``score_toolchains_rust``, ``score_itf`` and ``yq.bzl`` are not. See
    :data:`_DEV_EDGE_LIMITATION`.
    """
    for dep in node.get("dependencies", []):
        name, original = dep.get("name"), dep.get("originalVersion")
        if name and original:
            acc.setdefault(name, set()).add(original)
        _collect_declared_versions(dep, acc)


# Bazel's own module-version grammar: a mandatory release part, an optional ``-prerelease``, and
# optional ``+build`` metadata that is deliberately not captured because it does not affect ordering.
_VERSION_RE = re.compile(r"^(?P<release>[a-zA-Z0-9.]+)(?:-(?P<prerelease>[a-zA-Z0-9.-]+))?(?:\+[a-zA-Z0-9.-]+)?$")


def _identifier_key(identifier: str) -> tuple[int, int, str]:
    """Sort key for one version identifier, matching Bazel's ``Identifier.COMPARATOR``.

    Digits-only identifiers sort *below* alphanumeric ones; two numeric identifiers compare
    numerically; two alphanumeric ones compare lexicographically.
    """
    if identifier.isdigit():
        return (0, int(identifier), "")
    return (1, 0, identifier)


def _version_key(version: str) -> tuple[list[tuple[int, int, str]], int, list[tuple[int, int, str]]]:
    """Sort key for a whole version, mirroring Bazel's ``Version.COMPARATOR`` chain.

    Release identifiers first (list comparison is lexicographic, so a shorter list sorts lower --
    ``1.17.0`` is below ``1.17.0.bcr.2``), then presence of a prerelease (a prerelease sorts *below*
    the same release without one), then the prerelease identifiers, which are dot-split like the
    release part rather than compared as one opaque string.
    """
    match = _VERSION_RE.match(version)
    if match is None:
        # Not a version Bazel would accept; order it as a single alphanumeric identifier so the
        # comparison stays total rather than raising on data we only ever report on.
        return ([_identifier_key(version)], 1, [])
    release = [_identifier_key(i) for i in match.group("release").split(".")]
    prerelease = match.group("prerelease")
    if not prerelease:
        return (release, 1, [])
    return (release, 0, [_identifier_key(i) for i in prerelease.split(".")])


def _compare_versions(left: str, right: str) -> int:
    """Order two Bazel module versions: -1, 0 or 1.

    Ports Bazel's own ordering (``Version.java``) rather than approximating it, because the report
    claims to say whether ref_int's pin is behind what a consumer asked for -- saying "unknown"
    where Bazel has a definite answer is misinformation, not caution. The ordering is total; Bazel
    has no incomparable pair.

    Deliberately not a string comparison: ``"0.0.10" < "0.0.6"`` holds lexically, which would report
    the real ``score_crates`` conflict backwards.
    """
    if left == right:
        return 0
    left_key, right_key = _version_key(left), _version_key(right)
    if left_key == right_key:
        return 0
    return -1 if left_key < right_key else 1


def _highest(versions: list[str]) -> str:
    """The greatest of ``versions`` under Bazel's ordering."""
    return max(versions, key=_version_key)


def _empty_report() -> dict:
    return {
        "schema": 1,
        "policy": POLICY,
        "counts": {
            "pinned": 0,
            "asserted": 0,
            "incidental": 0,
            "uncarried": 0,
            "differs": 0,
            "ref_int_internal_drift": 0,
        },
        "pins": {},
        "uncarried": [],
        "ref_int_internal_drift": [],
        "limitations": [],
    }


_DEV_EDGE_LIMITATION = (
    "A non-root dev_dependency edge is never loaded by Bazel, so a consumer's dev-declared version "
    "cannot appear in declared_versions. Measured on ref_int: score_toolchains_rust (0.9.1), "
    "score_itf (0.4.0) and score_rules_imagefs are dev-declared by modules under test. Stage 2 "
    "completes this from each module's own MODULE.bazel."
)
_OUT_OF_GRAPH_LIMITATION = (
    "A dependency of a module outside ref_int's own graph is invisible here: rules_distroless "
    "requires yq.bzl 0.3.1 and never appears in ref_int's graph, so ref_int's incidental yq.bzl "
    "pin looks unconflicted while it breaks that module's load phase."
)
_NO_VERBOSE_LIMITATION = (
    "The graph carried no originalVersion for any module, so consumer requests were unavailable "
    "and every verdict is 'unknown'. Produce the graph with "
    "'bazel mod graph --verbose --output=json' to populate them."
)


def _build_report(
    resolved: dict[str, Module],
    provenance: dict[str, str],
    uncarried: list[dict[str, str]],
    declared_by: dict[str, set[str]],
    internal_drift: list[dict[str, object]],
) -> dict:
    """Assemble the sidecar: where each pin came from, and who disagrees with it.

    ``provenance`` separates the two: ``asserted`` means ref_int wrote an override, so the version
    is a decision; ``incidental`` means it merely inherited whatever MVS selected. Both are imposed
    with equal force -- the ``yq.bzl`` pin that breaks score_communication is incidental, since
    nothing in ref_int declares yq.bzl at all.
    """
    report = _empty_report()
    differs: list[str] = []
    for name in sorted(resolved):
        module = resolved[name]
        wanted = sorted(declared_by.get(name, ()))
        entry: dict[str, object] = {
            "pin": {"version": module.version} if module.version else {"repo": module.repo, "hash": module.hash},
            "provenance": provenance.get(name, "incidental"),
            "declared_versions": wanted,
            "verdict": "unknown",
            "direction": None,
        }
        if not wanted:
            # Nothing asked for a different version, or the request rode an edge Bazel never loaded.
            # Indistinguishable here, hence "unknown" rather than "agree".
            entry["verdict"] = "by_commit" if not module.version else "unknown"
        elif not module.version:
            entry["verdict"] = "differs"  # a commit replaced a version request: not comparable
        elif all(v == module.version for v in wanted):
            entry["verdict"] = "agree"
        else:
            entry["verdict"] = "differs"
            order = _compare_versions(module.version, _highest(wanted))
            entry["direction"] = "ref_int_lower" if order < 0 else "ref_int_higher"
        if entry["verdict"] == "differs":
            differs.append(name)
        report["pins"][name] = entry

    report["uncarried"] = uncarried
    report["ref_int_internal_drift"] = internal_drift
    asserted = sum(1 for v in provenance.values() if v == "asserted")
    report["counts"] = {
        "pinned": len(resolved),
        "asserted": asserted,
        "incidental": len(resolved) - asserted,
        "uncarried": len(uncarried),
        "differs": len(differs),
        "ref_int_internal_drift": len(internal_drift),
    }
    # The first two are properties of what Bazel loads, not of this run, so they always apply.
    report["limitations"] = [_DEV_EDGE_LIMITATION, _OUT_OF_GRAPH_LIMITATION]
    if not declared_by:
        report["limitations"].append(_NO_VERBOSE_LIMITATION)
    return report


def _warn_report(report: dict) -> None:
    """Surface the report's findings as GitHub annotations, without failing the export.

    ``::warning::`` rather than ``logging.warning``, which does not reach the job UI -- the reason
    silent downgrades and the dropped ``rules_oci`` pin went unnoticed. The export always exits 0;
    ref_int's version is imposed and reported rather than blocking the run.
    """
    if _NO_VERBOSE_LIMITATION in report["limitations"]:
        # Without this the "differs" half of the report is silently a constant: every verdict is
        # "unknown" and no consumer disagreement can be detected, which reads identically to a
        # graph in which nobody disagrees.
        print(
            "::warning::resolved_dependencies - the graph carries no originalVersion, so no "
            "consumer version differences can be detected. Produce it with "
            "'bazel mod graph --verbose --output=json' to enable them."
        )
    for entry in report["uncarried"]:
        print(
            f"::warning::resolved_dependencies - ref_int declares an override for "
            f"{entry['module']} that the manifest cannot carry: {entry['reason']}. {entry['consequence']}."
        )
    for name, pin in report["pins"].items():
        if pin["verdict"] != "differs":
            continue
        pinned = pin["pin"].get("version") or f"commit {pin['pin'].get('hash', '')[:12]}"
        direction = f" ({pin['direction']})" if pin["direction"] else ""
        print(
            f"::warning::resolved_dependencies - ref_int pins {name} at {pinned}{direction}; "
            f"consumers in ref_int's graph declare {', '.join(pin['declared_versions'])}. "
            f"ref_int's version is imposed."
        )


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
        "--resolved-deps",
        type=Path,
        default=None,
        help=(
            "Inject mode (required): Stage-1 stage1-resolved-deps artifact dir, holding "
            f"{MANIFEST_NAME} and {GRAPH_NAME}."
        ),
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
        "--report",
        type=Path,
        default=None,
        help=(
            f"Export mode: write the pin report to this path instead of {REPORT_NAME} beside the "
            f"manifest. Produce the graph with 'bazel mod graph --verbose --output=json' so the "
            f"report can name the consumers that asked for a different version."
        ),
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
        mod_graph = workspace_path(args.mod_graph)
        if not mod_graph.is_file():
            raise SystemExit(
                f"--mod-graph {mod_graph} does not exist. Produce it first with: "
                "bazel mod graph --output=json > graph.json"
            )
        root = repo_root()
        override_files = [
            f for f in [root / "MODULE.bazel", *sorted((root / "bazel_common").glob("*.MODULE.bazel"))] if f.is_file()
        ]
        resolved = ResolvedDependencies.from_mod_graph(mod_graph, override_files)
        export = workspace_path(args.export)
        export.parent.mkdir(parents=True, exist_ok=True)
        resolved.to_file(export)
        # Stage 2 needs the graph too: the manifest says which version each module resolves
        # to, the graph says which of them a given module actually depends on.
        graph_copy = export.parent / GRAPH_NAME
        graph_copy.write_text(mod_graph.read_text())
        # And the patch bytes, without which Stage 2 can only record that ref_int patched it.
        patches_copy = export.parent / PATCHES_DIRNAME
        copied = resolved.export_patches(patches_copy, root)
        report_path = workspace_path(args.report) if args.report else export.parent / REPORT_NAME
        resolved.write_report(report_path)
        counts = resolved.report["counts"]
        print(f"Wrote resolved dependency manifest ({len(resolved.names)} modules) to {export}")
        print(f"Stored dependency graph for Stage 2 at {graph_copy}")
        print(f"Copied {len(copied)} dependency patch file(s) for Stage 2 to {patches_copy}")
        print(
            f"Wrote pin report to {report_path} "
            f"({counts['asserted']} asserted, {counts['incidental']} incidental, "
            f"{counts['differs']} differing, {counts['uncarried']} uncarried)"
        )
        return

    # Inject mode (Stage 2): overwrite a module's MODULE.bazel with the resolved set.
    if args.module_bazel is None:
        raise SystemExit("module_bazel is required unless --export is given")

    # known_good.json is not a valid inject source: it carries only first-party score
    # modules with no transitive registry versions, so the closure could not be pinned.
    if not args.resolved_deps:
        raise SystemExit(
            "--resolved-deps is required for inject mode: Stage 2 must pin against the "
            "Stage-1 resolved set. known_good.json carries only first-party pins and no "
            "transitive versions, so it cannot back the injection."
        )
    module_bazel = workspace_path(args.module_bazel)
    resolved_deps = workspace_path(args.resolved_deps)
    resolved = ResolvedDependencies.from_resolved_artifact(resolved_deps)
    graph = DependencyGraph.from_file(resolved_deps / GRAPH_NAME)

    patches = resolved_deps / PATCHES_DIRNAME
    patched = resolved.overwrite(
        module_bazel,
        graph,
        module_under_test=args.module_under_test,
        patch_source=patches if patches.is_dir() else None,
        write=not args.dry_run,
    )
    if args.dry_run:
        print(patched)
    else:
        print(f"Injected resolved-deps overrides into {module_bazel}")


if __name__ == "__main__":
    main()
