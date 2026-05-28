"""src/datasets/recommender/pipeline.py -- Recommender pipeline orchestration."""

from __future__ import annotations

from datasets.connectors.base import SourceConnector
from datasets.metadata.schema import (
    CandidateArtifact,
    DifficultyLevel,
    EvalType,
    SourceType,
)
from datasets.recommender.scorer import score_candidate

EVAL_TYPE_HEURISTICS: dict[SourceType, EvalType] = {
    SourceType.github_pr: EvalType.agent_coding,
    SourceType.github_issue: EvalType.agent_coding,
    SourceType.github_commit: EvalType.agent_coding,
    SourceType.jira_issue: EvalType.agent_coding,
    SourceType.cve: EvalType.safety,
    SourceType.compliance: EvalType.safety,
    SourceType.confluence_page: EvalType.model_quality,
}


def _bucket_difficulty(score: float) -> DifficultyLevel:
    if score < 35:
        return DifficultyLevel.easy
    if score < 65:
        return DifficultyLevel.medium
    return DifficultyLevel.hard


class RecommenderPipeline:
    def __init__(
        self,
        connectors: list[SourceConnector],
        skip_ai_detection: bool = False,
    ) -> None:
        self._connectors = connectors
        self._skip_ai_detection = skip_ai_detection

    def run(
        self,
        limit: int = 100,
        min_suitability: float = 0.0,
        artifact_types: list[str] | None = None,
        **kwargs: str,
    ) -> list[CandidateArtifact]:
        all_candidates: list[CandidateArtifact] = []

        for connector in self._connectors:
            candidates = connector.scan(
                artifact_types=artifact_types,
                limit=limit,
                **kwargs,
            )
            all_candidates.extend(candidates)

        for candidate in all_candidates:
            candidate.suitability = score_candidate(candidate)
            candidate.difficulty_bucket = _bucket_difficulty(
                candidate.suitability.difficulty
            )
            candidate.suggested_eval_type = EVAL_TYPE_HEURISTICS.get(
                candidate.source_type, EvalType.agent_coding
            )

        if not self._skip_ai_detection:
            self._run_ai_detection(all_candidates)

        filtered = [
            c
            for c in all_candidates
            if c.suitability is not None and c.suitability.overall >= min_suitability
        ]

        filtered.sort(
            key=lambda c: c.suitability.overall if c.suitability else 0.0,
            reverse=True,
        )
        return filtered[:limit]

    def _run_ai_detection(self, candidates: list[CandidateArtifact]) -> None:
        from datasets.recommender.ai_detection import detect_ai_content

        for candidate in candidates:
            artifacts: dict[str, str] = {}
            patches = candidate.raw_data.get("patches", {})
            if patches:
                artifacts.update(patches)
            if not artifacts and candidate.description:
                artifacts["description"] = candidate.description

            if artifacts:
                candidate.ai_detection = detect_ai_content(artifacts)
