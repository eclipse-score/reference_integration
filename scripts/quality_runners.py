import argparse
import re
import select
import sys
from dataclasses import dataclass
from pprint import pprint
from subprocess import PIPE, Popen

from known_good.models.known_good import KnownGood, Path, load_known_good


@dataclass
class ProcessResult:
    stdout: str
    stderr: str
    exit_code: int


def run_unit_test(known: KnownGood) -> int:
    print("Running unit tests...")
    unit_tests_summary = {}

    CURERNTLY_DISABLED_MODULES = [
        "score_communication",
        "score_scrample",
        "score_logging",
        "score_lifecycle_health",
        "score_feo",
    ]

    for module in known.modules["target_sw"].values():
        if module.name in CURERNTLY_DISABLED_MODULES:
            print(
                f"Skipping module {module.name} as it is currently disabled for unit tests."
            )
            continue
        else:
            print(f"Testing module: {module.name}")
        call = [
            "bazel",
            "test",
            "--config=unit-tests",
            "--test_summary=testcase",
            "--test_output=errors",
            # "--nocache_test_results",
            f"@{module.name}{module.metadata.code_root_path}",
            "--",
        ] + [
            # Exclude test targets specified in module metadata, if any
            f"-@{module.name}{target}"
            for target in module.metadata.exclude_test_targets
        ]

        print(f"Running command: `{' '.join(call)}`")
        result = run_command(call)
        unit_tests_summary[module.name] = extract_summary(result.stdout)
        unit_tests_summary[module.name] |= {"exit_code": result.exit_code}

    generate_markdown_report(
        unit_tests_summary,
        output_path=Path(__file__).parent.parent
        / "docs/verification/unit_test_summary.md",
    )
    print("UNIT TEST EXECUTION SUMMARY".center(120, "="))
    pprint(unit_tests_summary, width=120)

    return sum(result["exit_code"] for result in unit_tests_summary.values())


def run_coverage(known: KnownGood) -> int:
    print("Running coverage analysis...")
    ...


def generate_markdown_report(
    data: dict[str, dict[str, int]], output_path: Path = Path("unit_test_summary.md")
) -> None:
    # Keys/columns for the table (ordered)
    columns = ["module", "passed", "failed", "skipped", "total"]

    # Build header and separator
    title = "# Unit Test Summary\n"
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"

    # Build rows
    rows = []
    for name, stats in data.items():
        rows.append(
            "| "
            + " | ".join(
                [
                    name,
                    str(stats.get("passed", "")),
                    str(stats.get("failed", "")),
                    str(stats.get("skipped", "")),
                    str(stats.get("total", "")),
                ]
            )
            + " |"
        )

    md = "\n".join([title, header, separator] + rows + [""])
    output_path.write_text(md)


def extract_summary(logs: str) -> dict[str, int]:
    summary = {"passed": 0, "failed": 0, "skipped": 0, "total": 0}

    pattern_summary_line = re.compile(r"Test cases: finished.*")
    if match := pattern_summary_line.search(logs):
        summary_line = match.group(0)
    else:
        print("Summary line not found in logs.")
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


def run_command(command: list[str]) -> ProcessResult:
    """
    Run a command and print output live while storing it.

    Args:
        command: Command and arguments to execute

    Returns:
        ProcessResult containing stdout, stderr, and exit code
    """

    stdout_data = []
    stderr_data = []

    with Popen(command, stdout=PIPE, stderr=PIPE, text=True, bufsize=1) as p:
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
        default=Path(__file__).parent / "known_good.json",
        help="Path to the known good JSON file",
    )
    parser.add_argument(
        "--unit-tests",
        action="store_true",
        default=True,
        help="Run unit tests for all modules specified in the known good file",
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run coverage analysis for all modules specified in the known good file",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    known = load_known_good(args.known_good_path.resolve())

    return_codes = []
    if args.unit_tests:
        return_codes.append(run_unit_test(known=known))
    if args.coverage:
        return_codes.append(run_coverage(known=known))

    return sum(return_codes)


if __name__ == "__main__":
    main()
