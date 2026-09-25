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

from known_good.check_disabled_modules import collect_edges  # noqa: E402
from known_good.models.known_good import KnownGood  # noqa: E402
from known_good.models.module import Module  # noqa: E402
from known_good.update_module_from_known_good import (  # noqa: E402
    check_bazelrc_fragments,
    check_bazelrc_has_no_module_flags,
    generate_docs_bundles_content,
    generate_module_flags_content,
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


def test_disabled_module_is_dropped_from_the_sbom():
    """The SBOM is filtered, not rejected: an SBOM entry alone must not block disabling."""
    known = KnownGood.from_dict(
        _raw_known_good(
            {
                "score_baselibs": _raw("score_baselibs"),
                "score_logging": _raw("score_logging", enabled=False, disabled_reason="blocked"),
            },
            sbom=["score_baselibs", "score_logging"],
        )
    )

    assert known.sbom_tracked_modules == ["score_baselibs", "score_logging"]
    assert known.enabled_sbom_modules == ["score_baselibs"]


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


def test_module_flags_file_imports_only_enabled_fragments(tmp_path):
    """The generated import list is the whole deactivation mechanism for .bazelrc flags."""
    known = KnownGood(
        modules={
            "target_sw": {
                "score_baselibs": _module("score_baselibs"),
                "score_logging": _module("score_logging", enabled=False, disabled_reason="blocked"),
            }
        },
        timestamp="2026-01-01T00:00:00Z",
    )
    (tmp_path / "score_baselibs.bazelrc").write_text("build --@score_baselibs//a:b=1\n", encoding="utf-8")
    (tmp_path / "score_logging.bazelrc").write_text("build --@score_logging//c:d=2\n", encoding="utf-8")

    content = generate_module_flags_content(known, tmp_path, "2026-01-01T00:00:00Z")

    assert "score_baselibs.bazelrc" in content
    assert "score_logging" not in content


def test_module_flags_file_skips_modules_without_a_fragment(tmp_path):
    """Most modules carry no flags at all; they must not produce a dangling import."""
    known = KnownGood(
        modules={"target_sw": {"score_time": _module("score_time")}},
        timestamp="2026-01-01T00:00:00Z",
    )

    content = generate_module_flags_content(known, tmp_path, "2026-01-01T00:00:00Z")

    assert "score_time" not in content


def test_module_flag_in_the_root_bazelrc_is_rejected(tmp_path):
    """The worst failure mode: such a flag breaks every bazel invocation, even 'query'."""
    bazelrc = tmp_path / ".bazelrc"
    bazelrc.write_text("build --@score_logging//score/datarouter:enabled=true\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="must not live in .bazelrc"):
        check_bazelrc_has_no_module_flags(bazelrc, tmp_path / "bazelrc")


def test_root_bazelrc_check_ignores_comments(tmp_path):
    bazelrc = tmp_path / ".bazelrc"
    bazelrc.write_text(
        "# build --@score_logging//score/datarouter:enabled=true\nbuild --config=_common\n",
        encoding="utf-8",
    )

    check_bazelrc_has_no_module_flags(bazelrc, tmp_path / "bazelrc")


def test_fragment_holding_another_modules_flag_is_rejected(tmp_path):
    """Grouping by owning repository is what makes removal by deletion correct."""
    known = KnownGood(
        modules={
            "target_sw": {
                "score_baselibs": _module("score_baselibs"),
                "score_logging": _module("score_logging"),
            }
        },
        timestamp="2026-01-01T00:00:00Z",
    )
    (tmp_path / "score_baselibs.bazelrc").write_text("build --@score_logging//c:d=2\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="score_logging"):
        check_bazelrc_fragments(known, tmp_path)


def test_fragment_without_a_matching_module_is_rejected(tmp_path):
    """An orphan fragment is a flag nobody can ever disable again."""
    known = KnownGood(
        modules={"target_sw": {"score_baselibs": _module("score_baselibs")}},
        timestamp="2026-01-01T00:00:00Z",
    )
    (tmp_path / "score_gone.bazelrc").write_text("build --@score_gone//a:b=1\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="score_gone"):
        check_bazelrc_fragments(known, tmp_path)


def test_mod_graph_walk_finds_who_pulls_a_module_back_in():
    """Dropping our bazel_dep does not remove a module another module still requires."""
    graph = {
        "key": "reference_integration@_",
        "root": True,
        "dependencies": [
            {
                "key": "score_persistency@_",
                "dependencies": [{"key": "score_logging@0.2.4", "dependencies": []}],
            }
        ],
    }

    present, consumers = collect_edges(graph)

    assert "score_logging" in present
    assert "reference_integration" not in present
    assert consumers["score_logging"] == {"score_persistency"}
