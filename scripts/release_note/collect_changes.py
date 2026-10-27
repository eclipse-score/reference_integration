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
"""Collect the evidence for the platform-level "Changes to the Platform" chapter.

Platform-level means: changes of this repository (reference_integration), and
module changes that matter for integrators. The latter come from the modules' own
release notes (their "breaking" and "new features" sections) together with hints
where this repository uses an affected flag, label or target. Detailed per-module
PR lists are only produced on request (``--module-prs``).

Examples:
    python3 scripts/release_note/collect_changes.py --release v0.9.0 --origin v0.8.0 --output changes.md
    python3 scripts/release_note/collect_changes.py --release v0.10.0 --origin v0.9.0 --module-prs --module score_logging
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import generate_release_note as grn

API = "https://api.github.com"

BOT_AUTHORS = ("[bot]", "dependabot", "renovate", "eclipse-score-bot")
NOISE_TITLE = re.compile(r"^(chore|build|ci)\(deps\)|\bbump\b|update dependency|^update .* to v?\d", re.I)
BREAKING_TITLE = re.compile(r"^\w+(\([^)]*\))?!:|\bbreaking\b", re.I)
FEATURE_TITLE = re.compile(r"^(feat|feature)(\([^)]*\))?:|^add(ed)?\b|^introduce|^implement|^support", re.I)
CLOSES = re.compile(r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)", re.I)


def api(path: str, params: dict[str, Any] | None = None) -> Any:
    url = f"{API}{path}" + (f"?{urllib.parse.urlencode(params)}" if params else "")
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if token := os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PAT"):
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def paged(path: str, params: dict[str, Any] | None = None, key: str | None = None) -> list[Any]:
    items: list[Any] = []
    for page in range(1, 30):
        data = api(path, {**(params or {}), "per_page": 100, "page": page})
        batch = data[key] if key else data
        items += batch
        if len(batch) < 100:
            break
    return items


@dataclass
class Issue:
    number: int
    title: str
    labels: list[str]
    url: str


@dataclass
class PullRequest:
    number: int
    title: str
    labels: list[str]
    author: str
    url: str
    body: str
    issues: list[Issue] = field(default_factory=list)

    @property
    def is_noise(self) -> bool:
        return any(b in self.author.lower() for b in BOT_AUTHORS) or bool(NOISE_TITLE.search(self.title))

    @property
    def kind(self) -> str:
        labels = " ".join(self.labels).lower() + " " + " ".join(l for i in self.issues for l in i.labels).lower()
        if "breaking" in labels or BREAKING_TITLE.search(self.title) or "BREAKING CHANGE" in self.body:
            return "breaking"
        if re.search(r"feature|enhancement|\bfeat\b", labels) or FEATURE_TITLE.search(self.title):
            return "feature"
        return "other"


def repo_slug(repo_url: str) -> str:
    return repo_url.removeprefix("https://github.com/")


def ref_date(slug: str, ref: str) -> str:
    return api(f"/repos/{slug}/commits/{ref}")["commit"]["committer"]["date"]


def merged_pulls(slug: str, start: str, end: str) -> list[dict]:
    """Closed PRs merged in [start, end]; sorted by update time so paging stops once PRs predate the window."""
    found: list[dict] = []
    for page in range(1, 60):
        batch = api(
            f"/repos/{slug}/pulls",
            {"state": "closed", "sort": "updated", "direction": "desc", "per_page": 100, "page": page},
        )
        found += [p for p in batch if p.get("merged_at") and start <= p["merged_at"] <= end]
        if len(batch) < 100 or batch[-1]["updated_at"] < start:
            break
    return found


def load_issue(slug: str, number: int) -> Issue | None:
    try:
        data = api(f"/repos/{slug}/issues/{number}")
    except urllib.error.HTTPError:
        return None
    return Issue(number, data["title"], [l["name"] for l in data["labels"]], data["html_url"])


def collect_prs(slug: str, base: str, head: str) -> list[PullRequest]:
    prs = []
    for data in sorted(merged_pulls(slug, ref_date(slug, base), ref_date(slug, head)), key=lambda p: p["merged_at"]):
        pr = PullRequest(
            data["number"],
            data["title"],
            [l["name"] for l in data["labels"]],
            data["user"]["login"],
            data["html_url"],
            data.get("body") or "",
        )
        for issue_number in dict.fromkeys(int(n) for n in CLOSES.findall(pr.body)):
            if issue := load_issue(slug, issue_number):
                pr.issues.append(issue)
        prs.append(pr)
    return prs


def collect_prs_by_commits(slug: str, base: str, head: str) -> list[PullRequest]:
    """PRs of a small repository via the commit range (squash commits end in "(#N)")."""
    numbers: dict[int, None] = {}
    for commit in paged(f"/repos/{slug}/compare/{base}...{head}", key="commits"):
        subject = commit["commit"]["message"].splitlines()[0]
        if match := re.search(r"\(#(\d+)\)\s*$", subject):
            numbers.setdefault(int(match.group(1)))
    prs = []
    for number in numbers:
        try:
            data = api(f"/repos/{slug}/pulls/{number}")
        except urllib.error.HTTPError:
            continue
        pr = PullRequest(
            number,
            data["title"],
            [l["name"] for l in data["labels"]],
            data["user"]["login"],
            data["html_url"],
            data.get("body") or "",
        )
        for issue_number in dict.fromkeys(int(n) for n in CLOSES.findall(pr.body)):
            if issue := load_issue(slug, issue_number):
                pr.issues.append(issue)
        prs.append(pr)
    return prs


def closed_issues(slug: str, base: str, head: str, linked: set[int]) -> list[Issue]:
    start, end = ref_date(slug, base), ref_date(slug, head)
    issues = paged(f"/repos/{slug}/issues", {"state": "closed", "since": start})
    return [
        Issue(i["number"], i["title"], [l["name"] for l in i["labels"]], i["html_url"])
        for i in issues
        if "pull_request" not in i and start <= i["closed_at"] <= end and i["number"] not in linked
    ]


def _line(pr: PullRequest, with_body: bool) -> str:
    labels = f" [{', '.join(pr.labels)}]" if pr.labels else ""
    text = f"- #{pr.number} {pr.title}{labels} ({pr.url})"
    for issue in pr.issues:
        issue_labels = f" [{', '.join(issue.labels)}]" if issue.labels else ""
        text += f"\n    - closes #{issue.number} {issue.title}{issue_labels} ({issue.url})"
    if with_body and pr.body.strip():
        excerpt = re.sub(r"\s+", " ", re.sub(r"<!--.*?-->", "", pr.body, flags=re.S)).strip()[:240]
        if excerpt:
            text += f"\n    - body: {excerpt}"
    return text


def render_module(name: str, slug: str, base: str, head: str, own_repo: bool = False) -> str:
    """own_repo: this repository; every PR is listed (version bumps and tooling updates are platform-level here)."""
    prs = collect_prs_by_commits(slug, base, head) if own_repo else collect_prs(slug, base, head)
    relevant = prs if own_repo else [p for p in prs if not p.is_noise]
    out = [
        f"## {name}: {base} -> {head} ({slug}, {len(prs)} merged PRs, {len(prs) - len(relevant)} bot/dependency PRs omitted)",
        "",
    ]
    for kind, title in (
        ("breaking", "Breaking candidates"),
        ("feature", "Feature candidates"),
        ("other", "Other merged PRs"),
    ):
        group = [p for p in relevant if p.kind == kind]
        out += [f"### {title} ({len(group)})"] + [_line(p, with_body=kind != "other") for p in group] + [""]
    linked = {i.number for p in prs for i in p.issues}
    extra = closed_issues(slug, base, head, linked)
    out += [f"### Closed issues in the release window, not linked to a PR ({len(extra)})"]
    out += [
        f"- #{i.number} {i.title}" + (f" [{', '.join(i.labels)}]" if i.labels else "") + f" ({i.url})" for i in extra
    ]
    return "\n".join(out) + "\n"


SECTION_HEADING = re.compile(r"^(#{2,4})\s+(.*?)\s*$", re.M)
WANTED_SECTION = re.compile(r"breaking|deprecat|incompatible|new feature|features", re.I)
IMPACT_PATHS = [
    "known_good.json",
    ".bazelrc",
    "bazel_common",
    "patches",
    "images",
    "showcases",
    "MODULE.bazel",
    "feature_integration_tests",
    "platform_integration_tests",
]


def release_sections(body: str) -> list[tuple[str, str]]:
    """(heading, text) of the breaking / new-feature sections of a GitHub release body."""
    marks = list(SECTION_HEADING.finditer(body))
    sections = []
    for i, mark in enumerate(marks):
        if WANTED_SECTION.search(mark.group(2)):
            end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
            sections.append((mark.group(2), body[mark.end() : end].strip()))
    return sections


def impact_hints(text: str, module_key: str) -> list[str]:
    """Lines in this repository that mention an identifier named in backticks and belong to the module."""
    short = module_key.removeprefix("score_")
    hints = []
    seen: set[tuple[str, str]] = set()
    for token in dict.fromkeys(re.findall(r"`([^`\s]{8,})`", text)):
        if not re.search(r"[/:_.-]", token):
            continue  # plain words like `result` match everywhere
        needles = {token, re.split(r"[:/]", token)[-1]} if re.search(r"[:/]", token) else {token}
        for needle in (n for n in needles if len(n) >= 8):
            result = subprocess.run(
                ["git", "grep", "-n", "-F", "-I", needle, "--", *IMPACT_PATHS],
                cwd=grn.REPO_ROOT,
                capture_output=True,
                text=True,
            )
            for line in result.stdout.splitlines():
                path = line.split(":", 1)[0]
                if (
                    short in line.lower() and (needle, path) not in seen
                ):  # one hint per file, line must concern this module
                    seen.add((needle, path))
                    hints.append(f"`{needle}` is used in {line[:160]}")
    return hints[:8]


def render_release_notes(name: str, slug: str, old: grn.Entry, new: grn.Entry) -> str:
    start, end = ref_date(slug, old.ref), ref_date(slug, new.ref)
    releases = [
        r
        for r in paged(f"/repos/{slug}/releases")
        if r.get("published_at")
        and start < r["published_at"] <= end[:10] + "T23:59:59Z"
        and not r["draft"]
        and r["tag_name"] != old.tag  # the origin release is already part of the previous platform release
    ]
    out = [f"## {name}: {old.version_label} -> {new.version_label} ({slug}), module release notes", ""]
    if not releases:
        out += ["No GitHub releases in this range.", ""]
    for release in sorted(releases, key=lambda r: r["published_at"]):
        out += [f"### {release['tag_name']} ({release['published_at'][:10]}, {release['html_url']})", ""]
        sections = release_sections(release.get("body") or "")
        if not sections:
            out += ["No breaking/new-feature sections found in the release text.", ""]
        for heading, text in sections:
            out += [f"#### {heading}", text, ""]
            if re.search(r"breaking|deprecat|incompatible", heading, re.I):
                out += [f"- impact hint: {hint}" for hint in impact_hints(text, new.key)] + [""]
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--release", required=True)
    parser.add_argument("--origin", required=True)
    parser.add_argument(
        "--module", action="append", help="Restrict module sections to these known_good keys (repeatable)"
    )
    parser.add_argument(
        "--module-prs",
        action="store_true",
        help="Also list the merged PRs of each changed module (slow, large modules have hundreds)",
    )
    parser.add_argument("--include-infra", action="store_true", help="Also cover the Associated Infrastructure Modules")
    parser.add_argument(
        "--known-good-ref",
        help="Git ref to read known_good.json from (default: release tag if it exists, else the working tree), e.g. origin/main",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    ref = args.known_good_ref or (args.release if grn._tag_exists(args.release) else None)
    current = {e.key: (g, e) for g, es in grn.collect(grn.load_known_good(ref)).items() for e in es}
    previous = {e.key: e for es in grn.collect(grn.load_known_good(args.origin)).values() for e in es}

    sections = []
    ref_slug = f"eclipse-score/{grn.RELEASE_REPO}"
    head = args.release if grn._tag_exists(args.release) else "main"
    sections.append(render_module("Reference integration", ref_slug, args.origin, head, own_repo=True))

    renamed_from = {new: old for old, new in grn.KEY_ALIASES.items()}
    for key, (group, entry) in current.items():
        if args.module and key not in args.module:
            continue
        if group == "tooling" and not args.include_infra:
            continue
        old = previous.get(key) or previous.get(renamed_from.get(key, ""))
        slug = repo_slug(entry.repo_url)
        if old is None:
            sections.append(f"## {entry.name}: newly integrated at {entry.version_label} ({slug})\n")
            continue
        if old.key != key:
            sections.append(f"## {entry.name}: RENAMED from `{old.key}` to `{key}` (breaking for integrators)\n")
        if old.pin != entry.pin:
            sections.append(render_release_notes(entry.name, slug, old, entry))
            if args.module_prs:
                sections.append(render_module(entry.name, slug, old.ref, entry.ref))
    for key, old in previous.items():
        if (
            key not in current
            and not (key in grn.KEY_ALIASES and grn.KEY_ALIASES[key] in current)
            and (not args.module or key in args.module)
        ):
            sections.append(f"## {old.name}: removed from the platform (was {old.version_label})\n")

    text = "\n".join(sections)
    if args.output:
        args.output.write_text(text)
    else:
        print(text)


if __name__ == "__main__":
    main()
