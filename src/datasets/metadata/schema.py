"""src/datasets/metadata/schema.py -- Pydantic models for dataset metadata."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class SourceType(StrEnum):
    github_pr = "github_pr"
    github_issue = "github_issue"
    github_commit = "github_commit"
    jira_issue = "jira_issue"
    confluence_page = "confluence_page"
    cve = "cve"
    compliance = "compliance"


class EvalType(StrEnum):
    agent_coding = "agent_coding"
    model_quality = "model_quality"
    safety = "safety"
    skills_effectiveness = "skills_effectiveness"


class DifficultyLevel(StrEnum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class AIDetectionResult(BaseModel):
    overall_score: float = Field(ge=0.0, le=1.0)
    per_artifact_scores: dict[str, float] = Field(default_factory=dict)
    method: str = "llm-as-judge"
    model: str = ""


class SuitabilityScore(BaseModel):
    clarity: float = Field(ge=0.0, le=1.0)
    verifiability: float = Field(ge=0.0, le=1.0)
    difficulty: float = Field(ge=0.0, le=1.0)
    domain_relevance: float = Field(ge=0.0, le=1.0)
    completeness: float = Field(ge=0.0, le=1.0)

    @property
    def overall(self) -> float:
        weights = {
            "clarity": 0.25,
            "verifiability": 0.30,
            "difficulty": 0.15,
            "domain_relevance": 0.15,
            "completeness": 0.15,
        }
        return sum(getattr(self, k) * w for k, w in weights.items())


class CandidateArtifact(BaseModel):
    source_type: SourceType
    source_url: str
    title: str
    description: str
    raw_data: dict = Field(default_factory=dict)
    suitability: SuitabilityScore | None = None
    ai_detection: AIDetectionResult | None = None
    suggested_eval_type: EvalType | None = None


class DatasetEntry(BaseModel):
    candidate_url: str
    ai_generation_score: float = Field(ge=0.0, le=1.0)
    domain_tags: list[str] = Field(default_factory=list)
    difficulty: DifficultyLevel = DifficultyLevel.medium


class DatasetMetadata(BaseModel):
    name: str
    description: str
    domain: str
    eval_type: EvalType
    difficulty: DifficultyLevel
    entries: list[DatasetEntry] = Field(min_length=1)
    curator: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    provenance: dict[str, str] = Field(default_factory=dict)

    @field_validator("entries")
    @classmethod
    def entries_not_empty(cls, v: list[DatasetEntry]) -> list[DatasetEntry]:
        if not v:
            raise ValueError("Dataset must have at least one entry")
        return v
