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
Git operations library for repository checkout.

Provides functions to clone repositories using GitPython library with GitHub token
authentication to avoid rate limits.
"""

import logging
import os
import re
from pathlib import Path
from typing import Optional

import git
from git import Repo

_LOG = logging.getLogger(__name__)


def is_commit_hash(ref: str) -> bool:
    """
    Check if reference looks like a commit hash (40 hex characters for SHA-1).

    Args:
        ref: Git reference (branch, tag, or hash)

    Returns:
        True if ref matches commit hash pattern
    """
    return bool(re.match(r"^[0-9a-fA-F]{40}$", ref))


def get_authenticated_url(url: str, token: Optional[str] = None) -> str:
    """
    Add authentication token to GitHub URL.

    Args:
        url: Repository URL
        token: GitHub token (if None, uses GITHUB_TOKEN env var)

    Returns:
        URL with embedded authentication token
    """
    if token is None:
        token = os.environ.get("GITHUB_TOKEN", "")

    if token and "github.com" in url:
        # Replace https://github.com/ with https://token@github.com/
        return url.replace("https://github.com/", f"https://{token}@github.com/")
    return url


def shallow_clone_repository(url: str, path: Path, ref: Optional[str] = None, token: Optional[str] = None) -> None:
    """
    Perform a shallow clone of a repository using GitPython library.

    Uses GitPython with GitHub token authentication to avoid rate limits.

    Args:
        url: Repository URL
        path: Local path to clone into
        ref: Optional git reference (branch, tag, or commit hash)
        token: Optional GitHub token (uses GITHUB_TOKEN env if not provided)

    Raises:
        git.exc.GitCommandError: If git clone/fetch/checkout fails
        Exception: For other unexpected errors
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    auth_url = get_authenticated_url(url, token)

    if ref and is_commit_hash(ref):
        # For commit hashes, clone with depth 1 then fetch specific commit
        _LOG.info(f"Cloning {url} with shallow depth (commit hash: {ref[:8]}...)")

        # Clone with depth 1 and all branches
        repo = Repo.clone_from(auth_url, str(path), depth=1, no_single_branch=True)

        # Fetch the specific commit
        _LOG.info(f"Fetching specific commit {ref[:8]}...")
        origin = repo.remotes.origin
        origin.fetch(ref, depth=1)

        # Checkout the commit
        repo.git.checkout(ref)
        _LOG.info(f"Successfully checked out commit {ref[:8]}")

    elif ref:
        # For branches/tags, use branch parameter for shallow clone
        _LOG.info(f"Cloning {url} with branch/tag {ref}")
        try:
            Repo.clone_from(auth_url, str(path), branch=ref, depth=1)
            _LOG.info(f"Successfully cloned branch/tag {ref}")
        except git.exc.GitCommandError:
            # Try with 'v' prefix if it looks like a version number
            if not ref.startswith("v") and re.match(r"^\d+\.\d+", ref):
                _LOG.info(f"Retrying with 'v' prefix: v{ref}")
                Repo.clone_from(auth_url, str(path), branch=f"v{ref}", depth=1)
                _LOG.info(f"Successfully cloned branch/tag v{ref}")
            else:
                raise
    else:
        # No ref specified, clone default branch
        _LOG.info(f"Cloning {url} (default branch)")
        Repo.clone_from(auth_url, str(path), depth=1)
        _LOG.info("Successfully cloned default branch")
