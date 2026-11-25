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
"""Tests for image deployment without debugfs or a real image."""

import io
import struct
import sys
import tarfile

import build_image
import pytest


def _tar(path, entries):
    with tarfile.open(path, "w") as archive:
        for name, kind, mode, uid, gid, data in entries:
            member = tarfile.TarInfo(name)
            member.mode, member.uid, member.gid = mode, uid, gid
            if kind == "dir":
                member.type = tarfile.DIRTYPE
            elif kind == "link":
                member.type = tarfile.SYMTYPE
                member.linkname = data
            else:
                member.size = len(data)
            archive.addfile(member, io.BytesIO(data) if kind == "file" else None)


def test_root_partition_selects_largest_linux_partition(tmp_path):
    image = tmp_path / "disk"
    mbr = bytearray(512)
    mbr[510:512] = b"\x55\xaa"
    for index, (kind, lba, count) in enumerate([(0x83, 2, 4), (0x0C, 40, 100), (0x83, 9, 8)]):
        offset = 446 + index * 16
        mbr[offset + 4] = kind
        struct.pack_into("<II", mbr, offset + 8, lba, count)
    image.write_bytes(mbr)
    assert build_image.root_partition(image) == f"{image}?offset={9 * 512}"


def test_main_requires_base_output_and_tar(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["build_image.py", "base", "output"])
    with pytest.raises(SystemExit, match="Usage: build_image.py"):
        build_image.main()


def test_tar_entries_preserves_paths_modes_owners_and_symlinks(tmp_path):
    archive = tmp_path / "files.tar"
    _tar(
        archive,
        [
            ("opt/app", "dir", 0o2750, 12, 34, None),
            ("opt/app/../app/config", "file", 0o640, 56, 78, b"config"),
            ("opt/app/current", "link", 0o777, 90, 91, "config"),
        ],
    )
    assert list(build_image.tar_entries(archive)) == [
        ("/opt/app", "dir", 0o2750, 12, 34, None),
        ("/opt/app/config", "file", 0o640, 56, 78, b"config"),
        ("/opt/app/current", "link", None, 90, 91, "config"),
    ]


def test_write_stashes_content_and_sets_file_mode_and_owner(tmp_path):
    fs = build_image.FileSystem("debugfs", "disk", str(tmp_path))
    commands = fs.write("/opt/config", b"hello", 0o640, 12, 34)
    assert (tmp_path / "file-1").read_bytes() == b"hello"
    assert commands == [
        "rm /opt/config",
        f"write {tmp_path}/file-1 /opt/config",
        "sif /opt/config mode 0100640",
        "sif /opt/config uid 12",
        "sif /opt/config gid 34",
    ]


def test_deploy_creates_parents_and_later_tar_replaces_file(tmp_path):
    first, second = tmp_path / "first.tar", tmp_path / "second.tar"
    _tar(first, [("opt/app/config", "file", 0o600, 1, 2, b"old")])
    _tar(
        second,
        [
            ("opt/app/config", "file", 0o640, 3, 4, b"new data"),
            ("opt/app/link", "link", 0o777, 5, 6, "config"),
            ("opt/app", "dir", 0o750, 7, 8, None),
        ],
    )
    fs = build_image.FileSystem("debugfs", "disk", str(tmp_path))
    commands = []
    fs.run = lambda batch: commands.extend(batch)
    expected = build_image.deploy(fs, [first, second])
    assert commands[:2] == ["mkdir /opt", "mkdir /opt/app"]
    assert commands.index("mkdir /opt/app", 2) < commands.index("symlink /opt/app/link config")
    assert "sif /opt/app mode 040750" in commands
    assert "sif /opt/app uid 7" in commands
    assert "sif /opt/app gid 8" in commands
    assert expected == {
        "/opt/app": {"kind": "dir", "mode": 0o750, "owner": (7, 8)},
        "/opt/app/config": {"kind": "file", "mode": 0o640, "owner": (3, 4), "size": 8},
        "/opt/app/link": {"kind": "link", "owner": (5, 6), "target": "config"},
    }


def test_stat_parses_mode_owner_and_link_target(tmp_path):
    fs = build_image.FileSystem("debugfs", "disk", str(tmp_path))
    fs.run = lambda _commands, **_kwargs: [
        b'Inode: 12 Type: symlink Mode:  0777 User:  12 Group:  34 Size: 6\nFast link dest: "config"\n'
    ]
    assert fs.stat(["/link"]) == {
        "/link": {"kind": "link", "mode": 0o777, "owner": (12, 34), "size": 6, "target": "config"}
    }


def test_verify_rejects_wrong_owner(tmp_path):
    fs = build_image.FileSystem("debugfs", "disk", str(tmp_path))
    fs.stat = lambda _paths: {"/file": {"kind": "file", "owner": (1, 99)}}
    with pytest.raises(SystemExit, match="owner is"):
        build_image.verify(fs, {"/file": {"kind": "file", "owner": (1, 2)}})
