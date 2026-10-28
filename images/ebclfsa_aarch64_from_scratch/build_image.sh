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

if [[ $# != 6 ]]; then
    echo "Usage: $0 TOOLKIT_SOURCE_DIR DEB KAS_CONFIG GETTY_CONFIG START_SCRIPT OUTPUT_DIR" >&2
    exit 1
fi

for tool in docker realpath; do
    if ! command -v "$tool" >/dev/null; then
        echo "Error: required image build tool is missing: $tool" >&2
        exit 1
    fi
done
docker info >/dev/null

toolkit=$(realpath "$1")
deb=$(realpath "$2")
config=$(realpath "$3")
getty=$(realpath "$4")
start=$(realpath "$5")
output=$(realpath "$6")
sources=$(dirname "$config")
# Keep the workspace on the same filesystem visible to the Docker daemon.
work=$(mktemp -d "$output/kas-work.XXXXXXXX")
trap 'rm -rf -- "$work"' EXIT

cp -R "$toolkit/kas" "$toolkit/layers" "$toolkit/.devcontainer" "$work/"
cp -R "$sources/meta-score" "$work/meta-score"
cp "$config" "$work/kas/score.yml"
packages="$work/meta-score/recipes-score/score-showcases/files"
console="$work/meta-score/recipes-crinit/fastdev/files"
mkdir -p "$packages" "$console"
cp "$deb" "$packages/score-showcases_1.0_arm64.deb"
cp "$getty" "$console/getty-console.crinit"
cp "$start" "$console/delayed-start.sh"

# Match the toolkit's v18 container, pinned independently of its mutable tag.
container=ghcr.io/elektrobit/eb-corbos-toolkit-devcontainer-amd64@sha256:10f487469c03fb2b5be1c804ec0b0c911d3903a9dd9a8fcbb8b8f401d43b158c
docker run --rm --init --privileged --user root \
    --mount "type=bind,src=$work,dst=/workspace" \
    --workdir /workspace "$container" \
    bash -euo pipefail -c '
        uid=$1
        gid=$2
        if ! getent group "$gid" >/dev/null; then
            groupmod -g "$gid" developer
        fi
        usermod -u "$uid" -g "$gid" developer
        trap '\''chown -R "$uid:$gid" /workspace'\'' EXIT
        if [[ ! -e /proc/sys/fs/binfmt_misc/qemu-aarch64 ]]; then
            mount -t binfmt_misc binfmt_misc /proc/sys/fs/binfmt_misc
            update-binfmts --import /workspace/.devcontainer/binfmt-config/qemu-aarch64
        fi
        # KAS resolves includes relative to the enclosing Git repository.
        runuser -u developer -- git init --quiet /workspace
        # The release checkout already includes the patched Isar tree; its internal
        # patch sources are not shipped.
        runuser -u developer -- kas build \
            --skip repos_checkout --skip repos_apply_patches \
            kas/public.yml:kas/score.yml
    ' bash "$(id -u)" "$(id -g)"

deploy="$work/build/tmp/deploy/images/ebcl-qemuarm64"
for artifact in fastdev-trixie-ebclfsa-ebcl-qemuarm64{.wic,-vmlinux}; do
    if [[ ! -f "$deploy/$artifact" ]]; then
        echo "Error: KAS did not produce the expected artifact: $deploy/$artifact" >&2
        exit 1
    fi
    cp --sparse=always -L "$deploy/$artifact" "$output/$artifact"
done
