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
"""Unit tests for the Stage-2 Bazel release rule (ref_int's version is a floor, not a ceiling).

Self-contained: the rule under test is a pure function over two version strings, so no module
checkout and no Bazel are required.
"""

import sys
from pathlib import Path

import pytest

# Make scripts/ importable so known_good.* package resolves when run via plain pytest.
_SCRIPTS_DIR = Path(__file__).resolve().parents[2]
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from known_good.bazel_version import resolve_stage2_bazel_version  # noqa: E402

REF_INT = "8.4.2"


class TestRefIntVersionIsAFloor:
    """A module is raised to ref_int's release, never lowered to it."""

    @pytest.mark.parametrize("module_version", ["8.3.0", "8.4.1", "7.4.1", "8.4"])
    def test_older_module_is_raised_to_ref_int(self, module_version):
        assert resolve_stage2_bazel_version(REF_INT, module_version) == REF_INT

    @pytest.mark.parametrize("module_version", ["8.5.1", "8.6.0", "9.0.0", "8.4.10"])
    def test_newer_module_keeps_its_own(self, module_version):
        assert resolve_stage2_bazel_version(REF_INT, module_version) == module_version

    def test_equal_versions_are_unchanged(self):
        assert resolve_stage2_bazel_version(REF_INT, REF_INT) == REF_INT

    def test_dotted_components_compare_numerically_not_lexically(self):
        # "8.10.0" < "8.9.0" as strings, but 10 > 9 as a release component. A lexical
        # comparison here would silently downgrade every module past the .9 boundary.
        assert resolve_stage2_bazel_version("8.9.0", "8.10.0") == "8.10.0"


class TestNonComparableVersions:
    """Values that cannot be ordered are left as the module wrote them."""

    @pytest.mark.parametrize("module_version", ["last_green", "latest", "8.4.0rc3", "8.4.2-score"])
    def test_unorderable_module_version_is_kept(self, module_version):
        assert resolve_stage2_bazel_version(REF_INT, module_version) == module_version

    def test_unorderable_ref_int_version_leaves_the_module_alone(self):
        assert resolve_stage2_bazel_version("last_green", "8.6.0") == "8.6.0"

    def test_missing_module_bazelversion_falls_back_to_ref_int(self):
        assert resolve_stage2_bazel_version(REF_INT, None) == REF_INT


class TestRegressionScoreBaselibs:
    """The measured case this rule exists for (see docs/dr8_stage2_bazel_version_floor.md).

    score_baselibs pins 8.6.0 and resolves cleanly there; under ref_int's 8.4.2 the identical
    MODULE.bazel fails bzlmod's compatibility-level check and the run executes zero tests.
    """

    def test_score_baselibs_keeps_the_bazel_it_resolves_under(self):
        assert resolve_stage2_bazel_version("8.4.2", "8.6.0") == "8.6.0"

    def test_score_orchestrator_is_still_raised_to_ref_ints_floor(self):
        # The other direction must keep working: 8.3.0 predates ref_int's rc.
        assert resolve_stage2_bazel_version("8.4.2", "8.3.0") == "8.4.2"
