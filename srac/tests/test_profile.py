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
import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest

from srac.tools.profile import build_enrichment_report, match_assertion_to_sbom, validate_assertion, validate_report

SRAC_ROOT = Path(__file__).parents[1]
REPOSITORY_ROOT = SRAC_ROOT.parent


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def assertion() -> dict:
    return json.loads((SRAC_ROOT / "examples" / "persistency-kvs.srac.json").read_text(encoding="utf-8"))


def test_example_satisfies_core_profile(assertion: dict) -> None:
    assert validate_assertion(assertion) == []


def test_missing_evidence_is_rejected(assertion: dict) -> None:
    invalid = deepcopy(assertion)
    invalid["evidence"] = []
    assert "evidence must contain at least one item" in validate_assertion(invalid)


def test_unapproved_example_does_not_claim_a_classification(assertion: dict) -> None:
    assert assertion["safetyRelevance"] == {
        "status": "undetermined",
        "classification": "not-assigned",
    }
    assert assertion["assertion"]["status"] == "draft"
    assert assertion["assertion"]["reviewer"] is None


def test_report_carries_unapproved_safety_state_from_assertion(assertion: dict) -> None:
    sbom = {"spdxVersion": "SPDX-2.3", "packages": []}
    integrity = {
        "algorithm": "SHA-256",
        "assertionSha256": "a" * 64,
        "sbomSha256": "b" * 64,
    }

    report = build_enrichment_report(assertion, sbom, integrity=integrity)

    assert report["safetyAssessment"] == {
        "source": "assertion",
        "safetyRelevance": "undetermined",
        "classification": "not-assigned",
        "assertionStatus": "draft",
        "reviewer": None,
    }
    assert validate_report(report) == []


def test_matches_spdx_module_purl_while_preserving_component_scope(assertion: dict) -> None:
    sbom = {
        "spdxVersion": "SPDX-2.3",
        "packages": [
            {
                "SPDXID": "SPDXRef-score-persistency",
                "name": "score_persistency",
                "versionInfo": assertion["subject"]["version"],
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": ("pkg:github/eclipse-score/persistency@" + assertion["subject"]["version"]),
                    }
                ],
            }
        ],
    }

    matches = match_assertion_to_sbom(assertion, sbom)

    assert matches == [
        {
            "format": "SPDX-2.3",
            "identifier": "SPDXRef-score-persistency",
            "name": "score_persistency",
            "version": assertion["subject"]["version"],
            "purl": "pkg:github/eclipse-score/persistency@" + assertion["subject"]["version"],
        }
    ]
    assert assertion["subject"]["componentPath"] == "score/kvs"


def test_matches_cyclonedx_component_by_purl_and_version(assertion: dict) -> None:
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "components": [
            {
                "bom-ref": "score_persistency",
                "name": "score_persistency",
                "version": assertion["subject"]["version"],
                "purl": "pkg:github/eclipse-score/persistency@" + assertion["subject"]["version"],
            }
        ],
    }

    assert len(match_assertion_to_sbom(assertion, sbom)) == 1


def test_different_version_does_not_match(assertion: dict) -> None:
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "components": [
            {
                "bom-ref": "score_persistency",
                "name": "score_persistency",
                "version": "different-version",
                "purl": "pkg:github/eclipse-score/persistency@different-version",
            }
        ],
    }

    report = build_enrichment_report(assertion, sbom)

    assert report["matchStatus"] == "unmatched"
    assert report["matchedComponents"] == []


def test_known_good_resolves_real_sbom_unknown_version(assertion: dict) -> None:
    sbom = {
        "spdxVersion": "SPDX-2.3",
        "packages": [
            {
                "SPDXID": "SPDXRef-score-persistency-unknown",
                "name": "score_persistency",
                "versionInfo": "unknown",
                "externalRefs": [
                    {
                        "referenceType": "purl",
                        "referenceLocator": "pkg:github/eclipse-score/score_persistency@unknown",
                    }
                ],
            }
        ],
    }
    known_good = {
        "modules": {
            "target_sw": {
                "score_persistency": {
                    "repo": "https://github.com/eclipse-score/persistency.git",
                    "hash": assertion["subject"]["version"],
                }
            }
        }
    }

    report = build_enrichment_report(assertion, sbom, known_good)

    assert report["matchStatus"] == "matched"
    assert report["bindingEvidence"] == {
        "strategy": "score-known-good",
        "module": "score_persistency",
        "repository": "https://github.com/eclipse-score/persistency.git",
        "hash": assertion["subject"]["version"],
    }


def test_known_good_hash_mismatch_does_not_resolve_unknown_version(assertion: dict) -> None:
    sbom = {
        "spdxVersion": "SPDX-2.3",
        "packages": [
            {
                "SPDXID": "SPDXRef-score-persistency-unknown",
                "name": "score_persistency",
                "versionInfo": "unknown",
                "externalRefs": [
                    {
                        "referenceType": "purl",
                        "referenceLocator": "pkg:github/eclipse-score/score_persistency@unknown",
                    }
                ],
            }
        ],
    }
    known_good = {
        "modules": {
            "target_sw": {
                "score_persistency": {
                    "repo": "https://github.com/eclipse-score/persistency.git",
                    "hash": "different-version",
                }
            }
        }
    }

    assert build_enrichment_report(assertion, sbom, known_good)["matchStatus"] == "unmatched"


def test_checked_in_persistency_pilot_matches_real_sbom(assertion: dict) -> None:
    assertion_path = SRAC_ROOT / "examples" / "persistency-kvs.srac.json"
    sbom_path = SRAC_ROOT / "pilot" / "persistency-kvs" / "input" / "reference-integration.spdx.json"
    known_good_path = REPOSITORY_ROOT / "known_good.json"
    sbom = json.loads(sbom_path.read_text(encoding="utf-8"))
    known_good = json.loads(known_good_path.read_text(encoding="utf-8"))
    expected_report = json.loads(
        (SRAC_ROOT / "pilot" / "persistency-kvs" / "output" / "persistency-kvs.srac-report.json").read_text(
            encoding="utf-8"
        )
    )

    integrity = {
        "algorithm": "SHA-256",
        "assertionSha256": _sha256(assertion_path),
        "sbomSha256": _sha256(sbom_path),
        "knownGoodSha256": _sha256(known_good_path),
    }
    report = build_enrichment_report(assertion, sbom, known_good, integrity)

    assert report == expected_report
    assert validate_report(report) == []
    assert report["matchStatus"] == "matched"
    assert report["matchedComponents"] == [
        {
            "format": "SPDX-2.3",
            "identifier": "SPDXRef-score-persistency-unknown",
            "name": "score_persistency",
            "version": "unknown",
            "purl": "pkg:github/eclipse-score/score_persistency@unknown",
        }
    ]
    assert report["bindingEvidence"]["hash"] == assertion["subject"]["version"]


def test_invalid_report_digest_is_rejected(assertion: dict) -> None:
    report = build_enrichment_report(
        assertion,
        {"spdxVersion": "SPDX-2.3", "packages": []},
        integrity={
            "algorithm": "SHA-256",
            "assertionSha256": "not-a-digest",
            "sbomSha256": "b" * 64,
        },
    )

    assert "integrity.assertionSha256 must be a lowercase SHA-256 digest" in validate_report(report)


def test_report_schema_is_checked_in() -> None:
    schema = json.loads((SRAC_ROOT / "schema" / "srac-report.schema.json").read_text(encoding="utf-8"))

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert "safetyAssessment" in schema["required"]
    assert "integrity" in schema["required"]
