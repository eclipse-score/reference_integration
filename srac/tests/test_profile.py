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
import json
from copy import deepcopy
from pathlib import Path

import pytest

from srac.tools.profile import build_enrichment_report, match_assertion_to_sbom, validate_assertion

SRAC_ROOT = Path(__file__).parents[1]


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
                        "referenceLocator": (
                            "pkg:github/eclipse-score/persistency@" + assertion["subject"]["version"]
                        ),
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
