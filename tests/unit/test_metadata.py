"""tests/unit/test_metadata.py"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from datasets.metadata.schema import (
    AIDetectionResult,
    CandidateArtifact,
    DatasetEntry,
    DatasetMetadata,
    DifficultyLevel,
    EvalType,
    SourceType,
    SuitabilityScore,
)


def test_candidate_artifact_minimum_valid():
    c = CandidateArtifact(
        source_type=SourceType.github_pr,
        source_url="https://github.com/org/repo/pull/42",
        title="Fix null pointer in auth handler",
        description="Fixes NPE when user has no session",
    )
    assert c.source_type == SourceType.github_pr
    assert c.ai_detection is None


def test_candidate_artifact_with_ai_detection():
    c = CandidateArtifact(
        source_type=SourceType.github_pr,
        source_url="https://github.com/org/repo/pull/42",
        title="Fix auth bug",
        description="Fixes auth",
        ai_detection=AIDetectionResult(
            overall_score=85,
            per_artifact_scores={"src/auth.py": 95, "README.md": 10},
            method="llm-as-judge",
            model="claude-sonnet-4-6",
        ),
    )
    assert c.ai_detection.overall_score == 85
    assert c.ai_detection.per_artifact_scores["src/auth.py"] == 95


def test_suitability_score_validates_range():
    s = SuitabilityScore(
        clarity=80,
        verifiability=90,
        difficulty=50,
        domain_relevance=70,
        completeness=60,
    )
    assert 0 <= s.overall <= 100

    with pytest.raises(ValidationError):
        SuitabilityScore(
            clarity=150,
            verifiability=90,
            difficulty=50,
            domain_relevance=70,
            completeness=60,
        )


def test_dataset_metadata_minimum_valid():
    m = DatasetMetadata(
        name="auth-bugfixes-v1",
        description="Authentication bug fixes from RHOAI",
        domain="security",
        eval_type=EvalType.agent_coding,
        difficulty=DifficultyLevel.medium,
        entries=[
            DatasetEntry(
                candidate_url="https://github.com/org/repo/pull/42",
                ai_generation_score=85,
                domain_tags=["auth", "security"],
                difficulty=DifficultyLevel.medium,
            ),
        ],
        curator="jeder",
    )
    assert len(m.entries) == 1
    assert m.eval_type == EvalType.agent_coding


def test_dataset_metadata_rejects_empty_entries():
    with pytest.raises(ValidationError):
        DatasetMetadata(
            name="empty",
            description="No entries",
            domain="test",
            eval_type=EvalType.agent_coding,
            difficulty=DifficultyLevel.easy,
            entries=[],
            curator="nobody",
        )


def test_eval_type_enum_values():
    assert EvalType.agent_coding.value == "agent_coding"
    assert EvalType.model_quality.value == "model_quality"
    assert EvalType.safety.value == "safety"
    assert EvalType.skills_effectiveness.value == "skills_effectiveness"
