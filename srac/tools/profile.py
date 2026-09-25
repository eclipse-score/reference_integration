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

from collections.abc import Iterable, Mapping
from copy import deepcopy
from typing import Any

SCHEMA_VERSION = "0.1-draft"
RELEVANCE_VALUES = {"safety-related", "not-safety-related", "undetermined"}
CLASSIFICATION_VALUES = {"QM", "ASIL-A", "ASIL-B", "ASIL-C", "ASIL-D", "not-assigned"}
ASSERTION_STATUS_VALUES = {"draft", "under-review", "reviewed", "approved", "superseded", "withdrawn"}


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

    assertion = _require_mapping(document, "assertion", errors)
    if assertion.get("status") not in ASSERTION_STATUS_VALUES:
        errors.append(f"assertion.status must be one of {sorted(ASSERTION_STATUS_VALUES)}")
    author = assertion.get("author")
    if not isinstance(author, Mapping) or not _is_non_empty_string(author.get("name")):
        errors.append("assertion.author.name must be a non-empty string")
    if not _is_non_empty_string(assertion.get("created")):
        errors.append("assertion.created must be a non-empty date-time string")
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


def match_assertion_to_sbom(assertion: Mapping[str, Any], sbom: Mapping[str, Any]) -> list[dict[str, Any]]:
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
        candidates = _spdx_components(sbom)
    elif sbom.get("bomFormat") == "CycloneDX":
        candidates = _cyclonedx_components(sbom)
    else:
        raise ValueError("Unsupported SBOM format; expected SPDX 2.x or CycloneDX")

    return [
        candidate
        for candidate in candidates
        if _purl_matches(subject_purl, str(candidate["purl"]), subject_version)
    ]


def build_enrichment_report(assertion: Mapping[str, Any], sbom: Mapping[str, Any]) -> dict[str, Any]:
    """Build a sidecar report without modifying the source SBOM."""

    matches = match_assertion_to_sbom(assertion, sbom)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "sourceFormat": "SPDX" if "spdxVersion" in sbom else "CycloneDX",
        "assertionId": assertion["assertionId"],
        "subject": deepcopy(assertion["subject"]),
        "matchedComponents": matches,
        "matchStatus": "matched" if matches else "unmatched",
    }
