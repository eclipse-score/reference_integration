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


@dataclass
class ProcessResult:
    stdout: str
    stderr: str
    exit_code: int


def print_centered(message: str, width: int = 120, fillchar: str = "-") -> None:
    print(message.center(width, fillchar))


def run_unit_test_with_coverage(module: Module) -> dict[str, str | int]:
    print_centered("QR: Running unit tests")

    call = (
        [
            "bazel",
            "test",  # Call coverage instead of test to get .dat files already
            "--test_verbose_timeout_warnings",
            "--test_timeout=1200",
            "--config=unit-tests",
            "--config=ferrocene-coverage",
            "--test_summary=testcase",
            "--test_output=errors",
            "--nocache_test_results",
            f"--instrumentation_filter=@{module.name}",
            f"@{module.name}{module.metadata.code_root_path}",
        ]
        + [f"--@{module.name}{target}" for target in module.metadata.extra_test_config]
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
    bazel_coverage_output_directory = run_command(
        ["bazel", "info", "output_path"]
    ).stdout.strip()
    bazel_source_directory = run_command(
        ["bazel", "info", "output_base"]
    ).stdout.strip()

    genhtml_call = [
        "genhtml",
        f"{bazel_coverage_output_directory}/_coverage/_coverage_report.dat",
        f"--output-directory={output_dir}",
        "--show-details",
        "--legend",
        "--function-coverage",
        "--branch-coverage",
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
) -> None:
    # Build header and separator
    title = f"# {title}\n"
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"

    # Build rows
    rows = []
    for name, stats in data.items():
        rows.append(
            "| "
            + " | ".join([name] + [str(stats.get(col, "")) for col in columns[1:]])
            + " |"
        )

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

    return ProcessResult(
        stdout="".join(stdout_data), stderr="".join(stderr_data), exit_code=exit_code
    )


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
    return parser.parse_args()


def main() -> bool:
    args = parse_arguments()
    args.coverage_output_dir.mkdir(parents=True, exist_ok=True)
    path_to_docs = Path(__file__).parent.parent / "docs/verification"

    known = load_known_good(args.known_good_path.resolve())

    unit_tests_summary, coverage_summary = {}, {}

    if args.modules_to_test:
        print_centered(
            f"QR: User requested tests only for specified modules: {', '.join(args.modules_to_test)}"
        )

    for module in known.modules["target_sw"].values():
        if args.modules_to_test and module.name not in args.modules_to_test:
            print_centered(f"QR: Skipping module {module.name}")
            continue

        print_centered(f"QR: Testing module: {module.name}")
        unit_tests_summary[module.name] = run_unit_test_with_coverage(module=module)

        if "cpp" in module.metadata.langs:
            coverage_summary[f"{module.name}_cpp"] = run_cpp_coverage_extraction(
                module=module, output_path=args.coverage_output_dir
            )

        if "rust" in module.metadata.langs:
            DISABLED_RUST_COVERAGE = [
                "score_communication",
                "score_orchestrator",
            ]  # Known issues with coverage extraction for these modules, mostly proc_macro
            if module.name in DISABLED_RUST_COVERAGE:
                print_centered(
                    f"QR: Skipping rust coverage extraction for module {module.name} due to known issues"
                )
                continue
            coverage_summary[f"{module.name}_rust"] = run_rust_coverage_extraction(
                module=module, output_path=args.coverage_output_dir
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
        for result_ut, result_cov in zip(
            unit_tests_summary.values(), coverage_summary.values()
        )
    )


if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)
    sys.exit(main())
