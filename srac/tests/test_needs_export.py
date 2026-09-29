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
"""Tests for the read-only Sphinx-needs projection."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest

from srac.tools.export_needs import build_assertion, build_reference_manifest
from srac.tools.profile import build_enrichment_report, validate_assertion, validate_report

SRAC_ROOT = Path(__file__).parents[1]
NEEDS_PATH = SRAC_ROOT / "examples" / "needs" / "communication.needs.json"
CONFIG_PATH = SRAC_ROOT / "examples" / "needs" / "communication.export.json"
GENERATED_PATH = SRAC_ROOT / "examples" / "generated" / "communication.srac.json"
REFERENCE_PATH = SRAC_ROOT / "examples" / "generated" / "communication.sbom-reference.json"


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_checked_in_needs_projection_is_reproducible() -> None:
    generated = build_assertion(_read(NEEDS_PATH), _read(CONFIG_PATH), _sha256(NEEDS_PATH))

    assert generated == _read(GENERATED_PATH)
    assert validate_assertion(generated) == []
    assert generated["safetyRelevance"] == {
        "status": "safety-related",
        "classification": "ASIL-B",
    }
    assert generated["sourceOfTruth"] == {
        "system": "sphinx-needs",
        "documentUri": "https://eclipse-score.github.io/score/main/needs.json",
        "version": "0.1",
        "rootElement": "comp__com_configuration",
        "rootElementType": "comp",
        "rootElementStatus": "valid",
        "includedElements": ["feat__com_communication", "aou_req__communication__1"],
        "sha256": _sha256(NEEDS_PATH),
    }
    assert [item["id"] for item in generated["requirements"]] == ["aou_req__communication__1"]
    assert [item["id"] for item in generated["evidence"]] == [
        "comp__com_configuration",
        "feat__com_communication",
    ]
    assert generated["assertion"]["status"] == "draft"
    assert generated["assertion"]["reviewer"] is None


def test_needs_projection_fails_closed_when_safety_is_missing() -> None:
    needs = _read(NEEDS_PATH)
    del needs["versions"]["0.1"]["needs"]["comp__com_configuration"]["safety"]

    generated = build_assertion(needs, _read(CONFIG_PATH), "a" * 64)

    assert generated["safetyRelevance"] == {
        "status": "undetermined",
        "classification": "not-assigned",
    }


def test_needs_projection_rejects_conflicting_source_safety_fields() -> None:
    needs = _read(NEEDS_PATH)
    needs["versions"]["0.1"]["needs"]["comp__com_configuration"]["safety_relevant"] = "NO"

    with pytest.raises(ValueError, match="conflicting safety and safety_relevant"):
        build_assertion(needs, _read(CONFIG_PATH), "a" * 64)


def test_reference_manifest_is_reproducible_and_integrity_protected() -> None:
    expected = _read(REFERENCE_PATH)

    assert build_reference_manifest(_read(CONFIG_PATH), _sha256(GENERATED_PATH)) == expected
    assert expected["artifact"]["sha256"] == _sha256(GENERATED_PATH)
    assert expected["cycloneDx16ExternalReference"]["hashes"][0]["content"] == _sha256(GENERATED_PATH)
    assert expected["spdx23PackageExternalRef"]["referenceCategory"] == "OTHER"


def test_enrichment_report_preserves_needs_source_of_truth() -> None:
    assertion = _read(GENERATED_PATH)
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "components": [
            {
                "bom-ref": "score-communication",
                "name": "score_communication",
                "version": assertion["subject"]["version"],
                "purl": "pkg:github/eclipse-score/communication@" + assertion["subject"]["version"],
            }
        ],
    }
    report = build_enrichment_report(
        assertion,
        sbom,
        integrity={
            "algorithm": "SHA-256",
            "assertionSha256": "a" * 64,
            "sbomSha256": "b" * 64,
        },
    )

    assert report["matchStatus"] == "matched"
    assert report["sourceOfTruth"] == assertion["sourceOfTruth"]
    assert validate_report(report) == []


def test_source_of_truth_digest_is_validated() -> None:
    assertion = deepcopy(_read(GENERATED_PATH))
    assertion["sourceOfTruth"]["sha256"] = "not-a-digest"

    assert "sourceOfTruth.sha256 must be a lowercase SHA-256 digest" in validate_assertion(assertion)
