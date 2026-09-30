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
"""Tests for receiving SRAC through SPDX and CycloneDX external references."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from srac.tools.receive_srac import (
    build_received_report,
    discover_srac_references,
    load_referenced_assertion,
)

GENERATED_ROOT = Path(__file__).parents[1] / "examples" / "generated"
SPDX_PATH = GENERATED_ROOT / "communication.spdx.json"
CYCLONEDX_PATH = GENERATED_ROOT / "communication.cdx.json"


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("sbom_path", "expected_format", "expected_identifier"),
    [
        (SPDX_PATH, "SPDX", "SPDXRef-score-communication-configuration"),
        (CYCLONEDX_PATH, "CycloneDX", "score-communication-configuration"),
    ],
)
def test_receiver_discovers_verifies_and_correlates_referenced_assertion(
    sbom_path: Path,
    expected_format: str,
    expected_identifier: str,
) -> None:
    report = build_received_report(sbom_path, GENERATED_ROOT)

    assert report["matchStatus"] == "matched"
    assert report["discoveredReference"] == {
        "format": expected_format,
        "componentIdentifier": expected_identifier,
        "uri": "https://example.org/srac/communication.srac.json",
        "sha256": "2108209f8a367eb370de5082b034ac015d6c9df9606c7a065c974d5c08344eea",
    }
    assert report["safetyAssessment"] == {
        "source": "assertion",
        "safetyRelevance": "safety-related",
        "classification": "ASIL-B",
        "assertionStatus": "draft",
        "reviewer": None,
    }


def test_receiver_rejects_digest_mismatch() -> None:
    sbom = _read(SPDX_PATH)
    sbom["packages"][0]["externalRefs"][1]["comment"] = f"SRAC sidecar; SHA-256: {'0' * 64}"

    with pytest.raises(ValueError, match="SRAC artifact SHA-256 mismatch"):
        load_referenced_assertion(sbom, GENERATED_ROOT)


def test_receiver_accepts_bazel_runfile_style_artifact_symlink(tmp_path: Path) -> None:
    artifact = tmp_path / "communication.srac.json"
    try:
        artifact.symlink_to((GENERATED_ROOT / artifact.name).resolve())
    except OSError as error:
        pytest.skip(f"symlinks are unavailable on this platform: {error}")

    assertion, _, resolved_artifact = load_referenced_assertion(_read(SPDX_PATH), tmp_path)

    assert assertion["id"] == "srac-score-communication-configuration"
    assert resolved_artifact == artifact.absolute()


def test_receiver_rejects_missing_reference() -> None:
    sbom = _read(CYCLONEDX_PATH)
    del sbom["components"][0]["externalReferences"]

    with pytest.raises(ValueError, match="no integrity-protected SRAC external reference"):
        load_referenced_assertion(sbom, GENERATED_ROOT)


def test_receiver_rejects_ambiguous_references() -> None:
    sbom = _read(CYCLONEDX_PATH)
    duplicate = deepcopy(sbom["components"][0])
    duplicate["bom-ref"] = "second-component"
    sbom["components"].append(duplicate)

    assert len(discover_srac_references(sbom)) == 2
    with pytest.raises(ValueError, match="refusing ambiguous selection"):
        load_referenced_assertion(sbom, GENERATED_ROOT)
