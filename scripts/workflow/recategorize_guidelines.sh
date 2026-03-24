#!/bin/bash
# *******************************************************************************
# Copyright (c) 2025 Contributors to the Eclipse Foundation
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
RECATEGORIZE_SCRIPT="codeql-coding-standards-repo/scripts/guideline_recategorization/recategorize.py"
CODING_STANDARDS_CONFIG="./.github/codeql/coding-standards.yml"
CODING_STANDARDS_SCHEMA="codeql-coding-standards-repo/schemas/coding-standards-schema-1.0.0.json"
SARIF_SCHEMA="codeql-coding-standards-repo/schemas/sarif-schema-2.1.0.json"
SARIF_FILE="sarif-results/cpp.sarif" 
mkdir -p sarif-results-recategorized
echo "Processing $SARIF_FILE for recategorization..."
python3 "$RECATEGORIZE_SCRIPT" \
  --coding-standards-schema-file "$CODING_STANDARDS_SCHEMA" \
  --sarif-schema-file "$SARIF_SCHEMA" \
  "$CODING_STANDARDS_CONFIG" \
  "$SARIF_FILE" \
  "sarif-results-recategorized/$(basename "$SARIF_FILE")"
PY_EXIT=$?
if [ $PY_EXIT -ne 0 ]; then
  echo "Recategorization failed (exit code $PY_EXIT). SARIF file not updated." >&2
  exit $PY_EXIT
fi
rm "$SARIF_FILE"
mv "sarif-results-recategorized/$(basename "$SARIF_FILE")" "$SARIF_FILE"

# Ensure jq is available
if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required but not installed. Please install jq and rerun this script." >&2
  exit 1
fi

# Filter SARIF to only include results from repos/* (relative or absolute)
echo "Filtering SARIF results to only include entries with paths matching (^|/)repos/ ..."
jq '(.runs) |= map(.results |= map(select((.locations // [] | length > 0) and ((.locations[0].physicalLocation.artifactLocation.uri // "") | test("(^|/)repos/")))) )' "$SARIF_FILE" > "${SARIF_FILE}.filtered"
if [ $? -eq 0 ]; then
  mv "${SARIF_FILE}.filtered" "$SARIF_FILE"
else
  echo "jq filtering failed. SARIF file was not modified." >&2
  rm -f "${SARIF_FILE}.filtered"
  exit 1
fi
