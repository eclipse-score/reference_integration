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
import json
import re
import select
import sys
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint
from subprocess import PIPE, Popen

from known_good.bazel_version import resolve_stage2_bazel_version
from known_good.models.known_good import load_known_good
from known_good.models.module import Module
from known_good.resolved_dependencies import (
    GRAPH_NAME,
    DependencyGraph,
    ResolvedDependencies,
    injected_override_names,
)


@dataclass
class ProcessResult:
    stdout: str
    stderr: str
    exit_code: int


def print_centered(message: str, width: int = 120, fillchar: str = "-") -> None:
    print(message.center(width, fillchar))


REF_INT_ROOT = Path(__file__).resolve().parent.parent
STAGE2_RC = REF_INT_ROOT / "ci" / "stage2" / "module.bazelrc"
RUST_COVERAGE_BUILD = REF_INT_ROOT / "rust_coverage" / "BUILD"
# Emitted for every module, so a missing or mistyped bazel_config can never leave a Stage-2
# run with no platform, no toolchain and no test filter. Per-module bazel_config entries are
# additive opt-ins only; this base config is unconditional.
STAGE2_BASE_CONFIG = "stage2-linux-x86_64"
# Central/legacy mode only (workspace=None): configs defined in ref_int's own root .bazelrc.
CENTRAL_MODE_CONFIGS = ["--config=unit-tests", "--config=ferrocene-coverage"]
# Known-broken rust coverage extraction (mostly proc_macro); applies in both modes.
DISABLED_RUST_COVERAGE = ["score_communication", "score_orchestrator"]
# The module's own post-MVS graph, captured by the resolution gate inside the module checkout.
# Distinct from Stage 1's GRAPH_NAME, which is rooted at ref_int: only this one is rooted at the
# module, so only this one contains the module's dev-dependency closure.
MODULE_GRAPH_NAME = "module_graph.json"
# Carries who owns a failure to the aggregate job, beside the two markdown summaries. Needed
# because those carry counts only, and a count of zero cannot distinguish a harness defect from an
# integration conflict. Written only on failure; absence means no verdict, not success.
ATTRIBUTION_NAME = "failure_attribution.json"


def rust_coverage_query(module_name: str, rust_coverage_build: Path = RUST_COVERAGE_BUILD) -> str:
    """The ``bazel query`` ref_int already runs for a module's rust_test targets.

    Read out of the generated ``rust_coverage/BUILD`` rather than duplicated, so known_good.json
    stays the single source of truth. The ``@<module>//`` prefix is stripped because in
    module-context mode the module is the Bazel root.
    """
    text = rust_coverage_build.read_text()
    match = re.search(rf'name = "rust_coverage_{re.escape(module_name)}".*?query = \'([^\']*)\'', text, re.S)
    if match is None:
        raise ValueError(f"No rust_coverage_{module_name} entry found in {rust_coverage_build}")
    return match.group(1).replace(f"@{module_name}//", "//")


def stage2_startup_flags() -> list[str]:
    """Bazel startup options that layer ref_int's Stage-2 config over the module's own.

    Deliberately not ``--noworkspace_rc``: the module's own ``.bazelrc`` carries settings
    unrelated to the configs ref_int names, and discarding them changes what Stage 2 validates.
    Read last, this file still wins every single-valued flag. Every Bazel call for a module must
    pass the same startup flags -- different ones start a server with a different output base.
    """
    return [f"--bazelrc={STAGE2_RC}"]


def stage2_config_flags(module: Module) -> list[str]:
    """``--config`` flags for a module: the mandatory base plus its additive opt-ins.

    Every ``bazel_config`` name must be defined in ref_int's Stage-2 rc; one that is not would
    otherwise apply nothing silently. The Rust coverage config is added in code rather than
    opted into per module, because rustc must be instrumented during the same run that produces
    the .profraw files the later ferrocene_report step reads.
    """
    defined = set(re.findall(r"^(?:build|test|coverage|common):([\w.-]+)", STAGE2_RC.read_text(), re.M))
    unknown = [c for c in module.metadata.bazel_config if c not in defined]
    if unknown:
        raise SystemExit(f"QR: {module.name} requests config(s) not defined in {STAGE2_RC}: {', '.join(unknown)}")
    configs = [STAGE2_BASE_CONFIG] + [c for c in module.metadata.bazel_config if c != STAGE2_BASE_CONFIG]
    if "rust" in module.metadata.langs and module.name not in DISABLED_RUST_COVERAGE:
        configs.append(module.metadata.rust_coverage_config or "ferrocene-coverage")
    return [f"--config={c}" for c in configs]


def stage2_target_args(module: Module) -> list[str]:
    """The target pattern, extra flags and exclusions shared by the gate and the test run.

    Both build it from here rather than assembling their own: the gate is only sound while it
    addresses the same target set as the test run (see :func:`run_resolution_gate`).
    """
    return (
        [module.metadata.code_root_path]
        + [f"--{target}" for target in module.metadata.extra_test_config]
        + ["--"]
        + [f"-{target}" for target in module.metadata.exclude_test_targets]
    )


def stage2_module_command(module: Module, startup: list[str] | None) -> list[str]:
    """The Stage-2 test command for a module checkout.

    ``--lockfile_mode=update``, not ``=error``: the gate's lock covers the extensions analysis
    needed, and a coverage run legitimately evaluates further ones (test runners, lcov tooling)
    that ``=error`` would reject. :func:`selection_digest` preserves the guarantee instead --
    extension results may grow, selected versions may not move.
    """
    return (
        ["bazel"]
        + (startup or [])
        + ["coverage"]  # coverage, not test: the .dat files come out of the same run
        + stage2_config_flags(module)
        + ["--lockfile_mode=update"]
        + stage2_target_args(module)
    )


def stage2_gate_command(module: Module, startup: list[str] | None) -> list[str]:
    """The resolution-gate command: analysis only, over the test run's exact target set."""
    return (
        ["bazel"]
        + (startup or [])
        + ["build", "--nobuild"]
        + stage2_config_flags(module)
        + ["--lockfile_mode=update"]
        + stage2_target_args(module)
    )


def run_resolution_gate(module: Module, workspace: Path, startup: list[str] | None = None) -> ProcessResult:
    """Resolve and analyse the module's test targets before a single test runs.

    Uses ``build --nobuild`` over :func:`stage2_target_args` -- the same target pattern, flags and
    exclusions the coverage run uses. Sharing the target set is the correctness argument: Bazel
    evaluates a module extension only when a target needs a repository it generates, so the gate
    cannot fail on a region of the graph the tests would never reach. ``bazel mod deps``, which
    this replaces, evaluates every extension and so failed ``score_lifecycle_health`` on a latent
    ``grpc``/``grpc-java`` ``use_repo`` inconsistency no build target reaches -- with and without
    ref_int's injection -- while its tests ran green at their 248-test baseline.
    ``coverage --nobuild`` is unusable: it exits 1 even when analysis succeeds.

    A failure here is not automatically ref_int's; :func:`classify_gate_failure` separates a
    harness defect from an integration conflict, because that decides who acts.
    """
    print_centered(f"QR: Resolving and analysing test targets for {module.name} (gate)")
    call = stage2_gate_command(module, startup)
    print_centered("QR: Running command:")
    print(" ".join(call))
    result = run_command(call, cwd=str(workspace))
    if result.exit_code == 0:
        capture_module_graph(workspace, startup)
    return result


def capture_module_graph(workspace: Path, startup: list[str] | None = None) -> Path | None:
    """Write the module's own post-MVS dependency graph next to its regenerated lock.

    Rooted at the module, this is the only place its dev-dependency closure is visible: bzlmod
    activates ``dev_dependency`` edges for the root module only, so ref_int's Stage-1 graph cannot
    show them. Captured in the gate so it describes the state the tests were pinned to and
    survives a failing test run. (The size of that gap is unmeasured: an earlier "29 vs 15 deps for
    score_baselibs" did not reproduce, so no number is claimed.)

    Failures are reported and swallowed -- evidence capture must never fail a passing gate. A
    non-zero exit is expected for some modules, because ``mod graph`` evaluates every extension and
    so inherits the over-reach that disqualified ``mod deps`` (see :func:`run_resolution_gate`); it
    still prints the complete graph, which the DR-008 verification step reads. So the dump is kept
    whenever it parses and the exit code is reported rather than obeyed.
    """
    graph_path = workspace.resolve() / MODULE_GRAPH_NAME
    call = ["bazel"] + (startup or []) + ["mod", "graph", "--output=json", "--lockfile_mode=update"]
    result = run_command(call, cwd=str(workspace))
    try:
        json.loads(result.stdout)
    except ValueError:
        print_centered(f"QR: could not capture {MODULE_GRAPH_NAME} (exit {result.exit_code}); continuing")
        return None
    graph_path.write_text(result.stdout)
    if result.exit_code != 0:
        print_centered(f"QR: {MODULE_GRAPH_NAME} captured from a partial 'mod graph' (exit {result.exit_code})")
    print_centered(f"QR: Captured module-rooted dependency graph -> {graph_path}")
    return graph_path


def selection_digest(lock: Path) -> dict[str, dict] | None:
    """The parts of ``MODULE.bazel.lock`` that decide which module *versions* get selected.

    Selection depends only on ``registryFileHashes`` and ``selectedYankedVersions``;
    ``moduleExtensions`` holds extension results, which legitimately grow as more of the build is
    exercised. Comparing only the first two proves no version moved while still allowing the test
    run to evaluate extensions the analysis-only gate never reached.

    Returns ``None`` when there is no readable lock -- callers must treat that as "cannot check",
    not "unchanged".
    """
    if not lock.is_file():
        return None
    try:
        data = json.loads(lock.read_text())
    except ValueError:
        return None
    return {
        "registryFileHashes": data.get("registryFileHashes", {}),
        "selectedYankedVersions": data.get("selectedYankedVersions", {}),
    }


def classify_gate_failure(output: str, module_bazel: Path) -> tuple[str, list[str]]:
    """Attribute a gate failure to ref_int's harness or to an integration conflict.

    An *integration conflict* is the third bucket: ref_int's resolved set and the module are each
    self-consistent but mutually incompatible -- ``score_communication`` needs
    ``@score_crates//:mockall``, absent at the ``score_crates`` commit ref_int integrates. Filing
    that as a harness defect sends it to the wrong owner.

    The signal is which repositories the error names, checked against ``injected_override_names``
    (the authoritative record of what ref_int pinned). Anything else stays ref_int's, keeping the
    default conservative.
    """
    try:
        injected = injected_override_names(module_bazel.read_text())
    except OSError:
        return "ref_int harness defect", []
    # Bazel spells an injected module's repo as @@<name>+ (canonical) or @<name>// (apparent).
    named = sorted(n for n in injected if f"@@{n}+" in output or f"@{n}//" in output)
    return ("integration conflict", named) if named else ("ref_int harness defect", [])


def run_unit_test_with_coverage(
    module: Module, workspace: Path | None = None, startup: list[str] | None = None
) -> dict[str, str | int]:
    """Run a module's unit tests + coverage.

    ``workspace`` None is central/legacy mode, addressing the module through ref_int's graph as
    ``@<module>//...``. Otherwise (DR-008 Option 4) the module is the Bazel root, targets are plain
    ``//...`` and the command runs with ``cwd=workspace``, starting from the lock the gate wrote.
    The resulting lock is the record of what the module was validated against and is uploaded as a
    Stage-2 artifact.
    """
    print_centered("QR: Running unit tests")

    if workspace is not None:
        call = stage2_module_command(module, startup)
    else:
        # Central/legacy mode: the module is addressed through ref_int's own graph.
        call = (
            ["bazel"]
            + (startup or [])
            + ["coverage"]  # Call coverage instead of test to get .dat files already
            + CENTRAL_MODE_CONFIGS
            + [
                "--test_verbose_timeout_warnings",
                "--test_timeout=1200",
                "--test_summary=testcase",
                "--test_output=errors",
                "--nocache_test_results",
                f"--instrumentation_filter=@{module.name}",
            ]
            + [f"@{module.name}{module.metadata.code_root_path}"]
            + [f"--{target}" for target in module.metadata.extra_test_config]
            + ["--"]
            + [
                # Exclude test targets specified in module metadata, if any
                f"-@{module.name}{target}"
                for target in module.metadata.exclude_test_targets
            ]
        )

    result = run_command(call, cwd=str(workspace)) if workspace is not None else run_command(call)
    summary = extract_ut_summary(result.stdout)
    return {**summary, "exit_code": result.exit_code}


def run_cpp_coverage_extraction(
    module: Module, output_path: Path, workspace: Path | None = None, startup: list[str] | None = None
) -> int:
    print_centered("QR: Running cpp coverage analysis")

    result_cpp = cpp_coverage(module, output_path, workspace=workspace, startup=startup)
    summary = extract_coverage_summary(result_cpp.stdout)

    return {**summary, "exit_code": result_cpp.exit_code}


def run_rust_coverage_extraction(
    module: Module, output_path: Path, workspace: Path | None = None, startup: list[str] | None = None
) -> int:
    print_centered("QR: Running rust coverage analysis")

    result_rust = rust_coverage(module, output_path, workspace=workspace, startup=startup)
    summary = extract_coverage_summary(result_rust.stdout)

    return {**summary, "exit_code": result_rust.exit_code}


def cpp_coverage(
    module: Module, artifact_dir: Path, workspace: Path | None = None, startup: list[str] | None = None
) -> ProcessResult:
    # .dat files are already generated in UT step

    # Run genhtml to generate the HTML report and get the summary
    # Create dedicated output directory for this module's coverage reports
    output_dir = artifact_dir / "cpp" / module.name
    output_dir.mkdir(parents=True, exist_ok=True)
    # Find input locations. In module-context mode (DR-008 Option 4) Bazel runs inside the
    # checked-out module, so query its output paths with cwd=workspace.
    # The same startup flags as the coverage run: different startup options mean a
    # different Bazel server and therefore a different output base.
    info_cwd = {"cwd": str(workspace)} if workspace is not None else {}
    info = ["bazel"] + (startup or []) + ["info"]
    bazel_coverage_output_directory = run_command([*info, "output_path"], **info_cwd).stdout.strip()
    bazel_source_directory = run_command([*info, "output_base"], **info_cwd).stdout.strip()

    dat_file = f"{bazel_coverage_output_directory}/_coverage/_coverage_report.dat"
    if not Path(dat_file).exists():
        print_centered(f"QR: No coverage dat file at {dat_file} — skipping genhtml for {module.name}")
        return ProcessResult(stdout="", stderr="", exit_code=0)

    # Some modules override Bazel's --coverage_report_generator in their own coverage.bazelrc
    # (e.g. score_communication's llvm_cov merger packages a pre-built HTML report as a zip at
    # this same path, for its own CI). genhtml only understands lcov's plain-text .info format,
    # so detect a zip (PK magic) and skip rather than crash trying to parse binary as text.
    with open(dat_file, "rb") as f:
        is_zip = f.read(2) == b"PK"
    if is_zip:
        print_centered(
            f"QR: {dat_file} is not lcov format (zip) — {module.name}'s own coverage.bazelrc overrides "
            "--coverage_report_generator; skipping genhtml"
        )
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


def _ensure_stage2_rc_importable(workspace: Path) -> None:
    """Make ref_int's Stage-2 config visible to bazel calls that don't inherit our flags.

    ``ferrocene_report`` shells out to its own nested bazel calls, which never see our
    ``--bazelrc=`` startup flag (that applies to the outer ``bazel run`` only) and would silently
    build under the module's config alone. An ``import`` line puts it on Bazel's normal default-rc
    discovery path instead. Ephemeral (this checkout only); idempotent.
    """
    module_bazelrc = workspace / ".bazelrc"
    import_line = f"import {STAGE2_RC}\n"
    existing = module_bazelrc.read_text() if module_bazelrc.exists() else ""
    if import_line not in existing:
        with module_bazelrc.open("a") as f:
            f.write(("\n" if existing and not existing.endswith("\n") else "") + import_line)


def _resolve_ferrocene_report_script(workspace: Path, startup: list[str] | None) -> Path:
    """The runfiles copy of ``@score_tooling//coverage:ferrocene_report``, not the bare binary.

    ``ferrocene_report.sh`` finds its helper scripts as
    ``$(dirname "${BASH_SOURCE[0]}")/scripts/*.py``, which resolves only from inside its own
    ``<target>.runfiles/`` tree, not from the bare ``bazel-bin`` symlink ``bazel run`` invokes. So
    this resolves that copy -- via the same ``cquery --output=starlark`` idiom the script itself
    uses for other binaries -- and calls it directly.
    """
    target = "@score_tooling//coverage:ferrocene_report"

    def bazel(args: list[str], what: str) -> ProcessResult:
        """Run a nested bazel call, failing loudly rather than on its empty output.

        ``run_command`` never raises, so an unchecked failure returns empty stdout and the
        path arithmetic below degrades silently: ``Path("") / ""`` is ``.``, which turns
        into the literal ``..runfiles``. That is how a dependency-resolution error once
        surfaced as ``No ferrocene_report.sh found under ..runfiles`` -- a message naming
        neither the failing command nor the real cause.
        """
        result = run_command(["bazel"] + (startup or []) + args, cwd=str(workspace))
        if result.exit_code != 0:
            raise RuntimeError(f"QR: {what} failed (exit {result.exit_code}) while resolving {target}")
        return result

    bazel(["build", target], "bazel build")
    bin_rel = bazel(
        ["cquery", "--output=starlark", "--starlark:expr=target.files_to_run.executable.path", target],
        "bazel cquery",
    ).stdout.strip()
    if bin_rel.startswith("/"):
        bin_path = Path(bin_rel)
    else:
        bin_path = Path(bazel(["info", "execution_root"], "bazel info execution_root").stdout.strip()) / bin_rel
    matches = list(Path(f"{bin_path}.runfiles").glob("*/coverage/ferrocene_report.sh"))
    if not matches:
        raise FileNotFoundError(f"No ferrocene_report.sh found under {bin_path}.runfiles")
    return matches[0]


def rust_coverage(
    module: Module, artifact_dir: Path, workspace: Path | None = None, startup: list[str] | None = None
) -> ProcessResult:
    # .profraw files are already generated in the UT step (ferrocene-coverage was active
    # there too — see stage2_config_flags — so instrumentation and extraction share one run).

    # Create dedicated output directory for this module's coverage reports
    output_dir = artifact_dir / "rust" / module.name
    output_dir.mkdir(parents=True, exist_ok=True)

    if workspace is not None:
        # ref_int's own rust_coverage/BUILD target addresses the module as @<module>//..., a
        # mapping that only exists in ref_int's graph. Run the underlying tool directly with
        # the same query, module-rooted (see rust_coverage_query), instead.
        _ensure_stage2_rc_importable(workspace)
        query = rust_coverage_query(module.name)
        config_flags = [c.removeprefix("--config=") for c in stage2_config_flags(module)]
        script = _resolve_ferrocene_report_script(workspace, startup)
        run_call = (
            [str(script)]
            + ["--query", query]
            + [flag for c in config_flags for flag in ("--bazel-config", c)]
            + ["--out-dir", str(output_dir.resolve())]
        )
        return run_command(run_call, cwd=str(workspace))

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

    with Popen(command, stdout=PIPE, stderr=PIPE, text=True, bufsize=1, errors="replace", **kwargs) as p:
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
            "Module-context mode (required with --module-dir): directory of the Stage-1 "
            "'stage1-resolved-deps' artifact, holding the resolved_versions.json manifest "
            "and the graph.json used to pin the module's full transitive closure."
        ),
    )
    return parser.parse_args()


def main() -> bool:
    args = parse_arguments()
    args.coverage_output_dir.mkdir(parents=True, exist_ok=True)
    path_to_docs = Path(__file__).parent.parent / "docs/verification_report"

    known = load_known_good(args.known_good_path.resolve())

    unit_tests_summary, coverage_summary = {}, {}
    # module -> {"owner", "conflicting"}; populated on failure only. See ATTRIBUTION_NAME.
    attribution: dict[str, dict[str, object]] = {}

    if args.modules_to_test:
        print_centered(f"QR: User requested tests only for specified modules: {', '.join(args.modules_to_test)}")

    workspace = args.module_dir
    startup: list[str] = []
    if workspace is not None:
        if len(args.modules_to_test) != 1:
            raise SystemExit("--module-dir requires exactly one --modules-to-test entry")
        if not STAGE2_RC.is_file():
            raise SystemExit(f"Stage-2 centralized config not found at {STAGE2_RC}")
        startup = stage2_startup_flags()
        print_centered(f"QR: Layering ref_int config {STAGE2_RC} over the module's own .bazelrc")
        # DR-008 Option 4: pin the checkout to the set ref_int resolved in Stage 1. That artifact
        # is mandatory -- known_good.json carries only first-party pins, no transitive registry
        # versions, so it cannot back the closure injection.
        if args.resolved_deps is None:
            raise SystemExit(
                "--resolved-deps is required with --module-dir: Stage 2 must pin against the "
                "Stage-1 resolved set, which known_good.json cannot supply."
            )
        resolved_dir = args.resolved_deps.resolve()
        resolved = ResolvedDependencies.from_resolved_artifact(resolved_dir)
        # The graph tells us which modules are in this module's transitive closure, so every
        # one of them is pinned — not just the deps it declares directly.
        graph = DependencyGraph.from_file(resolved_dir / GRAPH_NAME)
        module_bazel = workspace.resolve() / "MODULE.bazel"
        print_centered(f"QR: Injecting resolved deps into {module_bazel}")
        resolved.overwrite(
            module_bazel,
            module_under_test=args.modules_to_test[0],
            graph=graph,
        )

        # The module's committed MODULE.bazel.lock is stale the moment we inject overrides.
        # Delete it so the resolution gate regenerates a lock reflecting exactly the resolved set
        # the module is validated against, which the test run then pins to (DR-008 record).
        module_lock = workspace.resolve() / "MODULE.bazel.lock"
        if module_lock.exists():
            print_centered(f"QR: Removing stale module lock {module_lock} (rewritten by the resolution gate)")
            module_lock.unlink()

        # ref_int's release is a floor, not a ceiling: raise a module pinning an older Bazel, keep
        # one pinning a newer. See resolve_stage2_bazel_version for why downgrading is unsafe.
        bazelversion_dst = workspace.resolve() / ".bazelversion"
        module_ver = bazelversion_dst.read_text().strip() if bazelversion_dst.is_file() else None
        ref_int_ver = (REF_INT_ROOT / ".bazelversion").read_text().strip()
        bazel_ver = resolve_stage2_bazel_version(ref_int_ver, module_ver)
        if bazel_ver == module_ver:
            print_centered(f"QR: Keeping the module's .bazelversion {bazel_ver} (ref_int's floor is {ref_int_ver})")
        else:
            print_centered(f"QR: Raising .bazelversion {module_ver or '<none>'} -> {bazel_ver} in {bazelversion_dst}")
            bazelversion_dst.write_text(bazel_ver + "\n")

    for module in known.modules["target_sw"].values():
        if args.modules_to_test and module.name not in args.modules_to_test:
            print_centered(f"QR: Skipping module {module.name}")
            continue

        print_centered(f"QR: Testing module: {module.name}")

        # Prove the injected set resolves, toolchains select and tests analyse before running
        # anything; also writes the lock the test run starts from.
        gate_selection = None
        if workspace is not None:
            gate = run_resolution_gate(module, workspace=workspace, startup=startup)
            if gate.exit_code != 0:
                owner, conflicting = classify_gate_failure(
                    gate.stdout + gate.stderr, workspace.resolve() / "MODULE.bazel"
                )
                detail = f" over {', '.join(conflicting)}" if conflicting else ""
                print_centered(f"QR: {module.name}: analysis failed -- {owner}{detail}; skipping tests")
                if owner == "integration conflict":
                    print_centered(
                        "QR: ref_int's resolved set is incompatible with this module's sources. "
                        "Resolve by moving the pin or the module, not by changing the harness."
                    )
                # Recorded, not just printed: without this the aggregate job re-derives ownership
                # from total == 0 and always reports "ref_int harness defect".
                attribution[module.name] = {"owner": owner, "conflicting": conflicting}
                unit_tests_summary[module.name] = {
                    "passed": 0,
                    "failed": 0,
                    "skipped": 0,
                    "total": 0,
                    "exit_code": gate.exit_code,
                }
                continue
            gate_selection = selection_digest(workspace.resolve() / "MODULE.bazel.lock")

        unit_tests_summary[module.name] = run_unit_test_with_coverage(
            module=module, workspace=workspace, startup=startup
        )

        # The guarantee --lockfile_mode=error used to give: the lock may grow with extensions the
        # analysis-only gate never reached, but if module *selection* moved, the tests ran against
        # a resolution nobody validated.
        if gate_selection is not None:
            after = selection_digest(workspace.resolve() / "MODULE.bazel.lock")
            if after is not None and after != gate_selection:
                print_centered(
                    f"QR: {module.name}: WARNING -- module selection changed during the test run; "
                    "the tests did not run against the resolution the gate validated"
                )

        # A run that fails without executing a single test failed at configuration, toolchain or
        # dependency resolution -- a ref_int harness defect, not a finding about the module.
        # Extraction has nothing to read and would bury the real error. A non-zero exit *with*
        # tests counted is real failing tests, whose coverage data exists and is still extracted.
        if unit_tests_summary[module.name]["exit_code"] != 0 and unit_tests_summary[module.name]["total"] == 0:
            print_centered(
                f"QR: {module.name}: 0 tests executed -- ref_int harness defect; skipping coverage extraction"
            )
            # Past the gate the injected set already analysed, so a run that then executes
            # nothing is ref_int's, not an integration conflict.
            attribution[module.name] = {"owner": "ref_int harness defect", "conflicting": []}
            continue

        if "cpp" in module.metadata.langs:
            coverage_summary[f"{module.name}_cpp"] = run_cpp_coverage_extraction(
                module=module, output_path=args.coverage_output_dir, workspace=workspace, startup=startup
            )

        if "rust" in module.metadata.langs:
            if module.name in DISABLED_RUST_COVERAGE:
                print_centered(f"QR: Skipping rust coverage extraction for module {module.name} due to known issues")
                continue
            coverage_summary[f"{module.name}_rust"] = run_rust_coverage_extraction(
                module=module, output_path=args.coverage_output_dir, workspace=workspace, startup=startup
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

    # Same directory as the two summaries above, so the aggregate job reads the owner instead of
    # guessing it from a zero count.
    if attribution:
        (path_to_docs / ATTRIBUTION_NAME).write_text(json.dumps(attribution, indent=2, sort_keys=True) + "\n")
        print_centered(f"QR: Recorded failure attribution -> {path_to_docs / ATTRIBUTION_NAME}")

    # Check all exit codes and return non-zero if any test or coverage extraction failed.
    # Checked independently per dict (not zip()'d together): a module can be missing from
    # coverage_summary entirely (e.g. DISABLED_RUST_COVERAGE with no "cpp" lang), and zip()
    # truncates to the shorter of the two — silently dropping that module's unit-test result
    # from the check instead of just skipping its (nonexistent) coverage result.
    return any(result["exit_code"] != 0 for result in unit_tests_summary.values()) or any(
        result["exit_code"] != 0 for result in coverage_summary.values()
    )


if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)
    sys.exit(main())
