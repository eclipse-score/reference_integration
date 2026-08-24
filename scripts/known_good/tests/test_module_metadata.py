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
"""Unit tests for the two rules ``Module.from_dict`` enforces on excluded test targets.

Both exist because Stage 2 (DR-008 Option 4) runs each module as the Bazel *root*. That retired
the blanket justification the exclusion list used to lean on -- dev_dependency-only deps being
invisible from ref_int's resolved graph -- and left a list of 16 entries nobody could account for.
An exclusion now has to name itself explicitly and say why.
"""

import sys
from pathlib import Path

import pytest

# Make scripts/ importable so known_good.* package resolves when run via plain pytest.
_SCRIPTS_DIR = Path(__file__).resolve().parents[2]
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from known_good.models.module import Module  # noqa: E402

_REPO = "https://github.com/eclipse-score/x.git"
_HASH = "a" * 40


def _module(metadata: dict) -> Module:
    return Module.from_dict("score_x", {"repo": _REPO, "hash": _HASH, "metadata": metadata})


class TestWildcardExclusionsRejected:
    """A wildcard hides how much it excludes, so the report cannot say what was skipped."""

    @pytest.mark.parametrize("target", ["//score/json/examples:*", "//score/mw/log/configuration:*"])
    def test_wildcard_is_rejected(self, target):
        with pytest.raises(ValueError, match="wildcard exclude_test_targets"):
            _module({"exclude_test_targets": [target], "exclude_test_target_reasons": {target: "why"}})

    def test_explicit_label_is_accepted(self):
        target = "//src/cpp/tests:bm_kvs_cpp"
        module = _module({"exclude_test_targets": [target], "exclude_test_target_reasons": {target: "benchmark"}})
        assert module.metadata.exclude_test_targets == [target]


class TestExclusionsMustCarryAReason:
    def test_missing_reason_is_rejected(self):
        with pytest.raises(ValueError, match="no recorded reason"):
            _module({"exclude_test_targets": ["//a:b"]})

    def test_blank_reason_is_rejected(self):
        """Whitespace is not an explanation."""
        with pytest.raises(ValueError, match="no recorded reason"):
            _module({"exclude_test_targets": ["//a:b"], "exclude_test_target_reasons": {"//a:b": "   "}})

    def test_reason_for_a_different_label_does_not_satisfy_the_rule(self):
        with pytest.raises(ValueError, match="no recorded reason"):
            _module({"exclude_test_targets": ["//a:b"], "exclude_test_target_reasons": {"//a:other": "why"}})

    def test_recorded_reason_is_accepted_and_preserved(self):
        module = _module({"exclude_test_targets": ["//a:b"], "exclude_test_target_reasons": {"//a:b": "needs TSan"}})
        assert module.metadata.exclude_test_target_reasons == {"//a:b": "needs TSan"}

    def test_no_exclusions_needs_no_reasons(self):
        assert _module({"exclude_test_targets": []}).metadata.exclude_test_target_reasons == {}

    def test_module_without_metadata_still_loads(self):
        module = Module.from_dict("score_x", {"repo": _REPO, "hash": _HASH})
        assert module.metadata.exclude_test_targets == []


class TestLegacyExclusionsAreSeparate:
    """The central-mode list predates the audit, so the two checks above must not apply to it."""

    def test_wildcards_allowed(self):
        module = _module({"legacy_exclude_test_targets": ["//score/mw/log/configuration:*"]})
        assert module.metadata.legacy_exclude_test_targets == ["//score/mw/log/configuration:*"]

    def test_no_reason_required(self):
        assert _module({"legacy_exclude_test_targets": ["//a:b"]}).metadata.legacy_exclude_test_targets == ["//a:b"]

    def test_does_not_leak_into_the_stage2_list(self):
        module = _module({"legacy_exclude_test_targets": ["//a:b"], "exclude_test_targets": []})
        assert module.metadata.exclude_test_targets == []

    def test_defaults_empty(self):
        assert _module({}).metadata.legacy_exclude_test_targets == []
