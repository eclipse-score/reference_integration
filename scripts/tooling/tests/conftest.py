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
"""Shared pytest fixtures and test utilities."""

import json
from pathlib import Path

import pytest
from lib.known_good import KnownGood, Module, load_known_good

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MINIMAL_JSON = {
    "modules": {
        "target_sw": {
            "score_baselibs": {
                "repo": "https://github.com/eclipse-score/baselibs.git",
                "hash": "abc123",
            }
        }
    },
    "timestamp": "2026-01-01T00:00:00+00:00Z",
}

FULL_JSON = {
    "modules": {
        "target_sw": {
            "score_baselibs": {
                "repo": "https://github.com/eclipse-score/baselibs.git",
                "hash": "158fe6a7b791c58f6eac5f7e4662b8db0cf9ac6e",
                "bazel_patches": ["//patches/baselibs:003-acl-fixes-for-aarch64.patch"],
                "metadata": {
                    "extra_test_config": [
                        "//score/json:base_library=nlohmann",
                        "//score/memory/shared/flags:use_typedshmd=False",
                    ],
                    "exclude_test_targets": [
                        "//score/language/safecpp/aborts_upon_exception:abortsuponexception_toolchain_test",
                        "//score/containers:dynamic_array_test",
                        "//score/mw/log/configuration:*",
                        "//score/json/examples:*",
                    ],
                    "langs": ["cpp"],
                },
            },
            "score_persistency": {
                "repo": "https://github.com/eclipse-score/persistency.git",
                "hash": "438bf9b5c447fd41ad43b321679dd3d1b3a6c737",
                "metadata": {"code_root_path": "//src/..."},
            },
        },
        "tooling": {
            "score_crates": {
                "repo": "https://github.com/eclipse-score/score-crates.git",
                "hash": "90539da0fd3e7e23e01f2b4de1679f7dfadd3b6b",
            },
            "score_itf": {
                "repo": "https://github.com/eclipse-score/itf.git",
                "hash": "44c75debab696a9c967455110a2c32f201159cdd",
            },
        },
    },
    "timestamp": "2026-01-01T00:00:00+00:00Z",
}

KNOWN_GOOD_JSON = Path(__file__).parents[3] / "known_good.json"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def make_known_good(**overrides) -> KnownGood:
    """Build a minimal KnownGood with one module.

    Args:
        **overrides: Additional fields to override in the module data.

    Returns:
        KnownGood instance with a single module in target_sw group.
    """
    module_data = {
        "repo": "https://github.com/eclipse-score/baselibs.git",
        "hash": "abc123def456abc123def456abc123def456abc123",
        **overrides,
    }
    module = Module.from_dict("score_baselibs", module_data)
    return KnownGood(
        modules={"target_sw": {"score_baselibs": module}},
        timestamp="2026-01-01T00:00:00+00:00Z",
    )


# ---------------------------------------------------------------------------
# Fixtures - File-based
# ---------------------------------------------------------------------------


@pytest.fixture
def minimal_json_file(tmp_path: Path) -> Path:
    """Create a temporary JSON file with minimal known good data."""
    p = tmp_path / "known_good.json"
    p.write_text(json.dumps(MINIMAL_JSON))
    return p


@pytest.fixture
def full_json_file(tmp_path: Path) -> Path:
    """Create a temporary JSON file with full known good data."""
    p = tmp_path / "known_good.json"
    p.write_text(json.dumps(FULL_JSON))
    return p


# ---------------------------------------------------------------------------
# Fixtures - KnownGood objects
# ---------------------------------------------------------------------------


@pytest.fixture
def minimal_known_good() -> KnownGood:
    """Create a minimal KnownGood instance."""
    return make_known_good()


@pytest.fixture
def multi_group_known_good() -> KnownGood:
    """Create a KnownGood instance with multiple groups."""
    m1 = Module.from_dict(
        "score_baselibs",
        {
            "repo": "https://github.com/eclipse-score/baselibs.git",
            "hash": "aaa",
        },
    )
    m2 = Module.from_dict(
        "score_crates",
        {
            "repo": "https://github.com/eclipse-score/score-crates.git",
            "hash": "bbb",
        },
    )
    return KnownGood(
        modules={
            "target_sw": {"score_baselibs": m1},
            "tooling": {"score_crates": m2},
        },
        timestamp="2026-02-01T00:00:00+00:00Z",
    )


@pytest.fixture
def real_known_good() -> KnownGood:
    """Load the actual known_good.json from the repository root."""
    return load_known_good(KNOWN_GOOD_JSON)


# ---------------------------------------------------------------------------
# Fixtures - Test data for check_approvals
# ---------------------------------------------------------------------------


@pytest.fixture
def modules_maintainers():
    """Sample modules and maintainers for testing."""
    return {
        "module_a": [
            {
                "name": "Alice Developer",
                "email": "alice@example.com",
                "github": "alice",
                "github_user_id": 100,
            },
            {
                "name": "Bob Developer",
                "email": "bob@example.com",
                "github": "bob",
                "github_user_id": 101,
            },
        ],
        "module_b": [
            {
                "name": "Charlie Developer",
                "email": "charlie@example.com",
                "github": "charlie",
                "github_user_id": 102,
            }
        ],
        "module_c": [
            {
                "name": "Diana Developer",
                "email": "diana@example.com",
                "github": "diana",
                "github_user_id": 103,
            },
            {
                "name": "Eve Developer",
                "email": "eve@example.com",
                "github": "eve",
                "github_user_id": 104,
            },
        ],
    }
