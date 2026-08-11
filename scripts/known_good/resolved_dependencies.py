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


def _repo_root() -> Path:
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


try:
    from known_good.models.known_good import load_known_good
    from known_good.models.module import Module
except ImportError:
    if str(_HERE) not in sys.path:
        sys.path.insert(0, str(_HERE))
    from models.known_good import load_known_good  # noqa: E402
    from models.module import Module  # noqa: E402

# Marker delimiting the block we append, so injection is idempotent / detectable.
INJECTION_BEGIN = "# --- BEGIN ref_int resolved-deps injection ---"
INJECTION_END = "# --- END ref_int resolved-deps injection ---"


def generate_override_directive(module: Module, repo_commit_dict: dict[str, str] | None = None) -> str | None:
    """Return the override directive (single_version_override / git_override) for a module.

    Returns just the override call without a preceding ``bazel_dep(...)`` line, so the
    same logic can be reused both to build ref_int's score_modules_*.MODULE.bazel files
    and to inject overrides into a module's own MODULE.bazel where bazel_dep is already
    declared (see :meth:`ResolvedDependencies.overwrite`).

    Returns ``None`` when the module has neither a usable version nor a valid repo+commit.
    """
    repo_commit_dict = repo_commit_dict or {}
    commit = module.hash

    if module.repo in repo_commit_dict:
        commit = repo_commit_dict[module.repo]

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

# Built-in / non-registry modules that must not be given a single_version_override.
_SKIP_MODULES = {"bazel_tools"}

# Capture the module name from any ``bazel_dep(name = "...")`` call (name is the first arg).
_BAZEL_DEP_RE = re.compile(r'bazel_dep\(\s*name\s*=\s*"([^"]+)"')
# The whole ``bazel_dep(...)`` argument list. ``[^)]*`` is sufficient: bazel_dep takes only
# scalar keyword arguments, never a nested call.
_BAZEL_DEP_CALL_RE = re.compile(r"bazel_dep\((?P<body>[^)]*)\)", re.S)
# The two override kinds ref_int declares, each mapping onto a single Module.
# multiple_version_override is unsupported: ref_int declares none. archive_override /
# local_path_override cannot be reproduced at all and are reported instead.
_GIT_OVERRIDE_BLOCK_RE = re.compile(r"git_override\((?P<body>.*?)\)", re.S)
_SINGLE_VERSION_BLOCK_RE = re.compile(r"single_version_override\((?P<body>.*?)\)", re.S)
_FIELD_RE = lambda field: re.compile(rf'{field}\s*=\s*"([^"]+)"')  # noqa: E731


def _declared_deps(text: str) -> set[str]:
    """Every dependency a module declares via ``bazel_dep``, dev-declared ones included.

    The ``dev_dependency`` flag is deliberately not reported: it does not decide whether ref_int
    pins a dependency -- presence in the resolved set does. See :meth:`ResolvedDependencies.overwrite`.
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

    def __init__(self, resolved: dict[str, Module]):
        self._resolved = resolved

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
        """Build the complete resolved set by merging two sources.

        * ref_int's own override directives, parsed from its root ``MODULE.bazel`` and the
          ``bazel_common/*.MODULE.bazel`` files it ``include()``s. The graph cannot supply these
          -- it reports overridden modules as version ``0.0.0``.
        * ``bazel mod graph --output=json`` for the post-MVS version of every other (registry)
          module, emitted as ``single_version_override`` so each module under test is forced to
          the version ref_int resolved -- MVS is graph-global, so a module's own subgraph could
          otherwise select a different one.

        ``archive_override`` / ``local_path_override`` targets cannot be represented and are
        logged as not carried.
        """
        resolved: dict[str, Module] = {}
        unrepresentable: list[str] = []
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
        versions: dict[str, str] = {}
        _collect_resolved_versions(graph, versions)
        skipped: list[str] = []
        for name, version in versions.items():
            if name in resolved or name in _SKIP_MODULES:
                continue  # already carried by an override directive, or non-overridable
            # 0.0.0 means ref_int pins it via an override this parser did not capture (an
            # archive_override), which single_version_override cannot reproduce. Empty versions
            # are already dropped by _collect_resolved_versions.
            if version == "0.0.0":
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
        modules: dict[str, dict[str, object]] = {}
        for name in sorted(self._resolved):
            m = self._resolved[name]
            entry: dict[str, object] = {"version": m.version} if m.version else {"repo": m.repo, "hash": m.hash}
            if m.bazel_patches:
                entry["bazel_patches"] = m.bazel_patches
            modules[name] = entry
        Path(path).write_text(json.dumps({"modules": dict(sorted(modules.items()))}, indent=2) + "\n")

    @classmethod
    def from_file(cls, path: Path) -> ResolvedDependencies:
        """Load a resolved set previously written by :meth:`to_file`."""
        data = json.loads(Path(path).read_text())
        entries = data.get("modules", {})
        return cls({name: Module.from_dict(name, md) for name, md in entries.items()})

    @staticmethod
    def _parse_override_file(text: str) -> list[Module]:
        """Reconstruct Module objects from ref_int's own git/single_version override blocks."""
        modules: list[Module] = []

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
        write: bool = True,
    ) -> str:
        """Overwrite a module's dependency versions with ref_int's resolved set.

        The rule is *presence in the resolved set*, not how the module declares a dependency:

        * ref_int resolved a version or commit for it -> pin it, whether the module declares it
          ``dev_dependency`` or not. ref_int has an answer, so it imposes it.
        * ref_int resolved nothing for it -> leave the module's own declaration untouched and log
          it. There is nothing to impose.

        ``dev_dependency`` is not the discriminator and is never read. The two properties are
        independent: ``score_baselibs`` declares 11 dev-only deps ref_int *has* resolved
        (``score_tooling``, ``score_docs_as_code``, ``toolchains_llvm``, ...), while
        ``score_baselibs_rust`` is a public dep ref_int has *not* resolved. A dependency is absent
        from the resolved set because nothing in ref_int's own graph reaches it -- usually it is
        only reachable through some module's dev edge, inactive while ref_int is root -- or because
        ref_int pins it with an ``archive_override`` the manifest cannot express.

        Scope is the module's declared deps plus ``closure()`` of the module and of each declared
        dep. The closure is what makes the rule above safe rather than merely permissive: pinning
        ``score_tooling`` without ``lobster``/``trlc`` aborts with ``module lobster@0.0.0 not found
        in registries``, since those are non-registry and resolvable only via a root override.
        ``graph`` is therefore required -- a caller that cannot supply the closure must not pin.

        Each closure member the module does not declare gets a ``bazel_dep`` alongside its
        override, without which Bazel rejects it as an override on a nonexistent module.

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
        for name in sorted(in_scope):
            if name == module_under_test or name in _SKIP_MODULES:
                continue  # the module under test is the root; never override it
            module = self._resolved.get(name)
            if module is None:
                unresolved.append(name)
                continue
            # Strip bazel_patches: they reference //patches/... labels in ref_int's
            # workspace which do not exist inside another module's checkout.
            module = _replace(module, bazel_patches=None)
            directive = generate_override_directive(module)
            if directive is None:
                continue
            # Only closure members the module does not declare need the bazel_dep line;
            # emitting a second one for a declared dep would be a duplicate declaration.
            if name not in declared:
                directives.append(generate_bazel_dep(module, name))
            directives.append(directive)
            injected_names.append(name)

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


_OVERRIDE_KINDS = (
    "git_override",
    "single_version_override",
    "archive_override",
    "local_path_override",
    "multiple_version_override",
)


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

    The authoritative answer to "did ref_int pin this?" — used by the Stage 2 verification
    to tell an override that failed to take effect (ref_int's bug) from a dependency that
    was never pinned at all (the module resolved it on its own).
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
        mod_graph = Path(args.mod_graph)
        if not mod_graph.is_file():
            raise SystemExit(
                f"--mod-graph {mod_graph} does not exist. Produce it first with: "
                "bazel mod graph --output=json > graph.json"
            )
        repo_root = _repo_root()
        override_files = [
            f
            for f in [repo_root / "MODULE.bazel", *sorted((repo_root / "bazel_common").glob("*.MODULE.bazel"))]
            if f.is_file()
        ]
        resolved = ResolvedDependencies.from_mod_graph(mod_graph, override_files)
        export = Path(args.export)
        export.parent.mkdir(parents=True, exist_ok=True)
        resolved.to_file(export)
        # Stage 2 needs the graph too: the manifest says which version each module resolves
        # to, the graph says which of them a given module actually depends on.
        graph_copy = export.parent / GRAPH_NAME
        graph_copy.write_text(mod_graph.read_text())
        print(f"Wrote resolved dependency manifest ({len(resolved.names)} modules) to {export}")
        print(f"Stored dependency graph for Stage 2 at {graph_copy}")
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
    resolved = ResolvedDependencies.from_resolved_artifact(args.resolved_deps)
    graph = DependencyGraph.from_file(Path(args.resolved_deps) / GRAPH_NAME)

    patched = resolved.overwrite(
        args.module_bazel,
        graph,
        module_under_test=args.module_under_test,
        write=not args.dry_run,
    )
    if args.dry_run:
        print(patched)
    else:
        print(f"Injected resolved-deps overrides into {args.module_bazel}")


if __name__ == "__main__":
    main()
