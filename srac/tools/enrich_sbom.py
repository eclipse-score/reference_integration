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
import json
from pathlib import Path
from typing import Any

from srac.tools.profile import build_enrichment_report, validate_assertion


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        document = json.load(stream)
    if not isinstance(document, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return document


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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    assertion = _read_json(args.assertion)
    errors = validate_assertion(assertion)
    if errors:
        raise ValueError("Invalid SRAC assertion: " + "; ".join(errors))
    known_good = _read_json(args.known_good) if args.known_good else None
    report = build_enrichment_report(assertion, _read_json(args.sbom), known_good)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    return 0 if report["matchStatus"] == "matched" else 1


if __name__ == "__main__":
    raise SystemExit(main())
