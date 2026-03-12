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
"""GitHub API helpers backed by PyGithub."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from github import Github, GithubException

_LOG = logging.getLogger(__name__)


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
    try:
        gh = Github(token) if token else Github()
        repo = gh.get_repo(owner_repo)
        comparison = repo.compare(base_hash, branch)
        commits = list(comparison.commits)
        head_sha = commits[-1].sha if commits else base_hash
        return CompareResult(
            ahead_by=comparison.ahead_by,
            status=comparison.status,
            head_sha=head_sha,
        )
    except GithubException as exc:
        _LOG.debug("GitHub compare error for %s %s...%s: %s", owner_repo, base_hash[:10], branch, exc)
    except Exception as exc:  # noqa: BLE001
        _LOG.debug("Unexpected error comparing %s: %s", owner_repo, exc)
    return None
