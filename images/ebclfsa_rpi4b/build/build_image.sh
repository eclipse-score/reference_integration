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

# Deploys tar files into the root file system of a Raspberry Pi disk image (.wic) without booting it:
# the QEMU image boots to copy the files in, which a Raspberry Pi image cannot do. Everything is
# written with debugfs into the root partition of a copy of the image, the build needs no privileges.
# Like the QEMU image it also allows root login without a password, for integration testing only.
#
# Usage: build_image.sh <working directory> <image source directory> <image target directory> <tar>...

set -euo pipefail

if [[ $# -lt 4 ]]; then
    echo "Error: expected a working directory, the image source and target directories and tar files" >&2
    exit 1
fi
WORKING_DIR="$1"
IMAGE_SOURCE="$2"
IMAGE_TARGET="$3"
shift 3
DEPLOY_SRCS=("$@")

DEBUGFS="$(command -v debugfs || true)"
for candidate in /usr/sbin/debugfs /sbin/debugfs; do
    [[ -n "$DEBUGFS" ]] || { [[ -x "$candidate" ]] && DEBUGFS="$candidate"; }
done
[[ -n "$DEBUGFS" ]] || { echo "Error: debugfs (e2fsprogs) is not installed" >&2; exit 1; }

for src in "${DEPLOY_SRCS[@]}"; do
    [[ -f "$src" && "$src" =~ \.tar(\.(gz|bz2|xz))?$ ]] || { echo "Error: not a tar file: $src" >&2; exit 1; }
done

mkdir -p "$IMAGE_TARGET"
rm -f "${IMAGE_TARGET:?}/"*
cp -L "$IMAGE_SOURCE"/*.wic "$IMAGE_TARGET"/
IMAGE="$(find "$IMAGE_TARGET" -maxdepth 1 -name '*.wic' -print -quit)"
chmod +w "$IMAGE"

python3 - "$DEBUGFS" "$IMAGE" "$WORKING_DIR" "${DEPLOY_SRCS[@]}" <<'PY'
import os
import re
import struct
import subprocess
import sys
import tarfile

debugfs, image, work = sys.argv[1:4]
tars = sys.argv[4:]

# The root file system is the largest Linux partition of the image.
mbr = open(image, "rb").read(512)
partitions = []
for i in range(4):
    entry = mbr[446 + 16 * i:446 + 16 * (i + 1)]
    lba, sectors = struct.unpack("<II", entry[8:16])
    if entry[4] == 0x83:
        partitions.append((sectors, lba))
if not partitions:
    sys.exit("no Linux partition in " + image)
rootfs = "%s?offset=%d" % (image, max(partitions)[1] * 512)

payload = os.path.join(work, "payload")
os.makedirs(payload, exist_ok=True)
counter = 0


def stash(data):
    global counter
    counter += 1
    path = os.path.join(payload, str(counter))
    with open(path, "wb") as out:
        out.write(data)
    return path


def run(commands):
    """Runs debugfs commands in the root file system and returns the output; errors that only say that
    something that is replaced does not exist, or exists already, are fine."""
    script = os.path.join(work, "debugfs.commands")
    with open(script, "w") as out:
        out.write("\n".join(commands) + "\n")
    result = subprocess.run([debugfs, "-w", "-f", script, rootfs], capture_output=True, text=True)
    errors = [
        line for line in (result.stdout + result.stderr).splitlines()
        if line.strip()
        and not line.startswith("debugfs")
        and not re.search(r"File not found by ext2_lookup|already exists|^Allocated inode", line)
    ]
    if errors:
        sys.exit("debugfs failed:\n" + "\n".join(errors[:20]))
    return result.stdout


def entries(tar_path):
    with tarfile.open(tar_path) as tar:
        for member in tar:
            path = "/" + member.name.lstrip("./").rstrip("/")
            if path == "/":
                continue
            if member.isdir():
                yield path, "dir", member.mode & 0o7777, None
            elif member.isreg():
                yield path, "file", member.mode & 0o7777, tar.extractfile(member).read()
            elif member.issym():
                yield path, "link", 0o777, member.linkname
            else:
                sys.exit("unsupported entry %s in %s" % (member.name, tar_path))


commands = []
expected = {}
for tar_path in tars:
    items = list(entries(tar_path))
    parents = set()
    for path, _, _, _ in items:
        parts = path.split("/")[1:-1]
        for n in range(1, len(parts) + 1):
            parents.add("/" + "/".join(parts[:n]))
    explicit = {path for path, kind, _, _ in items if kind == "dir"}
    for directory in sorted(parents - explicit, key=lambda d: d.count("/")):
        commands += ["mkdir " + directory]
    for path, kind, mode, data in sorted(items, key=lambda i: (i[0].count("/"), i[0])):
        if kind == "dir":
            commands += ["mkdir " + path, "sif %s mode 0%o" % (path, 0o40000 | mode)]
        elif kind == "file":
            commands += ["rm " + path, "write %s %s" % (stash(data), path), "sif %s mode 0%o" % (path, 0o100000 | mode)]
            expected[path] = len(data)
        else:
            commands += ["rm " + path, "symlink %s %s" % (path, data)]
        commands += ["sif %s uid 0" % path, "sif %s gid 0" % path]
run(commands)

# Allow root login without a password, like the QEMU image, for integration testing only.
commands = [
    "rm /etc/ssh/sshd_config.d/99-integration-test.conf",
    "write %s /etc/ssh/sshd_config.d/99-integration-test.conf" % stash(
        b"PermitRootLogin yes\nPermitEmptyPasswords yes\nPasswordAuthentication yes\n"),
    "sif /etc/ssh/sshd_config.d/99-integration-test.conf mode 0100644",
    "sif /etc/ssh/sshd_config.d/99-integration-test.conf uid 0",
    "sif /etc/ssh/sshd_config.d/99-integration-test.conf gid 0",
]
run(commands)
shadow = subprocess.run([debugfs, "-R", "cat /etc/shadow", rootfs], capture_output=True, text=True).stdout
stat = subprocess.run([debugfs, "-R", "stat /etc/shadow", rootfs], capture_output=True, text=True).stdout
owner = re.search(r"Mode:\s+(\d+).*?User:\s+(\d+)\s+Group:\s+(\d+)", stat, re.S)
if not shadow.startswith("root:") or not owner:
    sys.exit("cannot read /etc/shadow")
mode, uid, gid = owner.groups()
run([
    "rm /etc/shadow",
    "write %s /etc/shadow" % stash(re.sub(r"^root:[^:]*:", "root::", shadow, count=1).encode()),
    "sif /etc/shadow mode 0100%s" % mode[-3:], "sif /etc/shadow uid " + uid, "sif /etc/shadow gid " + gid,
])

# Everything that was deployed has to be in the image with the size that it has in the tar.
for path, size in expected.items():
    out = subprocess.run([debugfs, "-R", "stat " + path, rootfs], capture_output=True, text=True).stdout
    found = re.search(r"Size:\s+(\d+)", out)
    if not found or int(found.group(1)) != size:
        sys.exit("%s is not in the image as it is in the tar (%s)" % (path, found.group(1) if found else "missing"))
print("deployed %d files into %s" % (len(expected), os.path.basename(image)))
PY
