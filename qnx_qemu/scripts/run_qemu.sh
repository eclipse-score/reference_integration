#!/bin/bash

set -euo pipefail

QNX_HOST=$1

IFS_IMAGE=$2

qemu-system-x86_64 \
                -smp 2 \
                --enable-kvm \
                -cpu Cascadelake-Server-v5 \
                -m 1G \
                -pidfile /tmp/qemu.pid \
                -nographic \
                -kernel "${IFS_IMAGE}" \
                -serial mon:stdio \
                -object rng-random,filename=/dev/urandom,id=rng0 \
                -device virtio-rng-pci,rng=rng0 