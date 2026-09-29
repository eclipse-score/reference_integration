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
"""Export a read-only SRAC projection from an authoritative Sphinx-needs file."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from srac.tools.profile import validate_assertion

SAFETY_CLASSIFICATIONS = {
    "QM": ("not-safety-related", "QM"),
    "ASIL_A": ("safety-related", "ASIL-A"),
    "ASIL_B": ("safety-related", "ASIL-B"),
    "ASIL_C": ("safety-related", "ASIL-C"),
    "ASIL_D": ("safety-related", "ASIL-D"),
}
SAFETY_RELEVANT_TRUE = {"TRUE", "YES", "Y", "1", "SAFETY_RELATED"}
SAFETY_RELEVANT_FALSE = {"FALSE", "NO", "N", "0", "NOT_SAFETY_RELATED"}


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalize_token(value: object) -> str:
    return str(value or "").strip().upper().replace("-", "_").replace(" ", "_")


def _safety_relevance(need: Mapping[str, Any]) -> dict[str, str]:
    safety = _normalize_token(need.get("safety"))
    mapped = SAFETY_CLASSIFICATIONS.get(safety, ("undetermined", "not-assigned"))
    explicit = _normalize_token(need.get("safety_relevant"))
    if explicit in SAFETY_RELEVANT_TRUE:
        if mapped[0] == "not-safety-related":
            raise ValueError(f"Need {need.get('id')!r} has conflicting safety and safety_relevant fields")
        return {"status": "safety-related", "classification": mapped[1]}
    if explicit in SAFETY_RELEVANT_FALSE:
        if mapped[0] == "safety-related":
            raise ValueError(f"Need {need.get('id')!r} has conflicting safety and safety_relevant fields")
        return {"status": "not-safety-related", "classification": mapped[1]}
    return {"status": mapped[0], "classification": mapped[1]}


def _need_uri(documentation_base_uri: str, need: Mapping[str, Any]) -> str:
    external_url = need.get("external_url")
    if isinstance(external_url, str) and external_url.strip():
        return external_url
    docname = need.get("docname")
    need_id = need.get("id")
    if not isinstance(docname, str) or not docname or not isinstance(need_id, str) or not need_id:
        raise ValueError(f"Need {need_id!r} has neither external_url nor a usable docname")
    return f"{documentation_base_uri.rstrip('/')}/{docname}.html#{need_id}"


def _reference(documentation_base_uri: str, need: Mapping[str, Any]) -> dict[str, str]:
    need_id = need.get("id")
    need_type = need.get("type")
    if not isinstance(need_id, str) or not need_id or not isinstance(need_type, str) or not need_type:
        raise ValueError("Every exported need must have non-empty id and type fields")
    return {
        "id": need_id,
        "type": f"sphinx-needs:{need_type}",
        "uri": _need_uri(documentation_base_uri, need),
    }


def _needs_for_version(needs_document: Mapping[str, Any], version: str) -> Mapping[str, Any]:
    versions = needs_document.get("versions")
    if not isinstance(versions, Mapping) or not isinstance(versions.get(version), Mapping):
        raise ValueError(f"Sphinx-needs version {version!r} is not present")
    needs = versions[version].get("needs")
    if not isinstance(needs, Mapping):
        raise ValueError(f"Sphinx-needs version {version!r} has no needs object")
    return needs


def build_assertion(needs_document: Mapping[str, Any], config: Mapping[str, Any], source_sha256: str) -> dict[str, Any]:
    """Build a deterministic projection without creating a new safety decision."""

    version = str(config.get("sourceVersion") or needs_document.get("current_version") or "")
    root_id = config.get("rootNeedId")
    included_ids = config.get("includedNeedIds", [])
    subject = config.get("subject")
    if not version or not isinstance(root_id, str) or not root_id:
        raise ValueError("sourceVersion/current_version and rootNeedId are required")
    if not isinstance(included_ids, list) or not all(isinstance(item, str) and item for item in included_ids):
        raise ValueError("includedNeedIds must be an array of non-empty strings")
    if not isinstance(subject, Mapping):
        raise ValueError("subject must be an object")
    for key in ("name", "purl", "version"):
        if not isinstance(subject.get(key), str) or not subject[key]:
            raise ValueError(f"subject.{key} must be a non-empty string")
    for key in ("sourceDocumentUri", "documentationBaseUri", "artifactUri", "created"):
        if not isinstance(config.get(key), str) or not config[key]:
            raise ValueError(f"{key} must be a non-empty string")

    needs = _needs_for_version(needs_document, version)
    selected_ids = [root_id, *included_ids]
    missing = [need_id for need_id in selected_ids if not isinstance(needs.get(need_id), Mapping)]
    if missing:
        raise ValueError(f"Needs not found in version {version!r}: {', '.join(missing)}")
    selected = [needs[need_id] for need_id in selected_ids]
    root = selected[0]
    documentation_base_uri = str(config["documentationBaseUri"])
    requirements = [
        _reference(documentation_base_uri, need) for need in selected[1:] if str(need.get("type", "")).endswith("_req")
    ]
    evidence = [
        _reference(documentation_base_uri, need)
        for need in selected
        if need is root or not str(need.get("type", "")).endswith("_req")
    ]
    source_status = str(root.get("status") or "")
    assertion = {
        "schemaVersion": "0.2-draft",
        "assertionId": f"srac-needs-export-{root_id}-{version}",
        "subject": dict(subject),
        "safetyRelevance": _safety_relevance(root),
        "rationale": (
            f"Read-only projection of S-CORE need {root_id!r} at needs.json version {version!r}. "
            f"The source lifecycle status is {source_status!r}. The export adds no safety decision; "
            "the referenced Sphinx-needs model remains authoritative."
        ),
        "requirements": requirements,
        "evidence": evidence,
        "sourceOfTruth": {
            "system": "sphinx-needs",
            "documentUri": config["sourceDocumentUri"],
            "version": version,
            "rootElement": root_id,
            "rootElementType": str(root.get("type") or ""),
            "rootElementStatus": source_status,
            "includedElements": included_ids,
            "sha256": source_sha256,
        },
        "assertion": {
            "status": "draft",
            "author": {
                "name": "S-CORE needs.json export",
                "uri": str(config["sourceDocumentUri"]),
            },
            "reviewer": None,
            "created": config["created"],
        },
    }
    errors = validate_assertion(assertion)
    if errors:
        raise ValueError("Generated an invalid SRAC assertion: " + "; ".join(errors))
    return assertion


def build_reference_manifest(config: Mapping[str, Any], assertion_sha256: str) -> dict[str, Any]:
    """Create illustrative SPDX 2.3 and CycloneDX 1.6 carrier fragments."""

    artifact_uri = str(config["artifactUri"])
    return {
        "artifact": {
            "uri": artifact_uri,
            "sha256": assertion_sha256,
        },
        "spdx23PackageExternalRef": {
            "referenceCategory": "OTHER",
            "referenceType": "srac",
            "referenceLocator": artifact_uri,
        },
        "cycloneDx16ExternalReference": {
            "type": "other",
            "url": artifact_uri,
            "comment": "Read-only SRAC projection from the authoritative S-CORE needs.json model",
            "hashes": [
                {
                    "alg": "SHA-256",
                    "content": assertion_sha256,
                }
            ],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--needs", required=True, type=Path, help="authoritative Sphinx-needs needs.json")
    parser.add_argument("--config", required=True, type=Path, help="transport-only export configuration")
    parser.add_argument("--output", required=True, type=Path, help="portable SRAC projection to write")
    parser.add_argument("--reference-output", type=Path, help="optional SPDX/CycloneDX reference fragments")
    return parser.parse_args()


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def main() -> int:
    args = parse_args()
    config = _read_json(args.config)
    assertion = build_assertion(_read_json(args.needs), config, _sha256(args.needs))
    _write_json(args.output, assertion)
    if args.reference_output:
        _write_json(args.reference_output, build_reference_manifest(config, _sha256(args.output)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
