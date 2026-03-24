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

set -euox pipefail

if ! declare -F rlocation > /dev/null; then
    echo "Error: this script is expected to be run via Bazel's sh_binary() function with the option use_bash_launcher = True"
    exit 1
fi

if [[ $# -lt 2 ]]; then
    echo "Error: This script requires at least 2 parameters"
    echo "Usage: $0 <kernel> <image> [additional qemu args]"
    exit 1
fi

KERNEL="$(rlocation _main/"$1")"
IMAGE="$(rlocation _main/"$2")"

echo "Kernel: ${KERNEL}"
echo "Image: ${IMAGE}"
shift 2
QEMU_ARGS=("$@")

# Make the image file writable, as QEMU needs to write to it
find -L "$(dirname "${IMAGE}")" -samefile "${IMAGE}" -exec chmod +w {} \;

# default QEMU parameters for running an aarch64 image with virtio devices and user networking
# these can be overridden by passing additional parameters to the script, e.g. to enable a graphical display or to use a different machine type
MACHINE="virt,virtualization=true,gic-version=3"
CPU="cortex-a53"
SMP="8"
MEM="4G"
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
    ${DISK_ARGS} \
    ${NETWORK_ARGS} \
    -nographic \
    -chardev stdio,id=char0,signal=on,mux=on \
    -mon chardev=char0,mode=readline \
    -serial chardev:char0 \
    "${QEMU_ARGS[@]}"
