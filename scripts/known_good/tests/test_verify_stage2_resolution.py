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
"""The patch half of the Stage-2 resolution check.

Version agreement proves nothing here: the same commit, patched and unpatched, resolves to
the same version.
"""

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from known_good.resolved_dependencies import INJECTION_BEGIN, INJECTION_END  # noqa: E402
from known_good.verify_stage2_resolution import missing_patches  # noqa: E402

MANIFEST = {
    "score_logging": {
        "repo": "https://e/logging.git",
        "hash": "a" * 40,
        "bazel_patches": ["//patches/logging:a.patch"],
    },
    "rules_cc": {"version": "0.2.17"},
}

LABEL = "//ref_int_patches:patches/logging/a.patch"


def _checkout(tmp_path: Path, injection: str, staged: list[str]) -> Path:
    """A module checkout whose MODULE.bazel carries ``injection`` inside ref_int's markers."""
    path = tmp_path / "MODULE.bazel"
    path.write_text(f'module(name = "score_persistency")\n\n{INJECTION_BEGIN}\n{injection}{INJECTION_END}\n')
    for relative in staged:
        patch = tmp_path / "ref_int_patches" / relative
        patch.parent.mkdir(parents=True, exist_ok=True)
        patch.write_text("payload\n")
    return path


def _override(patches: str = "") -> str:
    return f'git_override(\n    module_name = "score_logging",\n    commit = "{"a" * 40}",\n{patches})\n'


def test_transported_patch_is_accepted(tmp_path: Path):
    module_bazel = _checkout(
        tmp_path,
        _override(f'    patch_strip = 1,\n    patches = ["{LABEL}"],\n'),
        ["patches/logging/a.patch"],
    )
    assert missing_patches(MANIFEST, module_bazel, "score_persistency") == []


def test_patch_never_injected_is_reported(tmp_path: Path):
    module_bazel = _checkout(tmp_path, _override(), [])
    assert missing_patches(MANIFEST, module_bazel, "score_persistency") == [
        "score_logging: //patches/logging:a.patch not injected"
    ]


def test_label_without_the_file_is_reported(tmp_path: Path):
    module_bazel = _checkout(tmp_path, _override(f'    patches = ["{LABEL}"],\n'), [])
    assert missing_patches(MANIFEST, module_bazel, "score_persistency") == [
        "score_logging: //patches/logging:a.patch injected but absent from the checkout"
    ]


def test_a_module_outside_the_closure_is_not_required_to_be_patched(tmp_path: Path):
    module_bazel = _checkout(tmp_path, 'single_version_override(\n    module_name = "rules_cc",\n)\n', [])
    assert missing_patches(MANIFEST, module_bazel, "score_persistency") == []


def test_the_module_under_test_is_excluded(tmp_path: Path):
    """Its own patches are applied directly, never through an override."""
    module_bazel = _checkout(tmp_path, _override(), [])
    assert missing_patches(MANIFEST, module_bazel, "score_logging") == []


def test_no_module_bazel_yields_nothing(tmp_path: Path):
    assert missing_patches(MANIFEST, tmp_path / "absent" / "MODULE.bazel", "score_persistency") == []
