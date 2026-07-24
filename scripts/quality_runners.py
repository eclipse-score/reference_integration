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
import re
import select
import sys
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint
from subprocess import PIPE, Popen

from known_good.models.known_good import load_known_good
from known_good.models.module import Module
from known_good.resolved_dependencies import ResolvedDependencies


@dataclass
class ProcessResult:
    stdout: str
    stderr: str
    exit_code: int


def print_centered(message: str, width: int = 120, fillchar: str = "-") -> None:
    print(message.center(width, fillchar))


def run_unit_test_with_coverage(module: Module, workspace: Path | None = None) -> dict[str, str | int]:
    """Run a module's unit tests + coverage.

    When ``workspace`` is None (central/legacy mode) the module is addressed through
    ref_int's Bazel graph as ``@<module>//...``.

    When ``workspace`` is a checked-out module directory (DR-008 Option 4 mode), the
    module *is* the Bazel root, so targets are plain ``//...`` and the command runs with
    ``cwd=workspace``. ``--lockfile_mode=update`` is used so Bazel *regenerates* the
    module's ``MODULE.bazel.lock`` to reflect the resolved-deps overrides we inject (the
    module's committed lock is deleted first in module-context mode); the regenerated lock
    is the verifiable record of exactly what the module was validated against and is
    uploaded as a Stage-2 artifact. Instrumentation falls back to Bazel's default (root
    code instrumented, external deps excluded).
    """
    print_centered("QR: Running unit tests")

    in_module = workspace is not None
    repo = "" if in_module else f"@{module.name}"

    # --config=unit-tests   is defined as "test:unit-tests" in ref_int's .bazelrc,
    # so Bazel ignores it for the "coverage" command and the module's .bazelrc has no
    # such entry at all. --config=ferrocene-coverage references @score_tooling which
    # is not in the module's own dep graph. Both are ref_int-specific; expand them to
    # their individual flags when running inside a module checkout.
    if in_module:
        config_flags = [f"--config={c}" for c in module.metadata.bazel_config] + [
            "--build_tests_only",
            "--test_tag_filters=-manual",
        ]
    else:
        config_flags = [
            "--config=unit-tests",
            "--config=ferrocene-coverage",
        ]

    call = (
        [
            "bazel",
            "coverage",  # Call coverage instead of test to get .dat files already
            "--test_verbose_timeout_warnings",
            "--test_timeout=1200",
        ]
        + config_flags
        + [
            "--test_summary=testcase",
            "--test_output=errors",
            "--nocache_test_results",
        ]
        + (["--lockfile_mode=update"] if in_module else [f"--instrumentation_filter=@{module.name}"])
        + [f"{repo}{module.metadata.code_root_path}"]
        + [f"--{target}" for target in module.metadata.extra_test_config]
        + ["--"]
        + [
            # Exclude test targets specified in module metadata, if any
            f"-{repo}{target}"
            for target in module.metadata.exclude_test_targets
        ]
    )

    result = run_command(call, cwd=str(workspace)) if in_module else run_command(call)
    summary = extract_ut_summary(result.stdout)
    return {**summary, "exit_code": result.exit_code}


def run_cpp_coverage_extraction(module: Module, output_path: Path, workspace: Path | None = None) -> int:
    print_centered("QR: Running cpp coverage analysis")

    result_cpp = cpp_coverage(module, output_path, workspace=workspace)
    summary = extract_coverage_summary(result_cpp.stdout)

    return {**summary, "exit_code": result_cpp.exit_code}


def run_rust_coverage_extraction(module: Module, output_path: Path, workspace: Path | None = None) -> int:
    print_centered("QR: Running rust coverage analysis")

    result_rust = rust_coverage(module, output_path, workspace=workspace)
    summary = extract_coverage_summary(result_rust.stdout)

    return {**summary, "exit_code": result_rust.exit_code}


def cpp_coverage(module: Module, artifact_dir: Path, workspace: Path | None = None) -> ProcessResult:
    # .dat files are already generated in UT step

    # Run genhtml to generate the HTML report and get the summary
    # Create dedicated output directory for this module's coverage reports
    output_dir = artifact_dir / "cpp" / module.name
    output_dir.mkdir(parents=True, exist_ok=True)
    # Find input locations. In module-context mode (DR-008 Option 4) Bazel runs inside the
    # checked-out module, so query its output paths with cwd=workspace.
    info_cwd = {"cwd": str(workspace)} if workspace is not None else {}
    bazel_coverage_output_directory = run_command(["bazel", "info", "output_path"], **info_cwd).stdout.strip()
    bazel_source_directory = run_command(["bazel", "info", "output_base"], **info_cwd).stdout.strip()

    dat_file = f"{bazel_coverage_output_directory}/_coverage/_coverage_report.dat"
    if not Path(dat_file).exists():
        print_centered(f"QR: No coverage dat file at {dat_file} — skipping genhtml for {module.name}")
        return ProcessResult(stdout="", stderr="", exit_code=0)

    genhtml_call = [
        "genhtml",
        f"{bazel_coverage_output_directory}/_coverage/_coverage_report.dat",
        f"--output-directory={output_dir}",
        "--show-details",
        "--legend",
        "--function-coverage",
        "--branch-coverage",
        "--ignore-errors=negative,negative,source,source,inconsistent,category,unmapped",
        "--synthesize-missing",
    ]
    genhtml_result = run_command(genhtml_call, cwd=bazel_source_directory)

    return genhtml_result


def rust_coverage(module: Module, artifact_dir: Path, workspace: Path | None = None) -> ProcessResult:
    # .profraw files are already generated in UT step

    # Run bazel covverage target
    # Create dedicated output directory for this module's coverage reports
    output_dir = artifact_dir / "rust" / module.name
    output_dir.mkdir(parents=True, exist_ok=True)

    if workspace is not None:
        # The rust_coverage_<module> target is generated in ref_int's rust_coverage/BUILD
        # and does not exist inside a module checkout. Module-context (DR-008 Option 4)
        # Rust coverage is tracked as a follow-up; skip without failing the job.
        print_centered(f"QR: Skipping ref_int rust_coverage target for {module.name} in module-context mode")
        return ProcessResult(stdout="", stderr="", exit_code=0)

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
) -> None:
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
        "--module-dir",
        type=Path,
        default=None,
        help=(
            "DR-008 Option 4 module-context mode: path to a checked-out module. The "
            "module's MODULE.bazel is overwritten with the resolved dependency set "
            "(see --resolved-deps / --known-good-path) and its tests run as the Bazel "
            "root (//...) instead of through ref_int (@<module>//...). Only valid with "
            "a single --modules-to-test entry."
        ),
    )
    parser.add_argument(
        "--resolved-deps",
        type=Path,
        default=None,
        help=(
            "Module-context mode: directory of the Stage-1 'stage1-resolved-deps' artifact "
            "(resolved_versions.json manifest) used as the resolved set to inject. "
            "Defaults to --known-good-path when omitted."
        ),
    )
    return parser.parse_args()


def main() -> bool:
    args = parse_arguments()
    args.coverage_output_dir.mkdir(parents=True, exist_ok=True)
    path_to_docs = Path(__file__).parent.parent / "docs/verification_report"

    known = load_known_good(args.known_good_path.resolve())

    unit_tests_summary, coverage_summary = {}, {}

    if args.modules_to_test:
        print_centered(f"QR: User requested tests only for specified modules: {', '.join(args.modules_to_test)}")

    workspace = args.module_dir
    if workspace is not None:
        if len(args.modules_to_test) != 1:
            raise SystemExit("--module-dir requires exactly one --modules-to-test entry")
        # DR-008 Option 4: overwrite the checked-out module's declared dependency versions
        # with the dependency set ref_int resolved (Stage-1 artifact, falling back to
        # known_good.json), so the module's tests run against the resolved versions.
        if args.resolved_deps is not None:
            resolved = ResolvedDependencies.from_resolved_artifact(args.resolved_deps.resolve())
        else:
            resolved = ResolvedDependencies.from_known_good(args.known_good_path.resolve())
        module_bazel = workspace.resolve() / "MODULE.bazel"
        print_centered(f"QR: Injecting resolved deps into {module_bazel}")
        resolved.overwrite(module_bazel, module_under_test=args.modules_to_test[0])

        # The module's committed MODULE.bazel.lock is stale the moment we inject overrides.
        # Delete it so the run (with --lockfile_mode=update) regenerates a lock reflecting
        # exactly the resolved set the module was validated against (DR-008 verifiable record).
        module_lock = workspace.resolve() / "MODULE.bazel.lock"
        if module_lock.exists():
            print_centered(f"QR: Removing stale module lock {module_lock} (regenerated by --lockfile_mode=update)")
            module_lock.unlink()

        # Overwrite .bazelversion in the module checkout with ref_int's pinned version
        # so all Stage-2 runs use the same Bazel binary as the integrated build.
        ref_int_root = args.known_good_path.resolve().parent
        bazelversion_src = ref_int_root / ".bazelversion"
        bazelversion_dst = workspace.resolve() / ".bazelversion"
        bazel_ver = bazelversion_src.read_text().strip()
        print_centered(f"QR: Pinning .bazelversion to ref_int's {bazel_ver} in {bazelversion_dst}")
        bazelversion_dst.write_text(bazel_ver + "\n")

    for module in known.modules["target_sw"].values():
        if args.modules_to_test and module.name not in args.modules_to_test:
            print_centered(f"QR: Skipping module {module.name}")
            continue

        print_centered(f"QR: Testing module: {module.name}")
        unit_tests_summary[module.name] = run_unit_test_with_coverage(module=module, workspace=workspace)

        if "cpp" in module.metadata.langs:
            coverage_summary[f"{module.name}_cpp"] = run_cpp_coverage_extraction(
                module=module, output_path=args.coverage_output_dir, workspace=workspace
            )

        if "rust" in module.metadata.langs:
            DISABLED_RUST_COVERAGE = [
                "score_communication",
                "score_orchestrator",
            ]  # Known issues with coverage extraction for these modules, mostly proc_macro
            if module.name in DISABLED_RUST_COVERAGE:
                print_centered(f"QR: Skipping rust coverage extraction for module {module.name} due to known issues")
                continue
            coverage_summary[f"{module.name}_rust"] = run_rust_coverage_extraction(
                module=module, output_path=args.coverage_output_dir, workspace=workspace
            )

        print_centered(f"QR: Finished testing module: {module.name}")

    generate_markdown_report(
        unit_tests_summary,
        title="Unit Test Execution Summary",
        columns=["module", "passed", "failed", "skipped", "total"],
        output_path=path_to_docs / "unit_test_summary.md",
    )
    print_centered("QR: UNIT TEST EXECUTION SUMMARY", fillchar="=")
    pprint(unit_tests_summary, width=120)

    generate_markdown_report(
        coverage_summary,
        title="Coverage Analysis Summary",
        columns=["module", "lines", "functions", "branches"],
        output_path=path_to_docs / "coverage_summary.md",
    )
    print_centered("QR: COVERAGE ANALYSIS SUMMARY", fillchar="=")
    pprint(coverage_summary, width=120)

    # Check all exit codes and return non-zero if any test or coverage extraction failed
    return any(
        result_ut["exit_code"] != 0 or result_cov["exit_code"] != 0
        for result_ut, result_cov in zip(unit_tests_summary.values(), coverage_summary.values())
    )


if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)
    sys.exit(main())
