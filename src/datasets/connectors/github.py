"""src/datasets/connectors/github.py -- GitHub API connector."""

from __future__ import annotations

from github import Github

from datasets.metadata.schema import CandidateArtifact, SourceType


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
        candidates: list[CandidateArtifact] = []

        if "pr" in types:
            candidates.extend(self._scan_prs(state=state or "closed", limit=limit))
        if "issue" in types:
            candidates.extend(self._scan_issues(state=state or "closed", limit=limit))

        return candidates[:limit]

    def _scan_prs(self, state: str, limit: int) -> list[CandidateArtifact]:
        candidates: list[CandidateArtifact] = []
        prs = self._repo.get_pulls(state=state, sort="updated", direction="desc")

        for pr in prs[:limit]:
            file_list = list(pr.get_files())
            files = [f.filename for f in file_list]
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

        return candidates

    def _scan_issues(self, state: str, limit: int) -> list[CandidateArtifact]:
        candidates: list[CandidateArtifact] = []
        issues = self._repo.get_issues(state=state, sort="updated", direction="desc")

        for issue in issues[:limit]:
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

        return candidates
