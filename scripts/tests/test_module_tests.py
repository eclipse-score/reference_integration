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

from module_tests import (
    STATUS_LINE,
    count_testcases,
    coverage_args,
    graph_modules,
    lcov_percentages,
    override_rc,
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
        "--combined_report=lcov",
        "--",
        "//score/...",
        "-//score/test/...",
    ]


def test_coverage_args_register_ferrocene_only_for_rust():
    args = coverage_args(["//src/..."], ["rust"])
    assert args[-2:] == ["--combined_report=lcov", "--config=unified-rust"]
    assert "--config=unified-rust" not in coverage_args(["//score/..."], ["cpp"])


def test_coverage_args_exclude_targets_after_separator():
    args = coverage_args(["--config=x86_64-linux", "//..."], ["rust"], ["//score/rust:miri_tests"])
    assert args[-3:] == ["--config=unified-rust", "--", "-//score/rust:miri_tests"]
    # An existing separator is reused, the excludes go after the module's own targets.
    args = coverage_args(["--", "//score/...", "-//score/test/..."], ["cpp"], ["//score/a:b"])
    assert args[-5:] == ["--combined_report=lcov", "--", "//score/...", "-//score/test/...", "-//score/a:b"]


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
