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
"""Create an SRAC-to-SBOM enrichment report."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from srac.tools.profile import build_enrichment_report, validate_assertion, validate_report


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        document = json.load(stream)
    if not isinstance(document, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return document


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assertion", required=True, type=Path, help="SRAC assertion sidecar")
    parser.add_argument("--sbom", required=True, type=Path, help="SPDX 2.x or CycloneDX SBOM")
    parser.add_argument(
        "--known-good",
        type=Path,
        help="S-CORE known_good.json used to resolve modules emitted with version 'unknown'",
    )
    parser.add_argument("--output", required=True, type=Path, help="enrichment report to write")
    parser.add_argument("--checksum-output", type=Path, help="optional SHA-256 checksum file for the report")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    assertion = _read_json(args.assertion)
    errors = validate_assertion(assertion)
    if errors:
        raise ValueError("Invalid SRAC assertion: " + "; ".join(errors))
    known_good = _read_json(args.known_good) if args.known_good else None
    integrity = {
        "algorithm": "SHA-256",
        "assertionSha256": _sha256(args.assertion),
        "sbomSha256": _sha256(args.sbom),
    }
    if args.known_good:
        integrity["knownGoodSha256"] = _sha256(args.known_good)
    report = build_enrichment_report(assertion, _read_json(args.sbom), known_good, integrity)
    report_errors = validate_report(report)
    if report_errors:
        raise ValueError("Invalid SRAC enrichment report: " + "; ".join(report_errors))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    if args.checksum_output:
        args.checksum_output.parent.mkdir(parents=True, exist_ok=True)
        args.checksum_output.write_text(f"{_sha256(args.output)}  {args.output.name}\n", encoding="utf-8", newline="\n")
    return 0 if report["matchStatus"] == "matched" else 1


if __name__ == "__main__":
    raise SystemExit(main())
