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

set -euo pipefail

IFS_IMAGE=$1

if ! command -v qemu-system-aarch64 > /dev/null; then
    echo "Please install qemu-system-aarch64"
    exit 1
fi

echo "Starting QEMU with IFS image: ${IFS_IMAGE}"
qemu-system-aarch64 \
    -m 1G \
    -machine virt,virtualization=true,gic-version=3 \
    -cpu cortex-a53 \
    -smp 2 \
    -pidfile /tmp/qemu.pid \
    -nographic \
    -kernel "${IFS_IMAGE}" \
    -chardev stdio,id=char0,signal=on,mux=on \
    -mon chardev=char0,mode=readline \
    -serial chardev:char0 \
    -object rng-random,filename=/dev/urandom,id=rng0 \
    -netdev user,id=net0,net=192.168.7.0/24,dhcpstart=192.168.7.2,dns=192.168.7.3,host=192.168.7.5,hostfwd=tcp::2222-:22,hostfwd=tcp::3333-:3333 \
    -device virtio-net-device,netdev=net0 \
    -device virtio-rng-device,rng=rng0
