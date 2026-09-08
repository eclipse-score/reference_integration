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
"""Unit tests for generating the docs() bundle mounts from known_good.json.

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
from known_good.models.module import Docs, Module  # noqa: E402
from known_good.update_module_from_known_good import (  # noqa: E402
    generate_docs_bundles_content,
)


def _known_good(groups: dict[str, list[Module]]) -> KnownGood:
    return KnownGood(
        modules={group: {m.name: m for m in modules} for group, modules in groups.items()},
        timestamp="2026-01-01T00:00:00Z",
    )


def _module(name: str, **kwargs) -> Module:
    return Module(name=name, hash="0" * 40, repo=f"https://github.com/eclipse-score/{name}.git", **kwargs)


def test_group_decides_the_section():
    """target_sw mounts under modules/, tooling under process_methods_tools/."""
    content = generate_docs_bundles_content(
        _known_good({"target_sw": [_module("score_logging")], "tooling": [_module("score_platform")]})
    )

    assert '"bundle": "@score_logging//:docs_bundle",' in content
    assert '"mount_at": "modules/score_logging",' in content
    assert '"mount_at": "process_methods_tools/score_platform",' in content


def test_docs_are_mounted_by_default():
    """A module that says nothing about docs is mounted: that is the common case."""
    content = generate_docs_bundles_content(_known_good({"target_sw": [_module("score_baselibs")]}))

    assert '"mount_at": "modules/score_baselibs",' in content


def test_docs_false_opts_a_module_out():
    """A module exposing no //:docs_bundle must be excludable, or the docs build breaks."""
    content = generate_docs_bundles_content(
        _known_good(
            {
                "target_sw": [
                    _module("score_communication", docs=Docs(enabled=False)),
                    _module("score_logging"),
                ]
            }
        )
    )

    assert "score_communication" not in content
    assert '"mount_at": "modules/score_logging",' in content


def test_overrides_are_passed_through():
    """bundle, mount_at and attach_to override the defaults."""
    content = generate_docs_bundles_content(
        _known_good(
            {
                "target_sw": [
                    _module(
                        "score_kyron",
                        docs=Docs(bundle="@score_kyron//docs:bundle", mount_at="modules/kyron", attach_to="index"),
                    )
                ]
            }
        )
    )

    assert '"bundle": "@score_kyron//docs:bundle",' in content
    assert '"mount_at": "modules/kyron",' in content
    assert '"attach_to": "index",' in content


def test_attach_to_is_omitted_when_unset():
    """docs() defaults attach_to to the mount parent's index; do not emit an empty one."""
    content = generate_docs_bundles_content(_known_good({"target_sw": [_module("score_logging")]}))

    assert "attach_to" not in content


def test_unmapped_group_with_docs_fails():
    """A new group needs a docs section; silently dropping its modules would hide docs."""
    with pytest.raises(SystemExit, match="no docs section"):
        generate_docs_bundles_content(_known_good({"new_group": [_module("score_new")]}))


def test_unmapped_group_is_fine_when_opted_out():
    """A group of modules that all opt out needs no section."""
    content = generate_docs_bundles_content(
        _known_good(
            {
                "target_sw": [_module("score_logging")],
                "new_group": [_module("score_new", docs=Docs(enabled=False))],
            }
        )
    )

    assert "score_new" not in content


def test_duplicate_mount_fails():
    """Two bundles at one mount point would silently shadow each other."""
    with pytest.raises(SystemExit, match="both mount their docs at"):
        generate_docs_bundles_content(
            _known_good(
                {
                    "target_sw": [
                        _module("score_logging"),
                        _module("score_other", docs=Docs(mount_at="modules/score_logging")),
                    ]
                }
            )
        )


def test_no_mounts_at_all_fails():
    """An empty DOCS_BUNDLES means a docs site with no module documentation in it."""
    with pytest.raises(SystemExit, match="No modules to mount"):
        generate_docs_bundles_content(_known_good({"target_sw": [_module("score_logging", docs=Docs(enabled=False))]}))


def test_generated_banner_names_the_generator():
    """The file is generated; a reader who edits it by hand must be told not to."""
    content = generate_docs_bundles_content(
        _known_good({"target_sw": [_module("score_logging")]}), "2026-01-01T00:00:00Z"
    )

    assert "# Generated from known_good.json at 2026-01-01T00:00:00Z" in content
    assert "Do not edit manually" in content
    assert "SPDX-License-Identifier: Apache-2.0" in content


@pytest.mark.parametrize(
    ("value", "enabled"),
    [(None, True), (True, True), (False, False), ({}, True), ({"mount_at": "modules/x"}, True)],
)
def test_docs_parsed_from_known_good_values(value, enabled):
    """known_good.json may omit docs, or give a bool or a dict of overrides."""
    assert Module.from_dict("score_x", {"repo": "r", "hash": "h", "docs": value}).docs.enabled == enabled


def test_docs_key_absent_means_enabled():
    assert Module.from_dict("score_x", {"repo": "r", "hash": "h"}).docs.enabled


def test_invalid_docs_value_is_rejected():
    with pytest.raises(ValueError, match="Invalid 'docs' value"):
        Module.from_dict("score_x", {"repo": "r", "hash": "h", "docs": "yes"})


def test_unknown_docs_key_is_rejected():
    """A typo like 'mount' instead of 'mount_at' would otherwise be silently ignored."""
    with pytest.raises(ValueError, match="Unknown keys in 'docs': mount"):
        Module.from_dict("score_x", {"repo": "r", "hash": "h", "docs": {"mount": "modules/x"}})


@pytest.mark.parametrize("value", [None, False, {"mount_at": "modules/x"}])
def test_docs_survives_a_round_trip(value):
    """Scripts that rewrite known_good.json must not drop or invent a docs entry."""
    data = {"repo": "r", "hash": "h"}
    if value is not None:
        data["docs"] = value

    round_tripped = Module.from_dict("score_x", data).to_dict()

    assert round_tripped.get("docs") == value
