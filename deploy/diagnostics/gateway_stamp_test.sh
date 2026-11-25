#!/usr/bin/env bash
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
set -euo pipefail

# --version and /version-info both use the same OpenSOVD build-script values.
gateway="$1"
module="$2"
expected_sha="$(sed -n '/module_name = "opensovd_core"/,/^[)]/s/.*commit = "\([0-9a-f]*\)".*/\1/p' "$module")"
[[ "$expected_sha" =~ ^[0-9a-f]{40}$ ]] || { echo "Missing OpenSOVD pin" >&2; exit 1; }
version="$("$gateway" --version)"
[[ "$version" == *"$expected_sha "* ]] || { echo "Wrong OpenSOVD revision: $version" >&2; exit 1; }
[[ "$version" =~ [0-9]{4}-[0-9]{2}-[0-9]{2} ]] || { echo "Missing OpenSOVD date: $version" >&2; exit 1; }
