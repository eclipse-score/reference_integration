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
from types import SimpleNamespace

import pytest
from module_tests import (
    STATUS_LINE,
    _collect_coverage,
    combine_reports,
    count_testcases,
    coverage_args,
    graph_modules,
    lcov_percentages,
    normalize_lcov,
    override_rc,
    report,
)


def test_graph_modules_walks_nested_and_indirect_deps():
    graph = {
        "key": "<root>",
        "dependencies": [
            {"name": "rules_cc", "version": "0.2.22", "dependencies": [{"name": "platforms", "version": "1.1.0"}]},
            {"name": "bazel_tools", "version": ""},
        ],
        "indirectDependencies": [{"name": "zlib", "version": "1.3.1"}],
    }
    assert graph_modules(graph) == {"rules_cc", "platforms", "zlib"}


def test_override_rc_is_sorted_one_line_per_module():
    rc = override_rc({"zlib": Path("/o/zlib+"), "platforms": Path("/o/platforms")})
    assert rc == "common --override_module=platforms=/o/platforms\ncommon --override_module=zlib=/o/zlib+\n"


def test_override_rc_appends_extra_test_config_as_build_flags():
    rc = override_rc({"zlib": Path("/o/zlib+")}, ["@m//p:flag=v"])
    assert rc == "common --override_module=zlib=/o/zlib+\nbuild --@m//p:flag=v\n"


def test_coverage_args_put_unified_config_before_target_separator():
    args = coverage_args(["--config=x86_64-linux", "--", "//score/...", "-//score/test/..."], ["cpp"])
    assert args == [
        "coverage",
        "--lockfile_mode=update",
        "--config=x86_64-linux",
        "--config=unified",
        "--build_tests_only",
        "--config=llvm_cov",
        "--",
        "//score/...",
        "-//score/test/...",
    ]


def test_coverage_args_register_ferrocene_only_for_rust():
    args = coverage_args(["//src/..."], ["rust"])
    assert args[-2:] == ["--config=llvm_cov", "--config=unified-rust"]
    assert "--config=unified-rust" not in coverage_args(["//score/..."], ["cpp"])


def test_coverage_args_exclude_targets_after_separator():
    args = coverage_args(["--config=x86_64-linux", "//..."], ["rust"], ["//score/rust:miri_tests"])
    assert args[-3:] == ["--config=unified-rust", "--", "-//score/rust:miri_tests"]
    # An existing separator is reused, the excludes go after the module's own targets.
    args = coverage_args(["--", "//score/...", "-//score/test/..."], ["cpp"], ["//score/a:b"])
    assert args[-5:] == ["--config=llvm_cov", "--", "//score/...", "-//score/test/...", "-//score/a:b"]


def test_baselibs_coverage_preserves_targets_and_only_adds_llvm_exclusions():
    """LLVM exceptions must not disable these tests in a regular GCC test run."""
    test_args = ["--config=score-linux-x86_64", "--", "//..."]
    normal = coverage_args(test_args, ["cpp"], enabled=False, module="score_baselibs")
    assert normal == [
        "test",
        "--lockfile_mode=update",
        "--config=score-linux-x86_64",
        "--config=unified",
        "--",
        "//...",
    ]

    coverage = coverage_args(test_args, ["cpp"], module="score_baselibs")
    assert "--config=score-linux-x86_64" not in coverage
    assert "--build_tests_only" in coverage
    assert coverage[coverage.index("--") + 1 :] == [
        "//...",
        "-//score/language/safecpp/aborts_upon_exception/...",
        "-//score/language/safecpp/safe_math/details:floating_point_environment_test",
        "-//score/os/linux/utils/test:network_interface_test",
    ]
    # ref_int selects nlohmann JSON, so the compatibility test's vajson-specific
    # pretty-printing exclusion is unnecessary here.
    assert not any("vajson" in target for target in coverage)
    assert "-//score/os/linux/utils/test:network_interface_test" not in coverage_args(
        ["--", "//score/..."], ["cpp"], module="score_logging"
    )


def test_status_line_reads_bazel_failures():
    log = (
        "//a:ok_test      PASSED in 1.0s\n"
        "//a:bad_test     FAILED in 2.0s\n"
        "//b:slow_test    TIMEOUT in 60.0s\n"
        "//c:lib_test     FAILED TO BUILD\n"
    )
    assert STATUS_LINE.findall(log) == [
        ("//a:bad_test", "FAILED"),
        ("//b:slow_test", "TIMEOUT"),
        ("//c:lib_test", "FAILED TO BUILD"),
    ]


def test_test_counts_classifies_testcases(tmp_path):
    xml = tmp_path / "a" / "test.xml"
    xml.parent.mkdir()
    xml.write_text(
        "<testsuites><testsuite>"
        '<testcase name="ok"/><testcase name="bad"><failure/></testcase>'
        '<testcase name="crash"><error/></testcase><testcase name="off" status="notrun"/>'
        "</testsuite></testsuites>"
    )
    assert count_testcases(tmp_path) == {"passed": 1, "failed": 2, "skipped": 1, "total": 4}


def test_lcov_percentages_sums_all_records(tmp_path):
    lcov = tmp_path / "lcov.dat"
    lcov.write_text("SF:a.cpp\nLF:10\nLH:5\nFNF:2\nFNH:2\nend_of_record\nSF:b.cpp\nLF:10\nLH:10\nend_of_record\n")
    assert lcov_percentages(lcov) == {"lines": "75.0%", "functions": "100.0%", "branches": ""}


def test_equal_relative_paths_in_different_modules_remain_distinct(tmp_path):
    for module, hits in [("first", 1), ("second", 0)]:
        report = tmp_path / module / "coverage" / "coverage_report.dat"
        report.parent.mkdir(parents=True)
        report.write_text(normalize_lcov(f"SF:src/lib.rs\nDA:1,{hits}\nend_of_record\n", module))
    output = tmp_path / "coverage-report" / "coverage_report.dat"
    combine_reports(tmp_path, ["second", "first", "missing"], output)
    assert output.read_text() == (
        "SF:external/first+/src/lib.rs\nDA:1,1\nend_of_record\nSF:external/second+/src/lib.rs\nDA:1,0\nend_of_record\n"
    )


@pytest.mark.parametrize("prefix", ["external/dep+/", "../dep+/"])
def test_external_dependency_is_not_reassigned_to_tested_module(prefix):
    assert normalize_lcov(f"SF:{prefix}src/lib.h\nDA:2,1\n", "owner") == ("SF:external/dep+/src/lib.h\nDA:2,1\n")


@pytest.mark.parametrize(
    "path", ["/unknown/lib.cpp", "src/../../lib.cpp", "../dep+/../lib.cpp", "_virtual_includes/a.h"]
)
def test_unresolvable_sources_fail_instead_of_silently_matching_wrong_files(path):
    with pytest.raises(ValueError, match="coverage source"):
        normalize_lcov(f"SF:{path}\n", "owner")


def test_coverage_tool_export_is_rebased_for_documentation(tmp_path, monkeypatch):
    """Packaging belongs to coverage_tool; ref_int consumes its exported plain LCOV."""
    workspace = tmp_path / "workspace"
    out = tmp_path / "reports" / "score_persistency"
    out.mkdir(parents=True)

    def export(args, cwd, env):
        assert cwd == workspace
        assert env == {"EXISTING": "value", "COVERAGE_THRESHOLD": "0"}
        assert args == [
            "run",
            "--lockfile_mode=update",
            "@score_coverage//:generate_coverage_html",
            "--",
            "--testlogs-subdir=",
            "--archive-dir",
            str(out / "coverage"),
        ]
        report = out / "coverage" / "coverage_report.dat"
        report.parent.mkdir()
        report.write_text("SF:score/kvs/kvs.cpp\nDA:1,3\nBRDA:1,0,0,-\nend_of_record\n")
        return SimpleNamespace(stdout="exported", returncode=0)

    monkeypatch.setattr("module_tests.bazel", export)
    assert _collect_coverage(workspace, out, {"EXISTING": "value"}) == 0
    assert (out / "coverage" / "coverage_report.dat").read_text() == (
        "SF:external/score_persistency+/score/kvs/kvs.cpp\nDA:1,3\nBRDA:1,0,0,-\nend_of_record\n"
    )


def test_coverage_export_failure_is_propagated(tmp_path, monkeypatch):
    monkeypatch.setattr("module_tests.bazel", lambda *_args: SimpleNamespace(stdout="export failed", returncode=2))
    assert _collect_coverage(tmp_path, tmp_path / "score_persistency", {}) == 2


def test_modules_awaiting_coverage_tool_still_run_tests():
    args = coverage_args(["--config=x86_64-linux", "--", "//score/..."], ["cpp"], enabled=False)
    assert args[0] == "test"
    assert "--config=unified" in args
    assert "--config=llvm_cov" not in args
    assert args[-2:] == ["--", "//score/..."]


def test_documentation_ignores_coverage_from_modules_awaiting_coverage_tool(tmp_path, monkeypatch):
    """Old artifacts must not bring an unsupported module back into the documentation report."""
    modules = {name: SimpleNamespace(name=name) for name in ("score_persistency", "score_communication")}
    monkeypatch.setattr("module_tests.REF_INT", tmp_path)
    monkeypatch.setattr("module_tests.load_known_good", lambda _path: SimpleNamespace(modules={"target_sw": modules}))
    for name in modules:
        lcov = tmp_path / "reports" / name / "coverage" / "coverage_report.dat"
        lcov.parent.mkdir(parents=True)
        lcov.write_text(f"SF:external/{name}+/source.cpp\nDA:1,1\nLF:1\nLH:1\nend_of_record\n")
    assert report(SimpleNamespace(reports_dir=tmp_path / "reports", out_dir=tmp_path / "summaries")) == 0
    combined = (tmp_path / "coverage-report" / "coverage_report.dat").read_text()
    assert "score_persistency+" in combined
    assert "score_communication+" not in combined
    summary = (tmp_path / "summaries" / "coverage_summary.md").read_text()
    assert "score_persistency" in summary
    assert "score_communication" not in summary


def test_missing_reports_remove_stale_coverage_instead_of_reusing_it(tmp_path):
    output = tmp_path / "coverage-report" / "coverage_report.dat"
    output.parent.mkdir()
    output.write_text("SF:external/old+/a.cpp\nDA:1,1\n")
    combine_reports(tmp_path, ["missing"], output)
    assert output.read_text() == ""
