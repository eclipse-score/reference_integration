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
"""Extract requirement mappings from platform_integration_tests.

Scans all PIT Python files for @add_test_properties(partially_verifies=[...])
and produces a requirements.json mapping suitable for the TCK bundle.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def extract_requirements(sources: list[str]) -> dict:
    """Extract requirement IDs from Python test files."""
    requirements = {}
    sbom_tracked_modules = [
        "score_baselibs",
        "score_communication", 
        "score_persistency",
        "score_kyron",
        "score_lifecycle",
        "score_logging",
        "score_time",
    ]

    pattern = re.compile(r'partially_verifies\s*=\s*\[([^\]]+)\]')

    for src in sources:
        path = Path(src)
        if not path.exists():
            continue
        content = path.read_text()
        match = pattern.search(content)
        if match:
            # Parse the list of requirement IDs
            reqs_str = match.group(1)
            reqs = [r.strip().strip('"\'') for r in reqs_str.split(",")]
            for req_id in reqs:
                if req_id not in requirements:
                    requirements[req_id] = {
                        "id": req_id,
                        "source_file": str(path),
                        "check_family": "behavioral",
                    }

    return {
        "sbom_tracked_modules": sbom_tracked_modules,
        "requirement_count": len(requirements),
        "requirements": requirements,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_requirements.py <file1.py> [file2.py] ...", file=sys.stderr)
        sys.exit(1)
    
    sources = sys.argv[1:]
    result = extract_requirements(sources)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
