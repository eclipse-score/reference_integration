#!/usr/bin/env python3
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
"""Derive the configuration of the unified CI pipeline from the triggering event.

Run by the ``prepare`` job of .github/workflows/unified_workflow.yml. Reads the event context
from environment variables (set from ``${{ }}`` expressions in the workflow, never interpolated
into shell code), writes the job outputs to ``$GITHUB_OUTPUT`` and a table to
``$GITHUB_STEP_SUMMARY``.

Rules:
- pull_request, merge_group, push and release derive level and known_good mode from the event
  and ignore all workflow inputs. This only protects against inputs: for pull_request and
  merge_group this script and the workflows are taken from the candidate commit, so a change can
  edit them like any other file. That grants nothing extra, because fork pull requests run with a
  read-only token and without secrets, and branch authors already have write access.
- schedule and workflow_dispatch (on_schedule.yml) honor the inputs, after validating them.
- QNX runs whenever its secrets are available. From the merge level up it is mandatory in the
  upstream repository, so missing secrets fail instead of silently dropping QNX.
- Publishing depends only on the event and the repository, never on the level or an input, and
  only happens while PUBLISHING_ENABLED is "true" (set in unified_workflow.yml). Documentation is
  published for push to main, releases and pull requests from branches of the upstream
  repository (preview under pr-<number>/); release assets for releases only.

Standard library only, so it runs on a bare runner before any setup.
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

UPSTREAM_REPOSITORY = "eclipse-score/reference_integration"
LEVELS = ("pr", "merge", "full", "full_clean")
MODES = ("pinned", "latest", "override")
# Used with fullmatch: `$` would also accept a trailing newline, which would corrupt $GITHUB_OUTPUT.
OVERRIDE_RE = re.compile(r"([A-Za-z0-9_]+)@(https://[A-Za-z0-9.-]+/[A-Za-z0-9._/-]+\.git@)?([0-9a-f]{40})")

# Jobs of unified_workflow.yml that every run requires. The status job's `needs` must be exactly
# prepare + BASE_JOBS + OPTIONAL_JOBS; tests/test_prepare_pipeline.py enforces that.
BASE_JOBS = (
    "common-checks",
    "internal-tests",
    "known-good",
    "gate",
    "resolve",
    "module-tests",
    "linux",
    "linux-target",
    "ebclfsa",
    "autosd",
    "integration-tests",
    "docs",
)
# Jobs that run only for some events. Every other dependency of the status job must be in
# BASE_JOBS; the status job fails on a job that is in neither list.
OPTIONAL_JOBS = ("qnx", "docs-deploy", "release-publish")


class ConfigError(Exception):
    """The event or the inputs do not describe a valid pipeline run."""


@dataclass(frozen=True)
class Context:
    event: str
    repository: str
    ref: str
    sha: str
    pr_head_repository: str = ""
    test_level: str = ""
    known_good_mode: str = ""
    module_override: str = ""
    has_qnx_secrets: bool = False
    publishing_enabled: bool = False
    upstream_repository: str = UPSTREAM_REPOSITORY

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> Context:
        return cls(
            event=env.get("EVENT", ""),
            repository=env.get("REPOSITORY", ""),
            ref=env.get("REF", ""),
            sha=env.get("SHA", ""),
            pr_head_repository=env.get("PR_HEAD_REPOSITORY", ""),
            test_level=env.get("IN_LEVEL", ""),
            known_good_mode=env.get("IN_MODE", ""),
            module_override=env.get("IN_OVERRIDE", ""),
            has_qnx_secrets=env.get("HAS_QNX_SECRETS", "") == "true",
            publishing_enabled=env.get("PUBLISHING_ENABLED", "") == "true",
            upstream_repository=env.get("UPSTREAM_REPOSITORY") or UPSTREAM_REPOSITORY,
        )


@dataclass(frozen=True)
class Config:
    test_level: str
    known_good_mode: str
    module_override: str
    run_qnx: bool
    fresh: bool
    publish_docs: bool
    publish_release: bool
    expected_jobs: list[str]
    notices: list[str] = field(default_factory=list)

    def outputs(self) -> dict[str, str]:
        return {
            "test_level": self.test_level,
            "known_good_mode": self.known_good_mode,
            "module_override": self.module_override,
            "run_qnx": _flag(self.run_qnx),
            "fresh": _flag(self.fresh),
            "publish_docs": _flag(self.publish_docs),
            "publish_release": _flag(self.publish_release),
            "expected_jobs": json.dumps(self.expected_jobs, separators=(",", ":")),
            "optional_jobs": json.dumps(OPTIONAL_JOBS, separators=(",", ":")),
        }


def _flag(value: object) -> str:
    """GitHub Actions style boolean output."""
    return "true" if value else "false"


def known_good_modules(known_good: Path) -> set[str]:
    """Names of all modules in known_good.json, across groups."""
    data = json.loads(known_good.read_text())
    return {name for group in data.get("modules", {}).values() for name in group}


def _level_and_mode(ctx: Context, known_good: Path) -> tuple[str, str, str]:
    """(level, mode, override) for the event; inputs count for schedule/workflow_dispatch only."""
    if ctx.event == "pull_request":
        return "pr", "pinned", ""
    if ctx.event == "merge_group":
        return "merge", "pinned", ""
    if ctx.event == "push":
        if ctx.ref == "refs/heads/main":
            return "full", "pinned", ""
        raise ConfigError(f"push to {ctx.ref} is not a supported pipeline trigger")
    if ctx.event == "release":
        return "full_clean", "pinned", ""
    if ctx.event not in ("schedule", "workflow_dispatch"):
        raise ConfigError(f"event '{ctx.event}' is not a supported pipeline trigger")

    level = ctx.test_level or "full"
    mode = ctx.known_good_mode or "latest"
    if level not in LEVELS:
        raise ConfigError(f"invalid test_level '{level}'")
    if mode not in MODES:
        raise ConfigError(f"invalid known_good_mode '{mode}'")
    if mode != "override":
        if ctx.module_override:
            raise ConfigError("module_override is only valid with known_good_mode=override")
        return level, mode, ""

    match = OVERRIDE_RE.fullmatch(ctx.module_override)
    if not match:
        raise ConfigError(
            "module_override must be <module>@<40-hex sha> or <module>@https://<host>/<path>.git@<40-hex sha>"
        )
    name = match.group(1)
    if name not in known_good_modules(known_good):
        raise ConfigError(f"module_override names '{name}', which is not a module in known_good.json")
    return level, mode, ctx.module_override


def derive(ctx: Context, known_good: Path = Path("known_good.json")) -> Config:
    level, mode, override = _level_and_mode(ctx, known_good)
    upstream = ctx.repository == ctx.upstream_repository
    notices: list[str] = []

    run_qnx = ctx.has_qnx_secrets
    if not run_qnx:
        if LEVELS.index(level) >= LEVELS.index("merge") and upstream:
            raise ConfigError(
                f"QNX secrets are not available, but QNX is mandatory for level '{level}' in {ctx.upstream_repository}"
            )
        notices.append("QNX secrets are not available to this run; skipping the QNX build.")

    publish = ctx.publishing_enabled and upstream
    same_repo_pr = ctx.event == "pull_request" and ctx.pr_head_repository == ctx.repository
    publish_docs = publish and (ctx.event in ("push", "release") or same_repo_pr)
    publish_release = publish and ctx.event == "release"
    if ctx.event == "pull_request" and publish and not same_repo_pr:
        notices.append(
            "Pull requests from forks get no deployed documentation preview (read-only token); "
            "download the github-pages-<sha> artifact of this run instead."
        )

    expected = list(BASE_JOBS)
    if run_qnx:
        expected.append("qnx")
    if publish_docs:
        expected.append("docs-deploy")
    if publish_release:
        expected.append("release-publish")

    return Config(
        test_level=level,
        known_good_mode=mode,
        module_override=override,
        run_qnx=run_qnx,
        fresh=level == "full_clean",
        publish_docs=publish_docs,
        publish_release=publish_release,
        expected_jobs=expected,
        notices=notices,
    )


def summary(ctx: Context, config: Config) -> str:
    override = f" (`{config.module_override}`)" if config.module_override else ""
    rows = [
        ("Event", f"`{ctx.event}`"),
        ("Test level", f"`{config.test_level}`"),
        ("known_good mode", f"`{config.known_good_mode}`{override}"),
        ("Commit", f"`{ctx.sha}`"),
        ("QNX", _flag(config.run_qnx)),
        ("Fresh build", _flag(config.fresh)),
        ("Publish docs / release", f"{_flag(config.publish_docs)} / {_flag(config.publish_release)}"),
    ]
    lines = ["## Pipeline configuration", "", "| Setting | Value |", "|---|---|"]
    lines += [f"| {name} | {value} |" for name, value in rows]
    return "\n".join(lines) + "\n"


def main(env: Mapping[str, str] = os.environ) -> int:
    ctx = Context.from_env(env)
    try:
        config = derive(ctx, Path(env.get("KNOWN_GOOD", "known_good.json")))
    except ConfigError as error:
        print(f"::error::{error}")
        return 1

    for notice in config.notices:
        print(f"::notice::{notice}")
    outputs = "".join(f"{key}={value}\n" for key, value in config.outputs().items())
    print(outputs, end="")
    if output_file := env.get("GITHUB_OUTPUT"):
        with open(output_file, "a", encoding="utf-8") as handle:
            handle.write(outputs)
    if summary_file := env.get("GITHUB_STEP_SUMMARY"):
        with open(summary_file, "a", encoding="utf-8") as handle:
            handle.write(summary(ctx, config))
    return 0


if __name__ == "__main__":
    sys.exit(main())
