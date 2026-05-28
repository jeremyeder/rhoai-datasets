"""GitHub API connector."""

from __future__ import annotations

import re
from datetime import UTC, datetime

from github import Github

from datasets.metadata.schema import CandidateArtifact, SourceType

_TEST_FILE_RE = re.compile(r"(^|/)tests?[/_]|_test\.|test_", re.IGNORECASE)
_DOCS_CONFIG_RE = re.compile(
    r"\.(md|txt|yaml|yml|json|toml|cfg|ini|lock)$"
    r"|^(README|LICENSE|CHANGELOG|OWNERS|CODEOWNERS|\.)",
    re.IGNORECASE,
)
MAX_SOURCE_FILES = 50


def _parse_since(since: str | None) -> datetime | None:
    if not since:
        return None
    return datetime.fromisoformat(since).replace(tzinfo=UTC)


def _has_test_files(filenames: list[str]) -> bool:
    return any(_TEST_FILE_RE.search(f) for f in filenames)


def _is_docs_config_only(filenames: list[str]) -> bool:
    return all(_DOCS_CONFIG_RE.search(f) for f in filenames)


def _source_file_count(filenames: list[str]) -> int:
    return sum(1 for f in filenames if not _TEST_FILE_RE.search(f))


class GitHubConnector:
    def __init__(self, token: str, repo: str) -> None:
        self._gh = Github(token)
        self._repo_name = repo
        self._repo = self._gh.get_repo(repo)

    @property
    def name(self) -> str:
        return "github"

    def scan(
        self,
        artifact_types: list[str] | None = None,
        state: str | None = None,
        limit: int = 100,
        **kwargs: str,
    ) -> list[CandidateArtifact]:
        types = artifact_types or ["pr"]
        since = kwargs.get("since")
        candidates: list[CandidateArtifact] = []

        if "pr" in types:
            candidates.extend(
                self._scan_prs(
                    state=state or "closed",
                    limit=limit,
                    since=since,
                )
            )
        if "issue" in types:
            candidates.extend(
                self._scan_issues(
                    state=state or "closed",
                    limit=limit,
                    since=since,
                )
            )

        return candidates[:limit]

    def _scan_prs(
        self,
        state: str,
        limit: int,
        since: str | None = None,
    ) -> list[CandidateArtifact]:
        candidates: list[CandidateArtifact] = []
        since_dt = _parse_since(since)
        prs = self._repo.get_pulls(state=state, sort="updated", direction="desc")

        for pr in prs[: limit * 3]:
            if since_dt and pr.updated_at < since_dt:
                break
            if not pr.merged:
                continue
            file_list = list(pr.get_files())
            files = [f.filename for f in file_list]

            if not _has_test_files(files):
                continue
            if _is_docs_config_only(files):
                continue
            if _source_file_count(files) > MAX_SOURCE_FILES:
                continue

            patches = {f.filename: (f.patch or "") for f in file_list}
            commit_messages = [c.commit.message for c in pr.get_commits()]

            candidates.append(
                CandidateArtifact(
                    source_type=SourceType.github_pr,
                    source_url=pr.html_url,
                    title=pr.title,
                    description=pr.body or "",
                    raw_data={
                        "number": pr.number,
                        "state": pr.state,
                        "merged": getattr(pr, "merged", False),
                        "files": files,
                        "patches": patches,
                        "commit_messages": commit_messages,
                    },
                )
            )

            if len(candidates) >= limit:
                break

        return candidates

    def _scan_issues(
        self,
        state: str,
        limit: int,
        since: str | None = None,
    ) -> list[CandidateArtifact]:
        candidates: list[CandidateArtifact] = []
        since_dt = _parse_since(since)
        issues = self._repo.get_issues(state=state, sort="updated", direction="desc")

        for issue in issues[: limit * 3]:
            if since_dt and issue.updated_at < since_dt:
                break
            if issue.pull_request:
                continue
            candidates.append(
                CandidateArtifact(
                    source_type=SourceType.github_issue,
                    source_url=issue.html_url,
                    title=issue.title,
                    description=issue.body or "",
                    raw_data={
                        "number": issue.number,
                        "state": issue.state,
                        "labels": [label.name for label in issue.labels],
                    },
                )
            )

            if len(candidates) >= limit:
                break

        return candidates
