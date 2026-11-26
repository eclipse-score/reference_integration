#!/usr/bin/env python3
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
"""Prepares a Raspberry Pi OS Lite image (.img) for the S-CORE deployment, in place.

The root partition is the ext4 partition with the largest size. It is grown to fill
the image's total size, which is set by --size, so the deployed files fit. Then the
systemd unit of SSH is enabled in the root file system, because Raspberry Pi OS
enables SSH by a file on the boot partition only when that is set up. Everything runs
without privileges: the partition is copied out, resized, and copied back.
"""

import argparse
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile

SECTOR = 512
TYPE_LINUX = 0x83
SSH_UNIT = "/lib/systemd/system/ssh.service"
SSH_WANT = "/etc/systemd/system/multi-user.target.wants/ssh.service"


def run(command, ok=(0,)):
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode not in ok:
        sys.exit("%s failed:\n%s%s" % (command[0], result.stdout, result.stderr))
    return result.stdout


def read_partitions(image):
    with open(image, "rb") as f:
        mbr = f.read(SECTOR)
    if mbr[510:512] != b"\x55\xaa":
        sys.exit("%s has no MBR" % image)
    partitions = []
    for index in range(4):
        entry = 446 + 16 * index
        ptype = mbr[entry + 4]
        if ptype:
            lba, count = struct.unpack("<II", mbr[entry + 8:entry + 16])
            partitions.append({"index": index, "type": ptype, "lba": lba, "count": count})
    return mbr, partitions


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("image")
    parser.add_argument("--size", type=int, required=True, help="total image size in bytes")
    args = parser.parse_args()

    mbr, partitions = read_partitions(args.image)
    root = max((p for p in partitions if p["type"] == TYPE_LINUX), key=lambda p: p["count"], default=None)
    if root is None:
        sys.exit("no Linux partition in %s" % args.image)
    start = root["lba"] * SECTOR
    if args.size % SECTOR or args.size <= start:
        sys.exit("--size must be a multiple of 512 and larger than the root partition's start")
    count = (args.size - start) // SECTOR
    if count < root["count"]:
        sys.exit("the image would shrink the root partition")

    with tempfile.TemporaryDirectory() as work:
        rootfs = os.path.join(work, "root.ext4")
        with open(args.image, "rb") as image, open(rootfs, "wb") as out:
            image.seek(start)
            remaining = root["count"] * SECTOR
            while remaining:
                chunk = image.read(min(1 << 20, remaining))
                if not chunk:
                    sys.exit("the image is shorter than its partition table")
                out.write(chunk)
                remaining -= len(chunk)
            out.truncate(count * SECTOR)

        # e2fsck exits with 1 when it corrected errors, which is fine for a resize.
        run(["e2fsck", "-f", "-y", rootfs], ok=(0, 1))
        run(["resize2fs", rootfs])

        def exists(path):
            return "Inode:" in subprocess.run(["debugfs", "-R", "stat " + path, rootfs],
                                              capture_output=True, text=True).stdout

        if not exists(SSH_UNIT):
            sys.exit("%s is not in the root file system: this is not a Raspberry Pi OS image" % SSH_UNIT)
        if not exists(SSH_WANT):
            script = os.path.join(work, "debugfs.commands")
            with open(script, "w") as commands:
                commands.write("symlink %s %s\n" % (SSH_WANT, SSH_UNIT))
            run(["debugfs", "-w", "-f", script, rootfs])
            if not exists(SSH_WANT):
                sys.exit("cannot enable %s" % SSH_UNIT)

        # Write the grown partition back, then the partition table with its new size.
        with open(rootfs, "rb") as src, open(args.image, "r+b") as image:
            image.seek(start)
            shutil.copyfileobj(src, image)
            entry = 446 + 16 * root["index"]
            mbr = bytearray(mbr)
            mbr[entry + 12:entry + 16] = struct.pack("<I", count)
            image.seek(0)
            image.write(bytes(mbr))
            image.truncate(args.size)

    print("grew the root partition of %s to %d MiB and enabled %s" % (
        os.path.basename(args.image), count * SECTOR // 2**20, os.path.basename(SSH_UNIT)))


if __name__ == "__main__":
    main()
