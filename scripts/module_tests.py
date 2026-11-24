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
  codeql <module>   analyse <module> the same way with score_tools' codeql_analysis (POC)
  lint <module>     lint <module> the same way with the central clang-tidy, clippy and ruff policies (POC)
  report <dir>      write the verification report's unit test and coverage summaries

Every module in the module's dependency graph that ref_int also resolves is pinned with
``--override_module``, pointing at ref_int's own fetched copy (so ref_int's patches come along);
ones ref_int cannot fetch are reported as not pinned. ``bazel_common/unified.bazelrc`` and the
module's ``extra_test_config`` are layered over the module's .bazelrc. The only edits to the module
are one ``include()`` of ref_int's ``unified_toolchains.MODULE.bazel``, as toolchains can only be
defined in MODULE files, and a ``bazel_dep`` raising score_devcontainer to its known_good version.
"""

import argparse
import json
import os
import re
import shlex
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
# Only enable the coverage_tool flow for releases already integrated in known_good.json.
COVERAGE_MODULES = {
    "score_baselibs",
    "score_persistency",
    "score_logging",
    "score_kyron",
    # "score_communication",  # Enable once ref_int integrates a release using coverage_tool.
    "score_lifecycle",
    "score_time",
    # "score_config_management",  # Enable once ref_int integrates a release using coverage_tool.
}
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
        command, cwd=cwd, env=env, text=True, errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT
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


def mod_graph(cwd: Path, env: dict | None = None, lockfile_mode: str = "update") -> dict:
    result = bazel(["mod", "graph", "--output=json", f"--lockfile_mode={lockfile_mode}"], cwd, env)
    if result.returncode:
        sys.exit(f"bazel mod graph failed in {cwd}")
    return json.loads(result.stdout)


def fetch(names: set[str]) -> dict[str, Path]:
    """Fetch modules in ref_int and return where their sources landed.

    Fetching in ref_int's context applies its ``git_override`` / ``single_version_override``
    (including the known_good.json patches) automatically. A repo that fails to fetch (e.g. a dead
    mirror of a module no build ever touches) is just missing from the result instead of failing
    the run. ``multiple_version_override`` is not supported: its repos are named
    ``<name>+<version>`` and are not found here.
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


def override_rc(paths: dict[str, Path], extra_test_config: list[str] = ()) -> str:
    """Pin each module to its path; the module's ``extra_test_config`` flags follow as build flags."""
    rc = "".join(f"common --override_module={name}={paths[name]}\n" for name in sorted(paths))
    return rc + "".join(f"build --{flag}\n" for flag in extra_test_config)


def coverage_args(
    test_args: list[str], langs: list[str], excludes: list[str] = (), *, enabled: bool = True, module: str = ""
) -> list[str]:
    """The module's own test args with ref_int's unified config added before any ``--``.

    Modules awaiting coverage_tool integration run their unit tests without coverage.
    ``excludes`` (the module's ``exclude_test_targets``) become negative patterns after ``--``.
    """
    # Coverage modules provide their own instrumented toolchain (Kyron keeps GCC for C++).
    # Share the integration platform and fallback toolchain without forcing unified Clang.
    ours = ["--config=unified-base" if enabled else "--config=unified"]
    if enabled:
        ours.extend(["--build_tests_only", "--config=llvm_cov"])
    if "rust" in langs:
        ours.append("--config=unified-rust")
    split = test_args.index("--") if "--" in test_args else len(test_args)
    flags = test_args[:split]
    if enabled:
        # The module's llvm_cov config chooses the coverage toolchain and instrumentation.
        # Regular test presets select GCC or sanitizers and can override or conflict with it.
        flags = [
            arg
            for arg in flags
            if arg not in ("--config=score-linux-x86_64", "--config=x86_64-linux", "--config=asan_ubsan_lsan")
        ]
    targets = list(test_args[split + 1 :])
    if enabled and module == "score_baselibs":
        targets.extend(
            [
                # This library interposes __cxa_allocate_exception; ld.lld rejects the
                # duplicate definition from the statically linked C++ runtime.
                "-//score/language/safecpp/aborts_upon_exception/...",
                # The static mock fails gMock's leak check with static linking; the module
                # release's own Coverage CI excludes this test too.
                "-//score/os/linux/utils/test:network_interface_test",
            ]
        )
    targets.extend(f"-{target}" for target in excludes)
    separator = ["--"] if targets else []
    return [
        "coverage" if enabled else "test",
        "--lockfile_mode=update",
        *flags,
        *ours,
        *separator,
        *targets,
    ]


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


def _setup_working_dir(work: Path, name: str) -> tuple[Path, Path]:
    """Fresh module workspace and report dir under ``work``."""
    workspace, out = work / name, work / "reports" / name
    shutil.rmtree(workspace, ignore_errors=True)
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    return workspace, out


def _copy_fetch_module(name: str, workspace: Path) -> None:
    """Copy ref_int's fetched (and patched) copy of the module into ``workspace``."""
    source = fetch({name}).get(name)
    if source is None:
        sys.exit(f"could not fetch {name} in ref_int")
    shutil.copytree(source, workspace, symlinks=True)


def _append_unified_toolchain(workspace: Path) -> None:
    shutil.copy(UNIFIED_TOOLCHAINS, workspace)
    module_file = workspace / "MODULE.bazel"
    module_file.chmod(0o644)  # read-only when copied from Bazel's repo cache
    with module_file.open("a") as f:
        f.write(f'\ninclude("//:{UNIFIED_TOOLCHAINS.name}")\n')


def _apply_extra_dependency_overrides(workspace: Path, devcontainer_version: str) -> None:
    """Raise dependencies the module's own graph cannot resolve as is.

    The module's own graph is resolved before any ref_int pin applies. score_devcontainer 1.11.1
    (from score_docs_as_code 8.3.0) had its tag re-pushed, so its archive fails the registry
    checksum. A module that depends on it itself gets a single_version_override (a second bazel_dep
    is an error); otherwise a bazel_dep lets MVS raise it, as an override errors when the module is
    not in the graph.
    """
    module_file = workspace / "MODULE.bazel"
    if re.search(r'bazel_dep\(\s*name\s*=\s*"score_devcontainer"', module_file.read_text()):
        line = f'single_version_override(module_name = "score_devcontainer", version = "{devcontainer_version}")\n'
    else:
        line = f'bazel_dep(name = "score_devcontainer", version = "{devcontainer_version}", dev_dependency = True)\n'
    with module_file.open("a") as f:
        f.write(line)


def normalize_lcov(text: str, module: str) -> str:
    """Rebase coverage_tool's canonical paths into ref_int's external module namespace."""
    lines = []
    for line in text.splitlines():
        if line.startswith("SF:"):
            path = line[3:]
            if path.startswith("/"):
                raise ValueError(f"{module}: coverage source must be repository-relative: {path}")
            if path.startswith("../"):
                path = "external/" + path[3:]
            if not path.startswith("external/"):
                path = f"external/{module}+/{path}"
            parts = path.split("/")
            if len(parts) < 3 or any(part in ("", ".", "..", "_virtual_includes") for part in parts):
                raise ValueError(f"{module}: coverage source is not canonical: {path}")
            if parts[1] == "_main":
                parts[1] = f"{module}+"
            line = "SF:" + "/".join(parts)
        lines.append(line)
    return "\n".join(lines) + "\n" if lines else ""


def combine_reports(reports: Path, modules: list[str], output: Path) -> None:
    """Combine available module reports, leaving absent measurements unavailable."""
    chunks = []
    for module in sorted(modules):
        report = reports / module / "coverage" / "coverage_report.dat"
        if report.is_file():
            chunks.append(report.read_text(encoding="utf-8"))
        else:
            print(f"::warning::{module}: no documentation coverage report available")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(chunk.rstrip("\n") + "\n" for chunk in chunks), encoding="utf-8")


def _collect_coverage(workspace: Path, out: Path, env: dict) -> int:
    # Export through coverage_tool's public CLI. It owns the backend's report packaging;
    # ref_int only translates the exported source identities into its workspace context.
    # Threshold zero collects evidence without adding a new percentage gate to module tests.
    result = bazel(
        [
            "run",
            "--lockfile_mode=update",
            "@score_coverage//:generate_coverage_html",
            "--",
            "--testlogs-subdir=",
            "--archive-dir",
            str(out / "coverage"),
        ],
        workspace,
        {**env, "COVERAGE_THRESHOLD": "0"},
    )
    print(result.stdout)
    if result.returncode:
        return result.returncode
    lcov = out / "coverage" / "coverage_report.dat"
    lcov.write_text(normalize_lcov(lcov.read_text(encoding="utf-8"), out.name), encoding="utf-8")
    return 0


def _write_summary(
    name: str, out: Path, exit_code: int, log: str, *, no_tests: bool, pinned: dict, unpinned: list[str]
) -> None:
    failed = STATUS_LINE.findall(log)
    summary = [f"## {name}: bazel exit code {exit_code}", ""]
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


def _collect_dependable_element_docs(workspace: Path, out: Path, targets: list[str], env: dict) -> None:
    """Build the module's dependable element sphinx targets and keep their HTML for the main docs.

    The main docs build cannot depend on them via Bazel (docs_as_code only takes docs()/docs_bundle
    labels as external needs), so the HTML travels as part of the module report instead. A failure
    here is reported but does not fail the module's tests.
    """
    if not targets:
        return
    code, _ = streamed(["bazel", "build", "--keep_going", *targets], workspace, env)
    for target in targets:
        package, name = target.removeprefix("//").split(":")
        html = workspace / "bazel-bin" / package / name / "html"
        if code != 0 or not html.is_dir():
            print(f"WARNING: no HTML for {target}", file=sys.stderr)
            continue
        shutil.copytree(html, out / "dependable_element_docs" / name, symlinks=False, dirs_exist_ok=True)


def _add_dependencies(workspace: Path, names: tuple[str, ...]) -> None:
    """Make ref_int's copies of ``names`` available; existing dependencies are pinned anyway."""
    module_file = workspace / "MODULE.bazel"
    text = module_file.read_text()
    missing = {name for name in names if not re.search(rf'bazel_dep\(\s*name\s*=\s*"{name}"', text)}
    if not missing:
        return
    sources = fetch(missing)
    if missing - set(sources):
        sys.exit(f"could not fetch {', '.join(sorted(missing - set(sources)))} in ref_int")
    with module_file.open("a") as f:
        for name in sorted(missing):
            f.write(
                f'bazel_dep(name = "{name}", dev_dependency = True)\n'
                f'local_path_override(module_name = "{name}", path = "{sources[name]}")\n'
            )


def _prepare_module(module, known, work: Path, *, extra_deps: tuple[str, ...] = ()):
    """The module as root workspace with ref_int's versions pinned.

    Returns the workspace, its report dir, the environment for the bazel wrapper and the
    pinned/unpinned modules.
    """
    # ref_int's committed lock plus --lockfile_mode=error make this the same set in every job.
    resolved = graph_modules(mod_graph(REF_INT, None, "error"))

    workspace, out = _setup_working_dir(work, module.name)
    _copy_fetch_module(module.name, workspace)
    _append_unified_toolchain(workspace)
    _apply_extra_dependency_overrides(workspace, known.modules["tooling"]["score_devcontainer"].version)
    _add_dependencies(workspace, extra_deps)

    # Every bazel call in the module goes through this wrapper, so they all see the overrides and
    # the unified config. Its own output base keeps
    # the overrides, which point into ref_int's output base, from pointing at the module's own repos
    # when ~/.bazelrc sets a shared one (setup-bazel does).
    rc = work / f"{module.name}.overrides.bazelrc"
    rc.write_text("")  # empty while the module's own graph is read
    wrapper = work / "bin" / "bazel"
    wrapper.parent.mkdir(parents=True, exist_ok=True)
    startup = [f"--output_base={work / 'output_base' / module.name}", f"--bazelrc={UNIFIED_RC}", f"--bazelrc={rc}"]
    wrapper.write_text(f'#!/bin/sh\nexec {shlex.quote(shutil.which("bazel"))} {shlex.join(startup)} "$@"\n')
    wrapper.chmod(0o755)
    env = {
        **os.environ,
        "PATH": f"{wrapper.parent}{os.pathsep}{os.environ['PATH']}",
        # Overrules the module's own .bazelversion: the module is tested with ref_int's Bazel.
        "USE_BAZEL_VERSION": (REF_INT / ".bazelversion").read_text().strip(),
    }

    # ponytail: single pass; modules that only enter the graph once these overrides apply stay
    # unpinned. Repeat until the set is stable if that ever matters.
    # Yanked versions in the module's own (unpinned) graph do not matter: only the module names are
    # used, and the test run below gets ref_int's versions.
    own_graph = mod_graph(workspace, {**env, "BZLMOD_ALLOW_YANKED_VERSIONS": "all"})
    shared = (graph_modules(own_graph) & resolved) - {module.name}
    pinned = fetch(shared)
    rc.write_text(override_rc(pinned, module.metadata.extra_test_config))
    unpinned = sorted(shared - set(pinned))
    shutil.copy(rc, out / "overrides.bazelrc")
    return workspace, out, env, pinned, unpinned


def run(args: argparse.Namespace) -> int:
    known = load_known_good(REF_INT / "known_good.json")
    module = known.modules["target_sw"].get(args.module)
    if module is None:
        sys.exit(f"{args.module} is not a target_sw module in known_good.json")
    workspace, out, env, pinned, unpinned = _prepare_module(module, known, args.work_dir.resolve())

    coverage_enabled = module.name in COVERAGE_MODULES
    command = coverage_args(
        module.metadata.test_args,
        module.metadata.langs,
        module.metadata.exclude_test_targets,
        enabled=coverage_enabled,
        module=module.name,
    )
    exit_code, log = streamed(["bazel", *command], workspace, env)

    results = list((workspace / "bazel-testlogs").glob("**/test.xml"))
    for xml in results:
        dest = out / "tests" / xml.relative_to(workspace / "bazel-testlogs")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(xml, dest)
    # Bazel exits 0 when every test is skipped (e.g. all incompatible with the platform).
    no_tests = not results
    exit_code = exit_code or int(no_tests)
    if coverage_enabled:
        coverage_exit = _collect_coverage(workspace, out, env)
        exit_code = exit_code or coverage_exit
    _collect_dependable_element_docs(workspace, out, module.metadata.dependable_element_docs, env)
    (out / "result.json").write_text(json.dumps({"exit_code": exit_code}) + "\n")
    _write_summary(module.name, out, exit_code, log, no_tests=no_tests, pinned=pinned, unpinned=unpinned)
    return exit_code


CODEQL_PACKAGE = "ref_int_codeql"
# The statically linked hermetic GCC cannot be traced by CodeQL, ref_int's LLVM toolchain can.
# clang-tidy also needs a Clang command line.
LLVM_TOOLCHAIN = "--extra_toolchains=@unified_llvm_toolchain//:cc-toolchain-x86_64-linux"


def module_configs(module) -> list[str]:
    """The module's own test configs without sanitizers, plus ref_int's unified platform."""
    split = module.metadata.test_args.index("--") if "--" in module.metadata.test_args else None
    configs = [
        arg.removeprefix("--config=")
        for arg in module.metadata.test_args[:split]
        if arg.startswith("--config=") and arg != "--config=asan_ubsan_lsan"
    ]
    configs.append("unified-base")
    if "rust" in module.metadata.langs:
        configs.append("unified-rust")
    return configs


def codeql_build_file(module, coding_standards_config: str | None) -> str:
    """BUILD file with score_tools' codeql_analysis of the module's code root (traced LLVM build)."""
    targets = [module.metadata.code_root_path, *(f"-{target}" for target in module.metadata.exclude_test_targets)]
    optional = (
        f"    coding_standards_config = {json.dumps(coding_standards_config)},\n" if coding_standards_config else ""
    )
    return (
        'load("@score_tools//codeql:defs.bzl", "codeql_analysis")\n\n'
        "codeql_analysis(\n"
        '    name = "codeql",\n'
        f"    bazel_args = {json.dumps([LLVM_TOOLCHAIN])},\n"
        f"    build_configs = {json.dumps(module_configs(module))},\n"
        f"{optional}"
        "    exclude_testonly = True,\n"
        "    keep_going = True,\n"
        f"    targets = {json.dumps(targets)},\n"
        ")\n"
    )


def find_coding_standards_config(workspace: Path) -> str | None:
    """The module's own coding-standards.yml (deviations, recategorizations), if exactly one exists."""
    found = [
        path.relative_to(workspace).as_posix()
        for name in ("coding-standards.yml", "coding-standards.yaml")
        for path in workspace.rglob(name)
        if not path.relative_to(workspace).parts[0].startswith("bazel-")
    ]
    return found[0] if len(found) == 1 else None


def normalize_sarif(document: dict, module: str, workspace: Path) -> dict:
    """Rebase workspace-relative SARIF locations into ref_int's external module namespace.

    Results outside the module (dependencies, toolchain headers) are dropped.
    """
    prefix = f"external/{module}+/"

    def rebase(uri: str) -> str:
        path = uri.removeprefix("file://")
        if path.startswith("/"):
            # Linters running in a sandbox report paths below its execroot.
            execroot = re.search(r"/execroot/[^/]+/(.*)$", path)
            if execroot:
                path = execroot.group(1)
            elif Path(path).is_relative_to(workspace):
                path = Path(path).relative_to(workspace).as_posix()
            else:
                return uri
        return path if path.startswith("external/") else f"{prefix}{path}"

    def visit(node) -> None:
        if isinstance(node, dict):
            if isinstance(node.get("uri"), str):
                node["uri"] = rebase(node["uri"])
                node.pop("uriBaseId", None)
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    def in_module(result: dict) -> bool:
        locations = result.get("locations") or [{}]
        uri = locations[0].get("physicalLocation", {}).get("artifactLocation", {}).get("uri")
        return uri is None or uri.startswith(prefix)

    for sarif_run in document.get("runs", []):
        # The base points into the module workspace of this job only.
        sarif_run.pop("originalUriBaseIds", None)
    visit(document.get("runs", []))
    for sarif_run in document.get("runs", []):
        sarif_run["results"] = [result for result in sarif_run.get("results", []) if in_module(result)]
    return document


def codeql(args: argparse.Namespace) -> int:
    """Analyse a module with CodeQL as root workspace, like ``run`` with ref_int's versions."""
    known = load_known_good(REF_INT / "known_good.json")
    module = known.modules["target_sw"].get(args.module)
    if module is None:
        sys.exit(f"{args.module} is not a target_sw module in known_good.json")
    work = args.work_dir.resolve()
    workspace, out, env, pinned, unpinned = _prepare_module(module, known, work, extra_deps=("score_tools",))
    # Nested bazel calls of the analysis do not pass a lockfile mode, a module's own .bazelrc may set error.
    with (work / f"{module.name}.overrides.bazelrc").open("a") as rc:
        rc.write("common --lockfile_mode=update\n")
    coding_standards = find_coding_standards_config(workspace)
    package = workspace / CODEQL_PACKAGE
    package.mkdir()
    (package / "BUILD").write_text(codeql_build_file(module, coding_standards), encoding="utf-8")
    shutil.copy(package / "BUILD", out / "codeql.BUILD")

    results = out / "codeql"
    exit_code, _ = streamed(
        [
            "bazel",
            "run",
            "--lockfile_mode=update",
            f"//{CODEQL_PACKAGE}:codeql",
            "--",
            # Bazelisk puts the real bazel first on PATH, so the nested build must use the wrapper explicitly.
            f"--bazel={work / 'bin' / 'bazel'}",
            f"--output-dir={results}",
            f"--output-prefix={module.name}",
        ],
        workspace,
        env,
    )
    sarif = results / f"{module.name}.sarif"
    findings = 0
    if sarif.is_file():
        document = normalize_sarif(json.loads(sarif.read_text(encoding="utf-8")), module.name, workspace)
        findings = sum(len(run.get("results", [])) for run in document.get("runs", []))
        target = out / "static_analysis" / f"{module.name}.sarif"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(document) + "\n", encoding="utf-8")
    else:
        exit_code = exit_code or 1
    summary = [f"## {module.name}: CodeQL exit code {exit_code}", ""]
    summary.append(f"- {findings} findings in the module (coding standards config: {coding_standards or 'none'})")
    if unpinned:
        summary.append(f"- not pinned (ref_int could not fetch them): {', '.join(unpinned)}")
    summary.append(f"- {len(pinned)} modules pinned to ref_int's versions (overrides.bazelrc)")
    integrity = results / "analysis_reports" / "database_integrity_report.md"
    if integrity.is_file():
        summary += ["", integrity.read_text(encoding="utf-8")]
    append_to_step_summary("\n".join(summary) + "\n")
    return exit_code


LINT_PACKAGE = "ref_int_lint"
LINT_DEPS = ("aspect_rules_lint", "score_cpp_policies", "score_rust_policies")
LINT_ASPECTS = (
    f"//{LINT_PACKAGE}:linters.bzl%clang_tidy",
    f"//{LINT_PACKAGE}:linters.bzl%ruff",
    "@score_rust_policies//clippy:linters.bzl%clippy_strict",
)
SARIF_PARSER = "sarif_parser_toolchains"
SARIF_PARSER_EXTENSION = (
    'ref_int_lint = use_extension("@aspect_rules_lint//lint:extensions.bzl", "toolchains", dev_dependency = True)\n'
    "ref_int_lint.sarif_parser()\n"
    f'use_repo(ref_int_lint, "{SARIF_PARSER}")\n'
)


def lint_config_files(workspace: Path) -> tuple[str | None, str | None]:
    """The module's root .clang-tidy and ruff config, if the root is a package."""
    if not any((workspace / name).is_file() for name in ("BUILD", "BUILD.bazel")):
        return None, None
    clang_tidy = ".clang-tidy" if (workspace / ".clang-tidy").is_file() else None
    ruff = next((name for name in ("ruff.toml", ".ruff.toml") if (workspace / name).is_file()), None)
    pyproject = workspace / "pyproject.toml"
    if ruff is None and pyproject.is_file() and "[tool.ruff" in pyproject.read_text(errors="replace"):
        ruff = "pyproject.toml"
    return clang_tidy, ruff


def export_root_files(workspace: Path, names: list[str]) -> None:
    """Export the config files, the module may disable implicit file exports."""
    build = next(path for name in ("BUILD.bazel", "BUILD") if (path := workspace / name).is_file())
    text = build.read_text(encoding="utf-8")
    exported = " ".join(re.findall(r"exports_files\(([^)]*)\)", text))
    missing = [name for name in names if f'"{name}"' not in exported]
    if missing:
        build.chmod(0o644)
        with build.open("a", encoding="utf-8") as f:
            f.write(f"\nexports_files({json.dumps(missing)})\n")


def linters_bzl(clang_tidy_config: str | None, ruff_config: str | None) -> str:
    """clang-tidy with the module's own config, else score_cpp_policies' baseline, and ruff."""
    # clang-tidy only finds configs above the linted file, so the baseline is passed explicitly.
    config = (
        f'configs = [Label("//:{clang_tidy_config}")]'
        if clang_tidy_config
        else 'global_config = [Label("@score_cpp_policies//clang_tidy:.clang-tidy")]'
    )
    ruff = f'[Label("//:{ruff_config}")]' if ruff_config else "[]"
    return (
        'load("@aspect_rules_lint//lint:clang_tidy.bzl", "lint_clang_tidy_aspect")\n'
        'load("@aspect_rules_lint//lint:ruff.bzl", "lint_ruff_aspect")\n\n'
        "# The defaults of score_cpp_policies' make_clang_tidy_aspect.\n"
        "clang_tidy = lint_clang_tidy_aspect(\n"
        '    binary = Label("@unified_llvm_toolchain//:clang-tidy"),\n'
        f"    {config},\n"
        "    lint_target_headers = True,\n"
        "    angle_includes_are_system = True,\n"
        ")\n\n"
        "ruff = lint_ruff_aspect(\n"
        '    binary = Label("@aspect_rules_lint//lint:ruff_bin"),\n'
        f"    configs = {ruff},\n"
        ")\n"
    )


def lint_query(module) -> str:
    """C++, Rust and Python rule targets below the module's code root that are not testonly."""
    selected = f'kind("^(cc|rust|py)_", {module.metadata.code_root_path}'
    selected += "".join(f" - {target}" for target in module.metadata.exclude_test_targets) + ")"
    return f"{selected} except attr(testonly, 1, {selected})"


def lint_command(module, targets_file: Path) -> list[str]:
    return [
        "bazel",
        "build",
        "--lockfile_mode=update",
        "--keep_going",
        "--skip_incompatible_explicit_targets",
        *(f"--config={config}" for config in module_configs(module)),
        LLVM_TOOLCHAIN,
        f"--extra_toolchains=@{SARIF_PARSER}//:all",
        f"--aspects={','.join(LINT_ASPECTS)}",
        # Only the SARIF reports, nothing else of the targets is built.
        "--output_groups=rules_lint_machine",
        "--@aspect_rules_lint//lint:fail_on_violation=false",
        # score_cpp_policies' warning flags are GCC only, as in the modules' own clang-tidy configs.
        "--features=-strict_warnings",
        "--features=-warnings_as_errors",
        "--features=-treat_warnings_as_errors",
        f"--target_pattern_file={targets_file}",
    ]


def merge_lint_reports(reports: list[Path], module: str, workspace: Path) -> tuple[dict, int]:
    """One SARIF document with every non-empty run (and one run per tool), plus the non-SARIF count."""
    runs, tools, raw = [], set(), 0
    for report in reports:
        text = report.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            continue
        try:
            document = json.loads(text)
        except json.JSONDecodeError:
            # Without a SARIF parser toolchain rules_lint keeps the linter's raw output.
            raw += 1
            continue
        for sarif_run in normalize_sarif(document, module, workspace).get("runs", []):
            tool = sarif_run.get("tool", {}).get("driver", {}).get("name")
            if sarif_run.get("results") or tool not in tools:
                tools.add(tool)
                runs.append(sarif_run)
    return {"version": "2.1.0", "runs": runs}, raw


def lint(args: argparse.Namespace) -> int:
    """Lint a module as root workspace with the central policies, like ``run`` with ref_int's versions."""
    known = load_known_good(REF_INT / "known_good.json")
    module = known.modules["target_sw"].get(args.module)
    if module is None:
        sys.exit(f"{args.module} is not a target_sw module in known_good.json")
    work = args.work_dir.resolve()
    workspace, out, env, pinned, unpinned = _prepare_module(module, known, work, extra_deps=LINT_DEPS)
    module_file = workspace / "MODULE.bazel"
    if SARIF_PARSER not in module_file.read_text():
        with module_file.open("a") as f:
            f.write(SARIF_PARSER_EXTENSION)
    clang_tidy_config, ruff_config = lint_config_files(workspace)
    export_root_files(workspace, [name for name in (clang_tidy_config, ruff_config) if name])
    package = workspace / LINT_PACKAGE
    package.mkdir()
    (package / "BUILD").write_text("", encoding="utf-8")
    (package / "linters.bzl").write_text(linters_bzl(clang_tidy_config, ruff_config), encoding="utf-8")
    shutil.copy(package / "linters.bzl", out / "linters.bzl")

    query = bazel(["query", "--lockfile_mode=update", lint_query(module), "--output=label"], workspace, env)
    if query.returncode:
        sys.exit(f"bazel query for the lint targets of {module.name} failed")
    targets_file = out / "lint_targets.txt"
    targets_file.write_text(query.stdout, encoding="utf-8")
    exit_code, _ = streamed(lint_command(module, targets_file), workspace, env)

    reports = sorted((workspace / "bazel-out").resolve().rglob("*.AspectRulesLint*.report"))
    document, raw = merge_lint_reports(reports, module.name, workspace)
    target = out / "static_analysis" / f"{module.name}.lint.sarif"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(document) + "\n", encoding="utf-8")
    counts = Counter(
        sarif_run.get("tool", {}).get("driver", {}).get("name", "unknown")
        for sarif_run in document["runs"]
        for _ in sarif_run.get("results", [])
    )
    summary = [f"## {module.name}: lint exit code {exit_code}", ""]
    summary.append(f"- {len(query.stdout.split())} targets, {len(reports)} reports, {raw} not in SARIF format")
    clang_tidy = clang_tidy_config or "score_cpp_policies baseline only"
    summary.append(f"- configs: .clang-tidy {clang_tidy}, ruff {ruff_config or 'none'}")
    summary += [
        f"- {tool}: {count} findings in the module (before de-duplication)" for tool, count in sorted(counts.items())
    ]
    if unpinned:
        summary.append(f"- not pinned (ref_int could not fetch them): {', '.join(unpinned)}")
    summary.append(f"- {len(pinned)} modules pinned to ref_int's versions (overrides.bazelrc)")
    append_to_step_summary("\n".join(summary) + "\n")
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
        lcov = reports / "coverage" / "coverage_report.dat"
        if module.name in COVERAGE_MODULES:
            numbers = lcov_percentages(lcov) if lcov.is_file() else {}
            coverage[module.name] = {**numbers, "exit_code": 0 if numbers.get("lines") else 1}

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
    combine_reports(
        args.reports_dir,
        sorted(COVERAGE_MODULES & known.modules["target_sw"].keys()),
        REF_INT / "coverage-report" / "coverage_report.dat",
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(required=True)
    run_parser = sub.add_parser("run")
    run_parser.add_argument("module")
    run_parser.add_argument("--work-dir", type=Path, default=REF_INT / "_module_tests")
    run_parser.set_defaults(func=run)
    codeql_parser = sub.add_parser("codeql")
    codeql_parser.add_argument("module")
    codeql_parser.add_argument("--work-dir", type=Path, default=REF_INT / "_module_codeql")
    codeql_parser.set_defaults(func=codeql)
    lint_parser = sub.add_parser("lint")
    lint_parser.add_argument("module")
    lint_parser.add_argument("--work-dir", type=Path, default=REF_INT / "_module_lint")
    lint_parser.set_defaults(func=lint)
    report_parser = sub.add_parser("report")
    report_parser.add_argument("reports_dir", type=Path, help="directory with one 'run' report per module")
    report_parser.add_argument("--out-dir", type=Path, default=REF_INT / "docs" / "verification_report")
    report_parser.set_defaults(func=report)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
