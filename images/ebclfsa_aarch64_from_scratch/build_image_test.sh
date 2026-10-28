#!/bin/bash
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

sources="$TEST_SRCDIR/_main/images/ebclfsa_aarch64_from_scratch"
overlay="$TEST_SRCDIR/_main/images/ebclfsa_aarch64/build/config-overlay"
fixture="$TEST_TMPDIR/fixture"
output="$TEST_TMPDIR/output"
mkdir -p "$fixture/"{kas,layers/isar,.devcontainer,prebuilt} "$output"
echo "must not use a prebuilt image" > "$fixture/prebuilt/image.wic"
echo "KAS configuration" > "$fixture/kas/public.yml"
echo "bundled Isar" > "$fixture/layers/isar/isar-init-build-env"
echo "container configuration" > "$fixture/.devcontainer/devcontainer.json"
echo "Debian package fixture" > "$TEST_TMPDIR/showcases.deb"

# Exercise staging, artifact export and error propagation without a privileged
# container or network access.
docker() {
    if [[ $1 == info ]]; then
        return 0
    fi
    local mount work deploy
    while [[ $# -gt 0 ]]; do
        if [[ $1 == --mount ]]; then
            mount=$2
            break
        fi
        shift
    done
    work=${mount#type=bind,src=}
    work=${work%,dst=/workspace}
    [[ ! -e "$work/prebuilt" ]]
    cmp "$TEST_TMPDIR/fixture/kas/public.yml" "$work/kas/public.yml"
    cmp "$TEST_TMPDIR/fixture/layers/isar/isar-init-build-env" "$work/layers/isar/isar-init-build-env"
    cmp "$TEST_TMPDIR/fixture/.devcontainer/devcontainer.json" "$work/.devcontainer/devcontainer.json"
    cmp "$TEST_TMPDIR/showcases.deb" \
        "$work/meta-score/recipes-score/score-showcases/files/score-showcases_1.0_arm64.deb"
    cmp "$TEST_SRCDIR/_main/images/ebclfsa_aarch64_from_scratch/kas.yml" "$work/kas/score.yml"
    cmp "$TEST_SRCDIR/_main/images/ebclfsa_aarch64/build/config-overlay/etc/crinit/crinit.d/getty-console.crinit" \
        "$work/meta-score/recipes-crinit/fastdev/files/getty-console.crinit"
    cmp "$TEST_SRCDIR/_main/images/ebclfsa_aarch64/build/config-overlay/usr/bin/delayed-start.sh" \
        "$work/meta-score/recipes-crinit/fastdev/files/delayed-start.sh"
    if [[ ${MOCK_DOCKER_FAIL:-0} == 1 ]]; then
        return 17
    fi
    deploy="$work/build/tmp/deploy/images/ebcl-qemuarm64"
    mkdir -p "$deploy"
    echo kernel > "$deploy/fastdev-trixie-ebclfsa-ebcl-qemuarm64-vmlinux"
    if [[ ${MOCK_MISSING_IMAGE:-0} != 1 ]]; then
        echo disk > "$deploy/fastdev-trixie-ebclfsa-ebcl-qemuarm64.wic"
    fi
}
export -f docker

build_image() {
    bash "$sources/build_image.sh" "$fixture" \
        "$TEST_TMPDIR/showcases.deb" "$sources/kas.yml" \
        "$overlay/etc/crinit/crinit.d/getty-console.crinit" \
        "$overlay/usr/bin/delayed-start.sh" "$output"
}

build_image
[[ ! -e "$fixture/kas/score.yml" ]]
[[ ! -e "$fixture/meta-score" ]]
[[ $(cat "$output/fastdev-trixie-ebclfsa-ebcl-qemuarm64-vmlinux") == kernel ]]
[[ $(cat "$output/fastdev-trixie-ebclfsa-ebcl-qemuarm64.wic") == disk ]]

export MOCK_DOCKER_FAIL=1
if build_image; then
    echo "Error: container failure was not propagated" >&2
    exit 1
fi
export MOCK_DOCKER_FAIL=0 MOCK_MISSING_IMAGE=1
if build_image; then
    echo "Error: missing image artifact was not rejected" >&2
    exit 1
fi
if find "$output" -maxdepth 1 -name 'kas-work.*' | grep -q .; then
    echo "Error: temporary KAS workspace was not cleaned up" >&2
    exit 1
fi
