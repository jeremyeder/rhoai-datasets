"""tests/unit/test_connectors.py"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from datasets.connectors.base import SourceConnector
from datasets.connectors.github import GitHubConnector
from datasets.metadata.schema import SourceType


def test_connector_protocol():
    """SourceConnector defines the expected interface."""
    assert hasattr(SourceConnector, "scan")
    assert hasattr(SourceConnector, "name")


def test_github_connector_scan_prs():
    """GitHubConnector.scan returns CandidateArtifacts from PRs."""
    mock_pr = MagicMock()
    mock_pr.number = 42
    mock_pr.title = "Fix null pointer in auth"
    mock_pr.body = "Fixes NPE when user session is missing"
    mock_pr.html_url = "https://github.com/org/repo/pull/42"
    mock_pr.state = "closed"
    mock_pr.merged = True
    mock_pr.get_files.return_value = [
        MagicMock(
            filename="src/auth.py",
            patch="@@ -10,3 +10,5 @@\n+if session is None:\n+    raise AuthError()",
        ),
    ]
    mock_pr.get_commits.return_value = [
        MagicMock(
            commit=MagicMock(
                message="fix: handle null session\n\nCo-Authored-By: Claude <noreply@anthropic.com>"
            )
        ),
    ]

    mock_repo = MagicMock()
    mock_repo.get_pulls.return_value = [mock_pr]

    with patch("datasets.connectors.github.Github") as mock_github:
        mock_github.return_value.get_repo.return_value = mock_repo
        connector = GitHubConnector(token="fake", repo="org/repo")
        candidates = connector.scan(artifact_types=["pr"], state="closed", limit=10)

    assert len(candidates) == 1
    assert candidates[0].source_type == SourceType.github_pr
    assert candidates[0].title == "Fix null pointer in auth"
    assert "Co-Authored-By" in str(candidates[0].raw_data.get("commit_messages", ""))


def test_github_connector_name():
    with patch("datasets.connectors.github.Github"):
        connector = GitHubConnector(token="fake", repo="org/repo")
    assert connector.name == "github"


def test_jira_connector_scan_bugs():
    from datasets.connectors.jira import JiraConnector

    mock_issue = MagicMock()
    mock_issue.key = "RHOAIENG-1234"
    mock_issue.fields.summary = "Auth middleware NPE on expired sessions"
    mock_issue.fields.description = (
        "Steps to reproduce: 1. Login 2. Wait for session expiry 3. Click any link"
    )
    mock_issue.fields.issuetype.name = "Bug"
    mock_issue.fields.status.name = "Closed"
    mock_issue.fields.resolution.name = "Done"
    mock_issue.fields.priority.name = "Critical"
    mock_issue.permalink.return_value = "https://issues.redhat.com/browse/RHOAIENG-1234"
    mock_issue.fields.labels = ["security"]

    with patch("datasets.connectors.jira.JIRA") as mock_jira:
        mock_jira.return_value.search_issues.return_value = [mock_issue]
        connector = JiraConnector(
            server="https://issues.redhat.com", token="fake", project="RHOAIENG"
        )
        candidates = connector.scan(artifact_types=["bug"], limit=10)

    assert len(candidates) == 1
    assert candidates[0].source_type == SourceType.jira_issue
    assert "NPE" in candidates[0].title
    assert candidates[0].raw_data["issue_type"] == "Bug"


def test_jira_connector_name():
    from datasets.connectors.jira import JiraConnector

    with patch("datasets.connectors.jira.JIRA"):
        connector = JiraConnector(
            server="https://issues.redhat.com", token="fake", project="TEST"
        )
    assert connector.name == "jira"
