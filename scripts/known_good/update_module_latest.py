#!/usr/bin/env python3
"""Update module commit hashes to latest on a given branch.

Reads a known_good.json file containing a list of modules with keys:
  name, hash, repo

For each module's repo (expected to be a GitHub HTTPS URL), queries the GitHub API
for the latest commit hash on the provided branch (default: main) and prints a
summary. Optionally writes out an updated JSON file with refreshed hashes.

Usage:
  python tools/update_module_latest.py \
	  --known-good score_reference_integration/known_good.json \
	  [--branch main] [--output updated_known_good.json]

Environment:
  Optionally set GITHUB_TOKEN to increase rate limits / access private repos.

Exit codes:
  0 success
  2 partial failure (at least one repo failed)
  3 fatal failure (e.g., cannot read JSON)
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import json
import os
import sys
from pathlib import Path

from models.known_good import load_known_good

try:
	from github import Github, GithubException
	HAS_PYGITHUB = True
except ImportError:
	HAS_PYGITHUB = False
	Github = None
	GithubException = None


def fetch_latest_commit(owner_repo: str, branch: str, token: str | None) -> str:
	"""Fetch latest commit sha for given owner_repo & branch using PyGithub."""
	if not HAS_PYGITHUB:
		raise RuntimeError("PyGithub not installed. Install it with: pip install PyGithub")
	try:
		gh = Github(token) if token else Github()
		repo = gh.get_repo(owner_repo)
		branch_obj = repo.get_branch(branch)
		return branch_obj.commit.sha
	except GithubException as e:
		raise RuntimeError(f"GitHub API error for {owner_repo}:{branch} - {e.status}: {e.data.get('message', str(e))}") from e
	except Exception as e:
		raise RuntimeError(f"Error fetching {owner_repo}:{branch} - {e}") from e


def fetch_latest_commit_gh(owner_repo: str, branch: str) -> str:
	"""Fetch latest commit using GitHub CLI 'gh' if installed.

	Uses: gh api repos/{owner_repo}/branches/{branch} --jq .commit.sha
	Raises RuntimeError on failure.
	"""
	if not shutil.which("gh"):
		raise RuntimeError("'gh' CLI not found in PATH")
	cmd = [
		"gh",
		"api",
		f"repos/{owner_repo}/branches/{branch}",
		"--jq",
		".commit.sha",
	]
	try:
		res = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=30)
	except subprocess.CalledProcessError as e:
		raise RuntimeError(f"gh api failed: {e.stderr.strip() or e}") from e
	sha = res.stdout.strip()
	if not sha:
		raise RuntimeError("Empty sha returned by gh")
	return sha


def parse_args(argv: list[str]) -> argparse.Namespace:
	p = argparse.ArgumentParser(description="Update module hashes to latest commit on branch")
	p.add_argument(
		"--known-good",
		default="known_good.json",
		help="Path to known_good.json file (default: known_good.json in CWD)",
	)
	p.add_argument("--branch", default="main", help="Git branch to fetch latest commits from (default: main)")
	p.add_argument("--output", help="Optional output path to write updated JSON")
	p.add_argument("--fail-fast", action="store_true", help="Stop on first failure instead of continuing")
	p.add_argument("--no-gh", action="store_true", help="Disable GitHub CLI usage even if installed; fall back to HTTP API; GITHUB_TOKEN has to be known in the environment")
	return p.parse_args(argv)


def main(argv: list[str]) -> int:
	args = parse_args(argv)
	try:
		known_good = load_known_good(Path(args.known_good))
	except FileNotFoundError as e:
		print(f"ERROR: {e}", file=sys.stderr)
		return 3
	except ValueError as e:
		print(f"ERROR: {e}", file=sys.stderr)
		return 3
	except json.JSONDecodeError as e:
		print(f"ERROR: Invalid JSON syntax: {e}", file=sys.stderr)
		return 3

	if not known_good.modules:
		print("ERROR: No modules found to update.", file=sys.stderr)
		return 3

	token = os.environ.get("GITHUB_TOKEN")
	failures = 0
	# Default: use gh if available unless --no-gh specified
	use_gh = (not args.no_gh) and shutil.which("gh") is not None
	
	# If PyGithub is not available and gh CLI is not available, error out
	if not use_gh and not HAS_PYGITHUB:
		print("ERROR: Neither 'gh' CLI nor PyGithub library found.", file=sys.stderr)
		print("Please install PyGithub (pip install PyGithub) or install GitHub CLI.", file=sys.stderr)
		return 3
	
	if not args.no_gh and not use_gh:
		print("INFO: 'gh' CLI not found; using direct GitHub API", file=sys.stderr)
	if args.no_gh and shutil.which("gh") is not None:
		print("INFO: --no-gh specified; ignoring installed 'gh' CLI", file=sys.stderr)

	for mod in known_good.modules.values():
		if mod.pin_version:
			print(f"{mod.name}: pinned, skipping")
			continue

		try:
			branch = mod.branch if mod.branch else args.branch
			if use_gh:
				latest = fetch_latest_commit_gh(mod.owner_repo, branch)
			else:
				latest = fetch_latest_commit(mod.owner_repo, branch, token)

			old_hash = mod.hash
			if latest != old_hash:
				mod.hash = latest
				mod.version = None  # Clear version when hash changes
				if mod.version:
					print(f"{mod.name}: {mod.version} -> {latest[:8]} (branch {branch})")
				else:
					print(f"{mod.name}: {old_hash[:8]} -> {latest[:8]} (branch {branch})")
			else:
				print(f"{mod.name}: {old_hash[:8]} (no update)")
		except Exception as e:  # noqa: BLE001
			failures += 1
			print(f"ERROR {mod.name}: {e}", file=sys.stderr)
			if args.fail_fast:
				break

	if args.output:
		try:
			known_good.write(Path(args.output))
			print(f"Updated JSON written to {args.output}")
		except OSError as e:
			print(f"ERROR: Failed writing output file: {e}", file=sys.stderr)
			return 3

	if failures:
		print(f"Completed with {failures} failure(s).", file=sys.stderr)
		return 2
	return 0


if __name__ == "__main__":  # pragma: no cover
	sys.exit(main(sys.argv[1:]))

