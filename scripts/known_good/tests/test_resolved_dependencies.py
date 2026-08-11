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
    DependencyGraph,
    ResolvedDependencies,
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

    def test_strips_patches(self, resolved: ResolvedDependencies, module_bazel: Path, flat_graph: DependencyGraph):
        # bazel_patches reference //patches/... labels that exist only in ref_int's
        # workspace, so they are stripped from the injected overrides.
        patched = resolved.overwrite(module_bazel, flat_graph, module_under_test="score_persistency", write=False)
        assert "patches/baselibs/001-fix.patch" not in patched
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

    The two properties are independent, measured on the real modules: ``score_baselibs`` declares
    11 dev-only deps ref_int *has* resolved, while ``score_baselibs_rust`` is a *public* dep of
    ``score_communication`` that ref_int has *not*. So the flag predicts neither case and cannot
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
        # Mirrors 'bazel mod graph --output=json': overridden modules report version 0.0.0.
        return {
            "key": "<root>",
            "name": "ref_int",
            "version": "",
            "dependencies": [
                {"name": "trlc", "version": "0.0.0"},  # git_override (carried from file)
                {"name": "rules_boost", "version": "0.0.0"},  # archive_override (not representable)
                {"name": "score_baselibs", "version": "0.0.0"},  # git_override (carried from file)
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
        # Overridden modules carried as their real git_override (graph's 0.0.0 ignored).
        assert rd.get("trlc").hash == "abc1234"
        assert rd.get("score_baselibs").hash == "def5678"
        # Registry modules carried from the resolved graph version.
        assert rd.get("protobuf").version == "29.1"
        assert rd.get("abseil-cpp").version == "20250512.1"
        # archive_override target at 0.0.0 is not representable -> not carried.
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
