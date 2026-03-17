#!/usr/bin/env python3
# *******************************************************************************
# Copyright (c) 2025 Contributors to the Eclipse Foundation
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

"""Check release branch PR approvals against required maintainers."""

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

from github import Auth, Github  # type: ignore[import-untyped]
from jinja2 import Template

from scripts.tooling.lib.known_good import load_known_good

# Jinja2 templates for markdown generation
MODULE_STATUS_TEMPLATE = Template(
    """{% if status == 'disapproved' -%}
- 🚫 **{{ module_name }}**: Changes requested by {{ disapproved_usernames|join(', ') }}
{%- if approved_usernames %} (approved by {{ approved_usernames|join(', ') }}){% endif %}
{% elif status == 'approved' -%}
- ✅ **{{ module_name }}**: Approved by {{ approved_usernames|join(', ') }}
{% else -%}
- ❌ **{{ module_name }}**: Awaiting approval (requires one of: {{ required_approvers|join(', ') }})
{% endif -%}
"""
)

SUMMARY_TEMPLATE = Template(
    """### Release Approval Check Results

**Target Branch:** {{ base_branch }}

{% if all_approved -%}
✅ **Status:** All modules have required approvals
{% else -%}
❌ **Status:** Some modules are missing required approvals
{% endif %}
#### Modules:
{% for module in modules -%}
{{ module }}
{% endfor -%}
"""
)


@dataclass
class ModuleResult:
    """Results of checking a module's reviews."""

    maintainers: list[dict[str, Any]]
    approved_maintainers: list[int]
    approved_usernames: list[str]
    disapproved_maintainers: list[int]
    disapproved_usernames: list[str]
    has_approval: bool
    has_disapproval: bool
    status: str  # 'approved', 'disapproved', or 'pending'


def _find_repo_root() -> Path:
    candidate = Path(__file__).resolve()
    for parent in candidate.parents:
        if (parent / "known_good.json").exists():
            return parent
    return Path.cwd()


def fetch_maintainers(known_good_path: Path) -> dict[str, list[dict[str, Any]]]:
    """Fetch maintainers from module metadata files.

    Returns:
        Dictionary mapping module names to lists of maintainer information.
    """
    known_good = load_known_good(known_good_path)
    sw_modules = known_good.modules.get("target_sw", {}).keys()

    # Add subset of tooling modules
    modules = list(sw_modules) + [
        "score_docs_as_code",
        "score_platform",
        "score_itf",
        "score_test_scenarios",
    ]

    modules_maintainers: dict[str, list[dict[str, Any]]] = {}

    for module_name in modules:
        try:
            url = f"https://raw.githubusercontent.com/eclipse-score/bazel_registry/main/modules/{module_name}/metadata.json"
            with urlopen(url) as response:
                data = json.loads(response.read())

            if "maintainers" in data and isinstance(data["maintainers"], list):
                modules_maintainers[module_name] = data["maintainers"]
                print(f"{module_name} maintainers: {data['maintainers']}", file=sys.stderr)
            else:
                print(f"Warning: No maintainers found for {module_name}", file=sys.stderr)
                modules_maintainers[module_name] = []
        except (URLError, json.JSONDecodeError) as error:
            print(f"Error fetching {module_name}: {error}", file=sys.stderr)
            modules_maintainers[module_name] = []

    # Add extra maintainers
    # TODO: move it to single config file
    modules_maintainers["Testing"] = [
        {
            "name": "Piotr Korkus",
            "email": "piotr.korkus.ext@qorix.ai",
            "github": "PiotrKorkus",
            "github_user_id": 209438333,
        }
    ]

    modules_maintainers["Infrastructure"] = [
        {
            "name": "Alexander Lanin",
            "email": "alexander.lanin@etas.com",
            "github": "AlexanderLanin",
            "github_user_id": 5074553,
        }
    ]

    modules_maintainers["Technical_Leads"] = [
        {
            "name": "Anton Krivoborodov",
            "email": "anton.krivoborodov@bmw.de",
            "github": "antonkri",
            "github_user_id": 63401640,
        },
        {
            "name": "Frank Scholter Peres",
            "email": "frank.scholter_peres@mercedes-benz.com",
            "github": "FScholPer",
            "github_user_id": 145544737,
        },
        {
            "name": "Lars Bauhofer",
            "email": "lars.bauhofer@qorix.ai",
            "github": "qor-lb",
            "github_user_id": 155632781,
        },
    ]

    return modules_maintainers


def check_pr_reviews(
    repo_owner: str,
    repo_name: str,
    pr_number: int,
    modules_maintainers: dict[str, list[dict[str, Any]]],
    github_token: str,
) -> dict[str, Any]:
    """Check PR reviews against required maintainers.

    Args:
        repo_owner: Repository owner (organization or user)
        repo_name: Repository name
        pr_number: Pull request number
        modules_maintainers: Dictionary mapping module names to maintainer lists
        github_token: GitHub authentication token

    Returns:
        Dictionary containing approval results for all modules
    """
    # Initialize GitHub client
    auth = Auth.Token(github_token)
    github = Github(auth=auth)

    # Get repository and pull request
    repo = github.get_repo(f"{repo_owner}/{repo_name}")
    pr = repo.get_pull(pr_number)

    # Get all reviews for this PR
    reviews = list(pr.get_reviews())

    print(f"Modules and their maintainers: {json.dumps(modules_maintainers, indent=2)}", file=sys.stderr)

    # Get the latest review state from each user
    latest_reviews_by_user: dict[int, Any] = {}
    for review in reviews:
        user_id = review.user.id
        submitted_at = review.submitted_at

        if user_id not in latest_reviews_by_user or latest_reviews_by_user[user_id].submitted_at < submitted_at:
            latest_reviews_by_user[user_id] = review

    review_summary = ", ".join([f"{user_id}: {review.state}" for user_id, review in latest_reviews_by_user.items()])
    print(f"Reviews by user ID: {review_summary}", file=sys.stderr)

    # Check which modules have at least one approval and no disapprovals
    module_results: dict[str, ModuleResult] = {}
    approved_modules: list[str] = []
    not_approved_modules: list[str] = []
    disapproved_modules: list[str] = []

    for module_name, maintainers in modules_maintainers.items():
        approved_maintainer_ids: list[int] = []
        approved_usernames: list[str] = []
        disapproved_maintainer_ids: list[int] = []
        disapproved_usernames: list[str] = []

        for maintainer in maintainers:
            if isinstance(maintainer, dict):
                maintainer_id = maintainer["github_user_id"]
                maintainer_username = maintainer["github"]
            else:
                maintainer_id = maintainer
                maintainer_username = str(maintainer)

            if maintainer_id in latest_reviews_by_user:
                user_review = latest_reviews_by_user[maintainer_id]
                if user_review.state == "APPROVED":
                    approved_maintainer_ids.append(maintainer_id)
                    approved_usernames.append(maintainer_username)
                elif user_review.state == "CHANGES_REQUESTED":
                    disapproved_maintainer_ids.append(maintainer_id)
                    disapproved_usernames.append(maintainer_username)

        # If any maintainer disapproved, the module is disapproved
        has_disapproval = len(disapproved_maintainer_ids) > 0
        has_approval = len(approved_maintainer_ids) > 0

        if has_disapproval:
            status = "disapproved"
        elif has_approval:
            status = "approved"
        else:
            status = "pending"

        module_results[module_name] = ModuleResult(
            maintainers=maintainers,
            approved_maintainers=approved_maintainer_ids,
            approved_usernames=approved_usernames,
            disapproved_maintainers=disapproved_maintainer_ids,
            disapproved_usernames=disapproved_usernames,
            has_approval=has_approval,
            has_disapproval=has_disapproval,
            status=status,
        )

        if has_disapproval:
            disapproved_modules.append(module_name)
            not_approved_modules.append(module_name)
            print(f"🚫 {module_name}: Changes requested by {', '.join(disapproved_usernames)}", file=sys.stderr)
        elif has_approval:
            approved_modules.append(module_name)
            print(f"✅ {module_name}: Approved by {', '.join(approved_usernames)}", file=sys.stderr)
        else:
            not_approved_modules.append(module_name)
            maintainer_usernames = [m["github"] if isinstance(m, dict) else str(m) for m in maintainers]
            required_str = f"requires one of: {', '.join(maintainer_usernames)}"
            print(f"❌ {module_name}: No approvals ({required_str})", file=sys.stderr)

    all_approved = len(not_approved_modules) == 0

    # Convert ModuleResult objects to dicts for JSON serialization
    module_results_dict = {
        name: {
            "maintainers": result.maintainers,
            "approvedMaintainers": result.approved_maintainers,
            "approvedUsernames": result.approved_usernames,
            "disapprovedMaintainers": result.disapproved_maintainers,
            "disapprovedUsernames": result.disapproved_usernames,
            "hasApproval": result.has_approval,
            "hasDisapproval": result.has_disapproval,
            "status": result.status,
        }
        for name, result in module_results.items()
    }

    return {
        "moduleResults": module_results_dict,
        "approvedModules": approved_modules,
        "notApprovedModules": not_approved_modules,
        "disapprovedModules": disapproved_modules,
        "allApproved": all_approved,
    }


def _format_module_status(module_name: str, result: dict[str, Any]) -> str:
    """Format a single module's approval status as markdown.

    Args:
        module_name: Name of the module
        result: Module result dictionary containing status and approver information

    Returns:
        Markdown-formatted status line
    """
    required_approvers = [m["github"] if isinstance(m, dict) else str(m) for m in result["maintainers"]]

    return MODULE_STATUS_TEMPLATE.render(
        module_name=module_name,
        status=result["status"],
        approved_usernames=result["approvedUsernames"],
        disapproved_usernames=result["disapprovedUsernames"],
        required_approvers=required_approvers,
    )


def _write_github_actions_summary(summary: str) -> None:
    """Write summary to GitHub Actions step summary if available.

    Args:
        summary: Markdown-formatted summary text
    """
    if "GITHUB_STEP_SUMMARY" in os.environ:
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write(summary)
            f.write("\n")


def _post_pr_comment(
    summary: str,
    repo_owner: str,
    repo_name: str,
    pr_number: int,
    github_token: str,
) -> None:
    """Post or update PR comment with approval summary.

    Args:
        summary: Markdown-formatted summary text
        repo_owner: Repository owner
        repo_name: Repository name
        pr_number: Pull request number
        github_token: GitHub authentication token
    """
    try:
        auth = Auth.Token(github_token)
        github = Github(auth=auth)
        repo = github.get_repo(f"{repo_owner}/{repo_name}")
        pr = repo.get_pull(pr_number)

        comment_marker = "<!-- release-approval-check -->"
        full_comment = f"{comment_marker}\n{summary}"

        # Find existing comment from this workflow
        existing_comment = None
        for comment in pr.get_issue_comments():
            if comment_marker in comment.body:
                existing_comment = comment
                break

        # Update existing or create new comment
        if existing_comment:
            existing_comment.edit(full_comment)
            print("Updated existing PR comment", file=sys.stderr)
        else:
            pr.create_issue_comment(full_comment)
            print("Created new PR comment", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Failed to post PR comment: {e}", file=sys.stderr)


def _build_summary_markdown(
    module_results: dict[str, dict[str, Any]],
    all_approved: bool,
    base_branch: str,
) -> str:
    """Build the markdown summary text.

    Args:
        module_results: Dictionary of module approval results
        all_approved: Whether all modules are approved
        base_branch: Target branch of the PR

    Returns:
        Markdown-formatted summary string
    """
    modules = [_format_module_status(module_name, result) for module_name, result in module_results.items()]

    return SUMMARY_TEMPLATE.render(
        base_branch=base_branch,
        all_approved=all_approved,
        modules=modules,
    )


def generate_summary(
    module_results: dict[str, dict[str, Any]],
    all_approved: bool,
    base_branch: str,
    repo_owner: str | None = None,
    repo_name: str | None = None,
    pr_number: int | None = None,
    github_token: str | None = None,
) -> str:
    """Generate a markdown summary of approval results.

    Args:
        module_results: Dictionary of module approval results
        all_approved: Whether all modules are approved
        base_branch: Target branch of the PR
        repo_owner: Repository owner (for posting comments)
        repo_name: Repository name (for posting comments)
        pr_number: Pull request number (for posting comments)
        github_token: GitHub authentication token (for posting comments)

    Returns:
        Markdown-formatted summary string
    """
    summary = _build_summary_markdown(module_results, all_approved, base_branch)

    _write_github_actions_summary(summary)

    if all([repo_owner, repo_name, pr_number, github_token]):
        _post_pr_comment(summary, repo_owner, repo_name, pr_number, github_token)

    return summary


def cmd_fetch_maintainers(known_good_path: Path) -> None:
    """Command: Fetch maintainers."""
    modules_maintainers = fetch_maintainers(known_good_path)
    print(json.dumps(modules_maintainers, indent=2))


def cmd_check_all(known_good_path: Path) -> int:
    """Command: Run all steps (fetch, check, summarize).

    Returns:
        Exit code: 0 if all approved, 1 otherwise
    """
    # Get required parameters from environment variables
    repo_owner = os.environ.get("REPO_OWNER", "")
    repo_name = os.environ.get("REPO_NAME", "")
    pr_number = int(os.environ.get("PR_NUMBER", "0"))
    base_branch = os.environ.get("BASE_BRANCH", "unknown")
    github_token = os.environ.get("GITHUB_TOKEN", "")

    if not all([repo_owner, repo_name, pr_number, github_token]):
        print("Error: Missing required environment variables", file=sys.stderr)
        print("Required: REPO_OWNER, REPO_NAME, PR_NUMBER, GITHUB_TOKEN", file=sys.stderr)
        print("Optional: BASE_BRANCH (defaults to 'unknown')", file=sys.stderr)
        return 1

    # Step 1: Fetch maintainers
    print("=== Fetching maintainers ===", file=sys.stderr)
    modules_maintainers = fetch_maintainers(known_good_path)

    # Step 2: Check PR reviews
    print("\n=== Checking PR reviews ===", file=sys.stderr)
    results = check_pr_reviews(
        repo_owner=repo_owner,
        repo_name=repo_name,
        pr_number=pr_number,
        modules_maintainers=modules_maintainers,
        github_token=github_token,
    )

    # Step 3: Generate summary
    print("\n=== Generating summary ===", file=sys.stderr)
    summary = generate_summary(
        module_results=results["moduleResults"],
        all_approved=results["allApproved"],
        base_branch=base_branch,
        repo_owner=repo_owner,
        repo_name=repo_name,
        pr_number=pr_number,
        github_token=github_token,
    )

    # Set GitHub Actions outputs if running in GitHub Actions
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"approved-modules={', '.join(results['approvedModules'])}\n")
            f.write(f"not-approved-modules={', '.join(results['notApprovedModules'])}\n")
            f.write(f"disapproved-modules={', '.join(results['disapprovedModules'])}\n")
            f.write(f"all-approved={'true' if results['allApproved'] else 'false'}\n")

    # Exit with error if not all approved
    if not results["allApproved"]:
        print("\n" + summary, file=sys.stderr)
        return 1
    else:
        print("\n" + summary)
        return 0


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register this command as a subparser."""
    parser = subparsers.add_parser(
        "check_approvals",
        help="Check release branch PR approvals against required maintainers",
    )
    parser.add_argument(
        "--known_good",
        metavar="PATH",
        default=str(_find_repo_root()),
        help="Directory containing known_good.json (default: repo root)",
    )
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    """Run the command with parsed arguments.

    Returns:
        Exit code: 0 on success, 1 on failure
    """
    known_good_path = Path(args.known_good) / "known_good.json"

    # Check if running in GitHub Actions (primary use case)
    if all(var in os.environ for var in ["REPO_OWNER", "REPO_NAME", "PR_NUMBER", "GITHUB_TOKEN"]):
        return cmd_check_all(known_good_path)
    else:
        print("Error: Missing required environment variables", file=sys.stderr)
        print("Required: REPO_OWNER, REPO_NAME, PR_NUMBER, GITHUB_TOKEN", file=sys.stderr)
        print("Optional: BASE_BRANCH (defaults to 'unknown')", file=sys.stderr)
        return 1


def main() -> None:
    print("This script should be run via `bazel` as part of CICD")


if __name__ == "__main__":
    main()
