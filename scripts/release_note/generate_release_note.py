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
"""Generate the deterministic skeleton of an S-CORE platform release note.

Everything that can be derived from ``known_good.json`` (platform scope and the
module tables) is rendered here. Narrative sections are emitted as
``.. AI-FILL: ...`` comments that the release-note agent replaces.

Examples:
    # Skeleton for an already tagged release (known_good.json is read from the tag)
    python3 scripts/release_note/generate_release_note.py --release v0.8.0 --origin v0.7.0

    # Skeleton for an upcoming release, run on its release candidate branch (known_good.json of the checkout)
    python3 scripts/release_note/generate_release_note.py --release v0.10.0 --origin v0.9.0

    # Module version changes between the two releases
    python3 scripts/release_note/generate_release_note.py --release v0.8.0 --origin v0.7.0 --changes

The release date is the due date of the milestone ``v<major>.<minor>`` in the
eclipse-score/score repository.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ORG_URL = "https://github.com/eclipse-score"
RELEASE_REPO = "reference_integration"
# Repository whose milestones v<major>.<minor> carry the planned platform release dates.
MILESTONE_REPO = "score"

# known_good.json group -> section title; score_platform is moved from "tooling" to "target_sw".
PLATFORM_MODULE = "score_platform"
SECTIONS = {
    "target_sw": "Integrated Software Modules",
    "tooling": "Associated Infrastructure Modules",
}

# Module verification reports are linked from the current docs tree (same convention as the platform report).
VERIFICATION_INDEX = "docs/verification_report/modules/index.rst"
EMPTY_CELL = "---"
# Old module names in earlier known_good.json versions -> current name used in the docs tree.
KEY_ALIASES = {"score_lifecycle_health": "score_lifecycle", "score_process": "score_process_description"}

# (name, images/<dir>, description, how-to candidates [(path, heading or None)] tried in order)
IMAGES = [
    (
        "Reference Linux x86_64 image",
        "linux_x86_64",
        "Linux x86_64 Docker image bundling the S-CORE showcases.",
        [("README.md", "Run showcases"), ("README.md", "Operating system integrations")],
    ),
    (
        "Reference QNX x86_64 image",
        "qnx_x86_64",
        "QNX x86_64 image, run in QEMU.",
        [("runners/qemu_x86_64/README.md", None)],
    ),
    (
        "Reference QNX aarch64 image",
        "qnx_aarch64",
        "QNX 8.0 aarch64 image, run in QEMU or on Raspberry Pi 4/5.",
        [("README.md", "Build and deploy showcases on Raspberry Pi (QNX aarch64)")],
    ),
    (
        "Reference Red Hat AutoSD Linux image (Experimental)",
        "autosd",
        "Red Hat AutoSD x86_64 image.",
        [("README.md", "Operating system integrations")],
    ),
    (
        "Reference Elektrobit corbos Linux for Safety Applications image (Experimental)",
        "ebclfsa_aarch64",
        "Elektrobit corbos Linux for Safety Applications (aarch64) image.",
        [("images/ebclfsa_aarch64/README.md", None)],
    ),
]

DISPLAY_NAMES = {
    "score_baselibs": "Baselibs",
    "score_baselibs_rust": "Baselibs Rust",
    "score_communication": "Communication",
    "score_persistency": "Persistency",
    "score_logging": "Logging",
    "score_time": "Time",
    "score_config_management": "Configuration Management",
    "score_orchestrator": "Orchestrator",
    "score_kyron": "Kyron",
    "score_lifecycle": "Lifecycle",
    "score_lifecycle_health": "Lifecycle & Health Management",
    "score_process": "Process description",
    "score_process_description": "Process description",
    "score_docs_as_code": "Docs-as-code",
    "score_tooling": "Tooling",
    "score_tools": "Tools",
    "score_platform": "Platform",
    "score_itf": "ITF (Integration Testing Framework)",
    "score_test_scenarios": "Test Scenarios",
    "score_crates": "Crates",
    "score_bazel_cpp_toolchains": "Bazel CPP Toolchain",
    "score_bazel_platforms": "Bazel Platforms",
}


@dataclass
class Entry:
    key: str
    name: str
    repo_url: str
    tag: str | None  # release tag the pin resolves to, None if unreleased
    ref: str  # tag or commit used for the source link
    pin: str  # version or hash as written in known_good.json
    verification_doc: str | None = None  # absolute Sphinx doc path of the module verification report

    @property
    def source_url(self) -> str:
        return f"{self.repo_url}/tree/{self.ref}"

    @property
    def release_notes_url(self) -> str | None:
        return f"{self.repo_url}/releases/tag/{self.tag}" if self.tag else None

    @property
    def version_label(self) -> str:
        return self.tag if self.tag else f"{self.pin[:7]} (unreleased)"


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, check=True, capture_output=True, text=True).stdout


def _tag_exists(tag: str) -> bool:
    cmd = ["git", "rev-parse", "-q", "--verify", f"refs/tags/{tag}"]
    return subprocess.run(cmd, cwd=REPO_ROOT, stdout=subprocess.DEVNULL).returncode == 0


def load_known_good(ref: str | None) -> dict:
    text = _git("show", f"{ref}:known_good.json") if ref else (REPO_ROOT / "known_good.json").read_text()
    return json.loads(text)


def remote_tags(repo: str, cache: dict[str, dict[str, str]]) -> dict[str, str]:
    """Map tag name -> commit sha (peeled for annotated tags)."""
    if repo not in cache:
        out = subprocess.run(
            ["git", "ls-remote", "--tags", repo], check=True, capture_output=True, text=True, timeout=60
        ).stdout
        tags: dict[str, str] = {}
        for line in out.splitlines():
            sha, ref = line.split("\t")
            name = ref.removeprefix("refs/tags/")
            if name.endswith("^{}"):
                tags[name[:-3]] = sha
            else:
                tags.setdefault(name, sha)
        cache[repo] = tags
    return cache[repo]


def _version_key(tag: str) -> tuple[int, ...]:
    return tuple(int(p) for p in re.findall(r"\d+", tag))


def resolve(key: str, module: dict, cache: dict[str, dict[str, str]]) -> Entry:
    repo = module["repo"]
    repo_url = repo.removesuffix(".git")
    tags = remote_tags(repo, cache)
    name = DISPLAY_NAMES.get(key) or key.removeprefix("score_").replace("_", " ").title()

    version = module.get("version")
    if version:
        tag = next((c for c in (f"v{version}", version) if c in tags), None)
        if tag is None:
            print(f"warning: {key}: no tag for version {version} in {repo}", file=sys.stderr)
            tag = f"v{version}"
        return Entry(key, name, repo_url, tag, tag, version)

    commit = module["hash"]
    matches = sorted((t for t, c in tags.items() if c == commit), key=_version_key)
    tag = matches[-1] if matches else None
    return Entry(key, name, repo_url, tag, tag or commit, commit)


def verification_docs() -> dict[str, str]:
    """Map module key -> Sphinx doc path, parsed from the module verification report index."""
    text = (REPO_ROOT / VERIFICATION_INDEX).read_text()
    return {m.group(2): m.group(1) for m in re.finditer(r":doc:`[^`<]*<(/modules/(\w+)/[^>\s]+)>`", text)}


def collect(known_good: dict) -> dict[str, list[Entry]]:
    cache: dict[str, dict[str, str]] = {}
    reports = verification_docs()
    result: dict[str, list[Entry]] = {}
    for group, modules in known_good["modules"].items():
        if group not in SECTIONS:
            raise SystemExit(f"error: unknown known_good group '{group}', extend SECTIONS")
        result[group] = [resolve(k, m, cache) for k, m in modules.items() if m.get("enabled", True)]
    for entries in result.values():
        for e in entries:
            e.verification_doc = reports.get(KEY_ALIASES.get(e.key, e.key))

    platform = next((e for e in result.get("tooling", []) if e.key == PLATFORM_MODULE), None)
    if platform:
        result["tooling"].remove(platform)
        result.setdefault("target_sw", []).insert(0, platform)
    return result


def render_table(entries: list[Entry], with_verification: bool = False) -> str:
    widths = "25 15 25 35" if with_verification else "30 25 45"
    rows = [
        "",
        ".. list-table::",
        "   :header-rows: 1",
        f"   :widths: {widths}",
        "",
        "   * - Name",
        "     - Version",
        "     - Release notes",
    ]
    if with_verification:
        rows.append("     - Module verification report")
    for e in entries:
        notes = f"`Release notes <{e.release_notes_url}>`__" if e.release_notes_url else EMPTY_CELL
        rows += [
            f"   * - `{e.name} <{e.source_url}>`__",
            f"     - ``{e.version_label}``",
            f"     - {notes}",
        ]
        if with_verification:
            rows.append(
                f"     - :doc:`Verification report <{e.verification_doc}>`"
                if e.verification_doc
                else f"     - {EMPTY_CELL}"
            )
    return "\n".join(rows)


def _exists(ref: str | None, path: str) -> bool:
    if ref is None:
        return (REPO_ROOT / path).exists()
    return (
        subprocess.run(["git", "cat-file", "-e", f"{ref}:{path}"], cwd=REPO_ROOT, capture_output=True).returncode == 0
    )


def _anchors(ref: str | None, path: str) -> set[str]:
    text = _git("show", f"{ref}:{path}") if ref else (REPO_ROOT / path).read_text()
    anchors = set()
    for line in text.splitlines():
        if line.startswith("#"):
            slug = re.sub(r"[^\w\- ]", "", line.lstrip("# ").strip().lower())
            anchors.add(slug.replace(" ", "-"))
    return anchors


def _howto(ref: str | None, release: str, candidates: list[tuple[str, str | None]]) -> str | None:
    for path, heading in candidates:
        if not _exists(ref, path):
            continue
        base = f"{ORG_URL}/{RELEASE_REPO}/blob/{release}/{path}"
        if heading is None:
            return base
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        if slug in _anchors(ref, path):
            return f"{base}#{slug}"
    return None


def _github_get(path: str) -> object:
    request = urllib.request.Request(f"https://api.github.com{path}", headers={"Accept": "application/vnd.github+json"})
    if token := os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PAT"):
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def milestone_date(release: str) -> str:
    """Due date of the milestone v<major>.<minor> in the S-CORE repository, e.g. v0.10.0 -> milestone v0.10."""
    title = "v" + ".".join(release.removeprefix("v").split(".")[:2])
    milestones = _github_get(f"/repos/eclipse-score/{MILESTONE_REPO}/milestones?state=all&per_page=100")
    due = next((m["due_on"] for m in milestones if m["title"] == title and m["due_on"]), None)
    if due is None:
        print(f"warning: no milestone {title} with a due date in eclipse-score/{MILESTONE_REPO}", file=sys.stderr)
        return "TBD"
    return due[:10]


def release_assets(release: str) -> list[dict]:
    try:
        return _github_get(f"/repos/eclipse-score/{RELEASE_REPO}/releases/tags/{release}").get("assets", [])
    except OSError:
        return []  # release not published yet


def render_images(release: str, ref: str | None) -> str:
    assets = release_assets(release)
    rows = [
        "",
        ".. list-table::",
        "   :header-rows: 1",
        "   :widths: 30 15 15 40",
        "",
        "   * - Name",
        "     - Tarball",
        "     - How-to",
        "     - Description",
    ]
    for name, directory, description, candidates in IMAGES:
        if not _exists(ref, f"images/{directory}"):
            continue
        asset = next((a for a in assets if directory in a["name"]), None)
        howto = _howto(ref, release, candidates)
        rows += [
            f"   * - {name}",
            f"     - `{asset['name']} <{asset['browser_download_url']}>`__" if asset else f"     - {EMPTY_CELL}",
            f"     - `How-to <{howto}>`__" if howto else f"     - {EMPTY_CELL}",
            f"     - {description}",
        ]
    return "\n".join(rows)


# Chapter icons; emoji are double-width, so the underline gets extra length.
ICONS = {
    "Overview": "📋",
    "Disclaimer": "📜",
    "Changes to the Platform": "🔄",
    "New Features": "✨",
    "Breaking Changes": "💥",
    "Reference Integration scope": "🎯",
    "Integrated Software Modules": "🧩",
    "Associated Infrastructure Modules": "🔧",
    "Images": "💿",
    "Known Issues/Vulnerabilities and Bug Fixes": "🐞",
    "Upgrade Instructions": "🚀",
    "Contact Information": "📧",
}


def _heading(text: str, char: str) -> str:
    icon = ICONS.get(text)
    if icon:
        text = f"{icon} {text}"
    return f"{text}\n{char * (len(text) + 2)}"


def status_banner(release: str, date: str, status: str) -> str:
    if status == "draft":
        return f"""
.. warning::

   **DRAFT - release in progress.** {release} is not released yet (planned for
   {date}). This note shows the current state of the integration and changes
   until the release is published.
"""
    return f"""
.. note::

   **FINAL.** This is the release note of release
   `{release} <{ORG_URL}/{RELEASE_REPO}/releases/tag/{release}>`__ ({date}).
"""


def render(release: str, origin: str, date: str, status: str, groups: dict[str, list[Entry]], ref: str | None) -> str:
    short = ".".join(release.removeprefix("v").split(".")[:2])
    doc_id = "v" + short.replace(".", "")
    title = f"S-CORE Platform v{short} release note" + (" (DRAFT)" if status == "draft" else "")
    release_url = f"{ORG_URL}/{RELEASE_REPO}"

    header = """..
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
"""
    parts = [
        header,
        _heading(title, "="),
        status_banner(release, date, status),
        f"""
.. document:: S-CORE v{short} release note
   :id: doc__score_{doc_id}_release_note
   :status: {status}
   :safety: QM
   :security: YES
   :realizes: wp__platform_sw_release_note
   :version: 1

| **Platform Name:** S-CORE
| **Release Tag:** {release}
| **Origin Release Tag:** {origin}
| **Release Date:** {date}

""",
        _heading("Overview", "^"),
        f"""
This document provides an overview of the changes, improvements, and bug fixes
included in the software platform release version {release} as compared to the
previous platform release ({origin}).

""",
        _heading("Disclaimer", "-"),
        """
This release note does not "release for production", as it does not come with a
safety argumentation and a performed safety assessment.
The work products compiled in the safety package are created with care according
to a process satisfying standards, but the project, being a non-profit and open
source organization, can not take over any liability for its content.

""",
        _heading("Changes to the Platform", "^"),
        "\n" + _heading("New Features", "-"),
        "\n.. AI-FILL: New Features - platform-level only (see skill): one subsection (~~~) per item, each with links to PR, issue or module release note.\n",
        _heading("Breaking Changes", "-"),
        "\n.. AI-FILL: Breaking Changes - only changes with impact on integrators (see skill), with migration hint; remove the chapter if none.\n",
        _heading("Reference Integration scope", "^"),
        f"""
- **Version:** ``{release}``
- **Source / tag:** `Reference integration <{release_url}/tree/{release}>`__
- **Release notes:** `Reference integration release notes <{release_url}/releases/tag/{release}>`__
- **Platform Verification Report:** :need:`doc__platform_verification_report_latest`

""",
    ]

    for group, title_text in SECTIONS.items():
        parts += [_heading(title_text, "-"), render_table(groups[group], with_verification=group == "target_sw") + "\n"]
    parts += [_heading("Images", "-"), render_images(release, ref) + "\n"]

    unreleased = any(e.tag is None for entries in groups.values() for e in entries)
    unreleased_hint = (
        "\n- Modules shown as *(unreleased)* are pinned to a commit and have no registry version; "
        "use the commit from ``known_good.json``."
        if unreleased
        else ""
    )

    parts += [
        _heading("Known Issues/Vulnerabilities and Bug Fixes", "-"),
        "\n- See the release notes of the individual modules.\n",
        _heading("Upgrade Instructions", "-"),
        f"""
- Increase to the newest Bazel registry versions: https://eclipse-score.github.io/bazel_registry_ui{unreleased_hint}
- The module versions of this release are listed in `known_good.json <{release_url}/blob/{release}/known_good.json>`__.

""",
        _heading("Contact Information", "-"),
        """
For any questions or support, please contact the *Project leads* or raise an issue/discussion.
https://projects.eclipse.org/projects/automotive.score
""",
    ]
    return "\n".join(parts)


def render_changes(origin: dict[str, list[Entry]], current: dict[str, list[Entry]]) -> str:
    old = {KEY_ALIASES.get(e.key, e.key): e for entries in origin.values() for e in entries}
    new = {KEY_ALIASES.get(e.key, e.key): e for entries in current.values() for e in entries}
    lines = ["| Module | Previous | Current |", "|---|---|---|"]
    for key in sorted(old.keys() | new.keys()):
        o, n = old.get(key), new.get(key)
        renamed = f" **renamed from `{o.key}`**" if o and n and o.key != n.key else ""
        if o and n and o.pin == n.pin and not renamed:
            continue
        lines.append(
            f"| {(n or o).name} (`{key}`){renamed} | {o.version_label if o else 'new'} | {n.version_label if n else 'removed'} |"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--release", required=True, help="Release tag, e.g. v0.10.0")
    parser.add_argument("--origin", required=True, help="Previous release tag, e.g. v0.9.0")
    parser.add_argument(
        "--known-good-ref",
        help="Git ref to read known_good.json from (default: release tag if it exists, else working tree)",
    )
    parser.add_argument(
        "--date",
        help="Override the release date YYYY-MM-DD (default: due date of the milestone in eclipse-score/score)",
    )
    # The note is part of the release and is finalised before the tag exists, so the state cannot be derived.
    parser.add_argument("--final", action="store_true", help="Final release note (default: draft)")
    parser.add_argument("--changes", action="store_true", help="Print module version changes instead of the skeleton")
    parser.add_argument("--output", type=Path, help="Write to file instead of stdout")
    args = parser.parse_args()

    ref = args.known_good_ref or (args.release if _tag_exists(args.release) else None)
    groups = collect(load_known_good(ref))

    if args.changes:
        text = render_changes(collect(load_known_good(args.origin)), groups)
    else:
        date = args.date or milestone_date(args.release)
        status = "valid" if args.final else "draft"
        text = render(args.release, args.origin, date, status, groups, ref)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n")
    else:
        print(text)


if __name__ == "__main__":
    main()
