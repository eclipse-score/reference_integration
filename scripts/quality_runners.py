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
import argparse
import os
import re
import select
import sys
from dataclasses import dataclass
from pathlib import Path
from subprocess import PIPE, Popen, run

from known_good.models.known_good import load_known_good
from known_good.models.module import Module


@dataclass
class ProcessResult:
    stdout: str
    stderr: str
    exit_code: int


def print_centered(message: str, width: int = 120, fillchar: str = "-") -> None:
    print(message.center(width, fillchar))


def configure_aslr_for_sanitizers() -> None:
    """Lower ASLR entropy so ThreadSanitizer/ASan tests can run.

    Modern kernels (e.g. Ubuntu 24.04 CI runners) default ``vm.mmap_rnd_bits``
    to 32. That is incompatible with the sanitizer shadow-memory layout and
    makes ThreadSanitizer abort before any test runs with
    ``FATAL: ThreadSanitizer: unexpected memory mapping``. Lowering the value
    to 28 is the documented workaround (see google/sanitizers#1614).

    Best-effort: silently ignored when sudo/sysctl is unavailable or the value
    is already low enough, so local runs without privileges are unaffected.
    """
    print_centered("QR: Configuring ASLR entropy for sanitizer tests")
    result = run(
        ["sudo", "sysctl", "-w", "vm.mmap_rnd_bits=28"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        print(result.stdout.strip())
    else:
        print(f"QR: Could not lower vm.mmap_rnd_bits (continuing anyway): {result.stderr.strip()}")


def run_unit_test_with_coverage(module: Module, trust_cache: bool = False) -> dict[str, str | int]:
    print_centered("QR: Running unit tests")

    call = (
        [
            "bazel",
            "coverage",  # Call coverage instead of test to get .dat files already
            "--test_verbose_timeout_warnings",
            "--test_timeout=1200",
            "--config=unit-tests",
            "--config=ferrocene-coverage",
            "--test_summary=testcase",
            "--test_output=errors",
        ]
        + ([] if trust_cache else ["--nocache_test_results"])
        + [
            f"--instrumentation_filter=@{module.name}",
            f"@{module.name}{module.metadata.code_root_path}",
        ]
        + [f"--{target}" for target in module.metadata.extra_test_config]
        + ["--"]
        + [
            # Exclude test targets specified in module metadata, if any
            f"-@{module.name}{target}"
            for target in module.metadata.exclude_test_targets
        ]
    )

    result = run_command(call)
    summary = extract_ut_summary(result.stdout)
    return {**summary, "exit_code": result.exit_code}


def run_cpp_coverage_extraction(module: Module, output_path: Path) -> int:
    print_centered("QR: Running cpp coverage analysis")

    result_cpp = cpp_coverage(module, output_path)
    summary = extract_coverage_summary(result_cpp.stdout)

    return {**summary, "exit_code": result_cpp.exit_code}


def run_rust_coverage_extraction(module: Module, output_path: Path) -> int:
    print_centered("QR: Running rust coverage analysis")

    result_rust = rust_coverage(module, output_path)
    summary = extract_coverage_summary(result_rust.stdout)

    return {**summary, "exit_code": result_rust.exit_code}


def cpp_coverage(module: Module, artifact_dir: Path) -> ProcessResult:
    # .dat files are already generated in UT step

    # Run genhtml to generate the HTML report and get the summary
    # Create dedicated output directory for this module's coverage reports
    output_dir = artifact_dir / "cpp" / module.name
    output_dir.mkdir(parents=True, exist_ok=True)
    # Find input locations
    bazel_coverage_output_directory = run_command(["bazel", "info", "output_path"]).stdout.strip()
    bazel_source_directory = run_command(["bazel", "info", "output_base"]).stdout.strip()

    genhtml_call = [
        "genhtml",
        f"{bazel_coverage_output_directory}/_coverage/_coverage_report.dat",
        f"--output-directory={output_dir}",
        "--show-details",
        "--legend",
        "--function-coverage",
        "--branch-coverage",
        "--ignore-errors=negative,negative,source,source",
        "--synthesize-missing",
    ]
    genhtml_result = run_command(genhtml_call, cwd=bazel_source_directory)

    return genhtml_result


def rust_coverage(module: Module, artifact_dir: Path) -> ProcessResult:
    # .profraw files are already generated in UT step

    # Run bazel covverage target
    # Create dedicated output directory for this module's coverage reports
    output_dir = artifact_dir / "rust" / module.name
    output_dir.mkdir(parents=True, exist_ok=True)

    bazel_call = [
        "bazel",
        "run",
        f"//rust_coverage:rust_coverage_{module.name}",
    ]
    bazel_result = run_command(bazel_call)

    return bazel_result


def generate_markdown_report(
    data: dict[str, dict[str, int]],
    title: str,
    columns: list[str],
    output_path: Path = Path("unit_test_summary.md"),
) -> str:
    # Build header and separator
    title = f"# {title}\n"
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"

    # Build rows
    rows = []
    for name, stats in data.items():
        rows.append("| " + " | ".join([name] + [str(stats.get(col, "")) for col in columns[1:]]) + " |")

    md = "\n".join([title, header, separator] + rows + [""])
    output_path.write_text(md)
    return md


def append_to_step_summary(*blocks: str) -> None:
    """Mirror the reports into the job summary GitHub shows above the log.

    Writing straight from the data keeps what gets published tied to this run.
    The markdown files are still needed by the documentation build, but nothing
    reads them back, so a stale or hand-edited copy cannot be mistaken for a
    result. Outside of Actions the variable is unset and this does nothing.
    """
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if not step_summary:
        return
    with open(step_summary, "a", encoding="utf-8") as handle:
        handle.write("\n".join(blocks))


STATUS_LABELS = {"pass": "✅ pass", "FAILED": "❌ FAILED", "skipped": "⚪ skipped"}


def with_status(data: dict[str, dict[str, int]]) -> dict[str, dict[str, int]]:
    """Derive a readable status column from the exit code each runner reports.

    Without it a module whose Bazel invocation aborted during analysis is
    indistinguishable from one that simply has no tests: both show up as all
    zeroes, and ``failed`` even claims zero failures. An explicit status set by
    the caller (``skipped``) wins over the derived one.

    The emoji carries the colour: Markdown offers no way to colour a table cell
    that survives both GitHub and the Sphinx build of these same files. The word
    stays next to it so the table is still readable where emoji are not.
    """
    return {
        name: {
            **stats,
            "status": STATUS_LABELS[stats.get("status") or ("pass" if stats.get("exit_code", 0) == 0 else "FAILED")],
        }
        for name, stats in data.items()
    }


def report_failures(unit_tests: dict[str, dict[str, int]], coverage: dict[str, dict[str, int]]) -> list[str]:
    """Name every module that failed, via annotations and a final summary block.

    ``::error`` annotations are rendered by GitHub above the step list of the
    run, so the failing module is visible without opening the log at all.
    """
    failed = sorted(name for name, stats in unit_tests.items() if stats.get("exit_code", 0) != 0)

    for name in failed:
        print(
            f"::error title=Unit tests failed::{name}: bazel exited with "
            f"{unit_tests[name]['exit_code']} and produced no test results"
        )
    for name, stats in coverage.items():
        # A coverage run that was skipped is already covered by the unit test
        # annotation for the same module; annotating it again is just noise.
        if stats.get("exit_code", 0) != 0 and stats.get("status") != "skipped":
            print(f"::error title=Coverage failed::{name}: coverage extraction did not succeed")

    print_centered("QR: UNIT TEST EXECUTION SUMMARY", fillchar="=")
    for name, stats in sorted(unit_tests.items()):
        if stats.get("exit_code", 0) == 0:
            print(f"  pass    {name:<26} {stats['passed']:>6} passed, {stats['skipped']:>3} skipped")
    for name in failed:
        print(f"  FAILED  {name:<26} bazel exit code {unit_tests[name]['exit_code']}, no results")

    if failed:
        print_centered(
            f"QR: {len(failed)} of {len(unit_tests)} MODULES FAILED: {', '.join(failed)}",
            fillchar="=",
        )
    return failed


def extract_ut_summary(logs: str) -> dict[str, int]:
    summary = {"passed": 0, "failed": 0, "skipped": 0, "total": 0}

    pattern_summary_line = re.compile(r"Test cases: finished.*")
    if match := pattern_summary_line.search(logs):
        summary_line = match.group(0)
    else:
        print_centered("QR: Summary line not found in logs")
        return summary

    pattern_passed = re.compile(r"(\d+) passing")
    pattern_skipped = re.compile(r"(\d+) skipped")
    pattern_failed = re.compile(r"(\d+) failing")
    pattern_total = re.compile(r"out of (\d+) test cases")

    if match := pattern_passed.search(summary_line):
        summary["passed"] = int(match.group(1))
    if match := pattern_skipped.search(summary_line):
        summary["skipped"] = int(match.group(1))
    if match := pattern_failed.search(summary_line):
        summary["failed"] = int(match.group(1))
    if match := pattern_total.search(summary_line):
        summary["total"] = int(match.group(1))
    return summary


def extract_coverage_summary(logs: str) -> dict[str, str]:
    """
    Extract coverage summary from coverage output (genhtml / rust_coverage_report).

    Args:
        logs: Output from coverage command

    Returns:
        Dictionary with coverage percentages for lines, functions, and branches
    """
    summary = {"lines": "", "functions": "", "branches": ""}

    # Pattern to match coverage percentages in genhtml output
    # Example: "  lines......: 93.0% (1234 of 1327 lines)"
    pattern_cpp_lines = re.compile(r"lines\.+:\s+([\d.]+%)")
    pattern_cpp_functions = re.compile(r"functions\.+:\s+([\d.]+%)")
    pattern_cpp_branches = re.compile(r"branches\.+:\s+([\d.]+%)")
    if match := pattern_cpp_lines.search(logs):
        summary["lines"] = match.group(1)
    if match := pattern_cpp_functions.search(logs):
        summary["functions"] = match.group(1)
    if match := pattern_cpp_branches.search(logs):
        summary["branches"] = match.group(1)

    # Rust coverage currently returns only line coverage
    pattern_rust_lines = re.compile(r"line coverage:\s+([\d.]+%)")
    if match := pattern_rust_lines.search(logs):
        summary["lines"] = match.group(1)

    return summary


def run_command(command: list[str], **kwargs) -> ProcessResult:
    """
    Run a command and print output live while storing it.

    Args:
        command: Command and arguments to execute

    Returns:
        ProcessResult containing stdout, stderr, and exit code
    """

    stdout_data = []
    stderr_data = []

    print_centered("QR: Running command:")
    print(f"{' '.join(command)}")

    with Popen(command, stdout=PIPE, stderr=PIPE, text=True, bufsize=1, **kwargs) as p:
        # Use select to read from both streams without blocking
        streams = {
            p.stdout: (stdout_data, sys.stdout),
            p.stderr: (stderr_data, sys.stderr),
        }

        try:
            while p.poll() is None or streams:
                # Check which streams have data available
                readable, _, _ = select.select(list(streams.keys()), [], [], 0.1)

                for stream in readable:
                    line = stream.readline()
                    if line:
                        storage, output_stream = streams[stream]
                        print(line, end="", file=output_stream, flush=True)
                        storage.append(line)
                    else:
                        # Stream closed
                        del streams[stream]

            exit_code = p.returncode

        except Exception:
            p.kill()
            p.wait()
            raise

    return ProcessResult(stdout="".join(stdout_data), stderr="".join(stderr_data), exit_code=exit_code)


def parse_arguments() -> argparse.Namespace:
    import argparse

    parser = argparse.ArgumentParser(description="Run quality checks on modules.")
    parser.add_argument(
        "--known-good-path",
        type=Path,
        default="known_good.json",
        help="Path to the known good JSON file",
    )
    parser.add_argument(
        "--coverage-output-dir",
        type=Path,
        default=Path(__file__).parent.parent / "artifacts/coverage",
        help="Path to the directory for coverage output files",
    )
    parser.add_argument(
        "--modules-to-test",
        type=lambda modules: modules.split(","),
        default=[],
        help="List of modules to test",
    )
    parser.add_argument(
        "--trust-cache",
        action="store_true",
        help="Allow Bazel to reuse cached test/coverage results for unchanged modules instead of always "
        "re-executing them (--nocache_test_results). Note that --nocache_test_results suppresses not only "
        "reading but also writing test results into the disk-cache, so omitting --trust-cache on a run that "
        "populates a shared cache makes that cache useless for subsequent runs. Omit it only for "
        "authoritative runs whose artifacts are published (e.g. release).",
    )
    return parser.parse_args()


def main() -> bool:
    args = parse_arguments()
    configure_aslr_for_sanitizers()
    args.coverage_output_dir.mkdir(parents=True, exist_ok=True)
    path_to_docs = Path(__file__).parent.parent / "docs/verification_report"
    path_to_docs.mkdir(parents=True, exist_ok=True)

    known = load_known_good(args.known_good_path.resolve())

    unit_tests_summary, coverage_summary = {}, {}

    if args.modules_to_test:
        print_centered(f"QR: User requested tests only for specified modules: {', '.join(args.modules_to_test)}")

    for module in known.modules["target_sw"].values():
        if args.modules_to_test and module.name not in args.modules_to_test:
            print_centered(f"QR: Skipping module {module.name}")
            continue

        print_centered(f"QR: Testing module: {module.name}")
        unit_tests_summary[module.name] = run_unit_test_with_coverage(module=module, trust_cache=args.trust_cache)

        # Coverage extraction reads the .dat file Bazel leaves in a fixed
        # location. When the test run failed, that file is still the one the
        # previous module produced, so genhtml would silently report another
        # module's numbers under this module's name.
        if unit_tests_summary[module.name]["exit_code"] != 0:
            print_centered(f"QR: Skipping coverage for {module.name}: unit test run failed")
            for lang in module.metadata.langs:
                coverage_summary[f"{module.name}_{lang}"] = {"exit_code": 1, "status": "skipped"}
            continue

        if "cpp" in module.metadata.langs:
            coverage_summary[f"{module.name}_cpp"] = run_cpp_coverage_extraction(
                module=module, output_path=args.coverage_output_dir
            )

        if "rust" in module.metadata.langs:
            DISABLED_RUST_COVERAGE = [
                "score_communication",
            ]  # Known issues with coverage extraction for these modules, mostly proc_macro
            if module.name in DISABLED_RUST_COVERAGE:
                print_centered(f"QR: Skipping rust coverage extraction for module {module.name} due to known issues")
                continue
            coverage_summary[f"{module.name}_rust"] = run_rust_coverage_extraction(
                module=module, output_path=args.coverage_output_dir
            )

        print_centered(f"QR: Finished testing module: {module.name}")

    unit_tests_md = generate_markdown_report(
        with_status(unit_tests_summary),
        title="Unit Test Execution Summary",
        columns=["module", "status", "passed", "failed", "skipped", "total"],
        output_path=path_to_docs / "unit_test_summary.md",
    )
    coverage_md = generate_markdown_report(
        with_status(coverage_summary),
        title="Coverage Analysis Summary",
        columns=["module", "status", "lines", "functions", "branches"],
        output_path=path_to_docs / "coverage_summary.md",
    )
    append_to_step_summary(unit_tests_md, coverage_md)

    report_failures(unit_tests_summary, coverage_summary)

    # Check all exit codes and return non-zero if any test or coverage extraction failed
    return any(r["exit_code"] != 0 for r in {**unit_tests_summary, **coverage_summary}.values())


if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)
    sys.exit(main())
