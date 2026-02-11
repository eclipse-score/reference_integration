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
echo "Starting QEMU with IFS image: ${IFS_IMAGE}"
qemu-system-x86_64 \
                -enable-kvm \
                -smp 2 \
                -cpu host\
                -m 1G \
                -pidfile /tmp/qemu.pid \
                -nographic \
                -kernel "${IFS_IMAGE}" \
                -chardev stdio,id=char0,signal=on,mux=on \
                -mon chardev=char0,mode=readline \
                -serial chardev:char0 \
                -rtc base="2026-02-11T12:00:00",clock=host,driftfix=slew \
                -object rng-random,filename=/dev/urandom,id=rng0 \
                -netdev bridge,id=net0,br=virbr0 -device virtio-net-pci,netdev=net0 \
                -device virtio-rng-pci,rng=rng0