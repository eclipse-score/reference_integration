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
"""Tests for the image preparation logic, using synthetic partition tables."""

import struct
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent / "build"))
import prepare  # noqa: E402


def _image(path, partitions):
    mbr = bytearray(512)
    mbr[510:512] = b"\x55\xaa"
    for index, (kind, lba, count) in enumerate(partitions):
        entry = 446 + index * 16
        mbr[entry + 4] = kind
        struct.pack_into("<II", mbr, entry + 8, lba, count)
    path.write_bytes(mbr + bytes(512 * 15))


def test_read_partitions_extracts_nonempty_entries(tmp_path):
    image = tmp_path / "disk"
    _image(image, [(0x0C, 1, 2), (0x83, 4, 5)])
    _, partitions = prepare.read_partitions(image)
    assert partitions == [
        {"index": 0, "type": 0x0C, "lba": 1, "count": 2},
        {"index": 1, "type": 0x83, "lba": 4, "count": 5},
    ]


def test_read_partitions_rejects_missing_signature(tmp_path):
    image = tmp_path / "disk"
    image.write_bytes(bytes(512))
    with pytest.raises(SystemExit, match="has no MBR"):
        prepare.read_partitions(image)


def test_main_requires_size(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["prepare.py", "disk"])
    with pytest.raises(SystemExit) as exc:
        prepare.main()
    assert exc.value.code == 2
    assert "--size" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("size", "error"),
    [(512 * 4, "--size must"), (512 * 4 + 1, "--size must"), (512 * 6, "would shrink")],
)
def test_main_rejects_invalid_size_before_running_tools(tmp_path, monkeypatch, size, error):
    image = tmp_path / "disk"
    _image(image, [(0x83, 4, 3)])
    monkeypatch.setattr(sys, "argv", ["prepare.py", str(image), "--size", str(size)])
    monkeypatch.setattr(prepare, "run", lambda *_args, **_kwargs: pytest.fail("must reject size first"))
    with pytest.raises(SystemExit, match=error):
        prepare.main()


def test_main_grows_largest_linux_partition_at_its_sector_offset(tmp_path, monkeypatch):
    image = tmp_path / "disk"
    _image(image, [(0x83, 1, 2), (0x0C, 3, 1), (0x83, 4, 3)])
    data = bytearray(image.read_bytes())
    data[4 * 512 : 7 * 512] = b"R" * (3 * 512)
    image.write_bytes(data)
    monkeypatch.setattr(sys, "argv", ["prepare.py", str(image), "--size", str(10 * 512)])
    calls = []
    monkeypatch.setattr(prepare, "run", lambda command, **kwargs: calls.append((command[0], kwargs)))
    monkeypatch.setattr(prepare.subprocess, "run", lambda *_args, **_kwargs: SimpleNamespace(stdout="Inode: 1"))
    prepare.main()
    _, parts = prepare.read_partitions(image)
    assert parts[0]["count"] == 2
    assert parts[2]["count"] == 6
    assert image.read_bytes()[4 * 512 : 7 * 512] == b"R" * (3 * 512)
    assert len(image.read_bytes()) == 10 * 512
    assert [name for name, _ in calls] == ["e2fsck", "resize2fs"]
    assert calls[0][1] == {"ok": (0, 1)}
