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
"""Discover and verify an SRAC sidecar referenced by an SPDX or CycloneDX SBOM."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from srac.tools.profile import build_enrichment_report, validate_assertion, validate_report

SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
SPDX_SRAC_COMMENT_PATTERN = re.compile(r"^SRAC sidecar; SHA-256: ([0-9a-f]{64})$")


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


def _spdx_references(sbom: Mapping[str, Any]) -> Iterable[dict[str, str]]:
    packages = sbom.get("packages")
    if not isinstance(packages, list):
        return
    for package in packages:
        if not isinstance(package, Mapping):
            continue
        external_references = package.get("externalRefs")
        if not isinstance(external_references, list):
            continue
        for reference in external_references:
            if not isinstance(reference, Mapping):
                continue
            if (
                reference.get("referenceCategory") != "OTHER"
                or str(reference.get("referenceType", "")).lower() != "srac"
            ):
                continue
            match = SPDX_SRAC_COMMENT_PATTERN.fullmatch(str(reference.get("comment", "")))
            if match is None:
                raise ValueError("SPDX SRAC external reference must carry a lowercase SHA-256 digest in its comment")
            uri = reference.get("referenceLocator")
            if not isinstance(uri, str) or not uri:
                raise ValueError("SPDX SRAC external reference must have a non-empty referenceLocator")
            yield {
                "format": "SPDX",
                "componentIdentifier": str(package.get("SPDXID") or ""),
                "uri": uri,
                "sha256": match.group(1),
            }


def _walk_cyclonedx_components(components: object) -> Iterable[Mapping[str, Any]]:
    if not isinstance(components, list):
        return
    for component in components:
        if not isinstance(component, Mapping):
            continue
        yield component
        yield from _walk_cyclonedx_components(component.get("components"))


def _cyclonedx_references(sbom: Mapping[str, Any]) -> Iterable[dict[str, str]]:
    roots: list[Mapping[str, Any]] = []
    metadata = sbom.get("metadata")
    if isinstance(metadata, Mapping) and isinstance(metadata.get("component"), Mapping):
        roots.append(metadata["component"])
    roots.extend(_walk_cyclonedx_components(sbom.get("components")))
    for component in roots:
        external_references = component.get("externalReferences")
        if not isinstance(external_references, list):
            continue
        for reference in external_references:
            if not isinstance(reference, Mapping):
                continue
            if reference.get("type") != "other" or reference.get("comment") != "SRAC sidecar":
                continue
            hashes = reference.get("hashes")
            digest = (
                next(
                    (
                        item.get("content")
                        for item in hashes
                        if isinstance(item, Mapping) and str(item.get("alg", "")).upper() == "SHA-256"
                    ),
                    None,
                )
                if isinstance(hashes, list)
                else None
            )
            if not isinstance(digest, str) or SHA256_PATTERN.fullmatch(digest) is None:
                raise ValueError("CycloneDX SRAC external reference must carry a lowercase SHA-256 hash")
            uri = reference.get("url")
            if not isinstance(uri, str) or not uri:
                raise ValueError("CycloneDX SRAC external reference must have a non-empty URL")
            yield {
                "format": "CycloneDX",
                "componentIdentifier": str(component.get("bom-ref") or ""),
                "uri": uri,
                "sha256": digest,
            }


def discover_srac_references(sbom: Mapping[str, Any]) -> list[dict[str, str]]:
    """Return integrity-protected SRAC references without fetching their targets."""

    if str(sbom.get("spdxVersion", "")).startswith("SPDX-2."):
        return list(_spdx_references(sbom))
    if sbom.get("bomFormat") == "CycloneDX":
        return list(_cyclonedx_references(sbom))
    raise ValueError("Unsupported SBOM format; expected SPDX 2.x or CycloneDX")


def load_referenced_assertion(
    sbom: Mapping[str, Any],
    artifact_root: Path,
) -> tuple[dict[str, Any], dict[str, str], Path]:
    """Resolve exactly one local artifact and verify it before parsing."""

    references = discover_srac_references(sbom)
    if not references:
        raise ValueError("SBOM has no integrity-protected SRAC external reference")
    if len(references) != 1:
        raise ValueError(f"SBOM has {len(references)} SRAC external references; refusing ambiguous selection")
    reference = references[0]
    filename = Path(unquote(urlparse(reference["uri"]).path)).name
    if not filename:
        raise ValueError("SRAC external reference URI has no artifact filename")
    root = artifact_root.resolve()
    artifact = (root / filename).resolve()
    if not artifact.is_relative_to(root):
        raise ValueError("Resolved SRAC artifact escapes artifact root")
    if not artifact.is_file():
        raise ValueError(f"Referenced SRAC artifact is unavailable: {artifact}")
    actual_digest = _sha256(artifact)
    if actual_digest != reference["sha256"]:
        raise ValueError(f"SRAC artifact SHA-256 mismatch: expected {reference['sha256']}, got {actual_digest}")
    assertion = _read_json(artifact)
    errors = validate_assertion(assertion)
    if errors:
        raise ValueError("Invalid referenced SRAC assertion: " + "; ".join(errors))
    return assertion, reference, artifact


def build_received_report(sbom_path: Path, artifact_root: Path) -> dict[str, Any]:
    """Execute discovery, integrity verification, validation and correlation."""

    sbom = _read_json(sbom_path)
    assertion, reference, artifact = load_referenced_assertion(sbom, artifact_root)
    report = build_enrichment_report(
        assertion,
        sbom,
        integrity={
            "algorithm": "SHA-256",
            "assertionSha256": _sha256(artifact),
            "sbomSha256": _sha256(sbom_path),
        },
    )
    report["discoveredReference"] = reference
    errors = validate_report(report)
    if errors:
        raise ValueError("Invalid SRAC receiving report: " + "; ".join(errors))
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sbom", required=True, type=Path, help="SPDX 2.x or CycloneDX SBOM containing an SRAC reference"
    )
    parser.add_argument(
        "--artifact-root",
        required=True,
        type=Path,
        help="local directory containing previously retrieved referenced artifacts",
    )
    parser.add_argument("--output", required=True, type=Path, help="receiving report to write")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_received_report(args.sbom, args.artifact_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    return 0 if report["matchStatus"] == "matched" else 1


if __name__ == "__main__":
    raise SystemExit(main())
