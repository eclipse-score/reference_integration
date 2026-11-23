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
import json
import os
import re
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest
from prepare_pipeline import BASE_JOBS, OPTIONAL_JOBS, ConfigError, Context, derive, main

UPSTREAM = "eclipse-score/reference_integration"
SHA = "a" * 40
# Not resolved: under Bazel this file is a runfiles symlink, and the workflow sits next to it there.
UNIFIED_WORKFLOW = Path(__file__).parents[2] / ".github" / "workflows" / "unified_workflow.yml"


@pytest.fixture
def known_good(tmp_path):
    path = tmp_path / "known_good.json"
    path.write_text(json.dumps({"modules": {"target_sw": {"score_baselibs": {}}, "tooling": {"score_tooling": {}}}}))
    return path


def ctx(event, ref="refs/heads/main", **kwargs):
    defaults = {"repository": UPSTREAM, "sha": SHA, "has_qnx_secrets": True, "publishing_enabled": True}
    return Context(event=event, ref=ref, **(defaults | kwargs))


@pytest.mark.parametrize(
    ("context", "level", "fresh", "docs", "release"),
    [
        (ctx("pull_request", "refs/pull/1/merge", pr_head_repository=UPSTREAM), "pr", False, True, False),
        (ctx("pull_request", "refs/pull/1/merge", pr_head_repository="someone/fork"), "pr", False, False, False),
        (ctx("merge_group", "refs/heads/gh-readonly-queue/main/pr-1"), "merge", False, False, False),
        (ctx("push"), "full", False, True, False),
        (ctx("release", "refs/tags/v1"), "full_clean", True, True, True),
        (ctx("schedule"), "full", False, False, False),
    ],
)
def test_event_matrix(known_good, context, level, fresh, docs, release):
    config = derive(context, known_good)
    assert (config.test_level, config.fresh, config.publish_docs, config.publish_release) == (
        level,
        fresh,
        docs,
        release,
    )
    assert config.known_good_mode == ("latest" if context.event == "schedule" else "pinned")


@pytest.mark.parametrize("event", ["pull_request", "merge_group", "push", "release"])
def test_inputs_are_ignored_for_repository_events(known_good, event):
    context = ctx(event, test_level="full_clean", known_good_mode="override", module_override="x@y")
    config = derive(context, known_good)
    assert config.known_good_mode == "pinned"
    assert config.module_override == ""
    if event == "pull_request":
        assert config.test_level == "pr"


@pytest.mark.parametrize(
    "context",
    [
        ctx("push", publishing_enabled=False),
        ctx("release", "refs/tags/v1", publishing_enabled=False),
        ctx("pull_request", "refs/pull/1/merge", pr_head_repository=UPSTREAM, publishing_enabled=False),
        ctx("push", repository="someone/reference_integration", has_qnx_secrets=False),
    ],
)
def test_nothing_is_published_when_disabled_or_outside_upstream(known_good, context):
    config = derive(context, known_good)
    assert not config.publish_docs
    assert not config.publish_release
    assert not {"docs-deploy", "release-publish"} & set(config.expected_jobs)


def test_publishers_are_expected_jobs(known_good):
    config = derive(ctx("release", "refs/tags/v1"), known_good)
    assert config.expected_jobs == [*BASE_JOBS, "qnx", "docs-deploy", "release-publish"]


def test_base_and_optional_jobs_are_disjoint():
    assert not set(BASE_JOBS) & set(OPTIONAL_JOBS)


def test_qnx_runs_when_secrets_are_available(known_good):
    config = derive(ctx("pull_request", "refs/pull/1/merge"), known_good)
    assert config.run_qnx
    assert config.expected_jobs == [*BASE_JOBS, "qnx"]


@pytest.mark.parametrize("repository", [UPSTREAM, "someone/reference_integration"])
def test_pr_without_secrets_skips_qnx(known_good, repository):
    config = derive(ctx("pull_request", "refs/pull/1/merge", repository=repository, has_qnx_secrets=False), known_good)
    assert not config.run_qnx
    assert "qnx" not in config.expected_jobs
    assert config.notices


@pytest.mark.parametrize("event", ["merge_group", "push", "release", "schedule"])
def test_missing_secrets_fail_from_merge_level_in_upstream(known_good, event):
    with pytest.raises(ConfigError, match="QNX is mandatory"):
        derive(ctx(event, has_qnx_secrets=False), known_good)


def test_missing_secrets_in_fork_repository_skip_qnx(known_good):
    config = derive(ctx("push", repository="someone/reference_integration", has_qnx_secrets=False), known_good)
    assert not config.run_qnx
    assert not config.publish_docs


def test_dispatch_inputs(known_good):
    config = derive(ctx("workflow_dispatch", test_level="pr", known_good_mode="pinned"), known_good)
    assert (config.test_level, config.known_good_mode) == ("pr", "pinned")


@pytest.mark.parametrize(
    "override",
    [f"score_baselibs@{SHA}", f"score_tooling@https://github.com/eclipse-score/tooling.git@{SHA}"],
)
def test_valid_override(known_good, override):
    config = derive(ctx("workflow_dispatch", known_good_mode="override", module_override=override), known_good)
    assert config.module_override == override


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"test_level": "bogus"}, "invalid test_level"),
        ({"known_good_mode": "bogus"}, "invalid known_good_mode"),
        ({"known_good_mode": "latest", "module_override": f"score_baselibs@{SHA}"}, "only valid with"),
        ({"known_good_mode": "override", "module_override": f"unknown@{SHA}"}, "not a module"),
        ({"known_good_mode": "override", "module_override": "score_baselibs@abc;rm -rf /"}, "must be"),
        ({"known_good_mode": "override", "module_override": "score_baselibs@abc1234"}, "must be"),
        ({"known_good_mode": "override", "module_override": f"score_baselibs@{SHA}\n"}, "must be"),
    ],
)
def test_invalid_dispatch_inputs(known_good, kwargs, message):
    with pytest.raises(ConfigError, match=message):
        derive(ctx("workflow_dispatch", **kwargs), known_good)


@pytest.mark.parametrize(
    "context",
    [
        ctx("push", "refs/heads/feature"),
        ctx("push", "refs/tags/v1"),
        ctx("pull_request_target"),
        ctx("issue_comment"),
    ],
)
def test_unsupported_triggers(known_good, context):
    with pytest.raises(ConfigError, match="not a supported pipeline trigger"):
        derive(context, known_good)


def test_main_writes_outputs_and_summary(tmp_path, known_good, capsys):
    output, summary = tmp_path / "output", tmp_path / "summary"
    env = {
        "EVENT": "pull_request",
        "REPOSITORY": UPSTREAM,
        "REF": "refs/pull/1/merge",
        "SHA": SHA,
        "HAS_QNX_SECRETS": "false",
        "KNOWN_GOOD": str(known_good),
        "GITHUB_OUTPUT": str(output),
        "GITHUB_STEP_SUMMARY": str(summary),
    }
    assert main(env) == 0
    outputs = dict(line.split("=", 1) for line in output.read_text().splitlines())
    assert outputs["test_level"] == "pr"
    assert outputs["run_qnx"] == "false"
    assert json.loads(outputs["expected_jobs"]) == list(BASE_JOBS)
    assert json.loads(outputs["optional_jobs"]) == list(OPTIONAL_JOBS)
    assert "| Test level | `pr` |" in summary.read_text()
    assert "::notice::" in capsys.readouterr().out


def test_main_reports_errors(known_good, capsys):
    assert main({"EVENT": "push", "REF": "refs/heads/feature", "KNOWN_GOOD": str(known_good)}) == 1
    assert "::error::push to refs/heads/feature" in capsys.readouterr().out


def test_context_from_env_defaults():
    context = Context.from_env({"EVENT": "schedule"})
    assert context == Context(event="schedule", repository="", ref="", sha="")


def _job_needs(workflow: str, job: str) -> set[str]:
    """The block-list `needs` of a top-level job (PyYAML is not a dependency of this test)."""
    block = re.search(rf"^  {re.escape(job)}:\n(.*?)(?=^  \S|\Z)", workflow, re.M | re.S)
    assert block, f"job '{job}' not found"
    needs = re.search(r"^    needs:\n((?:^      - .*\n)+)", block.group(1), re.M)
    assert needs, f"job '{job}' has no block-list needs"
    return {line.strip()[2:].strip() for line in needs.group(1).splitlines()}


def _job_ids(workflow: str) -> set[str]:
    jobs = workflow[workflow.index("\njobs:\n") :]
    return set(re.findall(r"^  ([A-Za-z0-9_-]+):\s*$", jobs, re.M))


def test_status_job_needs_exactly_the_known_jobs():
    workflow = UNIFIED_WORKFLOW.read_text()
    assert _job_needs(workflow, "status") == {"prepare", *BASE_JOBS, *OPTIONAL_JOBS}


def test_every_pipeline_job_is_known():
    workflow = UNIFIED_WORKFLOW.read_text()
    assert _job_ids(workflow) == {"prepare", "status", *BASE_JOBS, *OPTIONAL_JOBS}


def _status_script(workflow: str) -> str:
    """The bash body of the status job's "Evaluate job results" step."""
    step = re.search(
        r"- name: Evaluate job results\n.*?^        run: \|\n((?:^          .*\n|^\n)+)", workflow, re.M | re.S
    )
    assert step, "status step not found"
    return textwrap.dedent(step.group(1))


@pytest.mark.skipif(not (shutil.which("bash") and shutil.which("jq")), reason="needs bash and jq")
@pytest.mark.parametrize(
    ("results", "succeeds"),
    [
        ({}, True),
        ({"linux": "failure"}, False),
        ({"docs": "skipped"}, False),
        ({"qnx": "skipped", "docs-deploy": "skipped", "release-publish": "skipped"}, True),
        ({"qnx": "failure"}, False),
    ],
)
def test_status_job_evaluation(tmp_path, results, succeeds):
    workflow = UNIFIED_WORKFLOW.read_text()
    needs = {job: {"result": "success"} for job in _job_needs(workflow, "status")}
    needs.update({job: {"result": result} for job, result in results.items()})
    expected = [*BASE_JOBS] + [job for job in OPTIONAL_JOBS if job not in results]
    # bash and jq may live outside /usr/bin (Homebrew, Nix): put their directories first.
    tool_dirs = [os.path.dirname(shutil.which(tool)) for tool in ("bash", "jq")]
    env = {
        "PATH": os.pathsep.join(dict.fromkeys([*tool_dirs, "/usr/bin", "/bin"])),
        "NEEDS": json.dumps(needs),
        "EXPECTED": json.dumps(expected),
        "OPTIONAL": json.dumps(OPTIONAL_JOBS),
        "PREPARE_RESULT": "success",
        **{name: "x" for name in ("EVENT", "LEVEL", "MODE", "SHA")},
        "GITHUB_STEP_SUMMARY": str(tmp_path / "summary.md"),
    }
    proc = subprocess.run(["bash", "-c", _status_script(workflow)], env=env, capture_output=True, text=True)
    assert (proc.returncode == 0) == succeeds, proc.stdout + proc.stderr
