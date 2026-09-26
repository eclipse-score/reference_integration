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


@pytest.fixture
def synthetic_reviewed_assertion() -> dict:
    return json.loads((SRAC_ROOT / "examples" / "synthetic-safety-related.srac.json").read_text(encoding="utf-8"))


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


def test_synthetic_reviewed_example_shows_complete_safety_related_flow(
    synthetic_reviewed_assertion: dict,
) -> None:
    assert validate_assertion(synthetic_reviewed_assertion) == []
    assert "Synthetic and illustrative example only" in synthetic_reviewed_assertion["rationale"]

    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "components": [
            {
                "bom-ref": "synthetic-brake-monitor",
                "name": "synthetic-brake-monitor",
                "version": "1.0.0",
                "purl": "pkg:generic/synthetic-brake-monitor@1.0.0",
            }
        ],
    }
    integrity = {
        "algorithm": "SHA-256",
        "assertionSha256": "a" * 64,
        "sbomSha256": "b" * 64,
    }

    report = build_enrichment_report(synthetic_reviewed_assertion, sbom, integrity=integrity)

    assert report["matchStatus"] == "matched"
    assert report["impactAnalysis"] == synthetic_reviewed_assertion["impactAnalysis"]
    analysis = report["impactAnalysis"][0]
    assert analysis["impactAnalysisStatus"] == "complete"
    assert analysis["impactLevel"] == "safetyImpact"
    assert analysis["safetyIntegrityLevel"] == "asilB"
    assert analysis["decisions"][0]["originatedBy"]["name"] == "Synthetic Example Safety Reviewer"
    assert analysis["requirementVerification"][0]["verifies"] == ["synthetic-req-001"]
    assert analysis["bundle"]["rootElement"] == [
        "synthetic-sia-configuration-change-001",
        "synthetic-decision-approve-001",
        "synthetic-verification-001",
    ]
    assert report["safetyAssessment"] == {
        "source": "assertion",
        "safetyRelevance": "safety-related",
        "classification": "ASIL-B",
        "assertionStatus": "reviewed",
        "reviewer": {
            "name": "Synthetic Example Safety Reviewer",
            "uri": "https://example.com/srac/people/synthetic-reviewer",
        },
    }
    assert validate_report(report) == []


def test_unmatched_report_still_carries_impact_analysis_without_reinterpreting_it(
    synthetic_reviewed_assertion: dict,
) -> None:
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "components": [
            {
                "bom-ref": "different-component",
                "name": "different-component",
                "version": "2.0.0",
                "purl": "pkg:generic/different-component@2.0.0",
            }
        ],
    }
    report = build_enrichment_report(
        synthetic_reviewed_assertion,
        sbom,
        integrity={
            "algorithm": "SHA-256",
            "assertionSha256": "a" * 64,
            "sbomSha256": "b" * 64,
        },
    )

    assert report["matchStatus"] == "unmatched"
    assert report["matchedComponents"] == []
    assert report["impactAnalysis"] == synthetic_reviewed_assertion["impactAnalysis"]
    assert validate_report(report) == []


@pytest.mark.parametrize(
    ("field_path", "invalid_value", "expected_error"),
    [
        (
            ("impactAnalysisStatus",),
            "pending",
            "impactAnalysis[0].impactAnalysisStatus must be one of",
        ),
        (("impactLevel",), "critical", "impactAnalysis[0].impactLevel must be one of"),
        (
            ("safetyIntegrityLevel",),
            "ASIL-B",
            "impactAnalysis[0].safetyIntegrityLevel must be one of",
        ),
        (
            ("decisions", 0, "decisionType"),
            "accept",
            "impactAnalysis[0].decisions[0].decisionType must be one of",
        ),
        (
            ("decisions", 0, "decisionStatus"),
            "approved",
            "impactAnalysis[0].decisions[0].decisionStatus must be one of",
        ),
    ],
)
def test_impact_analysis_rejects_values_outside_spdx_vocabularies(
    synthetic_reviewed_assertion: dict,
    field_path: tuple[str | int, ...],
    invalid_value: str,
    expected_error: str,
) -> None:
    invalid = deepcopy(synthetic_reviewed_assertion)
    target = invalid["impactAnalysis"][0]
    for key in field_path[:-1]:
        target = target[key]
    target[field_path[-1]] = invalid_value

    assert any(error.startswith(expected_error) for error in validate_assertion(invalid))


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
    assert report["integrity"]["knownGoodSha256"] == _sha256(known_good_path)
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
    assert "impactAnalysis" not in report


def test_checked_in_pilot_integrity_matches_live_lf_files() -> None:
    pilot_root = SRAC_ROOT / "pilot" / "persistency-kvs"
    report_path = pilot_root / "output" / "persistency-kvs.srac-report.json"
    checksum_path = pilot_root / "output" / "persistency-kvs.srac-report.sha256"
    known_good_path = REPOSITORY_ROOT / "known_good.json"
    assertion_path = SRAC_ROOT / "examples" / "persistency-kvs.srac.json"
    sbom_path = pilot_root / "input" / "reference-integration.spdx.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    provenance = json.loads((pilot_root / "provenance.json").read_text(encoding="utf-8"))

    assert report["integrity"]["knownGoodSha256"] == _sha256(known_good_path)
    assert provenance["integrity"]["assertionSha256"] == _sha256(assertion_path)
    assert provenance["sha256"] == _sha256(sbom_path)
    assert provenance["integrity"]["knownGoodSha256"] == _sha256(known_good_path)
    assert provenance["integrity"]["reportSha256"] == _sha256(report_path)
    assert checksum_path.read_text(encoding="utf-8") == f"{_sha256(report_path)}  {report_path.name}\n"


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
    assertion_schema = json.loads((SRAC_ROOT / "schema" / "srac.schema.json").read_text(encoding="utf-8"))

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["properties"]["schemaVersion"] == {"const": "0.2-draft"}
    assert "impactAnalysis" in schema["properties"]
    assert "safetyAssessment" in schema["required"]
    assert "integrity" in schema["required"]
    assert assertion_schema["properties"]["schemaVersion"] == {"const": "0.2-draft"}
    assert "impactAnalysis" in assertion_schema["properties"]


def test_persistency_evidence_metrics_are_pinned_and_non_authoritative() -> None:
    metrics = json.loads(
        (SRAC_ROOT / "pilot" / "persistency-kvs" / "evidence-metrics.json").read_text(encoding="utf-8")
    )

    assert metrics["subject"]["revision"] == "9ae529ba9f413976ff5c9948c6490afa51bbfdc3"
    assert metrics["unsafeRust"]["unsafeKeywordOccurrences"] == 0
    assert metrics["interfaceComplexity"]["cpp"]["callableInterfaces"] == 46
    assert metrics["interfaceComplexity"]["cpp"]["parameterMaximum"] == 4
    assert metrics["interfaceComplexity"]["rust"]["callableInterfaces"] == 46
    assert metrics["interfaceComplexity"]["rust"]["parameterMaximum"] == 3
    assert metrics["requirementsTraceability"]["componentRequirements"] == 35
    assert metrics["requirementsTraceability"]["requirementsDirectlyReferencedByPythonTestMetadata"] == 15
    assert len(metrics["requirementsTraceability"]["directlyReferenced"]) == 15
    assert len(metrics["requirementsTraceability"]["withoutDirectReference"]) == 20
    assert set(metrics["requirementsTraceability"]["directlyReferenced"]).isdisjoint(
        metrics["requirementsTraceability"]["withoutDirectReference"]
    )
    assert metrics["coverage"]["workflowRun"].endswith("/32867923248")
    assert metrics["coverage"]["configuredThresholdPercent"] == 0

    traceability = (SRAC_ROOT / "pilot" / "persistency-kvs" / "requirements-traceability.md").read_text(
        encoding="utf-8"
    )
    assert traceability.count("| `comp_req__kvs__") == 35
