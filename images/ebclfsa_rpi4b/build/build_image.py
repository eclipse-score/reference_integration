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
"""Deploys tar files into the root file system of a Raspberry Pi disk image, without booting it.

Usage: build_image.py <base image> <output image> <tar>...

The base image is copied to the output image. The entries of the tars are written into its root
file system, the largest Linux partition, with debugfs, which edits the file system as a file and
needs no privileges. A later tar replaces files of an earlier one. Mode, owner and symlinks are
taken from the tars. Empty passwords in the base image are locked before deployment is verified.

debugfs runs a list of commands and exits with 0 even when one of them fails, so its error messages
are checked, and at the end every file, symlink and directory of the tars is compared with the image.
"""

import os
import re
import shutil
import struct
import subprocess
import sys
import tarfile
import tempfile

SECTOR = 512
TYPE_LINUX = 0x83
# Messages that are expected: rm of a path that does not exist yet, mkdir of one that does.
HARMLESS = re.compile(r"^debugfs[ :]|File not found by ext2_lookup|already exists|^Allocated inode")
TYPES = {"regular": "file", "directory": "dir", "symlink": "link"}


def find_debugfs():
    for candidate in (shutil.which("debugfs"), "/usr/sbin/debugfs", "/sbin/debugfs"):
        if candidate and os.access(candidate, os.X_OK):
            return candidate
    sys.exit("debugfs (e2fsprogs) is not installed")


def root_partition(image):
    """The root file system as debugfs takes it: the image with the offset of the partition."""
    with open(image, "rb") as f:
        mbr = f.read(SECTOR)
    if mbr[510:512] != b"\x55\xaa":
        sys.exit("%s has no MBR" % image)
    partitions = []
    for index in range(4):
        entry = mbr[446 + 16 * index:446 + 16 * (index + 1)]
        if entry[4] == TYPE_LINUX:
            lba, count = struct.unpack("<II", entry[8:16])
            partitions.append((count, lba))
    if not partitions:
        sys.exit("no Linux partition in %s" % image)
    return "%s?offset=%d" % (image, max(partitions)[1] * SECTOR)


class FileSystem:
    """An ext4 file system edited with debugfs, one session per call of run()."""

    def __init__(self, debugfs, device, work):
        self.debugfs = debugfs
        self.device = device
        self.work = work
        self.files = 0

    def stash(self, data):
        """debugfs writes files from the host only: data goes to a file of the working directory."""
        self.files += 1
        path = os.path.join(self.work, "file-%d" % self.files)
        with open(path, "wb") as out:
            out.write(data)
        return path

    def run(self, commands, write=True):
        """Runs the commands in one session and returns the output of each, in order."""
        script = os.path.join(self.work, "commands")
        with open(script, "w") as out:
            out.write("".join(command + "\n" for command in commands))
        result = subprocess.run(
            [self.debugfs] + (["-w"] if write else []) + ["-f", script, self.device],
            capture_output=True,
            env=dict(os.environ, DEBUGFS_PAGER="__none__", PAGER="__none__"),
        )
        stderr = result.stderr.decode(errors="replace")
        errors = [line for line in stderr.splitlines() if line.strip() and not HARMLESS.search(line)]
        if result.returncode or errors:
            sys.exit("debugfs failed:\n" + "\n".join(errors[:20]))
        # With -f, debugfs prints each command as "debugfs: <command>" before its output.
        outputs = re.split(rb"^debugfs: .*\n", result.stdout, flags=re.M)[1:]
        if len(outputs) != len(commands):
            sys.exit("unexpected output of debugfs")
        return outputs

    def write(self, path, data, mode, uid, gid):
        return [
            "rm " + path,
            "write %s %s" % (self.stash(data), path),
            "sif %s mode 0%o" % (path, 0o100000 | mode),
            "sif %s uid %d" % (path, uid),
            "sif %s gid %d" % (path, gid),
        ]

    def stat(self, paths):
        """Type, mode, owner, size and symlink target of each path, None if it does not exist."""
        result = {}
        for path, out in zip(paths, self.run(["stat " + p for p in paths], write=False)):
            text = out.decode(errors="replace")
            found = re.search(r"Type:\s+(\S+)\s+Mode:\s+(\d+).*?User:\s+(\d+)\s+Group:\s+(\d+).*?Size:\s+(\d+)", text, re.S)
            if not found:
                result[path] = None
                continue
            kind, mode, uid, gid, size = found.groups()
            target = re.search(r'Fast link dest:\s+"(.*)"', text)
            result[path] = {
                "kind": TYPES.get(kind, kind),
                "mode": int(mode, 8) & 0o7777,
                "owner": (int(uid), int(gid)),
                "size": int(size),
                "target": target.group(1) if target else None,
            }
        return result

    def read(self, path):
        return self.run(["cat " + path], write=False)[0]


def tar_entries(path):
    """(path, kind, mode, uid, gid, data) for each entry of a tar; data is the target of a symlink."""
    if not tarfile.is_tarfile(path):
        sys.exit("not a tar file: %s" % path)
    with tarfile.open(path) as tar:
        for member in tar:
            name = os.path.normpath("/" + member.name)
            if name == "/":
                continue
            if member.isdir():
                yield name, "dir", member.mode & 0o7777, member.uid, member.gid, None
            elif member.isreg():
                yield name, "file", member.mode & 0o7777, member.uid, member.gid, tar.extractfile(member).read()
            elif member.issym():
                yield name, "link", None, member.uid, member.gid, member.linkname
            else:
                sys.exit("unsupported entry %s in %s" % (member.name, path))


def deploy(fs, tars):
    """Writes the tars into the file system and returns what each path must look like afterwards."""
    commands = []
    expected = {}
    for tar in tars:
        entries = sorted(tar_entries(tar), key=lambda e: (e[0].count("/"), e[0]))
        listed = {e[0] for e in entries if e[1] == "dir"}
        # debugfs creates no parent directories. Those that the tar does not list are created with
        # the defaults of debugfs if they do not exist; existing ones are left as they are.
        parents = sorted({os.path.dirname(e[0]) for e in entries} - listed - {"/"})
        for parent in parents:
            parts = parent.split("/")
            for n in range(2, len(parts) + 1):
                commands.append("mkdir " + "/".join(parts[:n]))
        for path, kind, mode, uid, gid, data in entries:
            if kind == "dir":
                commands += ["mkdir " + path, "sif %s mode 0%o" % (path, 0o40000 | mode)]
                commands += ["sif %s uid %d" % (path, uid), "sif %s gid %d" % (path, gid)]
                expected[path] = {"kind": "dir", "mode": mode, "owner": (uid, gid)}
            elif kind == "file":
                commands += fs.write(path, data, mode, uid, gid)
                expected[path] = {"kind": "file", "mode": mode, "owner": (uid, gid), "size": len(data)}
            else:
                commands += ["rm " + path, "symlink %s %s" % (path, data)]
                commands += ["sif %s uid %d" % (path, uid), "sif %s gid %d" % (path, gid)]
                expected[path] = {"kind": "link", "owner": (uid, gid), "target": data}
    fs.run(commands)
    return expected


def lock_empty_passwords(fs):
    """Disable empty passwords while preserving other base image credentials."""
    found = fs.stat(["/etc/shadow"])["/etc/shadow"]
    if not found:
        sys.exit("cannot read /etc/shadow")
    shadow = fs.read("/etc/shadow")
    lines = shadow.splitlines(keepends=True)
    root_count = 0
    for index, line in enumerate(lines):
        fields = line.split(b":", 2)
        if len(fields) != 3 or not fields[0]:
            sys.exit("invalid /etc/shadow")
        root_count += fields[0] == b"root"
        if not fields[1]:
            lines[index] = fields[0] + b":!:" + fields[2]
    if root_count != 1:
        sys.exit("invalid /etc/shadow")
    locked = b"".join(lines)
    if locked == shadow:
        return {}
    fs.run(fs.write("/etc/shadow", locked, found["mode"], *found["owner"]))
    return {
        "/etc/shadow": {"kind": "file", "mode": found["mode"], "owner": found["owner"], "size": len(locked)},
    }


def verify(fs, expected):
    actual = fs.stat(sorted(expected))
    wrong = []
    for path, want in sorted(expected.items()):
        have = actual[path]
        if have is None:
            wrong.append("%s: missing" % path)
            continue
        for key, value in want.items():
            # The target of a long symlink is not in the inode; its size is its length.
            if key == "target" and have["target"] is None:
                key, value = "size", len(value.encode())
            if have[key] != value:
                wrong.append("%s: %s is %r, not %r" % (path, key, have[key], value))
    if wrong:
        sys.exit("the image is not as deployed:\n" + "\n".join(wrong[:20]))


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__.split("\n\n")[1])
    base, output, tars = sys.argv[1], sys.argv[2], sys.argv[3:]
    shutil.copyfile(base, output)
    os.chmod(output, 0o644)
    with tempfile.TemporaryDirectory() as work:
        fs = FileSystem(find_debugfs(), root_partition(output), work)
        expected = deploy(fs, tars)
        expected.update(lock_empty_passwords(fs))
        verify(fs, expected)
    print("deployed %d entries of %d tars into %s" % (len(expected), len(tars), os.path.basename(output)))


if __name__ == "__main__":
    main()
