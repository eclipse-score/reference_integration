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

# # --- begin runfiles.bash initialization v3 ---
# # Copy-pasted from the Bazel Bash runfiles library v3.
# set -uo pipefail; set +e; f=bazel_tools/tools/bash/runfiles/runfiles.bash
# # shellcheck disable=SC1090
# source "${RUNFILES_DIR:-/dev/null}/$f" 2>/dev/null || \
#   source "$(grep -sm1 "^$f " "${RUNFILES_MANIFEST_FILE:-/dev/null}" | cut -f2- -d' ')" 2>/dev/null || \
#   source "$0.runfiles/$f" 2>/dev/null || \
#   source "$(grep -sm1 "^$f " "$0.runfiles_manifest" | cut -f2- -d' ')" 2>/dev/null || \
#   source "$(grep -sm1 "^$f " "$0.exe.runfiles_manifest" | cut -f2- -d' ')" 2>/dev/null || \
#   { echo>&2 "ERROR: cannot find $f"; exit 1; }; f=; set -e
# # --- end runfiles.bash initialization v3 ---

set -euox pipefail

#BASEFOLDER=$1

echo "Image: ${2}"
echo "Kernel: ${1}"

IMAGE="$(rlocation _main/$2)"
KERNEL="$(rlocation _main/$1)"

echo "Image: ${IMAGE}"
echo "Kernel: ${KERNEL}"

# Make the image file writable, as QEMU needs to write to it.
find -L "$(dirname "${IMAGE}")" -samefile "${IMAGE}" -exec chmod +w {} \;

MACHINE="virt,virtualization=true,gic-version=3"
CPU="cortex-a53"
SMP="8"
MEM="4G"
KERNEL_ARGS=("-append" "root=/dev/vda1 sdk_enable lisa_syscall_whitelist=2026 rw sharedmem.enable_sharedmem=0 init=/usr/bin/ebclfsa-cflinit")
DISK_ARGS="-device virtio-blk-device,drive=vd0 -drive if=none,format=raw,file=${IMAGE},id=vd0"
NETWORK_ARGS="-netdev user,id=net0,net=192.168.7.0/24,dhcpstart=192.168.7.2,dns=192.168.7.3,host=192.168.7.5,hostfwd=tcp::2222-:22,hostfwd=tcp::3333-:3333 -device virtio-net-device,netdev=net0 "

if ! command -v qemu-system-aarch64 > /dev/null; then
    echo "Please install qemu-system-aarch64"
    exit 1
fi

echo "pwd=$(pwd)"

qemu-system-aarch64  \
    -m "${MEM}" \
    -machine "${MACHINE}" \
    -cpu "${CPU}" \
    -smp "${SMP}" \
    -kernel "${KERNEL}" \
    "${KERNEL_ARGS[@]}" \
    ${DISK_ARGS} \
    ${NETWORK_ARGS} \
    -nographic \
    -chardev stdio,id=char0,signal=on,mux=on \
    -mon chardev=char0,mode=readline \
    -serial chardev:char0
