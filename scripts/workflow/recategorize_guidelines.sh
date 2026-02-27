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
  rm "$SARIF_FILE"
  mv "sarif-results-recategorized/$(basename "$SARIF_FILE")" "$SARIF_FILE"
