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
from subprocess import PIPE, Popen, run
from typing import Any

try:
    from known_good.models.known_good import load_known_good
    from known_good.models.module import Module
except ModuleNotFoundError:
    from scripts.known_good.models.known_good import load_known_good
    from scripts.known_good.models.module import Module


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


def run_cpp_coverage_extraction(module: Module, output_path: Path) -> dict[str, str | int]:
    print_centered("QR: Running cpp coverage analysis")

    result_cpp = cpp_coverage(module, output_path)
    summary = extract_coverage_summary(result_cpp.stdout)
    dashboard_link = f'<a href="../coverage/cpp/{module.name}/index.html">C++ Dashboard</a>'

    return {**summary, "dashboard": dashboard_link, "exit_code": result_cpp.exit_code}


def run_rust_coverage_extraction(module: Module, output_path: Path) -> dict[str, str | int]:
    print_centered("QR: Running rust coverage analysis")

    result_rust = rust_coverage(module, output_path)
    summary = extract_coverage_summary(result_rust.stdout)
    dashboard_link = f'<a href="../coverage/rust/{module.name}/index.html">Rust Dashboard</a>'

    return {**summary, "dashboard": dashboard_link, "exit_code": result_rust.exit_code}


def cpp_coverage(module: Module, artifact_dir: Path) -> ProcessResult:
    # .dat files are already generated in UT step

    # Run genhtml to generate the HTML report and get the summary
    # Create dedicated output directory for this module's coverage reports
    output_dir = (artifact_dir / "cpp" / module.name).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    # Find input locations
    bazel_coverage_output_directory = run_command(["bazel", "info", "output_path"]).stdout.strip()
    bazel_source_directory = run_command(["bazel", "info", "output_base"]).stdout.strip()

    # Check lcov version (lcov 1.x vs 2.x+)
    version_res = run_command(["genhtml", "-v"])
    match = re.search(r"version\s+(\d+)\.", version_res.stdout)
    is_lcov_2_plus = match is not None and int(match.group(1)) >= 2

    if is_lcov_2_plus:
        ignore_errors = "--ignore-errors=negative,negative,source,source"
    else:
        ignore_errors = "--ignore-errors=source,source"

    genhtml_call = [
        "genhtml",
        f"{bazel_coverage_output_directory}/_coverage/_coverage_report.dat",
        f"--output-directory={output_dir}",
        "--show-details",
        "--legend",
        "--function-coverage",
        "--branch-coverage",
        ignore_errors,
    ]
    if is_lcov_2_plus:
        genhtml_call.append("--synthesize-missing")

    return run_command(genhtml_call, cwd=bazel_source_directory)


def generate_rust_module_index(module_name: str, output_dir: Path) -> None:
    """Generate an index.html in the module's rust coverage directory linking to target reports."""
    targets = []
    if output_dir.is_dir():
        for target_dir in sorted(output_dir.iterdir()):
            if target_dir.is_dir() and (target_dir / "blanket" / "index.html").is_file():
                targets.append(target_dir)

    if not targets:
        return

    # If there is only one target, redirect directly to its blanket report
    if len(targets) == 1:
        rel_path = f"{targets[0].name}/blanket/index.html"
        content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url={rel_path}">
    <title>Rust Coverage - {module_name}</title>
</head>
<body>
    <p>Redirecting to <a href="{rel_path}">coverage report</a>...</p>
</body>
</html>
"""
    else:
        links = "\n".join(
            f'        <li><a href="{t.name}/blanket/index.html">{t.name}</a></li>'
            for t in targets
        )
        content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Rust Coverage - {module_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 2rem;
        }}
        h1 {{ font-size: 1.5rem; }}
        ul {{ list-style-type: none; padding-left: 0; }}
        li {{ margin: 0.5rem 0; }}
        a {{ color: #0066cc; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>Rust Coverage Reports: {module_name}</h1>
    <p>Select a test target to view detailed coverage:</p>
    <ul>
{links}
    </ul>
    <p><a href="../../index.html">&larr; Back to Coverage Portal</a></p>
</body>
</html>
"""
    (output_dir / "index.html").write_text(content, encoding="utf-8")


def generate_coverage_portal(
    coverage_dir: Path,
    coverage_summary: dict[str, dict[str, Any]],
) -> None:
    """Generate a top-level index.html in the coverage output directory listing all dashboards."""
    cpp_modules = []
    rust_modules = []

    for key, data in coverage_summary.items():
        if key.endswith("_cpp"):
            mod_name = key[:-4]
            cpp_modules.append((mod_name, data))
        elif key.endswith("_rust"):
            mod_name = key[:-5]
            rust_modules.append((mod_name, data))

    def make_rows(modules: list[tuple[str, dict[str, Any]]], lang: str) -> str:
        rows = []
        for mod_name, data in sorted(modules, key=lambda x: x[0]):
            lines = data.get("lines", "-") or "-"
            functions = data.get("functions", "-") or "-"
            branches = data.get("branches", "-") or "-"
            rows.append(
                f"""        <tr>
            <td><strong>{mod_name}</strong></td>
            <td>{lines}</td>
            <td>{functions}</td>
            <td>{branches}</td>
            <td><a class="btn" href="{lang}/{mod_name}/index.html">View Dashboard &rarr;</a></td>
        </tr>"""
            )
        return "\n".join(rows) if rows else "<tr><td colspan='5'>No reports generated.</td></tr>"

    cpp_rows = make_rows(cpp_modules, "cpp")
    rust_rows = make_rows(rust_modules, "rust")

    portal_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Code Coverage Dashboards - S-CORE Reference Integration</title>
    <style>
        :root {{
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --muted: #64748b;
            --primary: #2563eb;
            --border: #e2e8f0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 2rem;
            background: var(--bg);
            color: var(--text);
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
        }}
        header {{
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 1rem;
        }}
        h1 {{
            margin: 0 0 0.5rem 0;
            font-size: 1.75rem;
            color: #0f172a;
        }}
        p.subtitle {{
            margin: 0;
            color: var(--muted);
            font-size: 0.95rem;
        }}
        .nav-back {{
            margin-top: 0.75rem;
            display: inline-block;
            color: var(--primary);
            text-decoration: none;
            font-size: 0.9rem;
        }}
        .nav-back:hover {{
            text-decoration: underline;
        }}
        .card {{
            background: var(--card-bg);
            border-radius: 8px;
            border: 1px solid var(--border);
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 2rem;
            overflow: hidden;
        }}
        .card-header {{
            padding: 1rem 1.5rem;
            background: #f1f5f9;
            border-bottom: 1px solid var(--border);
            font-weight: 600;
            font-size: 1.1rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}
        th, td {{
            padding: 0.75rem 1.5rem;
            border-bottom: 1px solid var(--border);
            font-size: 0.9rem;
        }}
        th {{
            background: #fafafa;
            color: var(--muted);
            font-weight: 600;
        }}
        tr:last-child td {{
            border-bottom: none;
        }}
        .btn {{
            display: inline-block;
            background: var(--primary);
            color: #fff;
            padding: 0.35rem 0.75rem;
            border-radius: 4px;
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 500;
        }}
        .btn:hover {{
            background: #1d4ed8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Code Coverage Dashboards</h1>
            <p class="subtitle">S-CORE Reference Integration CI Test Execution & Verification Reports</p>
            <a class="nav-back" href="../index.html">&larr; Return to Documentation Site</a>
        </header>

        <div class="card">
            <div class="card-header">C++ Modules (genhtml / lcov)</div>
            <table>
                <thead>
                    <tr>
                        <th>Module</th>
                        <th>Line Coverage</th>
                        <th>Function Coverage</th>
                        <th>Branch Coverage</th>
                        <th>Dashboard</th>
                    </tr>
                </thead>
                <tbody>
{cpp_rows}
                </tbody>
            </table>
        </div>

        <div class="card">
            <div class="card-header">Rust Modules (Ferrocene / Blanket)</div>
            <table>
                <thead>
                    <tr>
                        <th>Module</th>
                        <th>Line Coverage</th>
                        <th>Function Coverage</th>
                        <th>Branch Coverage</th>
                        <th>Dashboard</th>
                    </tr>
                </thead>
                <tbody>
{rust_rows}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""
    coverage_dir.mkdir(parents=True, exist_ok=True)
    (coverage_dir / "index.html").write_text(portal_html, encoding="utf-8")


def rust_coverage(module: Module, artifact_dir: Path) -> ProcessResult:
    # .profraw files are already generated in UT step

    # Run bazel coverage target
    # Create dedicated output directory for this module's coverage reports
    output_dir = (artifact_dir / "rust" / module.name).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    bazel_call = [
        "bazel",
        "run",
        f"//rust_coverage:rust_coverage_{module.name}",
        "--",
        "--out-dir",
        str(output_dir),
    ]
    bazel_result = run_command(bazel_call)
    generate_rust_module_index(module.name, output_dir)

    return bazel_result


def generate_markdown_report(
    data: dict[str, dict[str, int | str]],
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
        "--trust-cache",
        action="store_true",
        help="Allow Bazel to reuse cached test/coverage results for unchanged modules instead of always "
        "re-executing them (--nocache_test_results). Intended for fast PR-iteration checks; authoritative "
        "runs (e.g. on push to main) should NOT set this, so coverage numbers are always freshly measured.",
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
        columns=["module", "lines", "functions", "branches", "dashboard"],
        output_path=path_to_docs / "coverage_summary.md",
    )
    generate_coverage_portal(args.coverage_output_dir, coverage_summary)
    print_centered("QR: COVERAGE ANALYSIS SUMMARY", fillchar="=")
    pprint(coverage_summary, width=120)

    # Check all exit codes and return non-zero if any test or coverage extraction failed
    return any(r["exit_code"] != 0 for r in {**unit_tests_summary, **coverage_summary}.values())


if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)
    sys.exit(main())
