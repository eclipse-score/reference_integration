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

QNX_HOST=$1
IFS_IMAGE=$2

# Set KVM options based on QEMU_NO_KVM if user does not have kvm - like nested VMs
if [ -z "${QEMU_NO_KVM:-}" ]; then
    QEMU_KVM_OPTS="-enable-kvm -smp 2 -cpu host"
else
    QEMU_KVM_OPTS="-smp 2 -cpu Cascadelake-Server-v5"
fi

echo "Starting QEMU with IFS image: ${IFS_IMAGE}"
qemu-system-x86_64 \
                ${QEMU_KVM_OPTS} \
                -m 1G \
                -pidfile /tmp/qemu.pid \
                -nographic \
                -kernel "${IFS_IMAGE}" \
                -chardev stdio,id=char0,signal=on,mux=on \
                -mon chardev=char0,mode=readline \
                -serial chardev:char0 \
                -object rng-random,filename=/dev/urandom,id=rng0 \
                -netdev bridge,id=net0,br=virbr0 -device virtio-net-pci,netdev=net0 \
                -device virtio-rng-pci,rng=rng0
