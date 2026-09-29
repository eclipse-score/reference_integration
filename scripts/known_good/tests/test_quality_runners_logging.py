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
"""Unit tests for logging and stream capture in quality_runners.py."""

import sys
from pathlib import Path

# Make repo root and scripts/ importable so quality_runners and known_good resolve.
_SCRIPTS_DIR = Path(__file__).resolve().parents[2]
_REPO_ROOT = Path(__file__).resolve().parents[3]
for p in (str(_SCRIPTS_DIR), str(_REPO_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from scripts.quality_runners import ProcessResult, run_command  # noqa: E402


def test_run_command_writes_to_log_file(tmp_path: Path, capsys):
    log_file = tmp_path / "test_module.log"
    # Generate output dynamically so the message does not appear as a literal in the command string
    cmd = [
        sys.executable,
        "-c",
        "import sys; sys.stdout.write('MSG_' + 'STDOUT\\n'); sys.stderr.write('MSG_' + 'STDERR\\n')",
    ]

    res = run_command(cmd, log_file=log_file, verbose=False)

    assert isinstance(res, ProcessResult)
    assert res.exit_code == 0
    assert "MSG_STDOUT" in res.stdout
    assert "MSG_STDERR" in res.stderr

    assert log_file.is_file()
    log_content = log_file.read_text(encoding="utf-8")
    assert "MSG_STDOUT" in log_content
    assert "MSG_STDERR" in log_content

    captured = capsys.readouterr()
    assert "MSG_STDOUT" not in captured.out
    assert "MSG_STDERR" not in captured.err


def test_run_command_verbose_mode(tmp_path: Path, capsys):
    log_file = tmp_path / "verbose_module.log"
    cmd = [
        sys.executable,
        "-c",
        "import sys; print('verbose stdout'); print('verbose stderr', file=sys.stderr)",
    ]

    res = run_command(cmd, log_file=log_file, verbose=True)

    assert res.exit_code == 0
    captured = capsys.readouterr()
    assert "verbose stdout" in captured.out
    assert "verbose stderr" in captured.err

    log_content = log_file.read_text(encoding="utf-8")
    assert "verbose stdout" in log_content
    assert "verbose stderr" in log_content


def test_run_command_prints_tail_on_failure(tmp_path: Path, capsys):
    log_file = tmp_path / "failing_module.log"
    cmd = [
        sys.executable,
        "-c",
        "import sys; print('failing out'); print('failing err detail', file=sys.stderr); sys.exit(7)",
    ]

    res = run_command(cmd, log_file=log_file, verbose=False)

    assert res.exit_code == 7
    captured = capsys.readouterr()
    assert "QR: Command failed with exit code 7" in captured.err or "QR: Command failed with exit code 7" in captured.out
    assert "failing err detail" in captured.err or "failing err detail" in captured.out


def test_run_command_creates_parent_directory(tmp_path: Path):
    log_file = tmp_path / "nested" / "logs" / "sub" / "run.log"
    cmd = [sys.executable, "-c", "print('nested ok')"]

    res = run_command(cmd, log_file=log_file, verbose=False)

    assert res.exit_code == 0
    assert log_file.is_file()
    assert "nested ok" in log_file.read_text(encoding="utf-8")
