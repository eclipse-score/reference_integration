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
"""Map the multi-repo CodeQL SARIF onto Bazel repository paths for the docs build (POC).

The scan checks modules out to ``repos/<module>/``; docs-as-code identifies the same
file as ``external/<module>+/<path>``, the canonical name of the Bazel module repo.
"""

import argparse
import json
import re
from pathlib import Path

_CHECKOUT = re.compile(r"^repos/([^/]+)/")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sarif", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    sarif = json.loads(args.sarif.read_text(encoding="utf-8"))
    for run in sarif.get("runs", []):
        for result in run.get("results", []):
            for location in result.get("locations", []):
                artifact = location.get("physicalLocation", {}).get("artifactLocation", {})
                if "uri" in artifact:
                    artifact["uri"] = _CHECKOUT.sub(r"external/\1+/", artifact["uri"])
                    artifact.pop("uriBaseId", None)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(sarif), encoding="utf-8")


if __name__ == "__main__":
    main()
