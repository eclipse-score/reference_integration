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
"""Unit tests for applying a module's own bazel_patches to its Stage-2 checkout.

Self-contained: builds a throwaway git checkout and patch files in tmp_path. Needs git, no
Bazel and no network.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Make scripts/ importable so known_good.* package resolves when run via plain pytest.
_SCRIPTS_DIR = Path(__file__).resolve().parents[2]
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from known_good.models.module import Module  # noqa: E402
from known_good.module_patches import (  # noqa: E402
    ModulePatchError,
    apply_module_patches,
    resolve_patch_path,
)
from known_good.resolved_dependencies import (  # noqa: E402
    INJECTION_BEGIN,
    INJECTION_END,
    DependencyGraph,
    ResolvedDependencies,
)

MODULE_BAZEL = """\
module(name = "score_time", version = "0.0.0")

bazel_dep(name = "score_baselibs", version = "0.2.9")
"""

# Generated with a real `git diff` against the checkout fixture below, not hand-authored.
# Mirrors patches/time/001: redirects a label and declares the dep it now needs.
ADD_DEP_PATCH = """\
diff --git a/MODULE.bazel b/MODULE.bazel
index eaac336..26f329f 100644
--- a/MODULE.bazel
+++ b/MODULE.bazel
@@ -1,3 +1,4 @@
 module(name = "score_time", version = "0.0.0")
\x20
 bazel_dep(name = "score_baselibs", version = "0.2.9")
+bazel_dep(name = "score_communication", version = "0.2.1")
"""

RC_PATCH = """\
diff --git a/.bazelrc b/.bazelrc
index 14041e7..9ec6ae3 100644
--- a/.bazelrc
+++ b/.bazelrc
@@ -1 +1 @@
-build --@score_baselibs//score/memory/shared/flags:use_typedshmd=False
+build --@score_communication//score/memory/shared/flags:use_typedshmd=False
"""

# Same shape as ADD_DEP_PATCH but with a context line that will never match the checkout.
NON_APPLYING_PATCH = """\
diff --git a/MODULE.bazel b/MODULE.bazel
index eaac336..26f329f 100644
--- a/MODULE.bazel
+++ b/MODULE.bazel
@@ -1,3 +1,4 @@
 module(name = "score_time", version = "0.0.0")
\x20
 bazel_dep(name = "score_this_context_never_matches", version = "0.2.9")
+bazel_dep(name = "score_communication", version = "0.2.1")
"""


def _git(workspace: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(workspace), *args], check=True, capture_output=True)


@pytest.fixture
def checkout(tmp_path: Path) -> Path:
    """A committed module checkout, as Stage 2's actions/checkout leaves it."""
    workspace = tmp_path / "_module"
    workspace.mkdir()
    (workspace / "MODULE.bazel").write_text(MODULE_BAZEL)
    (workspace / ".bazelrc").write_text("build --@score_baselibs//score/memory/shared/flags:use_typedshmd=False\n")
    _git(workspace, "init", "-q")
    _git(workspace, "config", "user.email", "t@example.com")
    _git(workspace, "config", "user.name", "t")
    _git(workspace, "add", "-A")
    _git(workspace, "commit", "-qm", "initial")
    return workspace


@pytest.fixture
def ref_int(tmp_path: Path) -> Path:
    """ref_int's patch tree, holding both label and bare-path spellings."""
    root = tmp_path / "ref_int"
    (root / "patches" / "time").mkdir(parents=True)
    (root / "patches" / "time" / "001-add-dep.patch").write_text(ADD_DEP_PATCH)
    (root / "patches" / "time" / "002-rc.patch").write_text(RC_PATCH)
    (root / "patches" / "time" / "003-broken.patch").write_text(NON_APPLYING_PATCH)
    return root


def _module(patches: list[str] | None) -> Module:
    return Module(
        name="score_time",
        hash="8c42d34698535dabeaa4782d5ec123256151fb30",
        repo="https://github.com/eclipse-score/time.git",
        bazel_patches=patches,
    )


class TestResolvePatchPath:
    def test_label_form(self, ref_int: Path):
        assert resolve_patch_path("//patches/time:001-add-dep.patch", ref_int).name == "001-add-dep.patch"

    def test_bare_path_form(self, ref_int: Path):
        assert resolve_patch_path("patches/time/001-add-dep.patch", ref_int).name == "001-add-dep.patch"

    def test_missing_file_raises(self, ref_int: Path):
        with pytest.raises(ModulePatchError, match="does not exist"):
            resolve_patch_path("//patches/time:999-nope.patch", ref_int)

    def test_absolute_path_rejected(self, ref_int: Path):
        with pytest.raises(ModulePatchError, match="workspace-relative"):
            resolve_patch_path("/etc/passwd", ref_int)


class TestApplyModulePatches:
    def test_applies_declared_patches(self, checkout: Path, ref_int: Path):
        applied = apply_module_patches(
            _module(["//patches/time:001-add-dep.patch", "patches/time/002-rc.patch"]),
            checkout,
            ref_int,
            log=lambda _: None,
        )
        assert len(applied) == 2
        assert 'bazel_dep(name = "score_communication"' in (checkout / "MODULE.bazel").read_text()
        assert "@score_communication//score/memory/shared/flags" in (checkout / ".bazelrc").read_text()

    def test_no_patches_leaves_checkout_untouched(self, checkout: Path, ref_int: Path):
        before = (checkout / "MODULE.bazel").read_text()
        assert apply_module_patches(_module(None), checkout, ref_int, log=lambda _: None) == []
        assert (checkout / "MODULE.bazel").read_text() == before

    def test_non_applying_patch_raises_not_skipped(self, checkout: Path, ref_int: Path):
        with pytest.raises(ModulePatchError, match="does not apply"):
            apply_module_patches(_module(["//patches/time:003-broken.patch"]), checkout, ref_int, log=lambda _: None)

    def test_already_applied_is_skipped(self, checkout: Path, ref_int: Path):
        module = _module(["//patches/time:001-add-dep.patch"])
        apply_module_patches(module, checkout, ref_int, log=lambda _: None)
        content = (checkout / "MODULE.bazel").read_text()

        # A second run must neither raise nor double-apply — ci_local.sh reuses _module/.
        assert apply_module_patches(module, checkout, ref_int, log=lambda _: None) == []
        assert (checkout / "MODULE.bazel").read_text() == content

    def test_failure_names_the_patch_and_commit(self, checkout: Path, ref_int: Path):
        with pytest.raises(ModulePatchError) as error:
            apply_module_patches(_module(["//patches/time:003-broken.patch"]), checkout, ref_int, log=lambda _: None)
        assert "003-broken.patch" in str(error.value)
        assert "8c42d34698535dabeaa4782d5ec123256151fb30" in str(error.value)


class TestOrderingAgainstInjection:
    """Patches must land before override injection, or a patch-added dep is double-declared."""

    @pytest.fixture
    def resolved(self, tmp_path: Path) -> ResolvedDependencies:
        # from_file reads the flat resolved-versions manifest shape (written by to_file), not
        # known_good.json's group-nested shape.
        manifest = tmp_path / "resolved_versions.json"
        manifest.write_text(
            '{"modules": {'
            '"score_baselibs": {"repo": "https://github.com/eclipse-score/baselibs.git", '
            '"hash": "cab36dd7de92aaaaaaaaaaaaaaaaaaaaaaaaaaaa"},'
            '"score_communication": {"repo": "https://github.com/eclipse-score/communication.git", '
            '"hash": "0e9187f79a99bbbbbbbbbbbbbbbbbbbbbbbbbbbb"}'
            "}}"
        )
        return ResolvedDependencies.from_file(manifest)

    @pytest.fixture
    def graph(self) -> DependencyGraph:
        def node(name: str, deps: list[dict] | None = None) -> dict:
            return {"name": name, "version": "1.0", "dependencies": deps or [], "indirectDependencies": []}

        return DependencyGraph(
            node("<root>", [node("score_time"), node("score_baselibs"), node("score_communication")])
        )

    def test_patch_first_declares_dep_once(
        self, checkout: Path, ref_int: Path, resolved: ResolvedDependencies, graph: DependencyGraph
    ):
        apply_module_patches(_module(["//patches/time:001-add-dep.patch"]), checkout, ref_int, log=lambda _: None)
        patched = resolved.overwrite(checkout / "MODULE.bazel", graph, module_under_test="score_time", write=False)
        # The patch declared it, so injection must not add a second bazel_dep line for it.
        assert patched.count('bazel_dep(name = "score_communication"') == 1
        assert 'module_name = "score_communication"' in patched.split(INJECTION_BEGIN)[1].split(INJECTION_END)[0]

    def test_injection_first_breaks_the_patch(
        self, checkout: Path, ref_int: Path, resolved: ResolvedDependencies, graph: DependencyGraph
    ):
        # Injecting first already adds a bazel_dep for score_communication, changing the file
        # out from under the patch's context -- it then fails to apply instead of double-declaring.
        module_bazel = checkout / "MODULE.bazel"
        resolved.overwrite(module_bazel, graph, module_under_test="score_time")
        with pytest.raises(ModulePatchError, match="does not apply"):
            apply_module_patches(_module(["//patches/time:001-add-dep.patch"]), checkout, ref_int, log=lambda _: None)
