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


def _get_repo(owner_repo: str, token: Optional[str]):
    """Return the PyGithub ``Repository`` for *owner_repo*, authenticated if *token* is set."""
    gh = Github(token) if token else Github()
    return gh.get_repo(owner_repo)


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
        repo = _get_repo(owner_repo, token)
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


def resolve_ref_sha(
    owner_repo: str,
    ref: str,
    token: Optional[str] = None,
) -> Optional[str]:
    """Resolve a git ref (tag, branch or SHA) to a commit SHA.

    Modules pinned by ``version`` store the bare release string (e.g. ``"0.2.9"``)
    while the git tag is usually prefixed with ``v`` (``"v0.2.9"``). Both spellings
    are tried so a version pin resolves to the tag's commit.

    Args:
        owner_repo: GitHub ``owner/repo`` slug (e.g. ``"eclipse-score/baselibs"``).
        ref: The tag/branch/version string to resolve.
        token: Optional GitHub PAT or ``GITHUB_TOKEN``.

    Returns:
        The resolved commit SHA, or ``None`` if no candidate ref could be resolved.
    """
    candidates = [ref]
    if not ref.startswith("v"):
        candidates.append(f"v{ref}")
    try:
        repo = _get_repo(owner_repo, token)
        for candidate in candidates:
            try:
                return repo.get_commit(candidate).sha
            except GithubException:
                continue
        _LOG.debug("Could not resolve ref %r for %s (tried %s)", ref, owner_repo, candidates)
    except Exception as exc:  # noqa: BLE001
        _LOG.debug("Unexpected error resolving ref %s for %s: %s", ref, owner_repo, exc)
    return None
