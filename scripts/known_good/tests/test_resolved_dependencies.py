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
import sys
from pathlib import Path

import pytest

# Make scripts/ importable so known_good.* package resolves when run via plain pytest.
_SCRIPTS_DIR = Path(__file__).resolve().parents[2]
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from known_good.resolved_dependencies import (  # noqa: E402
    INJECTION_BEGIN,
    INJECTION_END,
    ResolvedDependencies,
    generate_override_directive,
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


class TestFromKnownGood:
    def test_names_span_all_groups(self, resolved: ResolvedDependencies):
        assert {"score_baselibs", "score_logging", "score_persistency", "score_tooling"} <= resolved.names

    def test_get_returns_resolved_commit(self, resolved: ResolvedDependencies):
        assert resolved.get("score_baselibs").hash.startswith("cab36dd7de92")

    def test_version_module_kept(self, resolved: ResolvedDependencies):
        assert resolved.get("score_tooling").version == "1.2.0"


class TestScan:
    def test_returns_declared_deps(self, resolved: ResolvedDependencies, module_bazel: Path):
        declared = resolved.scan(module_bazel)
        assert "score_baselibs" in declared
        assert "score_unpinned" in declared
        assert "rules_cc" in declared


class TestOverwrite:
    def test_pins_declared_resolved_siblings(self, resolved: ResolvedDependencies, module_bazel: Path):
        patched = resolved.overwrite(module_bazel, module_under_test="score_persistency", write=False)
        block = patched.split(INJECTION_BEGIN)[1].split(INJECTION_END)[0]
        assert 'git_override(\n    module_name = "score_baselibs"' in block
        assert 'commit = "cab36dd7de92aaaaaaaaaaaaaaaaaaaaaaaaaaaa"' in block
        # version module -> single_version_override
        assert 'single_version_override(\n    module_name = "score_tooling"' in block
        assert 'version = "1.2.0"' in block

    def test_strips_patches(self, resolved: ResolvedDependencies, module_bazel: Path):
        # bazel_patches reference //patches/... labels that exist only in ref_int's
        # workspace, so they are stripped from the injected overrides.
        patched = resolved.overwrite(module_bazel, module_under_test="score_persistency", write=False)
        assert "patches/baselibs/001-fix.patch" not in patched
        assert "patch_strip" not in patched

    def test_skips_resolved_dep_not_declared(self, resolved: ResolvedDependencies, tmp_path: Path):
        # Only declared deps are injected. Overriding a module that is NOT in the module's
        # dependency graph makes Bazel fail ("overrides on nonexistent module(s)"), so a
        # resolved dep the module does not declare must NOT be injected.
        mod = tmp_path / "MODULE.bazel"
        mod.write_text(
            'module(name = "score_persistency", version = "0.0.0")\n'
            'bazel_dep(name = "score_baselibs", version = "0.1")\n'
        )
        block = resolved.overwrite(mod, module_under_test="score_persistency", write=False).split(INJECTION_BEGIN)[1]
        assert 'module_name = "score_baselibs"' in block  # declared -> injected
        assert 'module_name = "score_logging"' not in block  # not declared -> not injected

    def test_skips_root_module(self, resolved: ResolvedDependencies, module_bazel: Path):
        patched = resolved.overwrite(module_bazel, module_under_test="score_persistency", write=False)
        block = patched.split(INJECTION_BEGIN)[1].split(INJECTION_END)[0]
        assert 'module_name = "score_persistency"' not in block

    def test_skips_unpinned_third_party(self, resolved: ResolvedDependencies, module_bazel: Path):
        patched = resolved.overwrite(module_bazel, module_under_test="score_persistency", write=False)
        block = patched.split(INJECTION_BEGIN)[1].split(INJECTION_END)[0]
        assert "score_unpinned" not in block
        assert "rules_cc" not in block

    def test_idempotent(self, resolved: ResolvedDependencies, module_bazel: Path):
        first = resolved.overwrite(module_bazel, module_under_test="score_persistency", write=True)
        second = resolved.overwrite(module_bazel, module_under_test="score_persistency", write=True)
        assert first == second
        assert second.count(INJECTION_BEGIN) == 1

    def test_overwrites_dep_with_existing_override(self, resolved: ResolvedDependencies, tmp_path: Path):
        # ref_int always decides the version — a pre-existing override in the module is replaced.
        mod = tmp_path / "MODULE.bazel"
        mod.write_text(
            MODULE_BAZEL + '\ngit_override(\n    module_name = "score_logging",\n    commit = "deadbeef",\n'
            '    remote = "https://example.com/x.git",\n)\n'
        )
        patched = resolved.overwrite(mod, module_under_test="score_persistency", write=False)
        block = patched.split(INJECTION_BEGIN)[1].split(INJECTION_END)[0]
        # ref_int's resolved commit must appear in the injection block, overwriting "deadbeef"
        assert 'module_name = "score_logging"' in block
        assert "deadbeef" not in block


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
    def test_prefers_manifest(self, tmp_path: Path, resolved: ResolvedDependencies):
        art = tmp_path / "art"
        art.mkdir()
        resolved.to_file(art / "resolved_versions.json")
        # With the manifest present, no lock / score_modules files are required.
        parsed = ResolvedDependencies.from_resolved_artifact(art)
        assert parsed.get("score_baselibs").hash == resolved.get("score_baselibs").hash
        assert parsed.get("score_tooling").version == "1.2.0"

    def test_requires_manifest_or_lockfile(self, tmp_path: Path):
        (tmp_path / "score_modules_target_sw.MODULE.bazel").write_text("bazel_dep(name='x')\n")
        with pytest.raises(FileNotFoundError):
            ResolvedDependencies.from_resolved_artifact(tmp_path)

    def test_roundtrip_known_good_to_artifact(self, tmp_path: Path, resolved: ResolvedDependencies):
        # Build an artifact dir mirroring stage1-resolved-deps (legacy format), then parse it back.
        art = tmp_path / "art"
        art.mkdir()
        (art / "MODULE.bazel.lock").write_text("{}")
        blocks = []
        for m in resolved.modules.values():
            directive = generate_override_directive(m)
            if directive:
                blocks.append(f'bazel_dep(name = "{m.name}")\n' + directive)
        (art / "score_modules_target_sw.MODULE.bazel").write_text("\n".join(blocks))

        parsed = ResolvedDependencies.from_resolved_artifact(art)
        assert parsed.get("score_baselibs").hash == resolved.get("score_baselibs").hash
        assert parsed.get("score_tooling").version == "1.2.0"
