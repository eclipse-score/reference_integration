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
"""Unit tests for the platform info header generator."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_platform_info  # noqa: E402


def _generate(tmp_path: Path, known_good: dict) -> str:
    known_good_path = tmp_path / "known_good.json"
    known_good_path.write_text(json.dumps(known_good), encoding="utf-8")
    header_path = tmp_path / "platform_info_data.h"
    gen_platform_info.main(str(known_good_path), str(header_path))
    return header_path.read_text(encoding="utf-8")


def test_lists_target_sw_modules_sorted_with_version_or_hash(tmp_path):
    header = _generate(
        tmp_path,
        {
            "modules": {
                "target_sw": {
                    "score_b": {"hash": "0123abcd"},
                    "score_a": {"version": "1.0.0"},
                },
                "tooling": {"score_tooling": {"version": "3.0.2"}},
            },
            "timestamp": "2026-11-01T00:00:00Z",
        },
    )

    assert 'kKnownGoodTimestamp{"2026-11-01T00:00:00Z"}' in header
    assert "std::array<ModuleEntry, 2U> kModules" in header
    assert header.index('ModuleEntry{"score_a", "1.0.0"},') < header.index('ModuleEntry{"score_b", "0123abcd"},')
    assert "score_tooling" not in header


def test_escapes_strings_and_defaults_the_timestamp(tmp_path):
    header = _generate(tmp_path, {"modules": {"target_sw": {"score_a": {"version": 'a"b'}}}})

    assert 'ModuleEntry{"score_a", "a\\"b"},' in header
    assert 'kKnownGoodTimestamp{""}' in header


def test_fails_for_a_module_without_version_and_hash(tmp_path):
    with pytest.raises(SystemExit, match="score_a has neither 'version' nor 'hash'"):
        _generate(tmp_path, {"modules": {"target_sw": {"score_a": {"repo": "r"}}}})
