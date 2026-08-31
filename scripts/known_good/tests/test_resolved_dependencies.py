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
"""Unit tests for ResolvedDependencies (DR-008 Option 4 dependency injection).

Self-contained: builds the resolved set from a temporary known_good.json and
overwrites a temporary module MODULE.bazel — no cloned repos or Bazel required.
"""

import json
import logging
import sys
from pathlib import Path

import pytest

# Make scripts/ importable so known_good.* package resolves when run via plain pytest.
_SCRIPTS_DIR = Path(__file__).resolve().parents[2]
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from known_good.models.module import Module  # noqa: E402
from known_good.resolved_dependencies import (  # noqa: E402
    INJECTION_BEGIN,
    INJECTION_END,
    MANIFEST_NAME,
    REPORT_NAME,
    DependencyGraph,
    ResolvedDependencies,
    _compare_versions,
    _declared_dep_specs,
    _declared_deps,
    workspace_path,
    module_resolution_hazards,
)

KNOWN_GOOD = {
    "modules": {
        "target_sw": {
            "score_baselibs": {
                "repo": "https://github.com/eclipse-score/baselibs.git",
                "hash": "cab36dd7de92aaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "bazel_patches": ["patches/baselibs/001-fix.patch"],
            },
            "score_logging": {
                "repo": "https://github.com/eclipse-score/logging.git",
                "hash": "0e9187f79a99bbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            },
            "score_persistency": {
                "repo": "https://github.com/eclipse-score/persistency.git",
                "hash": "4d1fa1ae3c55cccccccccccccccccccccccccccc",
            },
        },
        "tooling": {
            "score_tooling": {
                "repo": "https://github.com/eclipse-score/tooling.git",
                "version": "1.2.0",
            },
        },
    },
    "timestamp": "2026-01-01T00:00:00+00:00Z",
}

MODULE_BAZEL = """\
module(name = "score_persistency", version = "0.0.0")

bazel_dep(name = "rules_cc", version = "0.2.17")
bazel_dep(name = "score_baselibs", version = "0.2.7")
bazel_dep(name = "score_logging", version = "0.2.0")
bazel_dep(name = "score_tooling", version = "1.0.0")
bazel_dep(name = "score_unpinned", version = "9.9.9")
"""


@pytest.fixture
def known_good_file(tmp_path: Path) -> Path:
    p = tmp_path / "known_good.json"
    p.write_text(json.dumps(KNOWN_GOOD))
    return p


@pytest.fixture
def module_bazel(tmp_path: Path) -> Path:
    p = tmp_path / "MODULE.bazel"
    p.write_text(MODULE_BAZEL)
    return p


@pytest.fixture
def resolved(known_good_file: Path) -> ResolvedDependencies:
    return ResolvedDependencies.from_known_good(known_good_file)


@pytest.fixture
def flat_graph() -> DependencyGraph:
    """MODULE_BAZEL's modules as edgeless nodes, so every closure is empty and scope == declared.

    overwrite() requires a graph, since without one it cannot honour "pin nothing whose closure I
    do not own". Tests that are not about closure use this to isolate the rest of the behaviour.
    """
    names = ["score_persistency", "rules_cc", "score_baselibs", "score_logging", "score_tooling", "score_unpinned"]
    return DependencyGraph(_node("<root>", "", [_node(n) for n in names]))


def _node(name: str, version: str = "1.0", deps: list[dict] | None = None, **extra) -> dict:
    """An expanded graph node, matching 'bazel mod graph --output=json'."""
    return {"name": name, "version": version, "dependencies": deps or [], "indirectDependencies": [], **extra}


def _unexpanded(name: str, version: str = "1.0") -> dict:
    """A repeated reference: no 'dependencies' key, so it must be resolved via the index."""
    return {"name": name, "version": version, "unexpanded": True}


class TestDependencyGraph:
    """Closure computation over the mod graph, including its unexpanded-node encoding."""

    def test_closure_follows_transitive_edges(self):
        baselibs = _node("score_baselibs", deps=[_node("flatbuffers")])
        graph = DependencyGraph(_node("<root>", "", [_node("score_persistency", deps=[baselibs])]))
        assert graph.closure("score_persistency") == {"score_baselibs", "flatbuffers"}

    def test_closure_resolves_unexpanded_references(self):
        # Bazel emits a module's children only at its first occurrence; every later
        # occurrence is an 'unexpanded' stub. Walking the subtree literally would stop at
        # the stub and miss flatbuffers, which is exactly the gap this must not have.
        graph = DependencyGraph(
            _node(
                "<root>",
                "",
                [
                    _node("score_baselibs", deps=[_node("flatbuffers")]),
                    _node("score_communication", deps=[_unexpanded("score_baselibs")]),
                ],
            )
        )
        assert graph.closure("score_communication") == {"score_baselibs", "flatbuffers"}

    def test_closure_excludes_the_module_itself(self):
        graph = DependencyGraph(_node("<root>", "", [_node("score_time", deps=[_node("rules_cc")])]))
        assert "score_time" not in graph.closure("score_time")

    def test_closure_terminates_on_cycles(self):
        a = _node("a")
        b = _node("b", deps=[_unexpanded("a")])
        a["dependencies"] = [b]
        assert DependencyGraph(_node("<root>", "", [a])).closure("a") == {"b"}

    def test_closure_of_unknown_module_is_empty(self):
        graph = DependencyGraph(_node("<root>", "", [_node("score_time")]))
        assert graph.closure("not_in_graph") == set()

    def test_from_file_reports_a_missing_graph(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError, match="bazel mod graph"):
            DependencyGraph.from_file(tmp_path / "graph.json")


class TestFromKnownGood:
    def test_names_span_all_groups(self, resolved: ResolvedDependencies):
        assert {"score_baselibs", "score_logging", "score_persistency", "score_tooling"} <= resolved.names

    def test_get_returns_resolved_commit(self, resolved: ResolvedDependencies):
        assert resolved.get("score_baselibs").hash.startswith("cab36dd7de92")

    def test_version_module_kept(self, resolved: ResolvedDependencies):
        assert resolved.get("score_tooling").version == "1.2.0"


class TestOverwrite:
    def test_pins_declared_resolved_siblings(
        self, resolved: ResolvedDependencies, module_bazel: Path, flat_graph: DependencyGraph
    ):
        patched = resolved.overwrite(module_bazel, flat_graph, module_under_test="score_persistency", write=False)
        block = patched.split(INJECTION_BEGIN)[1].split(INJECTION_END)[0]
        assert 'git_override(\n    module_name = "score_baselibs"' in block
        assert 'commit = "cab36dd7de92aaaaaaaaaaaaaaaaaaaaaaaaaaaa"' in block
        # version module -> single_version_override
        assert 'single_version_override(\n    module_name = "score_tooling"' in block
        assert 'version = "1.2.0"' in block

    def test_strips_patches_without_a_patch_source(
        self, resolved: ResolvedDependencies, module_bazel: Path, flat_graph: DependencyGraph
    ):
        # Nothing to re-host from, so they are dropped rather than emitted as dead labels.
        patched = resolved.overwrite(module_bazel, flat_graph, module_under_test="score_persistency", write=False)
        assert "patches/baselibs/001-fix.patch" not in patched
        assert "patch_strip" not in patched

    def test_transports_patches_from_the_stage1_artifact(
        self, resolved: ResolvedDependencies, module_bazel: Path, flat_graph: DependencyGraph, tmp_path: Path
    ):
        source = tmp_path / "stage1_patches"
        (source / "patches" / "baselibs").mkdir(parents=True)
        (source / "patches" / "baselibs" / "001-fix.patch").write_text("--- a\n+++ b\n")

        patched = resolved.overwrite(
            module_bazel,
            flat_graph,
            module_under_test="score_persistency",
            patch_source=source,
            write=False,
        )

        assert 'patches = [\n        "//ref_int_patches:patches/baselibs/001-fix.patch",' in patched
        assert "patch_strip = 1" in patched
        staged = module_bazel.parent / "ref_int_patches" / "patches" / "baselibs" / "001-fix.patch"
        assert staged.read_text() == "--- a\n+++ b\n"
        assert (module_bazel.parent / "ref_int_patches" / "BUILD").is_file()

    def test_drops_the_whole_set_when_one_patch_is_missing(
        self, resolved: ResolvedDependencies, module_bazel: Path, flat_graph: DependencyGraph, tmp_path: Path
    ):
        empty = tmp_path / "stage1_patches"
        empty.mkdir()

        patched = resolved.overwrite(
            module_bazel,
            flat_graph,
            module_under_test="score_persistency",
            patch_source=empty,
            write=False,
        )

        assert "001-fix.patch" not in patched
        assert "patch_strip" not in patched

    def test_skips_resolved_dep_not_declared(
        self, resolved: ResolvedDependencies, tmp_path: Path, flat_graph: DependencyGraph
    ):
        # Only declared deps are injected. Overriding a module that is NOT in the module's
        # dependency graph makes Bazel fail ("overrides on nonexistent module(s)"), so a
        # resolved dep the module does not declare must NOT be injected.
        mod = tmp_path / "MODULE.bazel"
        mod.write_text(
            'module(name = "score_persistency", version = "0.0.0")\n'
            'bazel_dep(name = "score_baselibs", version = "0.1")\n'
        )
        block = resolved.overwrite(mod, flat_graph, module_under_test="score_persistency", write=False).split(
            INJECTION_BEGIN
        )[1]
        assert 'module_name = "score_baselibs"' in block  # declared -> injected
        assert 'module_name = "score_logging"' not in block  # not declared -> not injected

    def test_skips_root_module(self, resolved: ResolvedDependencies, module_bazel: Path, flat_graph: DependencyGraph):
        patched = resolved.overwrite(module_bazel, flat_graph, module_under_test="score_persistency", write=False)
        block = patched.split(INJECTION_BEGIN)[1].split(INJECTION_END)[0]
        assert 'module_name = "score_persistency"' not in block

    def test_skips_unpinned_third_party(
        self, resolved: ResolvedDependencies, module_bazel: Path, flat_graph: DependencyGraph
    ):
        patched = resolved.overwrite(module_bazel, flat_graph, module_under_test="score_persistency", write=False)
        block = patched.split(INJECTION_BEGIN)[1].split(INJECTION_END)[0]
        assert "score_unpinned" not in block
        assert "rules_cc" not in block

    def test_idempotent(self, resolved: ResolvedDependencies, module_bazel: Path, flat_graph: DependencyGraph):
        first = resolved.overwrite(module_bazel, flat_graph, module_under_test="score_persistency", write=True)
        second = resolved.overwrite(module_bazel, flat_graph, module_under_test="score_persistency", write=True)
        assert first == second
        assert second.count(INJECTION_BEGIN) == 1

    def test_warns_on_declared_dep_not_in_resolved_set(
        self,
        resolved: ResolvedDependencies,
        module_bazel: Path,
        flat_graph: DependencyGraph,
        caplog: pytest.LogCaptureFixture,
    ):
        # "score_unpinned" is declared in MODULE_BAZEL but has no known_good.json entry.
        # This is expected to be effectively impossible once the resolved set is sourced
        # from the full 'bazel mod graph' (a superset of any module's own graph), so it
        # must be surfaced as a warning rather than silently ignored.
        with caplog.at_level(logging.WARNING):
            resolved.overwrite(module_bazel, flat_graph, module_under_test="score_persistency", write=False)
        assert "score_unpinned" in caplog.text

    def test_overwrites_dep_with_existing_override(
        self, resolved: ResolvedDependencies, tmp_path: Path, flat_graph: DependencyGraph
    ):
        # ref_int always decides the version — a pre-existing override in the module is replaced.
        mod = tmp_path / "MODULE.bazel"
        mod.write_text(
            MODULE_BAZEL + '\ngit_override(\n    module_name = "score_logging",\n    commit = "deadbeef",\n'
            '    remote = "https://example.com/x.git",\n)\n'
        )
        patched = resolved.overwrite(mod, flat_graph, module_under_test="score_persistency", write=False)
        block = patched.split(INJECTION_BEGIN)[1].split(INJECTION_END)[0]
        # ref_int's resolved commit must appear in the injection block, overwriting "deadbeef"
        assert 'module_name = "score_logging"' in block
        assert "deadbeef" not in block
        # the module's OWN override must be removed from the whole file — otherwise Bazel
        # aborts with "multiple overrides for dep score_logging found".
        assert "deadbeef" not in patched
        assert patched.count('module_name = "score_logging"') == 1

    def test_overwrites_dep_whose_own_override_is_written_on_one_line(
        self, resolved: ResolvedDependencies, tmp_path: Path, flat_graph: DependencyGraph
    ):
        # Bazel rejects two overrides for one module, so a single-line override must be stripped
        # like a multi-line one -- otherwise ref_int's is the second and nothing resolves.
        mod = tmp_path / "MODULE.bazel"
        mod.write_text(
            MODULE_BAZEL + '\ngit_override(module_name = "score_logging", commit = "deadbeef", remote = "u")\n'
        )
        patched = resolved.overwrite(mod, flat_graph, module_under_test="score_persistency", write=False)
        assert "deadbeef" not in patched
        assert patched.count('module_name = "score_logging"') == 1

    def test_strip_leaves_an_override_for_a_dep_it_does_not_inject(
        self, resolved: ResolvedDependencies, tmp_path: Path, flat_graph: DependencyGraph
    ):
        # A dep with no entry in the resolved set is never injected, so the module's own override
        # for it must survive -- a too-greedy strip would take neighbours with it.
        mod = tmp_path / "MODULE.bazel"
        mod.write_text(MODULE_BAZEL + '\nsingle_version_override(module_name = "score_unpinned", version = "9.9.9")\n')
        patched = resolved.overwrite(mod, flat_graph, module_under_test="score_persistency", write=False)
        assert 'module_name = "score_unpinned"' in patched


class TestOverwriteTransitive:
    """Closure injection: pin transitive deps the module never declares itself."""

    @staticmethod
    def _graph() -> DependencyGraph:
        # score_persistency -> score_baselibs -> score_logging. Only score_baselibs is
        # declared directly by the module; score_logging arrives through it.
        return DependencyGraph(
            _node(
                "<root>",
                "",
                [_node("score_persistency", deps=[_node("score_baselibs", deps=[_node("score_logging")])])],
            )
        )

    @pytest.fixture
    def only_baselibs(self, tmp_path: Path) -> Path:
        p = tmp_path / "MODULE.bazel"
        p.write_text('module(name = "score_persistency", version = "0.0.0")\nbazel_dep(name = "score_baselibs")\n')
        return p

    def test_injects_transitive_dep_with_its_bazel_dep(self, resolved: ResolvedDependencies, only_baselibs: Path):
        patched = resolved.overwrite(only_baselibs, self._graph(), module_under_test="score_persistency", write=False)
        block = patched.split(INJECTION_BEGIN)[1].split(INJECTION_END)[0]
        assert 'module_name = "score_baselibs"' in block
        assert 'module_name = "score_logging"' in block
        # The override alone would be rejected ("overrides on nonexistent module(s)") since
        # the module never declares score_logging — the bazel_dep is what makes it legal.
        assert 'bazel_dep(name = "score_logging")' in block

    def test_declared_dep_gets_no_extra_bazel_dep(self, resolved: ResolvedDependencies, only_baselibs: Path):
        # score_baselibs is already declared above the block; re-declaring it would be a
        # duplicate declaration of the same module.
        patched = resolved.overwrite(only_baselibs, self._graph(), module_under_test="score_persistency", write=False)
        block = patched.split(INJECTION_BEGIN)[1].split(INJECTION_END)[0]
        assert "bazel_dep" not in block.split('module_name = "score_baselibs"')[0]
        assert patched.count('bazel_dep(name = "score_baselibs")') == 1

    def test_registry_dep_stub_repeats_the_resolved_version(self, resolved: ResolvedDependencies, tmp_path: Path):
        # score_tooling is registry-pinned (version 1.2.0). Its stub must carry that exact
        # version so it matches MVS and --check_direct_dependencies stays quiet; a
        # git-overridden module instead gets a bare bazel_dep with no version at all.
        mod = tmp_path / "MODULE.bazel"
        mod.write_text('module(name = "score_persistency", version = "0.0.0")\n')
        graph = DependencyGraph(
            _node("<root>", "", [_node("score_persistency", deps=[_node("score_tooling"), _node("score_logging")])])
        )
        block = (
            resolved.overwrite(mod, graph, module_under_test="score_persistency", write=False)
            .split(INJECTION_BEGIN)[1]
            .split(INJECTION_END)[0]
        )
        assert 'bazel_dep(name = "score_tooling", version = "1.2.0")' in block
        assert 'bazel_dep(name = "score_logging")\n' in block

    def test_graph_is_required(self, resolved: ResolvedDependencies, only_baselibs: Path):
        # Without a graph the closure cannot be computed, and pinning a module without the modules
        # it needs is what produced "module lobster@0.0.0 not found in registries". Unrepresentable
        # rather than merely discouraged.
        with pytest.raises(TypeError):
            resolved.overwrite(only_baselibs, module_under_test="score_persistency", write=False)

    def test_closure_member_absent_from_resolved_set_is_skipped(
        self, resolved: ResolvedDependencies, only_baselibs: Path, caplog: pytest.LogCaptureFixture
    ):
        # ref_int resolved nothing for it, so there is nothing to impose. Warn, never fail.
        graph = DependencyGraph(
            _node("<root>", "", [_node("score_persistency", deps=[_node("rules_doxygen")])]),
        )
        with caplog.at_level(logging.WARNING):
            patched = resolved.overwrite(only_baselibs, graph, module_under_test="score_persistency", write=False)
        assert "rules_doxygen" not in patched
        assert "rules_doxygen" in caplog.text

    def test_module_under_test_inferred_from_module_declaration(
        self, resolved: ResolvedDependencies, only_baselibs: Path
    ):
        # module(name = "...") identifies the root, so --module-under-test is optional.
        patched = resolved.overwrite(only_baselibs, self._graph(), write=False)
        assert 'module_name = "score_persistency"' not in patched
        assert 'module_name = "score_baselibs"' in patched


class TestScopeIsDecidedByTheResolvedSet:
    """Presence in the resolved set decides the pin scope. ``dev_dependency`` plays no part.

    The two properties are independent, measured on the real modules: ``score_baselibs`` at 0.2.9
    declares 13 dev-only deps ref_int *has* resolved, while ``score_baselibs_rust`` is a *public*
    dep of ``score_logging`` that ref_int has *not*. So the flag predicts neither case and cannot
    be the discriminator.
    """

    @pytest.fixture
    def dev_and_public(self, tmp_path: Path) -> Path:
        p = tmp_path / "MODULE.bazel"
        p.write_text(
            'module(name = "score_persistency", version = "0.0.0")\n'
            'bazel_dep(name = "score_baselibs", version = "0.2.7")\n'
            'bazel_dep(name = "score_tooling", version = "1.0.0", dev_dependency = True)\n'
        )
        return p

    @staticmethod
    def _graph_with_tooling_closure() -> DependencyGraph:
        # ref_int declares score_tooling publicly, so its closure is in the Stage-1 graph even
        # though the module-under-test's edge to it is dev-only and therefore absent.
        return DependencyGraph(
            _node(
                "<root>",
                "",
                [
                    _node("score_persistency", deps=[_node("score_baselibs")]),
                    _node("score_tooling", deps=[_node("trlc"), _node("lobster")]),
                ],
            )
        )

    def test_dev_declared_dep_is_pinned_because_ref_int_resolved_it(
        self, resolved: ResolvedDependencies, dev_and_public: Path
    ):
        # ref_int has a version for score_tooling, so it imposes it. How the module declares the
        # edge is irrelevant. Excluding these left 11 of score_baselibs' deps unvalidated.
        patched = resolved.overwrite(
            dev_and_public, self._graph_with_tooling_closure(), module_under_test="score_persistency", write=False
        )
        assert 'module_name = "score_tooling"' in patched

    def test_its_closure_is_pinned_with_it(self, resolved: ResolvedDependencies, dev_and_public: Path):
        # What makes the rule safe rather than merely permissive: score_tooling must never arrive
        # without the modules it needs, or the graph is unresolvable.
        with_closure = ResolvedDependencies(
            {
                **resolved.modules,
                "trlc": Module(name="trlc", hash="", repo="", version="2.0.0"),
                "lobster": Module(name="lobster", hash="", repo="", version="0.9.0"),
            }
        )
        patched = with_closure.overwrite(
            dev_and_public, self._graph_with_tooling_closure(), module_under_test="score_persistency", write=False
        )
        assert 'module_name = "trlc"' in patched
        assert 'module_name = "lobster"' in patched

    def test_public_dep_ref_int_did_not_resolve_is_left_alone(
        self, resolved: ResolvedDependencies, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ):
        # The case that disproves the flag as a discriminator: score_unpinned is declared with no
        # dev flag at all and still has no resolved entry, exactly like score_baselibs_rust in
        # score_communication. It must be reported and left untouched, not forced to anything.
        p = tmp_path / "MODULE.bazel"
        p.write_text(
            'module(name = "score_persistency", version = "0.0.0")\n'
            'bazel_dep(name = "score_unpinned", version = "9.9.9")\n'
        )
        graph = DependencyGraph(_node("<root>", "", [_node("score_persistency"), _node("score_unpinned")]))
        with caplog.at_level(logging.WARNING):
            patched = resolved.overwrite(p, graph, module_under_test="score_persistency", write=False)
        assert 'module_name = "score_unpinned"' not in patched
        assert "score_unpinned" in caplog.text

    def test_dev_declared_dep_ref_int_did_not_resolve_is_left_alone(
        self, resolved: ResolvedDependencies, tmp_path: Path
    ):
        # Same outcome as the public case above, reached by the same rule rather than by the flag.
        p = tmp_path / "MODULE.bazel"
        p.write_text(
            'module(name = "score_persistency", version = "0.0.0")\n'
            'bazel_dep(name = "score_unpinned", version = "9.9.9", dev_dependency = True)\n'
        )
        graph = DependencyGraph(_node("<root>", "", [_node("score_persistency"), _node("score_unpinned")]))
        patched = resolved.overwrite(p, graph, module_under_test="score_persistency", write=False)
        assert 'module_name = "score_unpinned"' not in patched

    def test_public_dep_is_still_pinned(self, resolved: ResolvedDependencies, dev_and_public: Path):
        # Widening scope must not disturb the public surface, or Stage 2 goes vacuously green.
        patched = resolved.overwrite(
            dev_and_public, self._graph_with_tooling_closure(), module_under_test="score_persistency", write=False
        )
        assert 'module_name = "score_baselibs"' in patched


class TestFromModGraph:
    @staticmethod
    def _graph() -> dict:
        # Mirrors 'bazel mod graph --output=json': an overridden module reports whatever version its
        # own MODULE.bazel declares, which is empty when it declares none -- never the version
        # ref_int meant to impose. All three values below are the ones ref_int's real graph reports.
        return {
            "key": "<root>",
            "name": "ref_int",
            "version": "",
            "dependencies": [
                {"name": "trlc", "version": "0.0.0"},  # git_override; trlc declares 0.0.0 itself
                {"name": "rules_boost", "version": ""},  # archive_override; declares no version
                {"name": "score_baselibs", "version": "0.2.9"},  # git_override; declares a real version
                {
                    "name": "protobuf",
                    "version": "29.1",
                    "dependencies": [
                        {"name": "abseil-cpp", "version": "20250512.1"},
                    ],
                },
            ],
        }

    def test_merges_overrides_and_registry_versions(self, tmp_path: Path):
        graph = tmp_path / "graph.json"
        graph.write_text(json.dumps(self._graph()))
        root = tmp_path / "MODULE.bazel"
        root.write_text(
            'git_override(\n    module_name = "trlc",\n    commit = "abc1234",\n'
            '    remote = "https://github.com/x/trlc.git",\n)\n'
            'archive_override(\n    module_name = "rules_boost",\n    urls = ["https://e/x.tar"],\n)\n'
        )
        scoremods = tmp_path / "score_modules_target_sw.MODULE.bazel"
        scoremods.write_text(
            'git_override(\n    module_name = "score_baselibs",\n    commit = "def5678",\n'
            '    remote = "https://github.com/eclipse-score/baselibs.git",\n)\n'
        )

        rd = ResolvedDependencies.from_mod_graph(graph, [root, scoremods])
        # Overridden modules carried as their real git_override; the graph's version is ignored.
        assert rd.get("trlc").hash == "abc1234"
        assert rd.get("score_baselibs").hash == "def5678"
        # Registry modules carried from the resolved graph version.
        assert rd.get("protobuf").version == "29.1"
        assert rd.get("abseil-cpp").version == "20250512.1"
        # An archive_override cannot be expressed as a manifest directive -> not carried.
        assert rd.get("rules_boost") is None

    def test_ignores_commented_out_overrides(self, tmp_path: Path):
        graph = tmp_path / "graph.json"
        graph.write_text(json.dumps({"key": "<root>", "name": "r", "version": "", "dependencies": []}))
        root = tmp_path / "MODULE.bazel"
        root.write_text(
            '# git_override(\n#     module_name = "rules_rpm",\n'
            '#     commit = "a78e559cf81754c199c926229dc6b4443e1ff149",\n'
            '#     remote = "https://github.com/eclipse-score/inc_os_autosd.git",\n# )\n'
        )
        rd = ResolvedDependencies.from_mod_graph(graph, [root])
        assert rd.get("rules_rpm") is None  # commented-out override must not be carried


class TestModuleResolutionHazards:
    """Ways a module resolves a dependency that ref_int's injected pins cannot reach."""

    def test_module_declared_override_is_reported(self):
        text = 'git_override(\n    module_name = "score_baselibs",\n    commit = "abc1234",\n)\n'
        assert module_resolution_hazards(text) == ["git_override for score_baselibs"]

    def test_an_overrides_patches_are_counted(self):
        text = (
            'single_version_override(\n    module_name = "rules_cc",\n    version = "1.0",\n'
            '    patches = ["//p:a.patch", "//p:b.patch"],\n)\n'
        )
        assert module_resolution_hazards(text) == ["single_version_override for rules_cc with 2 patch(es)"]

    @pytest.mark.parametrize(
        "rule", ["http_archive", "http_file", "git_repository", "new_git_repository", "local_repository"]
    )
    def test_non_bzlmod_fetches_are_reported(self, rule: str):
        text = f'{rule}(\n    name = "foo",\n)\n'
        assert module_resolution_hazards(text) == [f"{rule} (fetched outside bzlmod; no override applies)"]

    def test_commented_out_declarations_are_ignored(self):
        text = '# git_override(\n#     module_name = "rules_rpm",\n# )\n# http_archive(\n#     name = "x",\n# )\n'
        assert module_resolution_hazards(text) == []

    def test_a_plain_module_reports_nothing(self):
        assert module_resolution_hazards(MODULE_BAZEL) == []


class TestPatchesTravelWithThePin:
    """A dependency ref_int patches in Stage 1 must be patched in Stage 2 too, or reported."""

    @staticmethod
    def _graph(tmp_path: Path) -> Path:
        graph = tmp_path / "graph.json"
        graph.write_text(json.dumps({"key": "<root>", "name": "ref_int", "version": "", "dependencies": []}))
        return graph

    def test_git_override_patches_are_collected(self, tmp_path: Path):
        root = tmp_path / "MODULE.bazel"
        root.write_text(
            'git_override(\n    module_name = "score_logging",\n    commit = "abc1234",\n'
            "    patch_strip = 1,\n"
            '    patches = [\n        "//patches/logging:002-a.patch",\n        "//patches/logging:003-b.patch",\n    ],\n'
            '    remote = "https://github.com/eclipse-score/logging.git",\n)\n'
        )
        rd = ResolvedDependencies.from_mod_graph(self._graph(tmp_path), [root])
        assert rd.get("score_logging").bazel_patches == [
            "//patches/logging:002-a.patch",
            "//patches/logging:003-b.patch",
        ]

    def test_single_version_override_patches_are_collected(self, tmp_path: Path):
        root = tmp_path / "MODULE.bazel"
        root.write_text(
            'single_version_override(\n    module_name = "rules_cc",\n    version = "0.2.17",\n'
            '    patch_strip = 1,\n    patches = ["//patches/rules_cc:001.patch"],\n)\n'
        )
        rd = ResolvedDependencies.from_mod_graph(self._graph(tmp_path), [root])
        assert rd.get("rules_cc").bazel_patches == ["//patches/rules_cc:001.patch"]

    def test_an_override_without_patches_carries_none(self, tmp_path: Path):
        root = tmp_path / "MODULE.bazel"
        root.write_text('single_version_override(\n    module_name = "rules_cc",\n    version = "0.2.17",\n)\n')
        rd = ResolvedDependencies.from_mod_graph(self._graph(tmp_path), [root])
        assert not rd.get("rules_cc").bazel_patches

    def test_export_patches_copies_the_files_workspace_relative(self, tmp_path: Path):
        ref_int = tmp_path / "ref_int"
        (ref_int / "patches" / "logging").mkdir(parents=True)
        (ref_int / "patches" / "logging" / "002-a.patch").write_text("payload\n")
        rd = ResolvedDependencies(
            {
                "score_logging": Module.from_dict(
                    "score_logging",
                    {
                        "repo": "https://github.com/eclipse-score/logging.git",
                        "hash": "a" * 40,
                        "bazel_patches": ["//patches/logging:002-a.patch"],
                    },
                )
            }
        )

        copied = rd.export_patches(tmp_path / "artifact" / "patches", ref_int)

        assert copied == ["patches/logging/002-a.patch"]
        assert (tmp_path / "artifact" / "patches" / "patches" / "logging" / "002-a.patch").read_text() == "payload\n"

    def test_export_patches_survives_a_missing_file(self, tmp_path: Path):
        rd = ResolvedDependencies(
            {
                "score_logging": Module.from_dict(
                    "score_logging",
                    {"repo": "https://e/x.git", "hash": "a" * 40, "bazel_patches": ["//patches/logging:gone.patch"]},
                )
            }
        )
        assert rd.export_patches(tmp_path / "out", tmp_path / "ref_int") == []


class TestUncarriedOverridesAreNeverSilent:
    """Every override ref_int declares reaches the manifest, or is named in the report.

    A silently dropped override is ref_int's authority quietly failing: the pin looks present in its
    MODULE.bazel while every module resolves its own version. ``rules_oci`` was exactly that, and
    logged nothing at all. The guard is a set difference over every override kind.
    """

    @staticmethod
    def _graph(*names: str) -> dict:
        # Overridden modules report an empty version, so the override file is the only source.
        return {
            "key": "<root>",
            "name": "ref_int",
            "version": "",
            "dependencies": [{"name": n, "version": ""} for n in names],
        }

    def _export(self, tmp_path: Path, override_text: str, *graph_names: str) -> ResolvedDependencies:
        graph = tmp_path / "graph.json"
        graph.write_text(json.dumps(self._graph(*graph_names)))
        root = tmp_path / "MODULE.bazel"
        root.write_text(override_text)
        return ResolvedDependencies.from_mod_graph(graph, [root])

    @staticmethod
    def _uncarried(rd: ResolvedDependencies) -> dict[str, dict]:
        return {entry["module"]: entry for entry in rd.report["uncarried"]}

    def test_git_override_with_tag_and_no_commit_is_reported(self, tmp_path: Path):
        # The real rules_oci shape: a mutable ref cannot be carried, but must not vanish silently.
        rd = self._export(
            tmp_path,
            'git_override(\n    module_name = "rules_oci",\n'
            '    remote = "https://github.com/bazel-contrib/rules_oci.git",\n    tag = "v2.3.1",\n)\n',
            "rules_oci",
        )
        assert rd.get("rules_oci") is None
        entry = self._uncarried(rd)["rules_oci"]
        assert entry["kind"] == "git_override"
        assert "v2.3.1" in entry["reason"]
        assert "commit" in entry["reason"]

    def test_archive_override_is_reported_with_its_kind(self, tmp_path: Path):
        rd = self._export(
            tmp_path,
            'archive_override(\n    module_name = "rules_boost",\n    urls = ["https://e/master.tar.gz"],\n)\n',
            "rules_boost",
        )
        assert rd.get("rules_boost") is None
        assert self._uncarried(rd)["rules_boost"]["kind"] == "archive_override"

    def test_local_path_override_is_reported(self, tmp_path: Path):
        # A third kind, so the guard is kind-agnostic rather than a list of known-bad cases.
        rd = self._export(
            tmp_path,
            'local_path_override(\n    module_name = "some_dep",\n    path = "../some_dep",\n)\n',
            "some_dep",
        )
        assert self._uncarried(rd)["some_dep"]["kind"] == "local_path_override"

    def test_single_version_override_without_a_version_is_reported(self, tmp_path: Path):
        rd = self._export(
            tmp_path,
            'single_version_override(\n    module_name = "googletest",\n    patch_strip = 1,\n)\n',
            "googletest",
        )
        assert rd.get("googletest") is None
        assert "version" in self._uncarried(rd)["googletest"]["reason"]

    def test_commented_out_override_is_not_reported_as_uncarried(self, tmp_path: Path):
        # A commented-out override is not a pin ref_int is making: neither manifest nor report.
        rd = self._export(
            tmp_path,
            '# git_override(\n#     module_name = "rules_rpm",\n#     tag = "v1",\n# )\n',
        )
        assert rd.get("rules_rpm") is None
        assert "rules_rpm" not in self._uncarried(rd)

    def test_a_carried_override_is_not_reported(self, tmp_path: Path):
        rd = self._export(
            tmp_path,
            'git_override(\n    module_name = "trlc",\n    commit = "abc1234",\n'
            '    remote = "https://github.com/x/trlc.git",\n)\n',
            "trlc",
        )
        assert rd.get("trlc").hash == "abc1234"
        assert self._uncarried(rd) == {}

    def test_every_declared_override_is_pinned_or_uncarried(self, tmp_path: Path):
        # The completeness invariant as a set identity, rather than a claim in a comment.
        rd = self._export(
            tmp_path,
            'git_override(\n    module_name = "trlc",\n    commit = "abc1234",\n'
            '    remote = "https://github.com/x/trlc.git",\n)\n'
            'git_override(\n    module_name = "rules_oci",\n    remote = "https://e/o.git",\n'
            '    tag = "v2.3.1",\n)\n'
            'archive_override(\n    module_name = "rules_boost",\n    urls = ["https://e/x.tar"],\n)\n',
            "trlc",
            "rules_oci",
            "rules_boost",
        )
        declared = {"trlc", "rules_oci", "rules_boost"}
        assert declared - rd.names == set(self._uncarried(rd))
        assert declared & rd.names == {"trlc"}


class TestPinProvenance:
    """Which pins ref_int decided, and which it merely inherited from MVS.

    Both are imposed equally, so the manifest cannot tell them apart, though fixing a bad pin needs
    to know which it is. The yq.bzl pin that breaks score_communication is incidental: nothing in
    ref_int declares yq.bzl, so nobody ever chose 0.1.1.
    """

    @staticmethod
    def _graph() -> dict:
        return {
            "key": "<root>",
            "name": "ref_int",
            "version": "",
            "dependencies": [
                {"name": "trlc", "version": ""},
                {"name": "protobuf", "version": "29.1"},
                {"name": "googletest", "version": "1.17.0.bcr.2"},
            ],
        }

    def _report(self, tmp_path: Path, override_text: str) -> dict:
        graph = tmp_path / "graph.json"
        graph.write_text(json.dumps(self._graph()))
        root = tmp_path / "MODULE.bazel"
        root.write_text(override_text)
        return ResolvedDependencies.from_mod_graph(graph, [root]).report

    def test_override_declared_by_ref_int_is_asserted(self, tmp_path: Path):
        report = self._report(
            tmp_path,
            'git_override(\n    module_name = "trlc",\n    commit = "abc1234",\n'
            '    remote = "https://github.com/x/trlc.git",\n)\n',
        )
        assert report["pins"]["trlc"]["provenance"] == "asserted"

    def test_registry_version_only_from_the_graph_is_incidental(self, tmp_path: Path):
        report = self._report(tmp_path, "")
        assert report["pins"]["protobuf"]["provenance"] == "incidental"

    def test_bare_single_version_override_promotes_a_graph_pin_to_asserted(self, tmp_path: Path):
        # The score_test_artifact_versions shape: a bare override for a module already in the graph
        # at that version. A no-op for manifest content, so provenance is what shows it doing anything.
        report = self._report(
            tmp_path,
            'single_version_override(\n    module_name = "googletest",\n    version = "1.17.0.bcr.2",\n)\n',
        )
        assert report["pins"]["googletest"]["provenance"] == "asserted"
        assert report["pins"]["googletest"]["pin"] == {"version": "1.17.0.bcr.2"}

    def test_counts_split_the_set(self, tmp_path: Path):
        report = self._report(
            tmp_path,
            'git_override(\n    module_name = "trlc",\n    commit = "abc1234",\n'
            '    remote = "https://github.com/x/trlc.git",\n)\n',
        )
        counts = report["counts"]
        assert counts["asserted"] + counts["incidental"] == counts["pinned"]
        assert counts["asserted"] == 1


class TestVersionComparison:
    """Version ordering, because a lexical compare silently inverts the whole report.

    ``"0.0.10" < "0.0.6"`` holds for strings, and score_crates is exactly that pair -- so a naive
    compare would report ref_int as ahead of its consumers on the case that matters most.
    """

    def test_numeric_identifiers_compare_numerically_not_lexically(self):
        assert _compare_versions("0.0.10", "0.0.6") == 1
        assert _compare_versions("0.0.6", "0.0.10") == -1

    @pytest.mark.parametrize(
        ("higher", "lower"),
        [
            ("0.4.0", "0.2.0"),  # score_itf
            ("0.9.1", "0.8.0"),  # score_toolchains_rust
            ("0.0.3", "0.0.1"),  # score_rules_imagefs
            ("0.3.1", "0.1.1"),  # yq.bzl
            ("0.68.2-score", "0.68.1-score"),  # rules_rust, prerelease suffix on both sides
            ("1.3.1.bcr.8", "1.3.1.bcr.5"),  # zlib, four-identifier registry version
            ("0.1.1", "0.1"),  # a longer numeric identifier list outranks a shorter one
        ],
    )
    def test_real_manifest_versions(self, higher: str, lower: str):
        assert _compare_versions(higher, lower) == 1
        assert _compare_versions(lower, higher) == -1

    def test_equal_versions_compare_equal(self):
        assert _compare_versions("1.17.0.bcr.2", "1.17.0.bcr.2") == 0

    def test_a_longer_release_list_outranks_its_prefix(self):
        # Bazel compares release identifiers lexicographically, so the shorter list sorts lower --
        # a BCR re-release of 1.17.0 is above it. This is ref_int's own googletest pin.
        assert _compare_versions("1.17.0.bcr.2", "1.17.0") == 1
        assert _compare_versions("1.17.0", "1.17.0.bcr.2") == -1

    def test_alphanumeric_identifiers_compare_lexicographically(self):
        # Bazel's ordering is total: two differing alphanumeric identifiers still have an order.
        assert _compare_versions("1.0.alpha", "1.0.beta") == -1
        assert _compare_versions("1.0.beta", "1.0.alpha") == 1

    def test_numeric_identifiers_sort_below_alphanumeric_ones(self):
        assert _compare_versions("1.0.2", "1.0.rc") == -1

    def test_prerelease_sorts_below_the_same_release(self):
        assert _compare_versions("0.51.0", "0.51.0-rc2") == 1

    def test_prerelease_identifiers_are_dot_split(self):
        # Compared identifier-wise like the release part, not as one opaque string -- otherwise
        # "rc.10" would sort below "rc.9".
        assert _compare_versions("1.0.0-rc.10", "1.0.0-rc.9") == 1

    def test_build_metadata_does_not_affect_ordering(self):
        assert _compare_versions("1.0.0+build1", "1.0.0+build2") == 0


class TestConflictReportDoesNotAbort:
    """ref_int's version is imposed, the disagreement is reported, and the export never aborts.

    Never raised to the consumer's version, never fallen back to. All that changes is visibility: an
    override suppresses Bazel's own --check_direct_dependencies warning, so before this report all
    five measured downgrades produced no output at all.
    """

    @staticmethod
    def _graph(name: str, resolved_version: str, *declared: str) -> dict:
        # --verbose records the version a dependent asked for whenever MVS moved the module off it.
        return {
            "key": "<root>",
            "name": "ref_int",
            "version": "",
            "dependencies": [{"name": name, "version": resolved_version, "originalVersion": d} for d in declared]
            or [{"name": name, "version": resolved_version}],
        }

    def _export(self, tmp_path: Path, graph: dict, override_text: str = "") -> ResolvedDependencies:
        graph_file = tmp_path / "graph.json"
        graph_file.write_text(json.dumps(graph))
        root = tmp_path / "MODULE.bazel"
        root.write_text(override_text)
        return ResolvedDependencies.from_mod_graph(graph_file, [root])

    def test_a_downgrade_is_reported_and_the_export_still_writes_the_manifest(self, tmp_path: Path):
        rd = self._export(tmp_path, self._graph("score_rules_imagefs", "0.0.1", "0.0.3"))
        pin = rd.report["pins"]["score_rules_imagefs"]
        assert pin["verdict"] == "differs"
        assert pin["direction"] == "ref_int_lower"
        assert pin["declared_versions"] == ["0.0.3"]
        # ref_int's version is imposed, not raised to the consumer's.
        assert rd.get("score_rules_imagefs").version == "0.0.1"
        manifest = tmp_path / "resolved_versions.json"
        rd.to_file(manifest)
        assert json.loads(manifest.read_text())["modules"]["score_rules_imagefs"] == {"version": "0.0.1"}

    def test_an_upgrade_is_reported_as_the_other_direction(self, tmp_path: Path):
        rd = self._export(tmp_path, self._graph("stardoc", "0.7.2", "0.7.1"))
        assert rd.report["pins"]["stardoc"]["direction"] == "ref_int_higher"

    def test_agreement_is_not_a_conflict(self, tmp_path: Path):
        rd = self._export(tmp_path, self._graph("protobuf", "29.1", "29.1"))
        assert rd.report["pins"]["protobuf"]["verdict"] == "agree"
        assert rd.report["counts"]["differs"] == 0

    def test_commit_pin_reports_the_conflict_with_null_direction(self, tmp_path: Path):
        # The score_crates shape: no comparable version, but the disagreement must stay visible --
        # otherwise the obvious "fix" is dropping commit pins from the report and losing 18 of them.
        rd = self._export(
            tmp_path,
            self._graph("score_crates", "0.0.6", "0.0.10", "0.0.9"),
            'git_override(\n    module_name = "score_crates",\n    commit = "a5f4f57",\n'
            '    remote = "https://github.com/eclipse-score/score-crates.git",\n)\n',
        )
        pin = rd.report["pins"]["score_crates"]
        assert pin["verdict"] == "differs"
        assert pin["direction"] is None
        assert pin["declared_versions"] == ["0.0.10", "0.0.9"]
        assert rd.report["counts"]["differs"] == 1

    def test_a_bcr_rerelease_is_reported_as_higher(self, tmp_path: Path):
        # ref_int's real googletest pin. Bazel orders 1.17.0.bcr.2 above 1.17.0, so the direction
        # is knowable and must be stated -- reporting "unknown" here would be misinformation.
        rd = self._export(tmp_path, self._graph("googletest", "1.17.0.bcr.2", "1.17.0"))
        pin = rd.report["pins"]["googletest"]
        assert pin["verdict"] == "differs"
        assert pin["direction"] == "ref_int_higher"

    def test_a_dev_declared_conflict_is_not_claimed_to_be_detected(self, tmp_path: Path):
        # A non-root dev edge leaves no originalVersion, so an empty declared_versions must not
        # read as "nobody disagrees".
        rd = self._export(tmp_path, self._graph("score_toolchains_rust", "0.8.0"))
        assert rd.report["pins"]["score_toolchains_rust"]["verdict"] == "unknown"
        assert any("dev_dependency" in limitation for limitation in rd.report["limitations"])

    def test_graph_without_verbose_says_so(self, tmp_path: Path):
        # No requests at all must not read as universal agreement.
        rd = self._export(tmp_path, self._graph("protobuf", "29.1"))
        assert any("originalVersion" in limitation for limitation in rd.report["limitations"])

    def test_a_non_verbose_graph_is_announced_not_just_recorded(self, tmp_path: Path, capsys):
        # The conflict half of the report is a constant without originalVersion -- every verdict
        # "unknown", no disagreement detectable, which reads exactly like a graph nobody disagrees
        # in. A limitations entry alone is invisible in a CI log, so it must be annotated too.
        self._export(tmp_path, self._graph("protobuf", "29.1"))
        assert "::warning::" in capsys.readouterr().out

    def test_a_verbose_graph_is_not_announced(self, tmp_path: Path, capsys):
        self._export(tmp_path, self._graph("protobuf", "29.1", "28.0"))
        assert "originalVersion" not in capsys.readouterr().out

    def test_verbose_graph_drops_the_no_requests_caveat(self, tmp_path: Path):
        rd = self._export(tmp_path, self._graph("protobuf", "29.1", "28.0"))
        assert not any("originalVersion" in limitation for limitation in rd.report["limitations"])
        # The structural caveats describe what Bazel loads, not this run, so they always apply.
        assert any("dev_dependency" in limitation for limitation in rd.report["limitations"])


class TestInternalDrift:
    """ref_int disagreeing with itself: a declared bazel_dep version it does not actually impose.

    The declaration reads like a decision but is only a floor, so the version in review is not the
    one Stage 2 imposes. Five are live today.
    """

    def test_declared_floor_below_the_resolved_version_is_reported(self, tmp_path: Path):
        graph = tmp_path / "graph.json"
        graph.write_text(
            json.dumps(
                {
                    "key": "<root>",
                    "name": "ref_int",
                    "version": "",
                    "dependencies": [{"name": "rules_cc", "version": "0.2.17"}],
                }
            )
        )
        root = tmp_path / "MODULE.bazel"
        root.write_text('bazel_dep(name = "rules_cc", version = "0.2.16")\n')
        report = ResolvedDependencies.from_mod_graph(graph, [root]).report
        assert report["ref_int_internal_drift"] == [
            {
                "module": "rules_cc",
                "declared": "0.2.16",
                "resolved": "0.2.17",
                "file": "MODULE.bazel",
                "dev_dependency": False,
            }
        ]

    def test_dev_scoped_declaration_is_recorded_as_such(self, tmp_path: Path):
        graph = tmp_path / "graph.json"
        graph.write_text(
            json.dumps(
                {
                    "key": "<root>",
                    "name": "ref_int",
                    "version": "",
                    "dependencies": [{"name": "score_toolchains_rust", "version": "0.9.1"}],
                }
            )
        )
        root = tmp_path / "MODULE.bazel"
        root.write_text('bazel_dep(name = "score_toolchains_rust", version = "0.8.0", dev_dependency = True)\n')
        drift = ResolvedDependencies.from_mod_graph(graph, [root]).report["ref_int_internal_drift"]
        assert drift[0]["dev_dependency"] is True

    def test_declaration_matching_the_resolved_version_is_not_drift(self, tmp_path: Path):
        graph = tmp_path / "graph.json"
        graph.write_text(
            json.dumps(
                {
                    "key": "<root>",
                    "name": "ref_int",
                    "version": "",
                    "dependencies": [{"name": "rules_pkg", "version": "1.2.0"}],
                }
            )
        )
        root = tmp_path / "MODULE.bazel"
        root.write_text('bazel_dep(name = "rules_pkg", version = "1.2.0")\n')
        report = ResolvedDependencies.from_mod_graph(graph, [root]).report
        assert report["ref_int_internal_drift"] == []


class TestDeclaredDepSpecs:
    def test_captures_version_and_dev_flag(self):
        # Real score_communication declarations, including a repo_name after the version.
        text = (
            'bazel_dep(name = "score_crates", version = "0.0.10", repo_name = "score_communication_crate_index")\n'
            'bazel_dep(name = "score_itf", version = "0.4.0", dev_dependency = True)\n'
            'bazel_dep(name = "score_toolchains_rust", version = "0.9.1", dev_dependency = True)\n'
        )
        specs = _declared_dep_specs(text)
        assert specs["score_crates"] == {"version": "0.0.10", "dev_dependency": False}
        assert specs["score_itf"] == {"version": "0.4.0", "dev_dependency": True}
        assert specs["score_toolchains_rust"]["dev_dependency"] is True

    def test_dep_without_version_is_captured_with_none(self):
        # The non-registry idiom: the override supplies the source, so no version is declared.
        assert _declared_dep_specs('bazel_dep(name = "score_tooling")\n') == {
            "score_tooling": {"version": None, "dev_dependency": False}
        }

    def test_declared_deps_set_is_unchanged(self):
        # The narrower contract overwrite() depends on: names only, dev-declared included.
        text = (
            'bazel_dep(name = "score_crates", version = "0.0.10")\n'
            'bazel_dep(name = "score_itf", version = "0.4.0", dev_dependency = True)\n'
        )
        assert _declared_deps(text) == {"score_crates", "score_itf"}


class TestManifestRoundtrip:
    def test_to_file_is_lean_and_roundtrips(self, tmp_path: Path, resolved: ResolvedDependencies):
        manifest = tmp_path / "resolved_versions.json"
        resolved.to_file(manifest)
        data = json.loads(manifest.read_text())["modules"]
        assert "metadata" not in data["score_baselibs"]  # lean: no test-config noise
        assert data["score_tooling"] == {"version": "1.2.0"}
        loaded = ResolvedDependencies.from_file(manifest)
        assert loaded.get("score_baselibs").hash == resolved.get("score_baselibs").hash
        assert loaded.get("score_tooling").version == "1.2.0"

    def test_report_is_a_sidecar_and_the_manifest_schema_is_unchanged(self, tmp_path: Path):
        # The manifest is the Stage1->Stage2 contract, so new fields go in the sidecar instead.
        graph = tmp_path / "graph.json"
        graph.write_text(
            json.dumps(
                {
                    "key": "<root>",
                    "name": "ref_int",
                    "version": "",
                    "dependencies": [
                        {"name": "protobuf", "version": "29.1", "originalVersion": "28.0"},
                        {"name": "trlc", "version": ""},
                    ],
                }
            )
        )
        root = tmp_path / "MODULE.bazel"
        root.write_text(
            'git_override(\n    module_name = "trlc",\n    commit = "abc1234",\n'
            '    remote = "https://github.com/x/trlc.git",\n)\n'
        )
        rd = ResolvedDependencies.from_mod_graph(graph, [root])

        manifest = tmp_path / MANIFEST_NAME
        rd.to_file(manifest)
        modules = json.loads(manifest.read_text())["modules"]
        # Exactly the two legal shapes; nothing leaks in from the report.
        assert modules == {
            "protobuf": {"version": "29.1"},
            "trlc": {"repo": "https://github.com/x/trlc.git", "hash": "abc1234"},
        }
        assert ResolvedDependencies.from_file(manifest).get("trlc").hash == "abc1234"

        report = tmp_path / REPORT_NAME
        rd.write_report(report)
        parsed = json.loads(report.read_text())
        assert parsed["schema"] == 1
        assert parsed["pins"]["protobuf"]["declared_versions"] == ["28.0"]

    def test_a_manifest_read_back_carries_no_report(self, tmp_path: Path, resolved: ResolvedDependencies):
        # The pins survive a round trip; the evidence behind them is not faked.
        manifest = tmp_path / MANIFEST_NAME
        resolved.to_file(manifest)
        assert ResolvedDependencies.from_file(manifest).report["pins"] == {}


class TestFromResolvedArtifact:
    def test_reads_the_manifest(self, tmp_path: Path, resolved: ResolvedDependencies):
        art = tmp_path / "art"
        art.mkdir()
        resolved.to_file(art / "resolved_versions.json")
        parsed = ResolvedDependencies.from_resolved_artifact(art)
        assert parsed.get("score_baselibs").hash == resolved.get("score_baselibs").hash
        assert parsed.get("score_tooling").version == "1.2.0"

    def test_missing_manifest_is_fatal(self, tmp_path: Path):
        # A silently empty resolved set would make Stage 2 pass while validating nothing. The lock
        # and the generated score_modules_*.MODULE.bazel files are not substitutes.
        (tmp_path / "MODULE.bazel.lock").write_text("{}")
        (tmp_path / "score_modules_target_sw.MODULE.bazel").write_text("bazel_dep(name='x')\n")
        with pytest.raises(FileNotFoundError, match=MANIFEST_NAME):
            ResolvedDependencies.from_resolved_artifact(tmp_path)


class TestWorkspacePath:
    """bazel run's cwd is the runfiles tree, so relative CLI paths must anchor at repo_root."""

    def test_relative_path_is_anchored_at_the_workspace(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("BUILD_WORKSPACE_DIRECTORY", str(tmp_path))
        assert workspace_path(Path("_resolved_deps") / MANIFEST_NAME) == tmp_path / "_resolved_deps" / MANIFEST_NAME

    def test_absolute_path_is_taken_as_given(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("BUILD_WORKSPACE_DIRECTORY", str(tmp_path / "workspace"))
        absolute = tmp_path / "elsewhere" / "graph.json"
        assert workspace_path(absolute) == absolute
