"""src/datasets/connectors/jira.py -- Jira API connector."""

from __future__ import annotations

from jira import JIRA

from datasets.metadata.schema import CandidateArtifact, SourceType

ARTIFACT_TYPE_TO_JQL = {
    "bug": "issuetype = Bug",
    "story": "issuetype = Story",
    "task": "issuetype = Task",
    "feature": "issuetype in (Feature, Epic)",
}


class JiraConnector:
    def __init__(self, server: str, token: str, project: str) -> None:
        self._jira = JIRA(server=server, token_auth=token)
        self._project = project

    @property
    def name(self) -> str:
        return "jira"

    def scan(
        self,
        artifact_types: list[str] | None = None,
        state: str | None = None,
        limit: int = 100,
        **kwargs: str,
    ) -> list[CandidateArtifact]:
        types = artifact_types or ["bug"]
        type_clauses = [ARTIFACT_TYPE_TO_JQL.get(t, f"issuetype = {t}") for t in types]
        type_jql = " OR ".join(type_clauses)

        jql = f"project = {self._project} AND ({type_jql})"
        if state:
            jql += f" AND status = '{state}'"
        else:
            jql += " AND status in (Closed, Done, Resolved)"
        jql += " ORDER BY updated DESC"

        issues = self._jira.search_issues(jql, maxResults=limit)
        candidates: list[CandidateArtifact] = []

        for issue in issues:
            candidates.append(
                CandidateArtifact(
                    source_type=SourceType.jira_issue,
                    source_url=issue.permalink(),
                    title=issue.fields.summary,
                    description=issue.fields.description or "",
                    raw_data={
                        "key": issue.key,
                        "issue_type": issue.fields.issuetype.name,
                        "status": issue.fields.status.name,
                        "resolution": getattr(issue.fields.resolution, "name", None),
                        "priority": getattr(issue.fields.priority, "name", None),
                        "labels": list(issue.fields.labels),
                    },
                )
            )

        return candidates
