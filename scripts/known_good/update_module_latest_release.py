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
"""Pin every known_good.json module to its latest Bazel registry release and report the versions.

For each module (target_sw and tooling, pinned ones included) the script looks up the
latest version in the Bazel registries of .bazelrc (pre-releases count, yanked versions
do not), resolves its release tag and date, and counts the commits on the module's
branch since that tag. The report is one markdown table with all modules; commit counts
from BOLD_COMMITS on are bold.

Usage:
  python3 scripts/known_good/update_module_latest_release.py \
      [--known-good known_good.json] [--apply] [--report pre_release_report.md]

Without --apply only the report is produced. With --apply every module gets
``"version": "<latest>"`` instead of its hash; regenerate the Bazel files and the
lockfile afterwards (see .github/skills/pre-release/SKILL.md).

Environment:
  GITHUB_TOKEN or GITHUB_PAT for the GitHub API (release dates, commit counts).
"""

from __future__ import annotations

import argparse
import datetime as dt
import functools
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

try:
    from known_good.models.known_good import load_known_good
except ImportError:
    _HERE = str(Path(__file__).resolve().parent)
    if _HERE not in sys.path:
        sys.path.insert(0, _HERE)
    from models.known_good import load_known_good  # noqa: E402

# Same order as the --registry flags in .bazelrc: the first registry that knows a module wins.
REGISTRIES = (
    "https://raw.githubusercontent.com/eclipse-score/bazel_registry/main",
    "https://bcr.bazel.build",
)
API = "https://api.github.com"
BOLD_COMMITS = 10
TAG_URL = re.compile(r"/refs/tags/(.+?)\.(?:tar\.gz|zip|tgz)$")


@dataclass
class Release:
    module: str
    group: str
    slug: str
    branch: str
    current: str
    version: str | None = None
    tag: str | None = None
    date: dt.date | None = None
    commits: int | None = None
    error: str | None = None
    current_date: dt.date | None = None
    current_tag: str | None = None
    current_ref: str | None = None
    delta: tuple[int, int] | None = None
    head_sha: str | None = None
    head_tag: str | None = None
    head_date: dt.date | None = None


def http_json(url: str, *, github: bool = False) -> dict | list | None:
    """GET a JSON document; None on 404."""
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"} if github else {})
    if github and (token := os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PAT")):
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def version_key(version: str) -> tuple:
    """Semver ordering: numeric parts numerically, a pre-release before its release."""
    version = version.split("+", 1)[0]
    core, _, pre = version.partition("-")

    def ident(part: str) -> tuple:
        return (0, int(part), "") if part.isdigit() else (1, 0, part)

    core_key = tuple(ident(p) for p in core.split("."))
    pre_key = (1,) if not pre else (0, *(ident(p) for p in pre.split(".")))
    return core_key, pre_key


def latest_version(metadata: dict) -> str | None:
    yanked = set(metadata.get("yanked_versions") or {})
    versions = [v for v in metadata.get("versions", []) if v not in yanked]
    return max(versions, key=version_key) if versions else None


def source_tag(registry: str, module: str, version: str) -> str | None:
    """Release tag of a registry version; None if the registry does not have it."""
    source = http_json(f"{registry}/modules/{module}/{version}/source.json")
    if source is None:
        return None
    match = TAG_URL.search(source.get("url", ""))
    return match.group(1) if match else f"v{version}"


def registry_release(module: str) -> tuple[str, str] | None:
    """(version, tag) of the latest release in the first registry that has the module."""
    for registry in REGISTRIES:
        metadata = http_json(f"{registry}/modules/{module}/metadata.json")
        if not metadata or not (version := latest_version(metadata)):
            continue
        return version, source_tag(registry, module, version) or f"v{version}"
    return None


def parse_date(stamp: str) -> dt.date:
    return dt.datetime.fromisoformat(stamp.replace("Z", "+00:00")).date()


def commit_date(slug: str, ref: str) -> dt.date:
    commit = http_json(f"{API}/repos/{slug}/commits/{ref}", github=True)
    if not commit:
        raise RuntimeError(f"{ref} not found in {slug}")
    return parse_date(commit["commit"]["committer"]["date"])


def release_date(slug: str, tag: str) -> dt.date:
    release = http_json(f"{API}/repos/{slug}/releases/tags/{tag}", github=True)
    if release and release.get("published_at"):
        return parse_date(release["published_at"])
    return commit_date(slug, tag)


@functools.cache
def repo_tags(slug: str) -> list[tuple[str, str]]:
    """(name, commit sha) of every tag of the repository."""
    tags, page = [], 1
    while batch := http_json(f"{API}/repos/{slug}/tags?per_page=100&page={page}", github=True):
        tags += [(t["name"], t["commit"]["sha"]) for t in batch]
        page += 1
    return tags


def tag_at(slug: str, sha: str) -> str | None:
    """Highest tag pointing exactly at the commit; None if the commit is untagged."""
    tags = [name for name, tag_sha in repo_tags(slug) if tag_sha.startswith(sha)]
    return max(tags, key=lambda t: version_key(t.removeprefix("v")), default=None)


def pinned_release(module) -> tuple[str | None, dt.date | None]:
    """(tag, date) of the pinned version or hash; tag is None for an untagged hash."""
    if module.version:
        tag = next(
            (t for registry in REGISTRIES if (t := source_tag(registry, module.name, module.version))),
            f"v{module.version}",
        )
        return tag, release_date(module.owner_repo, tag)
    if module.hash:
        if tag := tag_at(module.owner_repo, module.hash):
            return tag, release_date(module.owner_repo, tag)
        return None, commit_date(module.owner_repo, module.hash)
    return None, None


def compare_counts(slug: str, base: str, head: str) -> tuple[int, int]:
    """(ahead_by, behind_by) of head compared to base."""
    compare = http_json(f"{API}/repos/{slug}/compare/{base}...{head}", github=True)
    if not compare:
        raise RuntimeError(f"cannot compare {base}...{head} in {slug}")
    return compare["ahead_by"], compare["behind_by"]


def head_commit(slug: str, branch: str) -> tuple[str, dt.date]:
    commit = http_json(f"{API}/repos/{slug}/commits/{branch}", github=True)
    if not commit:
        raise RuntimeError(f"branch {branch} not found in {slug}")
    return commit["sha"], parse_date(commit["commit"]["committer"]["date"])


def collect(known_good_path: Path) -> list[Release]:
    known_good = load_known_good(known_good_path)
    releases = []
    for group, modules in known_good.modules.items():
        for module in modules.values():
            current = module.version or (module.hash[:8] if module.hash else "?")
            entry = Release(module.name, group, module.owner_repo, module.branch, current)
            releases.append(entry)
            try:
                found = registry_release(module.name)
                if not found:
                    entry.error = "not found in any Bazel registry"
                    continue
                entry.version, entry.tag = found
                entry.date = release_date(entry.slug, entry.tag)
                entry.head_sha, entry.head_date = head_commit(entry.slug, entry.branch)
                entry.head_tag = tag_at(entry.slug, entry.head_sha)
                if entry.head_tag:
                    entry.head_date = release_date(entry.slug, entry.head_tag)
                entry.commits = compare_counts(entry.slug, entry.tag, entry.head_sha)[0]
                entry.current_tag, entry.current_date = pinned_release(module)
                if module.hash and entry.current_tag:
                    entry.current = entry.current_tag.removeprefix("v")
                entry.current_ref = entry.current_tag or module.hash
                if entry.current_ref:
                    entry.delta = compare_counts(entry.slug, entry.current_ref, entry.tag)
            except Exception as e:  # noqa: BLE001
                entry.error = str(e)
            print(
                f"{entry.module}: {entry.current} -> {entry.version or '-'}"
                f" ({entry.tag or '-'}, {entry.date or '-'}, {entry.commits if entry.commits is not None else '-'}"
                f" commits since){' ERROR: ' + entry.error if entry.error else ''}",
                file=sys.stderr,
            )
    return releases


def apply_versions(path: Path, releases: list[Release]) -> None:
    """Swap hash/version for the new version in place; leave every other key untouched."""
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    for r in releases:
        if not r.version:
            continue
        modules = data["modules"][r.group]
        modules[r.module] = {
            ("version" if key == "hash" else key): (r.version if key in ("hash", "version") else value)
            for key, value in modules[r.module].items()
        }
    data["timestamp"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    path.write_text(json.dumps(data, indent=4) + ("\n" if text.endswith("\n") else ""), encoding="utf-8")


def render(releases: list[Release], today: dt.date) -> str:
    def ref_cell(r: Release, label: str, tag: str | None, date: dt.date | None) -> str:
        if not tag:
            return f"`{label}` ({date or '?'})"
        return f"[{label}](https://github.com/{r.slug}/releases/tag/{tag}) ({date or '?'})"

    def now_cell(r: Release) -> str:
        if not r.version:
            return "-"
        cell = ref_cell(r, r.version, r.tag, r.date)
        if not r.delta:
            return cell
        ahead, behind = r.delta
        text = f"+{ahead}/-{behind}" if ahead and behind else f"-{behind}" if behind else f"+{ahead}"
        if behind:
            text = f"**{text}**"
        return f"{cell} [{text}](https://github.com/{r.slug}/compare/{r.current_ref}...{r.tag})"

    def head_cell(r: Release) -> str:
        if r.error:
            return f"Error: {r.error}"
        if r.commits is None or not r.head_sha:
            return "-"
        label = r.head_tag.removeprefix("v") if r.head_tag else r.head_sha[:8]
        count = f"**{r.commits}**" if r.commits >= BOLD_COMMITS else str(r.commits)
        link = f"https://github.com/{r.slug}/compare/{r.tag}...{r.head_sha}"
        return f"{ref_cell(r, label, r.head_tag, r.head_date)} [{count}]({link})"

    lines = [
        f"<!-- generated by scripts/known_good/update_module_latest_release.py on {today} -->",
        "### Module versions",
        "",
        (
            "- **Before:** release or commit pinned in `known_good.json` so far (release or commit date);"
            " a commit is shown as the release whose tag points at it, if there is one."
        ),
        (
            "- **Now:** latest registry release this PR switches to (release date), followed by the commits"
            " it gains (+) or drops (-, bold) compared to Before."
        ),
        (
            "- **Head:** head commit of the module's branch, shown as release if a tag points at it"
            " (commit or release date), followed by the commits since the Now release,"
            f" bold from {BOLD_COMMITS} on."
        ),
        "- **OK/NOK:** set by hand.",
        "",
        "All commit numbers link to the commit list.",
        "",
        "| Module | Group | Before | Now | Head | OK/NOK |",
        "|---|---|---|---|---|---|",
    ]
    for r in releases:
        lines.append(
            f"| {r.module} | {r.group} | {ref_cell(r, r.current, r.current_tag, r.current_date)}"
            f" | {now_cell(r)} | {head_cell(r)} | |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--known-good", default="known_good.json", type=Path)
    parser.add_argument("--apply", action="store_true", help="Write the latest versions into --known-good")
    parser.add_argument("--report", type=Path, help="Write the markdown report (PR body section) here")
    parser.add_argument("--today", type=dt.date.fromisoformat, default=dt.date.today(), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    releases = collect(args.known_good)
    report = render(releases, args.today)
    if args.report:
        args.report.write_text(report, encoding="utf-8")
    else:
        print(report)
    if args.apply:
        apply_versions(args.known_good, releases)
    errors = [r for r in releases if r.error]
    return 2 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
