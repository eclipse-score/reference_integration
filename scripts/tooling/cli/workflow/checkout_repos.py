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
Checkout all pinned repositories for CodeQL analysis.

Clones repositories directly from known_good.json using GitPython library
with GitHub token authentication to avoid rate limits.
"""

import logging
import os
import sys
from pathlib import Path

from scripts.tooling.lib.git_operations import shallow_clone_repository
from scripts.tooling.lib.known_good import load_known_good

_LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")


def checkout_repo(name: str, url: str, ref: str, path: Path) -> None:
    """
    Checkout a single repository using git_operations library.

    Args:
        name: Repository name
        url: Repository URL
        ref: Git reference (branch, tag, or commit hash)
        path: Local path to checkout into

    Raises:
        Exception: If checkout fails
    """
    _LOG.info(f"Checking out {name} ({ref}) to {path}")

    shallow_clone_repository(url=url, path=path, ref=ref)


def main() -> int:
    """Main entry point for standalone execution."""
    # When running with bazel, use BUILD_WORKING_DIRECTORY to find workspace root
    workspace_root = Path(os.environ.get("BUILD_WORKING_DIRECTORY", "."))
    known_good_path = workspace_root / "known_good.json"

    if not known_good_path.exists():
        _LOG.error(f"known_good.json not found at {known_good_path}")
        return 1

    try:
        known_good = load_known_good(known_good_path)
    except Exception as e:
        _LOG.error(f"Failed to parse known_good.json: {e}")
        return 1

    # Extract target_sw modules
    modules = known_good.modules.get("target_sw", {})
    repo_count = len(modules)

    _LOG.info(f"Checking out {repo_count} repositories from known_good.json...")

    # Track successfully checked out repositories
    repo_paths = []

    # Checkout each repository
    for name, module in modules.items():
        url = module.repo
        # Prioritize hash and version over branch to ensure pinned commits
        ref = module.hash or module.version or module.branch
        # Use workspace-relative path
        path = workspace_root / "repos" / name

        try:
            checkout_repo(name, url, ref, path)
            repo_paths.append(str(path))
        except Exception as e:
            _LOG.error(f"Failed to checkout {name}: {e}")
            return 1

    # Output all paths (comma-separated for GitHub Actions compatibility)
    repo_paths_output = ",".join(repo_paths)

    # Write to GITHUB_OUTPUT if available
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        try:
            with open(github_output, "a") as f:
                f.write(f"repo_paths={repo_paths_output}\n")
        except IOError as e:
            _LOG.warning(f"Failed to write GITHUB_OUTPUT: {e}")

    # Log summary
    _LOG.info(f"Successfully checked out {len(repo_paths)} of {repo_count} repositories")

    return 0


if __name__ == "__main__":
    sys.exit(main())
