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

from known_good.models.module import Metadata, Module  # noqa: E402

from scripts import quality_runners as qr  # noqa: E402
from scripts.quality_runners import ProcessResult, parse_arguments, run_command  # noqa: E402


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
    fail_marker = "QR: Command failed with exit code 7"
    assert fail_marker in captured.err or fail_marker in captured.out
    assert "failing err detail" in captured.err or "failing err detail" in captured.out


def test_run_command_creates_parent_directory(tmp_path: Path):
    log_file = tmp_path / "nested" / "logs" / "sub" / "run.log"
    cmd = [sys.executable, "-c", "print('nested ok')"]

    res = run_command(cmd, log_file=log_file, verbose=False)

    assert res.exit_code == 0
    assert log_file.is_file()
    assert "nested ok" in log_file.read_text(encoding="utf-8")


def test_parse_arguments_log_dir_defaults(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["quality_runners.py"])
    args = parse_arguments()

    expected_log_dir = Path(qr.__file__).parent.parent / "artifacts/logs"
    assert args.log_output_dir == expected_log_dir
    assert args.verbose is False


def test_parse_arguments_custom_flags(monkeypatch, tmp_path: Path):
    custom_log_dir = tmp_path / "custom_logs"
    monkeypatch.setattr(
        sys,
        "argv",
        ["quality_runners.py", "--log-output-dir", str(custom_log_dir), "--verbose"],
    )
    args = parse_arguments()

    assert args.log_output_dir == custom_log_dir
    assert args.verbose is True


def test_run_unit_test_routes_to_module_log(monkeypatch, tmp_path: Path):
    module = Module(
        name="score_testmod",
        repo="https://example.com/mod.git",
        hash="abc12345",
        metadata=Metadata(code_root_path="/...", langs=["cpp"]),
    )

    recorded_kwargs = {}

    def fake_run_command(_command, **kwargs):
        recorded_kwargs.update(kwargs)
        return ProcessResult(
            stdout="Test cases: finished (2 passing, 0 failing, 0 skipped, out of 2 test cases)",
            stderr="",
            exit_code=0,
        )

    monkeypatch.setattr(qr, "run_command", fake_run_command)

    res = qr.run_unit_test_with_coverage(module, log_dir=tmp_path, verbose=False)

    assert res["passed"] == 2
    assert res["exit_code"] == 0
    assert recorded_kwargs.get("log_file") == tmp_path / "score_testmod.log"
    assert recorded_kwargs.get("verbose") is False


def test_run_cpp_coverage_routes_to_module_log(monkeypatch, tmp_path: Path):
    module = Module(
        name="score_testmod",
        repo="https://example.com/mod.git",
        hash="abc12345",
        metadata=Metadata(code_root_path="/...", langs=["cpp"]),
    )

    recorded_kwargs = {}

    def fake_cpp_coverage(_mod, _artifact_dir, **kwargs):
        recorded_kwargs.update(kwargs)
        return ProcessResult(
            stdout="lines......: 85.0% (100 of 118 lines)\nfunctions..: 90.0%\nbranches...: 70.0%",
            stderr="",
            exit_code=0,
        )

    monkeypatch.setattr(qr, "cpp_coverage", fake_cpp_coverage)

    res = qr.run_cpp_coverage_extraction(module, output_path=tmp_path / "coverage", log_dir=tmp_path, verbose=False)

    assert res["exit_code"] == 0
    assert recorded_kwargs.get("log_file") == tmp_path / "score_testmod.log"
    assert recorded_kwargs.get("verbose") is False


def test_run_rust_coverage_routes_to_module_log(monkeypatch, tmp_path: Path):
    module = Module(
        name="score_testmod",
        repo="https://example.com/mod.git",
        hash="abc12345",
        metadata=Metadata(code_root_path="/...", langs=["rust"]),
    )

    recorded_kwargs = {}

    def fake_rust_coverage(_mod, _artifact_dir, **kwargs):
        recorded_kwargs.update(kwargs)
        return ProcessResult(
            stdout="line coverage: 92.5%",
            stderr="",
            exit_code=0,
        )

    monkeypatch.setattr(qr, "rust_coverage", fake_rust_coverage)

    res = qr.run_rust_coverage_extraction(module, output_path=tmp_path / "coverage", log_dir=tmp_path, verbose=False)

    assert res["exit_code"] == 0
    assert recorded_kwargs.get("log_file") == tmp_path / "score_testmod.log"
    assert recorded_kwargs.get("verbose") is False
