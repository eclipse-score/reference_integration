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
from pathlib import Path

try:
    from scripts.quality_runners import (
        extract_coverage_summary,
        extract_ut_summary,
        generate_coverage_portal,
        generate_markdown_report,
        generate_rust_module_index,
    )
except ModuleNotFoundError:
    from quality_runners import (
        extract_coverage_summary,
        extract_ut_summary,
        generate_coverage_portal,
        generate_markdown_report,
        generate_rust_module_index,
    )


def test_generate_markdown_report_with_dashboard_column(tmp_path: Path):
    output_path = tmp_path / "coverage_summary.md"
    data = {
        "score_baselibs_cpp": {
            "lines": "93.0%",
            "functions": "85.8%",
            "branches": "64.1%",
            "dashboard": '<a href="../coverage/cpp/score_baselibs/index.html">C++ Dashboard</a>',
        },
        "score_lifecycle_rust": {
            "lines": "88.5%",
            "functions": "",
            "branches": "",
            "dashboard": '<a href="../coverage/rust/score_lifecycle/index.html">Rust Dashboard</a>',
        },
    }
    columns = ["module", "lines", "functions", "branches", "dashboard"]

    generate_markdown_report(data, title="Coverage Analysis Summary", columns=columns, output_path=output_path)

    content = output_path.read_text(encoding="utf-8")
    assert "# Coverage Analysis Summary" in content
    assert "| module | lines | functions | branches | dashboard |" in content
    assert (
        '| score_baselibs_cpp | 93.0% | 85.8% | 64.1% | <a href="../coverage/cpp/score_baselibs/index.html">C++ Dashboard</a> |'
        in content
    )
    assert (
        '| score_lifecycle_rust | 88.5% |  |  | <a href="../coverage/rust/score_lifecycle/index.html">Rust Dashboard</a> |'
        in content
    )


def test_generate_rust_module_index_single_target(tmp_path: Path):
    module_dir = tmp_path / "rust" / "score_logging"
    target_dir = module_dir / "_score_logging__tests" / "blanket"
    target_dir.mkdir(parents=True)
    (target_dir / "index.html").write_text("<html>Blanket report</html>")

    generate_rust_module_index("score_logging", module_dir)

    index_file = module_dir / "index.html"
    assert index_file.is_file()
    content = index_file.read_text(encoding="utf-8")
    assert 'meta http-equiv="refresh"' in content
    assert "_score_logging__tests/blanket/index.html" in content


def test_generate_rust_module_index_multiple_targets(tmp_path: Path):
    module_dir = tmp_path / "rust" / "score_lifecycle"
    target1 = module_dir / "_score_lifecycle__tests" / "blanket"
    target1.mkdir(parents=True)
    (target1 / "index.html").write_text("<html>Report 1</html>")
    target2 = module_dir / "_score_lifecycle__loom_tests" / "blanket"
    target2.mkdir(parents=True)
    (target2 / "index.html").write_text("<html>Report 2</html>")

    generate_rust_module_index("score_lifecycle", module_dir)

    index_file = module_dir / "index.html"
    assert index_file.is_file()
    content = index_file.read_text(encoding="utf-8")
    assert "_score_lifecycle__tests/blanket/index.html" in content
    assert "_score_lifecycle__loom_tests/blanket/index.html" in content


def test_generate_coverage_portal(tmp_path: Path):
    coverage_dir = tmp_path / "coverage"
    summary = {
        "score_baselibs_cpp": {
            "lines": "93.0%",
            "functions": "85.8%",
            "branches": "64.1%",
            "dashboard": "[C++ Dashboard](../coverage/cpp/score_baselibs/index.html)",
        },
        "score_logging_rust": {
            "lines": "89.2%",
            "functions": "",
            "branches": "",
            "dashboard": "[Rust Dashboard](../coverage/rust/score_logging/index.html)",
        },
    }

    generate_coverage_portal(coverage_dir, summary)

    portal_index = coverage_dir / "index.html"
    assert portal_index.is_file()
    content = portal_index.read_text(encoding="utf-8")
    assert "Code Coverage Dashboards" in content
    assert "score_baselibs" in content
    assert "cpp/score_baselibs/index.html" in content
    assert "score_logging" in content
    assert "rust/score_logging/index.html" in content


def test_extract_coverage_summary_cpp():
    logs = """
    Overall coverage rate:
      lines......: 93.0% (1234 of 1327 lines)
      functions..: 85.8% (295 of 344 functions)
      branches...: 64.1% (702 of 1096 branches)
    """
    summary = extract_coverage_summary(logs)
    assert summary["lines"] == "93.0%"
    assert summary["functions"] == "85.8%"
    assert summary["branches"] == "64.1%"


def test_extract_coverage_summary_rust():
    logs = """
    ---
    Overall line coverage: 87.50% (350/400 lines across 2 targets)
    ---
    """
    summary = extract_coverage_summary(logs)
    assert summary["lines"] == "87.50%"
    assert summary["functions"] == ""
    assert summary["branches"] == ""
