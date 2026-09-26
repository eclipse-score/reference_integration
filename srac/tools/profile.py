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
"""Validation and SBOM matching for the experimental SRAC sidecar profile."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from copy import deepcopy
from typing import Any
from urllib.parse import urlparse

SCHEMA_VERSION = "0.2-draft"
TOOL_VERSION = "0.2.0-draft"
RELEVANCE_VALUES = {"safety-related", "not-safety-related", "undetermined"}
CLASSIFICATION_VALUES = {"QM", "ASIL-A", "ASIL-B", "ASIL-C", "ASIL-D", "not-assigned"}
ASSERTION_STATUS_VALUES = {"draft", "under-review", "reviewed", "approved", "superseded", "withdrawn"}
IMPACT_ANALYSIS_STATUS_VALUES = {"new", "inProgress", "complete", "stopped", "duplicate", "other"}
IMPACT_LEVEL_VALUES = {
    "noCriticalImpact",
    "safetyImpact",
    "securityImpact",
    "safetyAndSecurityImpact",
    "qualityImpact",
    "availabilityImpact",
    "customerSatisfactionImpact",
    "other",
}
DECISION_TYPE_VALUES = {
    "approve",
    "approveConditionally",
    "reject",
    "defer",
    "delegate",
    "requestChange",
    "requestInformation",
    "noAction",
    "close",
    "duplicate",
    "other",
}
DECISION_STATUS_VALUES = {
    "proposed",
    "requested",
    "inProgress",
    "recorded",
    "superseded",
    "withdrawn",
    "enteredInError",
    "other",
}
SAFETY_INTEGRITY_LEVEL_VALUES = {
    "qm",
    "asilA",
    "asilB",
    "asilC",
    "asilD",
    "sil1",
    "sil2",
    "sil3",
    "sil4",
    "dalA",
    "dalB",
    "dalC",
    "dalD",
    "dalE",
    "other",
    "noAssertion",
}
CLASSIFICATION_TO_SAFETY_INTEGRITY_LEVEL = {
    "QM": "qm",
    "ASIL-A": "asilA",
    "ASIL-B": "asilB",
    "ASIL-C": "asilC",
    "ASIL-D": "asilD",
    "not-assigned": "noAssertion",
}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _require_mapping(document: Mapping[str, Any], key: str, errors: list[str]) -> Mapping[str, Any]:
    value = document.get(key)
    if not isinstance(value, Mapping):
        errors.append(f"{key} must be an object")
        return {}
    return value


def _validate_references(value: object, path: str, errors: list[str], *, require_one: bool) -> None:
    if not isinstance(value, list):
        errors.append(f"{path} must be an array")
        return
    if require_one and not value:
        errors.append(f"{path} must contain at least one item")
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append(f"{path}[{index}] must be an object")
            continue
        for key in ("id", "type", "uri"):
            if not _is_non_empty_string(item.get(key)):
                errors.append(f"{path}[{index}].{key} must be a non-empty string")


def _validate_identifier_list(value: object, path: str, errors: list[str], *, require_one: bool = False) -> None:
    if not isinstance(value, list):
        errors.append(f"{path} must be an array")
        return
    if require_one and not value:
        errors.append(f"{path} must contain at least one item")
    for index, item in enumerate(value):
        if not _is_non_empty_string(item):
            errors.append(f"{path}[{index}] must be a non-empty string")


def _validate_resolved_identifiers(
    value: object, path: str, errors: list[str], resolvable_ids: set[str] | None
) -> None:
    if resolvable_ids is None or not isinstance(value, list):
        return
    for index, identifier in enumerate(value):
        if _is_non_empty_string(identifier) and identifier not in resolvable_ids:
            errors.append(f"{path}[{index}] references {identifier!r}, which does not resolve to an assertion element")


def _validate_impact_analysis(
    value: object,
    path: str,
    errors: list[str],
    *,
    classification: object = None,
    resolvable_ids: set[str] | None = None,
) -> None:
    if not isinstance(value, list):
        errors.append(f"{path} must be an array")
        return
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if not isinstance(item, Mapping):
            errors.append(f"{item_path} must be an object")
            continue
        if not _is_non_empty_string(item.get("id")):
            errors.append(f"{item_path}.id must be a non-empty string")

        trigger = item.get("trigger")
        if not isinstance(trigger, Mapping):
            errors.append(f"{item_path}.trigger must be an object")
        else:
            for key in ("type", "uri"):
                if not _is_non_empty_string(trigger.get(key)):
                    errors.append(f"{item_path}.trigger.{key} must be a non-empty string")

        if item.get("impactAnalysisStatus") not in IMPACT_ANALYSIS_STATUS_VALUES:
            errors.append(f"{item_path}.impactAnalysisStatus must be one of {sorted(IMPACT_ANALYSIS_STATUS_VALUES)}")
        impact_level = item.get("impactLevel")
        if impact_level is not None and impact_level not in IMPACT_LEVEL_VALUES:
            errors.append(f"{item_path}.impactLevel must be one of {sorted(IMPACT_LEVEL_VALUES)}")
        safety_integrity_level = item.get("safetyIntegrityLevel")
        if safety_integrity_level is not None and safety_integrity_level not in SAFETY_INTEGRITY_LEVEL_VALUES:
            errors.append(f"{item_path}.safetyIntegrityLevel must be one of {sorted(SAFETY_INTEGRITY_LEVEL_VALUES)}")
        expected_safety_integrity_level = CLASSIFICATION_TO_SAFETY_INTEGRITY_LEVEL.get(classification)
        if (
            safety_integrity_level is not None
            and expected_safety_integrity_level is not None
            and safety_integrity_level != expected_safety_integrity_level
        ):
            errors.append(
                f"{item_path}.safetyIntegrityLevel must be {expected_safety_integrity_level!r} "
                f"when safety relevance classification is {classification!r}"
            )

        process = item.get("impactAnalysisProcess")
        if process is not None and (not isinstance(process, Mapping) or not _is_non_empty_string(process.get("uri"))):
            errors.append(f"{item_path}.impactAnalysisProcess.uri must be a non-empty string")

        for key in ("impactedElement", "addedElement", "modifiedElement", "removedElement"):
            _validate_identifier_list(item.get(key), f"{item_path}.{key}", errors)
            _validate_resolved_identifiers(item.get(key), f"{item_path}.{key}", errors, resolvable_ids)

        decisions = item.get("decisions")
        if not isinstance(decisions, list):
            errors.append(f"{item_path}.decisions must be an array")
            continue
        for decision_index, decision in enumerate(decisions):
            decision_path = f"{item_path}.decisions[{decision_index}]"
            if not isinstance(decision, Mapping):
                errors.append(f"{decision_path} must be an object")
                continue
            if decision.get("decisionType") not in DECISION_TYPE_VALUES:
                errors.append(f"{decision_path}.decisionType must be one of {sorted(DECISION_TYPE_VALUES)}")
            if decision.get("decisionStatus") not in DECISION_STATUS_VALUES:
                errors.append(f"{decision_path}.decisionStatus must be one of {sorted(DECISION_STATUS_VALUES)}")
            _validate_identifier_list(decision.get("appliesTo"), f"{decision_path}.appliesTo", errors, require_one=True)
            _validate_resolved_identifiers(
                decision.get("appliesTo"), f"{decision_path}.appliesTo", errors, resolvable_ids
            )
            originated_by = decision.get("originatedBy")
            if originated_by is not None and (
                not isinstance(originated_by, Mapping) or not _is_non_empty_string(originated_by.get("name"))
            ):
                errors.append(f"{decision_path}.originatedBy.name must be a non-empty string or null")
            if not _is_non_empty_string(decision.get("rationale")):
                errors.append(f"{decision_path}.rationale must be a non-empty string")

        verification = item.get("requirementVerification")
        if verification is not None:
            if not isinstance(verification, list):
                errors.append(f"{item_path}.requirementVerification must be an array")
            else:
                for verification_index, verification_item in enumerate(verification):
                    verification_path = f"{item_path}.requirementVerification[{verification_index}]"
                    if not isinstance(verification_item, Mapping):
                        errors.append(f"{verification_path} must be an object")
                        continue
                    if not _is_non_empty_string(verification_item.get("id")):
                        errors.append(f"{verification_path}.id must be a non-empty string")
                    _validate_identifier_list(
                        verification_item.get("verifies"),
                        f"{verification_path}.verifies",
                        errors,
                        require_one=True,
                    )
                    _validate_resolved_identifiers(
                        verification_item.get("verifies"),
                        f"{verification_path}.verifies",
                        errors,
                        resolvable_ids,
                    )
                    _validate_identifier_list(
                        verification_item.get("evidence"), f"{verification_path}.evidence", errors
                    )
                    _validate_resolved_identifiers(
                        verification_item.get("evidence"),
                        f"{verification_path}.evidence",
                        errors,
                        resolvable_ids,
                    )

        bundle = item.get("bundle")
        if bundle is not None:
            if not isinstance(bundle, Mapping):
                errors.append(f"{item_path}.bundle must be an object")
            else:
                if not _is_non_empty_string(bundle.get("id")):
                    errors.append(f"{item_path}.bundle.id must be a non-empty string")
                _validate_identifier_list(
                    bundle.get("rootElement"), f"{item_path}.bundle.rootElement", errors, require_one=True
                )
                _validate_resolved_identifiers(
                    bundle.get("rootElement"), f"{item_path}.bundle.rootElement", errors, resolvable_ids
                )


def _assertion_element_ids(document: Mapping[str, Any], errors: list[str]) -> set[str]:
    identifiers: list[str] = []
    for key in ("requirements", "evidence"):
        value = document.get(key)
        if isinstance(value, list):
            identifiers.extend(
                str(item["id"]) for item in value if isinstance(item, Mapping) and _is_non_empty_string(item.get("id"))
            )
    impact_analysis = document.get("impactAnalysis")
    if isinstance(impact_analysis, list):
        for analysis in impact_analysis:
            if not isinstance(analysis, Mapping):
                continue
            if _is_non_empty_string(analysis.get("id")):
                identifiers.append(str(analysis["id"]))
            for key in ("decisions", "requirementVerification"):
                value = analysis.get(key)
                if isinstance(value, list):
                    identifiers.extend(
                        str(item["id"])
                        for item in value
                        if isinstance(item, Mapping) and _is_non_empty_string(item.get("id"))
                    )
    duplicates = sorted({identifier for identifier in identifiers if identifiers.count(identifier) > 1})
    for identifier in duplicates:
        errors.append(f"assertion element id {identifier!r} is defined more than once")
    return set(identifiers)


def validate_assertion(document: Mapping[str, Any]) -> list[str]:
    """Validate the core constraints also expressed by ``srac.schema.json``.

    The PoC deliberately has no runtime dependency on a particular JSON Schema
    implementation. Consumers should use the published schema with their
    standard validator; this function keeps the Bazel pilot self-contained.
    """

    errors: list[str] = []
    if document.get("schemaVersion") != SCHEMA_VERSION:
        errors.append(f"schemaVersion must be {SCHEMA_VERSION!r}")
    if not _is_non_empty_string(document.get("assertionId")):
        errors.append("assertionId must be a non-empty string")

    subject = _require_mapping(document, "subject", errors)
    for key in ("name", "purl", "version"):
        if not _is_non_empty_string(subject.get(key)):
            errors.append(f"subject.{key} must be a non-empty string")
    if _is_non_empty_string(subject.get("purl")) and not str(subject["purl"]).startswith("pkg:"):
        errors.append("subject.purl must start with 'pkg:'")

    relevance = _require_mapping(document, "safetyRelevance", errors)
    if relevance.get("status") not in RELEVANCE_VALUES:
        errors.append(f"safetyRelevance.status must be one of {sorted(RELEVANCE_VALUES)}")
    if relevance.get("classification") not in CLASSIFICATION_VALUES:
        errors.append(f"safetyRelevance.classification must be one of {sorted(CLASSIFICATION_VALUES)}")

    if not _is_non_empty_string(document.get("rationale")):
        errors.append("rationale must be a non-empty string")
    if "requirements" in document:
        _validate_references(document["requirements"], "requirements", errors, require_one=False)
    _validate_references(document.get("evidence"), "evidence", errors, require_one=True)
    if "impactAnalysis" in document:
        _validate_impact_analysis(
            document["impactAnalysis"],
            "impactAnalysis",
            errors,
            classification=relevance.get("classification"),
            resolvable_ids=_assertion_element_ids(document, errors),
        )

    assertion = _require_mapping(document, "assertion", errors)
    if assertion.get("status") not in ASSERTION_STATUS_VALUES:
        errors.append(f"assertion.status must be one of {sorted(ASSERTION_STATUS_VALUES)}")
    author = assertion.get("author")
    if not isinstance(author, Mapping) or not _is_non_empty_string(author.get("name")):
        errors.append("assertion.author.name must be a non-empty string")
    if not _is_non_empty_string(assertion.get("created")):
        errors.append("assertion.created must be a non-empty date-time string")
    return errors


def validate_report(document: Mapping[str, Any]) -> list[str]:
    """Validate the core constraints expressed by ``srac-report.schema.json``."""

    errors: list[str] = []
    if document.get("schemaVersion") != SCHEMA_VERSION:
        errors.append(f"schemaVersion must be {SCHEMA_VERSION!r}")
    if document.get("sourceFormat") not in {"SPDX", "CycloneDX"}:
        errors.append("sourceFormat must be 'SPDX' or 'CycloneDX'")
    if document.get("matchStatus") not in {"matched", "unmatched"}:
        errors.append("matchStatus must be 'matched' or 'unmatched'")
    if not isinstance(document.get("matchedComponents"), list):
        errors.append("matchedComponents must be an array")

    safety = _require_mapping(document, "safetyAssessment", errors)
    if safety.get("source") != "assertion":
        errors.append("safetyAssessment.source must be 'assertion'")
    if safety.get("safetyRelevance") not in RELEVANCE_VALUES:
        errors.append(f"safetyAssessment.safetyRelevance must be one of {sorted(RELEVANCE_VALUES)}")
    if safety.get("classification") not in CLASSIFICATION_VALUES:
        errors.append(f"safetyAssessment.classification must be one of {sorted(CLASSIFICATION_VALUES)}")
    if safety.get("assertionStatus") not in ASSERTION_STATUS_VALUES:
        errors.append(f"safetyAssessment.assertionStatus must be one of {sorted(ASSERTION_STATUS_VALUES)}")
    if "impactAnalysis" in document:
        _validate_impact_analysis(
            document["impactAnalysis"], "impactAnalysis", errors, classification=safety.get("classification")
        )

    generator = _require_mapping(document, "generator", errors)
    for key in ("name", "version"):
        if not _is_non_empty_string(generator.get(key)):
            errors.append(f"generator.{key} must be a non-empty string")

    integrity = _require_mapping(document, "integrity", errors)
    if integrity.get("algorithm") != "SHA-256":
        errors.append("integrity.algorithm must be 'SHA-256'")
    for key in ("assertionSha256", "sbomSha256"):
        value = integrity.get(key)
        if not isinstance(value, str) or SHA256_PATTERN.fullmatch(value) is None:
            errors.append(f"integrity.{key} must be a lowercase SHA-256 digest")
    known_good_digest = integrity.get("knownGoodSha256")
    if known_good_digest is not None and (
        not isinstance(known_good_digest, str) or SHA256_PATTERN.fullmatch(known_good_digest) is None
    ):
        errors.append("integrity.knownGoodSha256 must be a lowercase SHA-256 digest")
    return errors


def _purl_identity(purl: str) -> tuple[str, str | None]:
    """Return a PURL without subpath and its version."""

    without_subpath = purl.split("#", maxsplit=1)[0]
    if "@" not in without_subpath:
        return without_subpath, None
    base, version = without_subpath.rsplit("@", maxsplit=1)
    return base, version


def _purl_matches(subject_purl: str, candidate_purl: str, subject_version: str) -> bool:
    subject_base, purl_version = _purl_identity(subject_purl)
    candidate_base, candidate_version = _purl_identity(candidate_purl)
    expected_version = purl_version or subject_version
    return subject_base == candidate_base and candidate_version == expected_version


def _normalize_repository(repository: str) -> str:
    normalized = repository.strip().rstrip("/")
    if normalized.endswith(".git"):
        normalized = normalized[:-4]
    return normalized.lower()


def _known_good_binding(assertion: Mapping[str, Any], known_good: Mapping[str, Any] | None) -> dict[str, str] | None:
    """Resolve an assertion subject to one exact S-CORE known-good module."""

    if known_good is None:
        return None
    subject = assertion["subject"]
    repository = subject.get("repository")
    if not _is_non_empty_string(repository):
        return None
    expected_repository = _normalize_repository(str(repository))
    expected_hash = str(subject["version"])
    modules = known_good.get("modules")
    if not isinstance(modules, Mapping):
        return None

    bindings: list[dict[str, str]] = []
    for group in modules.values():
        if not isinstance(group, Mapping):
            continue
        for module_name, module in group.items():
            if not isinstance(module_name, str) or not isinstance(module, Mapping):
                continue
            module_repository = module.get("repo")
            module_hash = module.get("hash")
            if not _is_non_empty_string(module_repository) or not _is_non_empty_string(module_hash):
                continue
            if (
                _normalize_repository(str(module_repository)) == expected_repository
                and str(module_hash) == expected_hash
            ):
                bindings.append(
                    {
                        "module": module_name,
                        "repository": str(module_repository),
                        "hash": str(module_hash),
                    }
                )
    return bindings[0] if len(bindings) == 1 else None


def _known_good_candidate_matches(candidate: Mapping[str, Any], binding: Mapping[str, str]) -> bool:
    """Match an ``unknown`` SBOM module only when known-good supplies its identity."""

    if candidate.get("name") != binding["module"] or candidate.get("version") != "unknown":
        return False
    candidate_base, candidate_version = _purl_identity(str(candidate.get("purl", "")))
    repository = urlparse(_normalize_repository(binding["repository"]))
    repository_parts = repository.path.strip("/").split("/")
    if len(repository_parts) != 2:
        return False
    expected_base = f"pkg:github/{repository_parts[0]}/{binding['module']}"
    return candidate_base.lower() == expected_base.lower() and candidate_version == "unknown"


def _spdx_components(sbom: Mapping[str, Any]) -> Iterable[dict[str, Any]]:
    for package in sbom.get("packages", []):
        if not isinstance(package, Mapping):
            continue
        for external_ref in package.get("externalRefs", []):
            if not isinstance(external_ref, Mapping):
                continue
            locator = external_ref.get("referenceLocator")
            reference_type = str(external_ref.get("referenceType", "")).lower()
            if _is_non_empty_string(locator) and (str(locator).startswith("pkg:") or reference_type.endswith("purl")):
                yield {
                    "format": "SPDX-2.3",
                    "identifier": package.get("SPDXID"),
                    "name": package.get("name"),
                    "version": package.get("versionInfo"),
                    "purl": str(locator),
                }


def _walk_cyclonedx_components(components: object) -> Iterable[Mapping[str, Any]]:
    if not isinstance(components, list):
        return
    for component in components:
        if not isinstance(component, Mapping):
            continue
        yield component
        yield from _walk_cyclonedx_components(component.get("components"))


def _cyclonedx_components(sbom: Mapping[str, Any]) -> Iterable[dict[str, Any]]:
    metadata = sbom.get("metadata")
    roots: list[Mapping[str, Any]] = []
    if isinstance(metadata, Mapping) and isinstance(metadata.get("component"), Mapping):
        roots.append(metadata["component"])
    roots.extend(_walk_cyclonedx_components(sbom.get("components")))
    for component in roots:
        purl = component.get("purl")
        if _is_non_empty_string(purl):
            yield {
                "format": "CycloneDX-1.6",
                "identifier": component.get("bom-ref"),
                "name": component.get("name"),
                "version": component.get("version"),
                "purl": str(purl),
            }


def _matches_and_binding(
    assertion: Mapping[str, Any],
    sbom: Mapping[str, Any],
    known_good: Mapping[str, Any] | None,
) -> tuple[list[dict[str, Any]], dict[str, str] | None]:
    """Find SBOM components representing the assertion subject.

    The component subpath in the assertion PURL is intentionally ignored for
    the initial module-level join. ``componentPath`` preserves the intended
    KVS scope until the SBOM emits target-level component identities.
    """

    errors = validate_assertion(assertion)
    if errors:
        raise ValueError("Invalid SRAC assertion: " + "; ".join(errors))
    subject = assertion["subject"]
    subject_purl = str(subject["purl"])
    subject_version = str(subject["version"])

    if str(sbom.get("spdxVersion", "")).startswith("SPDX-2."):
        candidates = list(_spdx_components(sbom))
    elif sbom.get("bomFormat") == "CycloneDX":
        candidates = list(_cyclonedx_components(sbom))
    else:
        raise ValueError("Unsupported SBOM format; expected SPDX 2.x or CycloneDX")

    direct_matches = [
        candidate for candidate in candidates if _purl_matches(subject_purl, str(candidate["purl"]), subject_version)
    ]
    if direct_matches:
        return direct_matches, None

    binding = _known_good_binding(assertion, known_good)
    if binding is None:
        return [], None
    return [candidate for candidate in candidates if _known_good_candidate_matches(candidate, binding)], binding


def match_assertion_to_sbom(
    assertion: Mapping[str, Any],
    sbom: Mapping[str, Any],
    known_good: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Find SBOM components representing the assertion subject."""

    matches, _ = _matches_and_binding(assertion, sbom, known_good)
    return matches


def build_enrichment_report(
    assertion: Mapping[str, Any],
    sbom: Mapping[str, Any],
    known_good: Mapping[str, Any] | None = None,
    integrity: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Build a sidecar report without modifying the source SBOM."""

    matches, binding = _matches_and_binding(assertion, sbom, known_good)
    report = {
        "schemaVersion": SCHEMA_VERSION,
        "sourceFormat": "SPDX" if "spdxVersion" in sbom else "CycloneDX",
        "assertionId": assertion["assertionId"],
        "subject": deepcopy(assertion["subject"]),
        "safetyAssessment": {
            "source": "assertion",
            "safetyRelevance": assertion["safetyRelevance"]["status"],
            "classification": assertion["safetyRelevance"]["classification"],
            "assertionStatus": assertion["assertion"]["status"],
            "reviewer": deepcopy(assertion["assertion"].get("reviewer")),
        },
        "matchedComponents": matches,
        "matchStatus": "matched" if matches else "unmatched",
        "generator": {
            "name": "srac.tools.enrich_sbom",
            "version": TOOL_VERSION,
        },
        "integrity": dict(integrity or {}),
    }
    if matches and binding is not None:
        report["bindingEvidence"] = {
            "strategy": "score-known-good",
            **binding,
        }
    if "impactAnalysis" in assertion:
        report["impactAnalysis"] = deepcopy(assertion["impactAnalysis"])
    return report
