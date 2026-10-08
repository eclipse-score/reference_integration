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
"""Collect per-release, per-module metrics for the Overall Status charts.

For every ``reference_integration`` release tag the module pins are read from
that tag's ``known_good.json``; the working tree's ``known_good.json`` supplies
the forecast column. Metrics are then counted from bare clones using git
plumbing, which keeps the whole run local and free of API rate limits.

Requires ``GITHUB_PAT`` for the tag/pin lookups. Writes
``overall_status_data.json``; run ``generate_progress_charts.py`` afterwards.
"""

import argparse
import base64
import json
import math
import os
import re
import subprocess
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = REPO_ROOT / "docs" / "s_core_v_1" / "roadmap" / "overall_status_data.json"
API = "https://api.github.com"
REF_INT = "eclipse-score/reference_integration"

# display name -> (repo, known_good keys oldest-first, score-repo path fragments)
MODULES = {
    "Baselibs": ("eclipse-score/baselibs", ["score_baselibs"], ["features/baselibs", "modules/baselibs"]),
    "Communication": (
        "eclipse-score/communication",
        ["score_communication"],
        ["features/communication", "modules/communication"],
    ),
    "Logging": (
        "eclipse-score/logging",
        ["score_logging"],
        ["features/logging", "features/analysis-infra/logging", "features/log_and_trace/logging", "modules/logging"],
    ),
    "Persistency": (
        "eclipse-score/persistency",
        ["score_persistency"],
        ["features/persistency", "modules/persistency"],
    ),
    "Time": ("eclipse-score/time", ["score_time"], ["features/time", "modules/time"]),
    "Config Mgmt": (
        "eclipse-score/config_management",
        ["score_config_management"],
        ["features/configuration", "modules/config"],
    ),
    "Lifecycle": (
        "eclipse-score/lifecycle",
        ["score_lifecycle", "score_lifecycle_health"],
        ["features/lifecycle", "modules/lifecycle"],
    ),
    "Kyron": ("eclipse-score/kyron", ["score_kyron"], ["features/kyron", "modules/kyron"]),
    "Security/Crypto": ("eclipse-score/inc_security_crypto", [], ["features/security_crypto", "modules/security"]),
    "Diagnostic Services": (None, [], ["features/diagnostics", "modules/diagnostic"]),
    "NM": (None, [], ["features/network_management", "features/nm/", "modules/network_management"]),
    "Some/IP": ("eclipse-score/inc_someip_gateway", [], ["features/communication/some_ip_gateway"]),
}
SCORE_REPO = "eclipse-score/score"
SCORE_KEY = "score_platform"
SOMEIP = "some_ip_gateway"

MODULE_COLORS = {
    "Baselibs": "#1f77b4",
    "Communication": "#ff7f0e",
    "Logging": "#2ca02c",
    "Persistency": "#d62728",
    "Time": "#9467bd",
    "Config Mgmt": "#8c564b",
    "Lifecycle": "#e377c2",
    "Kyron": "#17becf",
    "Security/Crypto": "#bcbd22",
    "Diagnostic Services": "#aec7e8",
    "NM": "#ffbb78",
    "Some/IP": "#98df8a",
}

CHARTS = [
    ("requirements", "req", "pa2_impl_progress.svg", "Requirements per release (feature + component)"),
    ("architecture", "arc", "pa3_arch_progress.svg", "Architecture elements per release (feature + component)"),
    ("implementation", "loc", "pa4_impl_progress.svg", "Lines of code per release"),
    ("verification", "tests", "pa5_verification_progress.svg", "Tests per release (unit + integration)"),
]

REQ_RST = re.compile(r"^\s*\.\.\s+(feat_req|comp_req|aou_req)::", re.M)
ARC_RST = re.compile(
    r"^\s*\.\.\s+(feat|feat_arc|feat_arc_sta|feat_arc_dyn|comp|comp_arc|comp_arc_sta"
    r"|comp_arc_dyn|logic_arc_int|logic_arc_int_op|real_arc_int|real_arc_int_op)::",
    re.M,
)
TRLC_OBJ = re.compile(r"^[ \t]*(?:\w+\.)?([A-Z]\w*)[ \t]+\w+[ \t]*\{", re.M)
TRLC_REQ_TYPES = {"CompReq", "FeatReq", "AoU", "ExternalCompReq", "AssumedSystemReq"}
TEST_PAT = re.compile(
    r"\bTEST(?:_F|_P)?\s*\(|\bTYPED_TEST(?:_P)?\s*\(|^\s*#\[\s*test\s*\]"
    r"|^\s*(?:async\s+)?def\s+test_",
    re.M,
)
SRC_EXT = (".cpp", ".cc", ".cxx", ".c", ".h", ".hpp", ".hh", ".rs", ".py")

_api_cache: dict[str, object] = {}


def gh(path):
    if path not in _api_cache:
        req = urllib.request.Request(
            API + path,
            headers={
                "Authorization": f"Bearer {os.environ['GITHUB_PAT']}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "overall-status",
            },
        )
        with urllib.request.urlopen(req) as r:
            _api_cache[path] = json.load(r)
    return _api_cache[path]


def resolve_tag(repo, tag):
    """Return the commit a tag points at, dereferencing annotated tags."""
    try:
        d = gh(f"/repos/{repo}/git/ref/tags/{tag}")
    except urllib.error.HTTPError:
        return None
    sha = d["object"]["sha"]
    if d["object"]["type"] == "tag":
        sha = gh(f"/repos/{repo}/git/tags/{sha}")["object"]["sha"]
    return sha


def commit_before(repo, iso_date):
    try:
        c = gh(f"/repos/{repo}/commits?until={iso_date}&per_page=1")
    except urllib.error.HTTPError:
        return None
    return c[0]["sha"] if c else None


def flatten(known_good):
    flat = {}
    for key, value in known_good.get("modules", {}).items():
        if isinstance(value, dict) and "repo" in value:
            flat[key] = value
        elif isinstance(value, dict):
            flat.update(value)
    return flat


def git(repo, cache, *args):
    return subprocess.run(
        ["git", f"--git-dir={cache}/{repo.split('/')[-1]}.git", *args],
        capture_output=True,
    )


def ensure_clone(repo, cache):
    target = cache / f"{repo.split('/')[-1]}.git"
    if target.exists():
        subprocess.run(["git", f"--git-dir={target}", "fetch", "-q", "--all", "--tags"], check=False)
        return
    token = os.environ["GITHUB_PAT"]
    print(f"  cloning {repo}")
    subprocess.run(
        ["git", "clone", "-q", "--bare", f"https://x-access-token:{token}@github.com/{repo}.git", str(target)],
        check=True,
    )


def ls_tree(repo, sha, cache):
    out = git(repo, cache, "ls-tree", "-r", "--long", sha)
    if out.returncode:
        return []
    entries = []
    for line in out.stdout.decode("utf-8", "replace").splitlines():
        meta, path = line.split("\t", 1)
        parts = meta.split()
        if parts[1] == "blob":
            entries.append((parts[2], path))
    return entries


def read_blobs(repo, shas, cache):
    """Stream several blobs through a single `git cat-file --batch` call."""
    if not shas:
        return {}
    p = subprocess.run(
        ["git", f"--git-dir={cache}/{repo.split('/')[-1]}.git", "cat-file", "--batch"],
        input=("\n".join(shas) + "\n").encode(),
        capture_output=True,
    )
    res, buf, pos = {}, p.stdout, 0
    for sha in shas:
        nl = buf.index(b"\n", pos)
        header = buf[pos:nl].decode()
        pos = nl + 1
        if "missing" in header:
            continue
        size = int(header.split()[2])
        res[sha] = buf[pos : pos + size].decode("utf-8", "replace")
        pos += size + 1
    return res


def is_doc(path):
    return path.endswith(".rst") and "chklst" not in path


def is_src(path):
    p = path.lower()
    if not p.endswith(SRC_EXT) or p.startswith("bazel-"):
        return False
    return not (p.startswith(("docs/", "third_party/")) or "/docs/" in p or "/third_party/" in p)


def measure(repo, sha, cache, path_ok=None, *, with_code=True):
    entries = [e for e in ls_tree(repo, sha, cache) if path_ok is None or path_ok(e[1])]
    counts = Counter()
    if not entries:
        return counts

    docs = [s for s, p in entries if is_doc(p)]
    blobs = read_blobs(repo, docs, cache)
    for sha_ in docs:
        body = blobs.get(sha_, "")
        counts["req"] += len(REQ_RST.findall(body))
        counts["arc"] += len(ARC_RST.findall(body))

    trlc = [s for s, p in entries if p.endswith(".trlc")]
    blobs = read_blobs(repo, trlc, cache)
    for sha_ in trlc:
        for kind in TRLC_OBJ.findall(blobs.get(sha_, "")):
            if kind in TRLC_REQ_TYPES:
                counts["req"] += 1

    if with_code:
        src = [s for s, p in entries if is_src(p)]
        blobs = read_blobs(repo, src, cache)
        for sha_ in src:
            body = blobs.get(sha_, "")
            counts["loc"] += body.count("\n")
            counts["tests"] += len(TEST_PAT.findall(body))
    return counts


def release_pins(cache):
    """Return [(label, {module: (repo, sha)})] oldest first, forecast last."""
    tags = [t["name"] for t in gh(f"/repos/{REF_INT}/tags?per_page=100")]
    columns = []
    for tag in sorted(t for t in tags if t != "v0.5.0-alpha"):
        ref = resolve_tag(REF_INT, tag)
        date = gh(f"/repos/{REF_INT}/commits/{ref}")["commit"]["committer"]["date"]
        blob = gh(f"/repos/{REF_INT}/contents/known_good.json?ref={ref}")
        flat = flatten(json.loads(base64.b64decode(blob["content"])))
        columns.append((tag, date, flat))

    local = flatten(json.loads((REPO_ROOT / "known_good.json").read_text(encoding="utf-8")))
    columns.append(("forecast", None, local))

    out = []
    for tag, date, flat in columns:
        resolved = {}
        for name, (repo, keys, _) in list(MODULES.items()) + [("__score__", (SCORE_REPO, [SCORE_KEY], []))]:
            if repo is None:
                continue
            entry = next((flat[k] for k in keys if k in flat), None)
            sha = entry.get("hash") if entry else None
            if not sha and entry and entry.get("version"):
                sha = resolve_tag(repo, f"v{entry['version']}") or resolve_tag(repo, entry["version"])
            if not sha:
                ensure_clone(repo, cache)
                sha = (
                    commit_before(repo, date)
                    if date
                    else git(repo, cache, "rev-parse", "main").stdout.decode().strip() or None
                )
            if sha:
                resolved[name] = (repo, sha)
        label = "v0.10 (forecast)" if tag == "forecast" else tag
        out.append((label, resolved))
    return out


def nice_axis(peak):
    """Round the axis maximum up to a readable step."""
    base = 10 ** math.floor(math.log10(peak))
    for mult in (0.1, 0.2, 0.25, 0.5, 1.0):
        step = base * mult
        if peak / step <= 10:
            top = math.ceil(peak / step) * step
            return int(top + step if top < peak * 1.04 else top), int(step)
    return int(peak), int(base)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path("/tmp/overall_status_repos"))
    parser.add_argument("--out", type=Path, default=DATA_FILE)
    parser.add_argument("--collected", default=None, help="data collection date, default today")
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)

    for repo, _, _ in MODULES.values():
        if repo:
            ensure_clone(repo, args.cache)
    ensure_clone(SCORE_REPO, args.cache)

    per_release = []
    for label, resolved in release_pins(args.cache):
        print(f"== {label}")
        score_repo, score_sha = resolved["__score__"]
        totals = {}
        for name, (_, _, fragments) in MODULES.items():
            counts = Counter()

            def score_ok(path, fragments=fragments, name=name):
                if not any(f in path for f in fragments):
                    return False
                return not (name == "Communication" and SOMEIP in path)

            counts.update(measure(score_repo, score_sha, args.cache, score_ok, with_code=False))
            if name in resolved:
                repo, sha = resolved[name]
                counts.update(measure(repo, sha, args.cache))
            totals[name] = counts
            summary = " ".join(f"{m}={counts[m]:>7d}" for _, m, _, _ in CHARTS)
            print(f"   {name:22s} {summary}")
        per_release.append((label, totals))

    from datetime import date

    data = {
        "data_collected": args.collected or date.today().isoformat(),
        "module_colors": MODULE_COLORS,
        "charts": {},
    }
    for key, metric, fname, title in CHARTS:
        releases = [
            {"name": label, "modules": {m: totals[m][metric] for m in MODULE_COLORS}} for label, totals in per_release
        ]
        peak = max(sum(r["modules"].values()) for r in releases)
        axis_max, axis_step = nice_axis(peak)
        data["charts"][key] = {
            "file": fname,
            "title": title,
            "axis_max": axis_max,
            "axis_step": axis_step,
            "releases": releases,
        }

    args.out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {args.out}")
    print("now run scripts/overall_status/generate_progress_charts.py")


if __name__ == "__main__":
    main()
