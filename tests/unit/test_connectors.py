"""tests/unit/test_connectors.py"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from datasets.connectors.base import SourceConnector
from datasets.connectors.github import GitHubConnector
from datasets.metadata.schema import SourceType


def _mock_pr(
    number: int,
    title: str,
    body: str,
    files: list[str],
    merged: bool = True,
) -> MagicMock:
    pr = MagicMock()
    pr.number = number
    pr.title = title
    pr.body = body
    pr.html_url = f"https://github.com/org/repo/pull/{number}"
    pr.state = "closed"
    pr.merged = merged
    pr.get_files.return_value = [
        MagicMock(filename=f, patch=f"+change in {f}") for f in files
    ]
    pr.get_commits.return_value = [MagicMock(commit=MagicMock(message=f"fix: {title}"))]
    return pr


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
        MagicMock(
            filename="tests/test_auth.py",
            patch="+def test_fix(): ...",
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


def test_github_connector_skips_prs_without_tests():
    """PRs that don't touch any test files are excluded."""
    pr_with_tests = _mock_pr(
        1,
        "Fix auth with tests",
        "Adds test coverage",
        ["src/auth.py", "tests/test_auth.py"],
    )
    pr_without_tests = _mock_pr(
        2,
        "Bump version",
        "Version bump",
        ["setup.py"],
    )

    mock_repo = MagicMock()
    mock_repo.get_pulls.return_value = [pr_with_tests, pr_without_tests]

    with patch("datasets.connectors.github.Github") as mock_github:
        mock_github.return_value.get_repo.return_value = mock_repo
        connector = GitHubConnector(token="fake", repo="org/repo")
        candidates = connector.scan(artifact_types=["pr"], limit=10)

    assert len(candidates) == 1
    assert candidates[0].title == "Fix auth with tests"


def test_github_connector_skips_docs_only_prs():
    """PRs touching only docs/config files are excluded."""
    pr_docs_only = _mock_pr(
        1,
        "Update README",
        "Docs update",
        ["README.md", "CHANGELOG.md", ".github/workflows/ci.yml"],
    )
    pr_with_code = _mock_pr(
        2,
        "Fix bug",
        "Bug fix with tests",
        ["src/handler.py", "tests/test_handler.py"],
    )

    mock_repo = MagicMock()
    mock_repo.get_pulls.return_value = [pr_docs_only, pr_with_code]

    with patch("datasets.connectors.github.Github") as mock_github:
        mock_github.return_value.get_repo.return_value = mock_repo
        connector = GitHubConnector(token="fake", repo="org/repo")
        candidates = connector.scan(artifact_types=["pr"], limit=10)

    assert len(candidates) == 1
    assert candidates[0].title == "Fix bug"


def test_github_connector_skips_oversized_prs():
    """PRs touching too many source files are excluded."""
    many_files = [f"src/file{i}.py" for i in range(60)] + ["tests/test_all.py"]
    pr_oversized = _mock_pr(3, "Giant refactor", "Touches everything", many_files)
    pr_normal = _mock_pr(
        4,
        "Small fix",
        "Targeted fix",
        ["src/auth.py", "tests/test_auth.py"],
    )

    mock_repo = MagicMock()
    mock_repo.get_pulls.return_value = [pr_oversized, pr_normal]

    with patch("datasets.connectors.github.Github") as mock_github:
        mock_github.return_value.get_repo.return_value = mock_repo
        connector = GitHubConnector(token="fake", repo="org/repo")
        candidates = connector.scan(artifact_types=["pr"], limit=10)

    assert len(candidates) == 1
    assert candidates[0].title == "Small fix"


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
