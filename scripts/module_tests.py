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
"""Run a known_good module's own unit tests against the dependency set ref_int resolves.

  run <module>      test <module> at its known_good commit with those versions forced
  report <dir>      write the verification report's unit test and coverage summaries

Each of the module's direct dependencies that ref_int also resolves is pinned with
``--override_module``, pointing at ref_int's own fetched copy (so ref_int's patches come along);
Bazel resolves the deeper ones from there. ``bazel_common/unified.bazelrc`` is layered over the
module's .bazelrc. The only edit to the module is one ``include()`` of ref_int's
``unified_toolchains.MODULE.bazel``, as toolchains can only be defined in MODULE files.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from known_good.models.known_good import load_known_good
from quality_runners import append_to_step_summary, generate_markdown_report, with_status

REF_INT = Path(__file__).resolve().parents[1]
UNIFIED_RC = REF_INT / "bazel_common" / "unified.bazelrc"
UNIFIED_TOOLCHAINS = REF_INT / "bazel_common" / "unified_toolchains.MODULE.bazel"
# Bazel's per-target result lines, e.g. "//score/foo:bar_test   FAILED in 2.1s".
STATUS_LINE = re.compile(r"^(//\S+|@\S+)\s+(FAILED TO BUILD|FAILED|TIMEOUT|NO STATUS|INCOMPLETE|FLAKY)\b", re.M)


def bazel(args: list[str], cwd: Path = REF_INT, env: dict | None = None) -> subprocess.CompletedProcess:
    print("+ bazel " + " ".join(args), file=sys.stderr, flush=True)
    return subprocess.run(["bazel", *args], cwd=cwd, env=env, text=True, stdout=subprocess.PIPE)


def streamed(command: list[str], cwd: Path, env: dict) -> tuple[int, str]:
    """Run a command, echoing its output live (the test run takes too long to stay silent)."""
    print("+ " + " ".join(command), file=sys.stderr, flush=True)
    lines = []
    with subprocess.Popen(
        command, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    ) as proc:
        for line in proc.stdout:
            print(line, end="", flush=True)
            lines.append(line)
    return proc.returncode, "".join(lines)


def graph_modules(graph: dict) -> set[str]:
    """Every module name in a ``bazel mod graph --output=json`` dump."""
    names, stack = set(), [graph]
    while stack:
        node = stack.pop()
        for dep in node.get("dependencies", []) + node.get("indirectDependencies", []):
            names.add(dep["name"])
            stack.append(dep)
    return names - {"bazel_tools"}


def direct_deps(graph: dict) -> set[str]:
    """The root module's own bazel_deps in a ``bazel mod graph --output=json`` dump."""
    return {dep["name"] for dep in graph["dependencies"]} - {"bazel_tools"}


def mod_graph(cwd: Path, env: dict | None = None, lockfile_mode: str = "update") -> dict:
    result = bazel(["mod", "graph", "--output=json", f"--lockfile_mode={lockfile_mode}"], cwd, env)
    if result.returncode:
        sys.exit(f"bazel mod graph failed in {cwd}")
    return json.loads(result.stdout)


def fetch(names: set[str]) -> dict[str, Path]:
    """Fetch modules in ref_int and return where their sources landed.

    A repo that fails to fetch (e.g. a dead mirror of a module no build ever touches) is just
    missing from the result instead of failing the run.
    """
    bazel(["fetch", "--keep_going", "--lockfile_mode=error", *(f"--repo=@@{n}+" for n in sorted(names))])
    external = Path(bazel(["info", "output_base"]).stdout.strip()) / "external"
    found = {}
    for name in names:
        # ponytail: "<name>+" is bzlmod's canonical name; a few built-ins (platforms) have none.
        for repo in (external / f"{name}+", external / name):
            if (repo / "MODULE.bazel").is_file():
                found[name] = repo.resolve()
                break
    return found


def override_rc(paths: dict[str, Path]) -> str:
    return "".join(f"common --override_module={name}={paths[name]}\n" for name in sorted(paths))


def coverage_args(test_args: list[str], langs: list[str], excludes: list[str] = ()) -> list[str]:
    """The module's own test args with ref_int's unified config added before any ``--``.

    ``excludes`` (the module's ``exclude_test_targets``) become negative patterns after ``--``.
    """
    ours = ["--config=unified", "--combined_report=lcov"]
    if "rust" in langs:
        ours.append("--config=unified-rust")
    split = test_args.index("--") if "--" in test_args else len(test_args)
    targets = [*test_args[split + 1 :], *(f"-{target}" for target in excludes)]
    separator = ["--"] if targets else []
    return ["coverage", "--lockfile_mode=update", *test_args[:split], *ours, *separator, *targets]


def _status(case: ET.Element) -> str:
    if case.find("failure") is not None or case.find("error") is not None:
        return "failed"
    return "skipped" if case.find("skipped") is not None or case.get("status") == "notrun" else "passed"


def count_testcases(tests_dir: Path) -> dict[str, int]:
    """passed/failed/skipped/total over every testcase in a module report's test.xml files."""
    counts = Counter(_status(case) for xml in tests_dir.glob("**/test.xml") for case in ET.parse(xml).iter("testcase"))
    return {key: counts[key] for key in ("passed", "failed", "skipped")} | {"total": counts.total()}


def lcov_percentages(lcov: Path) -> dict[str, str]:
    """lines/functions/branches hit ratios summed over an lcov tracefile; "" where nothing is found."""
    totals = dict.fromkeys(("LF", "LH", "FNF", "FNH", "BRF", "BRH"), 0)
    for line in lcov.read_text(errors="replace").splitlines():
        key, _, value = line.partition(":")
        if key in totals and value.isdigit():
            totals[key] += int(value)

    def ratio(found: str, hit: str) -> str:
        return f"{100 * totals[hit] / totals[found]:.1f}%" if totals[found] else ""

    return {"lines": ratio("LF", "LH"), "functions": ratio("FNF", "FNH"), "branches": ratio("BRF", "BRH")}


def run(args: argparse.Namespace) -> int:
    known = load_known_good(REF_INT / "known_good.json")
    module = known.modules["target_sw"].get(args.module)
    if module is None:
        sys.exit(f"{args.module} is not a target_sw module in known_good.json")
    # ref_int's committed lock plus --lockfile_mode=error make this the same set in every job.
    resolved = graph_modules(mod_graph(REF_INT, None, "error"))

    work = args.work_dir.resolve()
    workspace, out = work / module.name, work / "reports" / module.name
    shutil.rmtree(workspace, ignore_errors=True)
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    source = fetch({module.name}).get(module.name)
    if source is None:
        sys.exit(f"could not fetch {module.name} in ref_int")
    shutil.copytree(source, workspace, symlinks=True)
    shutil.copy(UNIFIED_TOOLCHAINS, workspace)
    module_file = workspace / "MODULE.bazel"
    module_file.chmod(0o644)  # read-only when copied from Bazel's repo cache
    with module_file.open("a") as f:
        f.write(f'\ninclude("//:{UNIFIED_TOOLCHAINS.name}")\n')

    # Every bazel call in the module goes through this wrapper, so they all see the overrides and
    # the unified config. Its own output base keeps
    # the overrides, which point into ref_int's output base, from pointing at the module's own repos
    # when ~/.bazelrc sets a shared one (setup-bazel does).
    rc = work / f"{module.name}.overrides.bazelrc"
    rc.write_text("")  # empty while the module's own graph is read
    wrapper = work / "bin" / "bazel"
    wrapper.parent.mkdir(parents=True, exist_ok=True)
    startup = f"--output_base={work / 'output_base' / module.name} --bazelrc={UNIFIED_RC} --bazelrc={rc}"
    wrapper.write_text(f'#!/bin/sh\nexec {shutil.which("bazel")} {startup} "$@"\n')
    wrapper.chmod(0o755)
    env = {
        **os.environ,
        "PATH": f"{wrapper.parent}{os.pathsep}{os.environ['PATH']}",
        "USE_BAZEL_VERSION": (REF_INT / ".bazelversion").read_text().strip(),
    }

    shared = direct_deps(mod_graph(workspace, env)) & resolved
    pinned = fetch(shared)
    rc.write_text(override_rc(pinned))
    unpinned = sorted(shared - set(pinned))
    shutil.copy(rc, out / "overrides.bazelrc")

    command = coverage_args(module.metadata.test_args, module.metadata.langs, module.metadata.exclude_test_targets)
    exit_code, log = streamed(["bazel", *command], workspace, env)

    results = list((workspace / "bazel-testlogs").glob("**/test.xml"))
    for xml in results:
        dest = out / "tests" / xml.relative_to(workspace / "bazel-testlogs")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(xml, dest)
    # Bazel exits 0 when every test is skipped (e.g. all incompatible with the platform).
    no_tests = not results
    exit_code = exit_code or int(no_tests)
    (out / "coverage").mkdir()
    lcov = Path(bazel(["info", "output_path"], workspace, env).stdout.strip()) / "_coverage" / "_coverage_report.dat"
    if lcov.is_file():
        shutil.copy(lcov, out / "coverage" / "lcov.dat")
    (out / "result.json").write_text(json.dumps({"exit_code": exit_code}) + "\n")

    failed = STATUS_LINE.findall(log)
    summary = [f"## {module.name}: bazel exit code {exit_code}", ""]
    summary += [f"- `{target}` {status}" for target, status in failed]
    if no_tests:
        summary.append("- no test was executed: all skipped or the build failed, see the job log")
    elif exit_code and not failed:
        summary.append("- no per-target results: the build or analysis failed, see the job log")
    if unpinned:
        summary.append(f"- not pinned (ref_int could not fetch them): {', '.join(unpinned)}")
    summary.append(f"- {len(pinned)} modules pinned to ref_int's versions (overrides.bazelrc)")
    text = "\n".join(summary) + "\n"
    (out / "summary.md").write_text(text)
    print(text)
    append_to_step_summary(text)
    return exit_code


def report(args: argparse.Namespace) -> int:
    """Write the verification report's unit test and coverage summaries from the module reports.

    A module without a report (its run never got that far) is listed as failed, not left out.
    """
    known = load_known_good(REF_INT / "known_good.json")
    unit_tests, coverage = {}, {}
    for module in known.modules["target_sw"].values():
        reports = args.reports_dir / module.name
        result_file = reports / "result.json"
        result = json.loads(result_file.read_text()) if result_file.is_file() else {"exit_code": 1}
        unit_tests[module.name] = {**count_testcases(reports / "tests"), "exit_code": result["exit_code"]}
        lcov = reports / "coverage" / "lcov.dat"
        if "cpp" in module.metadata.langs:
            numbers = lcov_percentages(lcov) if lcov.is_file() else {}
            coverage[f"{module.name}_cpp"] = {**numbers, "exit_code": 0 if numbers.get("lines") else 1}

    args.out_dir.mkdir(parents=True, exist_ok=True)
    unit_tests_md = generate_markdown_report(
        with_status(unit_tests),
        title="Unit Test Execution Summary",
        columns=["module", "status", "passed", "failed", "skipped", "total"],
        output_path=args.out_dir / "unit_test_summary.md",
    )
    coverage_md = generate_markdown_report(
        with_status(coverage),
        title="Coverage Analysis Summary",
        columns=["module", "status", "lines", "functions", "branches"],
        output_path=args.out_dir / "coverage_summary.md",
    )
    append_to_step_summary(unit_tests_md, coverage_md)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(required=True)
    run_parser = sub.add_parser("run")
    run_parser.add_argument("module")
    run_parser.add_argument("--work-dir", type=Path, default=REF_INT / "_module_tests")
    run_parser.set_defaults(func=run)
    report_parser = sub.add_parser("report")
    report_parser.add_argument("reports_dir", type=Path, help="directory with one 'run' report per module")
    report_parser.add_argument("--out-dir", type=Path, default=REF_INT / "docs" / "verification_report")
    report_parser.set_defaults(func=report)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
