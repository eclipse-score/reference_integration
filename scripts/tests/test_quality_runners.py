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
"""Tests for the Stage-2 decision logic in quality_runners.py.

Scoped to the functions that take data rather than a Bazel server. Anything that shells out
(run_resolution_gate, capture_module_graph, the coverage extractors) needs a real module checkout
and is exercised by the Stage-2 job itself.
"""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import quality_runners  # noqa: E402
from known_good.models.module import Metadata, Module  # noqa: E402
from known_good.resolved_dependencies import DependencyGraph  # noqa: E402
from quality_runners import (  # noqa: E402
    STAGE2_BASE_CONFIG,
    classify_gate_failure,
    selection_digest,
    stage2_config_flags,
    stage2_gate_command,
    stage2_module_command,
    stage2_target_args,
    unpatched_dependencies,
)

# Pointed at via STAGE2_RC so the tests do not read ci/stage2/module.bazelrc, which is not at a
# fixed relative path under Bazel and would couple these assertions to unrelated rc edits.
_TEST_RC = """
build:stage2-linux-x86_64 --platforms=//:x
build:stage2-gcc --extra_toolchains=//:gcc
build:stage2-rust --extra_toolchains=//:rust
build:ferrocene-coverage --copt=-x
build:ferrocene-coverage-per --config=ferrocene-coverage
"""


@pytest.fixture(autouse=True)
def stage2_rc(tmp_path_factory, monkeypatch) -> Path:
    rc = tmp_path_factory.mktemp("rc") / "module.bazelrc"
    rc.write_text(_TEST_RC)
    monkeypatch.setattr(quality_runners, "STAGE2_RC", rc)
    return rc


INJECTED = (
    'module(name = "score_communication")\n'
    "# --- BEGIN ref_int resolved-deps injection ---\n"
    'bazel_dep(name = "score_crates")\n'
    'git_override(\n    module_name = "score_crates",\n    commit = "a5f4f57",\n    remote = "r",\n)\n'
    "# --- END ref_int resolved-deps injection ---\n"
)


def _module(name: str = "score_persistency", **meta) -> Module:
    defaults = {
        "code_root_path": "//src/...",
        "langs": ["cpp"],
        "extra_test_config": [],
        "exclude_test_targets": [],
    }
    defaults.update(meta)
    return Module(name=name, hash="a" * 40, repo="https://example.com/x.git", metadata=Metadata(**defaults))


class TestTargetArgsAreSharedWithTheTestRun:
    """Invariant I6: the gate must address exactly the target set the test run addresses.

    Bazel evaluates a module extension only when a target needs a repository it generates, so a
    gate sharing the test run's targets cannot fail on graph the tests never reach.
    """

    def test_gate_and_test_run_address_the_identical_target_set(self):
        m = _module(exclude_test_targets=["//src:slow_test"], extra_test_config=["@a//b:c=d"])
        gate, run = stage2_gate_command(m, []), stage2_module_command(m, [])
        # Only the verb and the coverage-specific flags may differ.
        assert gate[gate.index(m.metadata.code_root_path) :] == run[run.index(m.metadata.code_root_path) :]

    def test_exclusions_are_negated_after_the_double_dash(self):
        args = stage2_target_args(_module(exclude_test_targets=["//src:a", "//src:b"]))
        assert args[args.index("--") + 1 :] == ["-//src:a", "-//src:b"]

    def test_extra_test_config_is_passed_as_flags(self):
        assert "--@a//b:c=d" in stage2_target_args(_module(extra_test_config=["@a//b:c=d"]))

    def test_gate_is_analysis_only(self):
        # Not 'coverage --nobuild': that exits 1 even when analysis succeeds.
        cmd = stage2_gate_command(_module(), [])
        assert cmd[1:3] == ["build", "--nobuild"]

    def test_test_run_uses_coverage_so_the_suite_is_not_run_twice(self):
        assert "coverage" in stage2_module_command(_module(), [])

    def test_startup_flags_precede_the_verb_in_both(self):
        # Different startup options start a different server with a different output base,
        # invalidating the paths the coverage steps compute.
        for cmd in (
            stage2_gate_command(_module(), ["--bazelrc=/x"]),
            stage2_module_command(_module(), ["--bazelrc=/x"]),
        ):
            assert cmd[:2] == ["bazel", "--bazelrc=/x"]


class TestConfigFlags:
    """Invariant I10: a config a module names must be defined in ref_int's rc, or fail loudly."""

    def test_base_config_is_emitted_unconditionally(self):
        # A mistyped per-module bazel_config must not leave a run with no platform or toolchain.
        assert f"--config={STAGE2_BASE_CONFIG}" in stage2_config_flags(_module(bazel_config=[]))

    def test_undefined_config_is_rejected_rather_than_silently_applying_nothing(self):
        with pytest.raises(SystemExit, match="not defined"):
            stage2_config_flags(_module(bazel_config=["stage2-does-not-exist"]))

    def test_base_config_is_not_duplicated_when_a_module_also_names_it(self):
        flags = stage2_config_flags(_module(bazel_config=[STAGE2_BASE_CONFIG]))
        assert flags.count(f"--config={STAGE2_BASE_CONFIG}") == 1

    def test_rust_module_gets_coverage_instrumentation_in_the_same_run(self):
        # rustc must be instrumented in the same run that produces the .profraw files.
        assert "--config=ferrocene-coverage" in stage2_config_flags(_module(langs=["rust"]))

    def test_rust_module_with_broken_extraction_still_gets_no_instrumentation_config(self):
        # In DISABLED_RUST_COVERAGE: its tests run, its coverage does not.
        flags = stage2_config_flags(_module(name="score_communication", langs=["rust"]))
        assert not any("ferrocene" in f for f in flags)

    def test_per_module_rust_coverage_config_overrides_the_default(self):
        flags = stage2_config_flags(_module(langs=["rust"], rust_coverage_config="ferrocene-coverage-per"))
        assert "--config=ferrocene-coverage-per" in flags
        assert "--config=ferrocene-coverage" not in flags


class TestSelectionDigest:
    """Invariant I7: extension results may grow between gate and test run; versions may not move.

    Replaces --lockfile_mode=error on the test run, so it must compare only the fields that decide
    selection -- a grown moduleExtensions section would otherwise warn on every module.
    """

    def _lock(self, tmp_path: Path, **fields) -> Path:
        p = tmp_path / "MODULE.bazel.lock"
        p.write_text(json.dumps(fields))
        return p

    def test_reads_only_the_selection_deciding_fields(self, tmp_path: Path):
        d = selection_digest(self._lock(tmp_path, registryFileHashes={"a": "1"}, selectedYankedVersions={}, other=1))
        assert set(d) == {"registryFileHashes", "selectedYankedVersions"}

    def test_growing_module_extensions_is_not_a_change(self, tmp_path: Path):
        before = selection_digest(self._lock(tmp_path, registryFileHashes={"a": "1"}, moduleExtensions={}))
        after = selection_digest(self._lock(tmp_path, registryFileHashes={"a": "1"}, moduleExtensions={"x": {"y": 1}}))
        assert before == after

    def test_a_moved_registry_hash_is_a_change(self, tmp_path: Path):
        before = selection_digest(self._lock(tmp_path, registryFileHashes={"a": "1"}))
        after = selection_digest(self._lock(tmp_path, registryFileHashes={"a": "2"}))
        assert before != after

    def test_missing_lock_is_none_so_callers_cannot_read_it_as_unchanged(self, tmp_path: Path):
        assert selection_digest(tmp_path / "absent.lock") is None

    def test_unparseable_lock_is_none_not_an_empty_digest(self, tmp_path: Path):
        # An empty digest compares equal to another, silently reporting "nothing moved".
        p = tmp_path / "MODULE.bazel.lock"
        p.write_text("{not json")
        assert selection_digest(p) is None


class TestClassifyGateFailure:
    """Invariant I13: a gate failure naming a dep ref_int injected is an integration conflict.

    The default stays ref_int's -- a harness defect filed against a module team goes to someone
    who cannot fix it.
    """

    @pytest.fixture
    def module_bazel(self, tmp_path: Path) -> Path:
        p = tmp_path / "MODULE.bazel"
        p.write_text(INJECTED)
        return p

    @pytest.mark.parametrize(
        "spelling",
        ["ERROR: no such target '@@score_crates+//:mockall'", "ERROR: no such target '@score_crates//:mockall'"],
        ids=["canonical", "apparent"],
    )
    def test_both_bazel_repo_spellings_are_recognised(self, spelling: str, module_bazel: Path):
        # Bazel writes the repo canonically (@@name+) or apparently (@name//) by error site.
        assert classify_gate_failure(spelling, module_bazel) == ("integration conflict", ["score_crates"])

    def test_a_bare_module_name_is_not_enough(self, module_bazel: Path):
        # A bare name can appear in unrelated prose; guessing hands ref_int's bugs to modules.
        assert classify_gate_failure("ERROR: score_crates is broken", module_bazel) == ("ref_int harness defect", [])

    def test_a_failure_naming_nothing_injected_stays_ref_ints(self, module_bazel: Path):
        assert classify_gate_failure("ERROR: no such package '@@grpc+//'", module_bazel)[0] == "ref_int harness defect"

    def test_an_unreadable_module_bazel_defaults_to_ref_int(self, tmp_path: Path):
        assert classify_gate_failure("anything", tmp_path / "absent")[0] == "ref_int harness defect"

    def test_no_injection_block_means_nothing_was_pinned(self, tmp_path: Path):
        # ref_int pinned nothing, so no failure can be a conflict between its pins and the module.
        p = tmp_path / "MODULE.bazel"
        p.write_text('module(name = "m")\n')
        assert classify_gate_failure("ERROR: '@@score_crates+//:mockall'", p) == ("ref_int harness defect", [])


class TestStage2StartupFlags:
    """The rc files Stage 2 reads for a module, and in which order."""

    def test_isolated_module_reads_shared_rc_only(self):
        flags = quality_runners.stage2_startup_flags("score_kyron")
        assert flags == ["--noworkspace_rc", f"--bazelrc={quality_runners.STAGE2_RC}"]

    def test_dedicated_rc_module_is_isolated_and_reads_both_rcs_in_order(self, tmp_path, monkeypatch):
        shared = tmp_path / "module.bazelrc"
        shared.write_text("build:stage2-linux-x86_64 --platforms=//:x\n")
        dedicated = tmp_path / "score_communication.bazelrc"
        dedicated.write_text("build --extra_toolchains=//bazel/toolchains:x\n")
        monkeypatch.setattr(quality_runners, "STAGE2_RC", shared)

        flags = quality_runners.stage2_startup_flags("score_communication")

        assert flags == [
            "--noworkspace_rc",
            f"--bazelrc={shared}",
            f"--bazelrc={dedicated}",
        ]

    def test_module_keeping_its_own_rc_is_not_isolated(self):
        flags = quality_runners.stage2_startup_flags("score_config_management")
        assert "--noworkspace_rc" not in flags

    def test_missing_dedicated_rc_is_loud(self, tmp_path, monkeypatch):
        monkeypatch.setattr(quality_runners, "STAGE2_RC", tmp_path / "module.bazelrc")
        with pytest.raises(SystemExit, match="declares a dedicated Stage-2 rc"):
            quality_runners.stage2_startup_flags("score_communication")

    def test_module_without_dedicated_rc_gets_none(self):
        assert quality_runners.stage2_module_rc("score_kyron") is None

    def test_dedicated_rc_is_looked_up_beside_the_shared_one(self, tmp_path, monkeypatch):
        shared = tmp_path / "nested" / "module.bazelrc"
        shared.parent.mkdir()
        shared.write_text("")
        (shared.parent / "score_communication.bazelrc").write_text("")
        monkeypatch.setattr(quality_runners, "STAGE2_RC", shared)

        assert quality_runners.stage2_module_rc("score_communication") == shared.parent / "score_communication.bazelrc"


class TestNestedBazelEnvironment:
    """A nested bazel must not inherit this process's 'bazel run' context."""

    def test_bazel_run_variables_are_removed(self, monkeypatch):
        monkeypatch.setenv("BUILD_WORKSPACE_DIRECTORY", "/ref_int")
        monkeypatch.setenv("RUNFILES_DIR", "/ref_int/bazel-bin/x.runfiles")
        monkeypatch.setenv("PATH", "/usr/bin")

        env = quality_runners._child_env()

        assert "BUILD_WORKSPACE_DIRECTORY" not in env
        assert "RUNFILES_DIR" not in env
        assert env["PATH"] == "/usr/bin"


class TestUnpatchedDependencies:
    """Deps ref_int patches in Stage 1 whose patches did not reach the injected MODULE.bazel."""

    _REPO = "https://example.invalid/x.git"
    _HASH = "a" * 40

    @pytest.fixture
    def uninjected(self, tmp_path):
        """A MODULE.bazel naming no patch at all: nothing was transported."""
        path = tmp_path / "MODULE.bazel"
        path.write_text('module(name = "score_config_management")\n')
        return path

    def _dep(self, name, patches=None):
        data = {"repo": self._REPO, "hash": self._HASH}
        if patches:
            data["bazel_patches"] = patches
        return Module.from_dict(name, data)

    def _known(self, **modules):
        return SimpleNamespace(modules={"target_sw": modules})

    def _graph(self, root, deps):
        return DependencyGraph({"name": root, "dependencies": [{"name": d, "dependencies": []} for d in deps]})

    def test_patched_dependency_is_reported_with_its_patch_count(self, uninjected):
        known = self._known(
            score_config_management=self._dep("score_config_management"),
            score_logging=self._dep("score_logging", ["//patches/logging:a.patch", "//patches/logging:b.patch"]),
        )
        graph = self._graph("score_config_management", ["score_logging"])

        assert unpatched_dependencies("score_config_management", known, graph, uninjected) == ["score_logging (2)"]

    def test_dependency_without_patches_is_not_reported(self, uninjected):
        known = self._known(
            score_kyron=self._dep("score_kyron"),
            score_baselibs=self._dep("score_baselibs"),
        )
        graph = self._graph("score_kyron", ["score_baselibs"])

        assert unpatched_dependencies("score_kyron", known, graph, uninjected) == []

    def test_the_module_under_tests_own_patches_are_not_reported(self, uninjected):
        """They are applied by apply_module_patches; only dependencies lose theirs."""
        known = self._known(score_time=self._dep("score_time", ["//patches/time:001.patch"]))
        graph = self._graph("score_time", [])

        assert unpatched_dependencies("score_time", known, graph, uninjected) == []

    def test_patched_module_outside_the_closure_is_not_reported(self, uninjected):
        known = self._known(
            score_kyron=self._dep("score_kyron"),
            score_logging=self._dep("score_logging", ["//patches/logging:a.patch"]),
        )
        graph = self._graph("score_kyron", [])

        assert unpatched_dependencies("score_kyron", known, graph, uninjected) == []

    def test_transported_patches_are_not_reported(self, tmp_path):
        known = self._known(
            score_config_management=self._dep("score_config_management"),
            score_logging=self._dep("score_logging", ["//patches/logging:a.patch"]),
        )
        graph = self._graph("score_config_management", ["score_logging"])
        injected = tmp_path / "MODULE.bazel"
        injected.write_text('git_override(\n    patches = ["//ref_int_patches:patches/logging/a.patch"],\n)\n')

        assert unpatched_dependencies("score_config_management", known, graph, injected) == []
