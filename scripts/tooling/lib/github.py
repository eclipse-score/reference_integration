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
"""GitHub REST API helpers.

Lightweight wrappers around the GitHub API using only stdlib (urllib).
No third-party dependencies are required.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional

_LOG = logging.getLogger(__name__)

_API_BASE = "https://api.github.com"


def _make_request(url: str, token: Optional[str]) -> urllib.request.Request:
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    return req


@dataclass
class CompareResult:
    """Result of comparing a pinned commit against a branch HEAD."""

    ahead_by: int
    """How many commits the branch HEAD is ahead of the pinned hash (i.e. commits behind)."""
    status: str
    """GitHub compare status: ``"identical"``, ``"ahead"``, ``"behind"``, or ``"diverged"``."""
    head_sha: str
    """Current HEAD SHA of the target branch."""


def fetch_compare(
    owner_repo: str,
    base_hash: str,
    branch: str,
    token: Optional[str] = None,
) -> Optional[CompareResult]:
    """Compare *base_hash* against the HEAD of *branch* in *owner_repo*.

    Returns a :class:`CompareResult` with the number of commits the pinned hash
    is behind and the current HEAD SHA, or ``None`` on any error.

    Args:
        owner_repo: GitHub ``owner/repo`` slug (e.g. ``"eclipse-score/baselibs"``).
        base_hash: The pinned commit SHA to compare from.
        branch: Branch name to compare against.
        token: Optional GitHub PAT or ``GITHUB_TOKEN``.
               Without a token requests are unauthenticated (60 req/h rate limit).
    """
    url = f"{_API_BASE}/repos/{owner_repo}/compare/{base_hash}...{branch}"
    req = _make_request(url, token)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            commits = data.get("commits", [])
            head_sha = commits[-1]["sha"] if commits else base_hash
            return CompareResult(
                ahead_by=data.get("ahead_by", 0),
                status=data.get("status", ""),
                head_sha=head_sha,
            )
    except urllib.error.HTTPError as exc:
        _LOG.debug(
            "GitHub compare HTTP %s for %s %s...%s: %s",
            exc.code, owner_repo, base_hash[:10], branch, exc.reason,
        )
    except OSError as exc:
        _LOG.debug("GitHub compare network error for %s: %s", owner_repo, exc)
    return None
