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
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from scripts.tooling.cli.release.check_approvals import check_pr_reviews


def _create_mock_review(user_id: int, username: str, state: str, submitted_at: datetime) -> Mock:
    """Create a mock GitHub review object.

    Args:
        user_id: GitHub user ID
        username: GitHub username
        state: Review state (APPROVED, CHANGES_REQUESTED, etc.)
        submitted_at: Timestamp of review submission

    Returns:
        Mock review object
    """
    review = Mock()
    review.user = Mock()
    review.user.id = user_id
    review.user.login = username
    review.state = state
    review.submitted_at = submitted_at
    return review


@patch("scripts.tooling.cli.release.check_approvals.Github")
def test_check_pr_reviews_all_approved(mock_github_class, modules_maintainers):
    """Test when all modules have required approvals."""
    # Setup mock GitHub API
    mock_github = MagicMock()
    mock_github_class.return_value = mock_github
    mock_repo = MagicMock()
    mock_github.get_repo.return_value = mock_repo
    mock_pr = MagicMock()
    mock_repo.get_pull.return_value = mock_pr

    # Create mock reviews - one approval per module
    reviews = [
        _create_mock_review(100, "alice", "APPROVED", datetime(2026, 1, 1, 10, 0)),  # module_a
        _create_mock_review(102, "charlie", "APPROVED", datetime(2026, 1, 1, 11, 0)),  # module_b
        _create_mock_review(103, "diana", "APPROVED", datetime(2026, 1, 1, 12, 0)),  # module_c
    ]
    mock_pr.get_reviews.return_value = reviews

    # Run the function
    result = check_pr_reviews(
        repo_owner="test-org",
        repo_name="test-repo",
        pr_number=123,
        modules_maintainers=modules_maintainers,
        github_token="test-token",
    )

    # Verify results
    assert result["allApproved"] is True
    assert len(result["approvedModules"]) == 3
    assert "module_a" in result["approvedModules"]
    assert "module_b" in result["approvedModules"]
    assert "module_c" in result["approvedModules"]
    assert len(result["notApprovedModules"]) == 0
    assert len(result["disapprovedModules"]) == 0

    # Verify module results
    assert result["moduleResults"]["module_a"]["status"] == "approved"
    assert result["moduleResults"]["module_a"]["hasApproval"] is True
    assert result["moduleResults"]["module_a"]["hasDisapproval"] is False
    assert "alice" in result["moduleResults"]["module_a"]["approvedUsernames"]


@patch("scripts.tooling.cli.release.check_approvals.Github")
def test_check_pr_reviews_no_approvals(mock_github_class, modules_maintainers):
    """Test when no modules have approvals."""
    # Setup mock GitHub API
    mock_github = MagicMock()
    mock_github_class.return_value = mock_github
    mock_repo = MagicMock()
    mock_github.get_repo.return_value = mock_repo
    mock_pr = MagicMock()
    mock_repo.get_pull.return_value = mock_pr

    # No reviews
    mock_pr.get_reviews.return_value = []

    # Run the function
    result = check_pr_reviews(
        repo_owner="test-org",
        repo_name="test-repo",
        pr_number=123,
        modules_maintainers=modules_maintainers,
        github_token="test-token",
    )

    # Verify results
    assert result["allApproved"] is False
    assert len(result["approvedModules"]) == 0
    assert len(result["notApprovedModules"]) == 3
    assert "module_a" in result["notApprovedModules"]
    assert "module_b" in result["notApprovedModules"]
    assert "module_c" in result["notApprovedModules"]

    # Verify module results
    for module_name in ["module_a", "module_b", "module_c"]:
        assert result["moduleResults"][module_name]["status"] == "pending"
        assert result["moduleResults"][module_name]["hasApproval"] is False
        assert result["moduleResults"][module_name]["hasDisapproval"] is False


@patch("scripts.tooling.cli.release.check_approvals.Github")
def test_check_pr_reviews_with_changes_requested(mock_github_class, modules_maintainers):
    """Test when some modules have changes requested."""
    # Setup mock GitHub API
    mock_github = MagicMock()
    mock_github_class.return_value = mock_github
    mock_repo = MagicMock()
    mock_github.get_repo.return_value = mock_repo
    mock_pr = MagicMock()
    mock_repo.get_pull.return_value = mock_pr

    # Create mock reviews - mix of approved and changes requested
    reviews = [
        _create_mock_review(100, "alice", "APPROVED", datetime(2026, 1, 1, 10, 0)),  # module_a approved
        _create_mock_review(102, "charlie", "CHANGES_REQUESTED", datetime(2026, 1, 1, 11, 0)),  # module_b blocked
        _create_mock_review(103, "diana", "APPROVED", datetime(2026, 1, 1, 12, 0)),  # module_c approved
    ]
    mock_pr.get_reviews.return_value = reviews

    # Run the function
    result = check_pr_reviews(
        repo_owner="test-org",
        repo_name="test-repo",
        pr_number=123,
        modules_maintainers=modules_maintainers,
        github_token="test-token",
    )

    # Verify results
    assert result["allApproved"] is False
    assert len(result["approvedModules"]) == 2
    assert "module_a" in result["approvedModules"]
    assert "module_c" in result["approvedModules"]
    assert len(result["disapprovedModules"]) == 1
    assert "module_b" in result["disapprovedModules"]
    assert "module_b" in result["notApprovedModules"]

    # Verify module results
    assert result["moduleResults"]["module_b"]["status"] == "disapproved"
    assert result["moduleResults"]["module_b"]["hasDisapproval"] is True
    assert "charlie" in result["moduleResults"]["module_b"]["disapprovedUsernames"]


@patch("scripts.tooling.cli.release.check_approvals.Github")
def test_check_pr_reviews_latest_review_wins(mock_github_class, modules_maintainers):
    """Test that the latest review from a user takes precedence."""
    # Setup mock GitHub API
    mock_github = MagicMock()
    mock_github_class.return_value = mock_github
    mock_repo = MagicMock()
    mock_github.get_repo.return_value = mock_repo
    mock_pr = MagicMock()
    mock_repo.get_pull.return_value = mock_pr

    # Create mock reviews - same user reviews multiple times
    reviews = [
        # Alice reviews module_a multiple times - latest is APPROVED
        _create_mock_review(100, "alice", "CHANGES_REQUESTED", datetime(2026, 1, 1, 10, 0)),
        _create_mock_review(100, "alice", "APPROVED", datetime(2026, 1, 1, 12, 0)),  # Latest wins
        # Charlie reviews module_b multiple times - latest is CHANGES_REQUESTED
        _create_mock_review(102, "charlie", "APPROVED", datetime(2026, 1, 1, 11, 0)),
        _create_mock_review(102, "charlie", "CHANGES_REQUESTED", datetime(2026, 1, 1, 13, 0)),  # Latest wins
        # Diana approves module_c
        _create_mock_review(103, "diana", "APPROVED", datetime(2026, 1, 1, 12, 0)),
    ]
    mock_pr.get_reviews.return_value = reviews

    # Run the function
    result = check_pr_reviews(
        repo_owner="test-org",
        repo_name="test-repo",
        pr_number=123,
        modules_maintainers=modules_maintainers,
        github_token="test-token",
    )

    # Verify results - latest reviews should be used
    assert result["moduleResults"]["module_a"]["status"] == "approved"
    assert result["moduleResults"]["module_a"]["hasApproval"] is True
    assert result["moduleResults"]["module_a"]["hasDisapproval"] is False

    assert result["moduleResults"]["module_b"]["status"] == "disapproved"
    assert result["moduleResults"]["module_b"]["hasDisapproval"] is True

    assert result["moduleResults"]["module_c"]["status"] == "approved"


@patch("scripts.tooling.cli.release.check_approvals.Github")
def test_check_pr_reviews_multiple_maintainers_one_approval(mock_github_class, modules_maintainers):
    """Test that only one maintainer approval is needed per module."""
    # Setup mock GitHub API
    mock_github = MagicMock()
    mock_github_class.return_value = mock_github
    mock_repo = MagicMock()
    mock_github.get_repo.return_value = mock_repo
    mock_pr = MagicMock()
    mock_repo.get_pull.return_value = mock_pr

    # module_a has two maintainers (alice=100, bob=101), only alice approves
    # module_c has two maintainers (diana=103, eve=104), only diana approves
    reviews = [
        _create_mock_review(100, "alice", "APPROVED", datetime(2026, 1, 1, 10, 0)),  # module_a
        _create_mock_review(102, "charlie", "APPROVED", datetime(2026, 1, 1, 11, 0)),  # module_b
        _create_mock_review(103, "diana", "APPROVED", datetime(2026, 1, 1, 12, 0)),  # module_c
    ]
    mock_pr.get_reviews.return_value = reviews

    # Run the function
    result = check_pr_reviews(
        repo_owner="test-org",
        repo_name="test-repo",
        pr_number=123,
        modules_maintainers=modules_maintainers,
        github_token="test-token",
    )

    # Verify results - one approval per module is sufficient
    assert result["allApproved"] is True
    assert len(result["approvedModules"]) == 3


@patch("scripts.tooling.cli.release.check_approvals.Github")
def test_check_pr_reviews_approval_with_disapproval(mock_github_class, modules_maintainers):
    """Test that a disapproval blocks approval even if another maintainer approved."""
    # Setup mock GitHub API
    mock_github = MagicMock()
    mock_github_class.return_value = mock_github
    mock_repo = MagicMock()
    mock_github.get_repo.return_value = mock_repo
    mock_pr = MagicMock()
    mock_repo.get_pull.return_value = mock_pr

    # module_a: alice approves, bob requests changes
    # module_c: diana approves, eve requests changes
    reviews = [
        _create_mock_review(100, "alice", "APPROVED", datetime(2026, 1, 1, 10, 0)),
        _create_mock_review(101, "bob", "CHANGES_REQUESTED", datetime(2026, 1, 1, 11, 0)),
        _create_mock_review(102, "charlie", "APPROVED", datetime(2026, 1, 1, 11, 0)),
        _create_mock_review(103, "diana", "APPROVED", datetime(2026, 1, 1, 12, 0)),
        _create_mock_review(104, "eve", "CHANGES_REQUESTED", datetime(2026, 1, 1, 13, 0)),
    ]
    mock_pr.get_reviews.return_value = reviews

    # Run the function
    result = check_pr_reviews(
        repo_owner="test-org",
        repo_name="test-repo",
        pr_number=123,
        modules_maintainers=modules_maintainers,
        github_token="test-token",
    )

    # Verify results - disapprovals should block
    assert result["allApproved"] is False
    assert len(result["disapprovedModules"]) == 2
    assert "module_a" in result["disapprovedModules"]
    assert "module_c" in result["disapprovedModules"]

    # Verify module states
    assert result["moduleResults"]["module_a"]["status"] == "disapproved"
    assert result["moduleResults"]["module_a"]["hasApproval"] is True
    assert result["moduleResults"]["module_a"]["hasDisapproval"] is True
    assert "alice" in result["moduleResults"]["module_a"]["approvedUsernames"]
    assert "bob" in result["moduleResults"]["module_a"]["disapprovedUsernames"]

    # module_b should still be approved
    assert result["moduleResults"]["module_b"]["status"] == "approved"
    assert "module_b" in result["approvedModules"]


@patch("scripts.tooling.cli.release.check_approvals.Github")
def test_check_pr_reviews_non_maintainer_reviews(mock_github_class, modules_maintainers):
    """Test that reviews from non-maintainers are ignored."""
    # Setup mock GitHub API
    mock_github = MagicMock()
    mock_github_class.return_value = mock_github
    mock_repo = MagicMock()
    mock_github.get_repo.return_value = mock_repo
    mock_pr = MagicMock()
    mock_repo.get_pull.return_value = mock_pr

    # Reviews from non-maintainers (user_id 999, 998)
    reviews = [
        _create_mock_review(999, "random-user", "APPROVED", datetime(2026, 1, 1, 10, 0)),
        _create_mock_review(998, "another-user", "CHANGES_REQUESTED", datetime(2026, 1, 1, 11, 0)),
        # Actual maintainer reviews
        _create_mock_review(100, "alice", "APPROVED", datetime(2026, 1, 1, 12, 0)),  # module_a
        _create_mock_review(102, "charlie", "APPROVED", datetime(2026, 1, 1, 13, 0)),  # module_b
        _create_mock_review(103, "diana", "APPROVED", datetime(2026, 1, 1, 14, 0)),  # module_c
    ]
    mock_pr.get_reviews.return_value = reviews

    # Run the function
    result = check_pr_reviews(
        repo_owner="test-org",
        repo_name="test-repo",
        pr_number=123,
        modules_maintainers=modules_maintainers,
        github_token="test-token",
    )

    # Verify results - only maintainer reviews count
    assert result["allApproved"] is True
    assert len(result["approvedModules"]) == 3

    # Verify that non-maintainer user IDs don't appear in results
    for module_result in result["moduleResults"].values():
        assert 999 not in module_result["approvedMaintainers"]
        assert 999 not in module_result["disapprovedMaintainers"]
        assert 998 not in module_result["approvedMaintainers"]
        assert 998 not in module_result["disapprovedMaintainers"]


@patch("scripts.tooling.cli.release.check_approvals.Github")
def test_check_pr_reviews_empty_maintainers(mock_github_class):
    """Test handling of modules with no maintainers."""
    # Setup mock GitHub API
    mock_github = MagicMock()
    mock_github_class.return_value = mock_github
    mock_repo = MagicMock()
    mock_github.get_repo.return_value = mock_repo
    mock_pr = MagicMock()
    mock_repo.get_pull.return_value = mock_pr

    # Some reviews
    reviews = [
        _create_mock_review(100, "alice", "APPROVED", datetime(2026, 1, 1, 10, 0)),
    ]
    mock_pr.get_reviews.return_value = reviews

    # Module with no maintainers
    modules_maintainers = {
        "module_no_maintainers": [],
    }

    # Run the function
    result = check_pr_reviews(
        repo_owner="test-org",
        repo_name="test-repo",
        pr_number=123,
        modules_maintainers=modules_maintainers,
        github_token="test-token",
    )

    # Verify results - module with no maintainers should be pending
    assert result["allApproved"] is False
    assert "module_no_maintainers" in result["notApprovedModules"]
    assert result["moduleResults"]["module_no_maintainers"]["status"] == "pending"
    assert result["moduleResults"]["module_no_maintainers"]["hasApproval"] is False


@patch("scripts.tooling.cli.release.check_approvals.Github")
def test_check_pr_reviews_mixed_scenario(mock_github_class, modules_maintainers):
    """Test a complex mixed scenario with various states."""
    # Setup mock GitHub API
    mock_github = MagicMock()
    mock_github_class.return_value = mock_github
    mock_repo = MagicMock()
    mock_github.get_repo.return_value = mock_repo
    mock_pr = MagicMock()
    mock_repo.get_pull.return_value = mock_pr

    # Complex scenario:
    # module_a: approved by alice
    # module_b: no reviews (pending)
    # module_c: diana approved, eve requested changes (disapproved)
    reviews = [
        _create_mock_review(100, "alice", "APPROVED", datetime(2026, 1, 1, 10, 0)),
        _create_mock_review(103, "diana", "APPROVED", datetime(2026, 1, 1, 12, 0)),
        _create_mock_review(104, "eve", "CHANGES_REQUESTED", datetime(2026, 1, 1, 13, 0)),
    ]
    mock_pr.get_reviews.return_value = reviews

    # Run the function
    result = check_pr_reviews(
        repo_owner="test-org",
        repo_name="test-repo",
        pr_number=123,
        modules_maintainers=modules_maintainers,
        github_token="test-token",
    )

    # Verify results
    assert result["allApproved"] is False

    # module_a: approved
    assert "module_a" in result["approvedModules"]
    assert result["moduleResults"]["module_a"]["status"] == "approved"

    # module_b: pending
    assert "module_b" in result["notApprovedModules"]
    assert result["moduleResults"]["module_b"]["status"] == "pending"

    # module_c: disapproved
    assert "module_c" in result["disapprovedModules"]
    assert "module_c" in result["notApprovedModules"]
    assert result["moduleResults"]["module_c"]["status"] == "disapproved"
