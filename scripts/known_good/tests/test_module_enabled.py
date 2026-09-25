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
"""Unit tests for temporarily disabling a module via known_good.json.

Self-contained: builds KnownGood objects in memory. Needs no Bazel, git or network.
"""

import sys
from pathlib import Path

import pytest

# Make scripts/ importable so known_good.* package resolves when run via plain pytest.
_SCRIPTS_DIR = Path(__file__).resolve().parents[2]
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from known_good.models.known_good import KnownGood  # noqa: E402
from known_good.models.module import Module  # noqa: E402
from known_good.update_module_from_known_good import (  # noqa: E402
    check_bazelrc_for_disabled_modules,
    generate_docs_bundles_content,
)

_HASH = "0" * 40


def _raw(name: str, **overrides) -> dict:
    module = {"repo": f"https://github.com/eclipse-score/{name}.git", "hash": _HASH}
    module.update(overrides)
    return module


def _raw_known_good(target_sw: dict, sbom: list[str] | None = None) -> dict:
    return {
        "modules": {"target_sw": target_sw},
        "sbom": {"tracked_modules": sbom or []},
        "timestamp": "2026-01-01T00:00:00Z",
    }


def _module(name: str, **kwargs) -> Module:
    return Module(name=name, hash=_HASH, repo=f"https://github.com/eclipse-score/{name}.git", **kwargs)


def test_modules_are_enabled_by_default():
    """Saying nothing about 'enabled' keeps a module in the integration: the common case."""
    module = Module.from_dict("score_logging", _raw("score_logging"))

    assert module.enabled is True
    assert module.disabled_reason is None
    # The key stays out of the file entirely, so enabling a module leaves no residue.
    assert "enabled" not in module.to_dict()


def test_disabling_requires_a_reason():
    """A disabled module without a reason becomes a permanent state nobody dares to revert."""
    with pytest.raises(ValueError, match="no 'disabled_reason'"):
        Module.from_dict("score_logging", _raw("score_logging", enabled=False))


def test_reason_without_disabling_is_rejected():
    """Catches the half-done edit that leaves the module silently running."""
    with pytest.raises(ValueError, match="but is enabled"):
        Module.from_dict("score_logging", _raw("score_logging", disabled_reason="broken"))


def test_enabled_must_be_a_boolean():
    with pytest.raises(ValueError, match="invalid 'enabled' value"):
        Module.from_dict("score_logging", _raw("score_logging", enabled="false"))


def test_disabled_module_round_trips():
    """Disabling is reversible: hash, patches and metadata survive the round trip."""
    raw = _raw(
        "score_logging",
        enabled=False,
        disabled_reason="blocked by eclipse-score/logging#123",
        bazel_patches=["//patches/logging:001-fix.patch"],
    )

    result = Module.from_dict("score_logging", raw).to_dict()

    assert result["enabled"] is False
    assert result["disabled_reason"] == "blocked by eclipse-score/logging#123"
    assert result["hash"] == _HASH
    assert result["bazel_patches"] == ["//patches/logging:001-fix.patch"]


def test_enabled_modules_filters_the_group():
    known = KnownGood.from_dict(
        _raw_known_good(
            {
                "score_baselibs": _raw("score_baselibs"),
                "score_logging": _raw("score_logging", enabled=False, disabled_reason="blocked"),
            }
        )
    )

    assert set(known.enabled_modules("target_sw")) == {"score_baselibs"}
    assert set(known.disabled_modules) == {"score_logging"}
    # The raw mapping still holds both: disabling must not lose the pinned state.
    assert set(known.modules["target_sw"]) == {"score_baselibs", "score_logging"}


def test_disabled_module_is_not_mounted_in_the_docs():
    known = KnownGood(
        modules={
            "target_sw": {
                "score_baselibs": _module("score_baselibs"),
                "score_logging": _module("score_logging", enabled=False, disabled_reason="blocked"),
            }
        },
        timestamp="2026-01-01T00:00:00Z",
    )

    content = generate_docs_bundles_content(known)

    assert "score_baselibs" in content
    assert "score_logging" not in content


def test_disabled_module_may_not_stay_in_the_sbom():
    """The SBOM would otherwise claim a module the build no longer contains."""
    with pytest.raises(ValueError, match="sbom.tracked_modules"):
        KnownGood.from_dict(
            _raw_known_good(
                {"score_logging": _raw("score_logging", enabled=False, disabled_reason="blocked")},
                sbom=["score_logging"],
            )
        )


def test_metadata_reference_to_a_disabled_module_is_rejected():
    """An enabled module's test config pointing into a disabled one would break at Bazel time."""
    with pytest.raises(ValueError, match="score_persistency.*score_logging"):
        KnownGood.from_dict(
            _raw_known_good(
                {
                    "score_logging": _raw("score_logging", enabled=False, disabled_reason="blocked"),
                    "score_persistency": _raw(
                        "score_persistency",
                        metadata={"extra_test_config": ["@score_logging//score/mw/log:config"]},
                    ),
                }
            )
        )


def test_bazelrc_flag_for_a_disabled_module_is_rejected(tmp_path):
    """The worst failure mode: such a flag breaks every bazel invocation, even 'query'."""
    known = KnownGood(
        modules={"target_sw": {"score_logging": _module("score_logging", enabled=False, disabled_reason="blocked")}},
        timestamp="2026-01-01T00:00:00Z",
    )
    bazelrc = tmp_path / ".bazelrc"
    bazelrc.write_text("build --@score_logging//score/datarouter:enabled=true\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="still referenced by .bazelrc"):
        check_bazelrc_for_disabled_modules(known, bazelrc)


def test_bazelrc_check_ignores_comments_and_enabled_modules(tmp_path):
    known = KnownGood(
        modules={
            "target_sw": {
                "score_baselibs": _module("score_baselibs"),
                "score_logging": _module("score_logging", enabled=False, disabled_reason="blocked"),
            }
        },
        timestamp="2026-01-01T00:00:00Z",
    )
    bazelrc = tmp_path / ".bazelrc"
    bazelrc.write_text(
        "# build --@score_logging//score/datarouter:enabled=true\nbuild --@score_baselibs//score/foo:enabled=true\n",
        encoding="utf-8",
    )

    check_bazelrc_for_disabled_modules(known, bazelrc)
