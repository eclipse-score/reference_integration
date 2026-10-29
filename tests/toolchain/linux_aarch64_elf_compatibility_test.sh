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

# Verify that all ELF binaries in the showcase payload are AArch64, require at
# most GLIBC_2.41, and have PT_LOAD alignment >= 16K.

tar_path="$1"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

tar -xf "$tar_path" -C "$tmpdir"

status=0
elf_count=0

while IFS= read -r -d '' binary; do
    if [[ ! -x "$binary" ]]; then
        continue
    fi
    if ! readelf -h "$binary" >/dev/null 2>&1; then
        continue
    fi

    elf_count=$((elf_count + 1))
    bin_name="${binary#"$tmpdir"/}"

    if ! readelf -h "$binary" | grep -q 'Machine:.*AArch64'; then
        echo "FAIL: $bin_name: expected AArch64 architecture" >&2
        status=1
        continue
    fi

    glibc_version="$(readelf --version-info "$binary" 2>/dev/null | grep -oE 'GLIBC_[0-9]+\.[0-9]+' | sort -Vu | tail -n 1 || true)"
    if [[ -n "$glibc_version" ]]; then
        glibc_number="${glibc_version#GLIBC_}"
        highest="$(printf '%s\n' "$glibc_number" 2.41 | sort -V | tail -n 1)"
        if [[ "$highest" != "2.41" ]]; then
            echo "FAIL: $bin_name: requires $glibc_version (> GLIBC_2.41)" >&2
            status=1
        fi
    fi

    while IFS= read -r alignment; do
        if (( alignment < 16384 )); then
            echo "FAIL: $bin_name: PT_LOAD alignment $alignment < 16K" >&2
            status=1
        fi
    done < <(readelf -lW "$binary" 2>/dev/null | awk '$1 == "LOAD" {print $NF}')
done < <(find "$tmpdir" -type f -print0)

if (( elf_count == 0 )); then
    echo "FAIL: no ELF binaries found in showcase payload" >&2
    status=1
fi

if (( status == 0 )); then
    echo "PASS: $elf_count ELF binaries satisfy AArch64, GLIBC<=2.41, PT_LOAD>=16K"
fi

exit "$status"
