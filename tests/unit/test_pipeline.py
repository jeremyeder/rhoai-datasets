"""tests/unit/test_pipeline.py"""

from __future__ import annotations

from unittest.mock import MagicMock

from datasets.connectors.base import SourceConnector
from datasets.metadata.schema import CandidateArtifact, DifficultyLevel, SourceType
from datasets.recommender.pipeline import RecommenderPipeline


def _make_candidate(title: str, description: str, **raw: object) -> CandidateArtifact:
    return CandidateArtifact(
        source_type=SourceType.github_pr,
        source_url="https://github.com/org/repo/pull/1",
        title=title,
        description=description,
        raw_data=dict(raw),
    )


def test_pipeline_scores_and_ranks():
    candidates = [
        _make_candidate("Vague thing", "Do stuff", merged=False),
        _make_candidate(
            "Fix NPE in auth",
            "## Steps\n1. Login\n2. Wait\n3. Click\n\n## Fix\nNull check added.",
            merged=True,
            files=["src/auth.py", "tests/test_auth.py"],
            patches={"src/auth.py": "+if s is None:"},
        ),
    ]

    mock_connector = MagicMock(spec=SourceConnector)
    mock_connector.scan.return_value = candidates

    pipeline = RecommenderPipeline(connectors=[mock_connector], skip_ai_detection=True)
    results = pipeline.run(limit=10, min_suitability=0.0)

    assert len(results) == 2
    assert all(c.suitability is not None for c in results)
    assert results[0].suitability.overall >= results[1].suitability.overall


def test_pipeline_filters_by_min_suitability():
    candidates = [
        _make_candidate("Vague", "x"),
        _make_candidate(
            "Good fix",
            "Detailed fix with steps.",
            merged=True,
            files=["a.py", "test_a.py"],
            patches={"a.py": "+fix"},
        ),
    ]

    mock_connector = MagicMock(spec=SourceConnector)
    mock_connector.scan.return_value = candidates

    pipeline = RecommenderPipeline(connectors=[mock_connector], skip_ai_detection=True)
    results = pipeline.run(limit=10, min_suitability=50)

    assert len(results) <= 2
    assert all(c.suitability.overall >= 50 for c in results)


def test_pipeline_assigns_difficulty_bucket():
    small_pr = _make_candidate(
        "Tiny fix",
        "One-liner.",
        merged=True,
        files=["src/a.py"],
        patches={"src/a.py": "+x = 1"},
    )
    large_pr = _make_candidate(
        "Major refactor",
        "Rewrites the auth system with new middleware.",
        merged=True,
        files=[f"src/{c}.py" for c in "abcdefghij"] + ["tests/test_a.py"],
        patches={
            f"src/{c}.py": "\n".join(f"+line{i}" for i in range(80))
            for c in "abcdefghij"
        },
    )

    mock_connector = MagicMock(spec=SourceConnector)
    mock_connector.scan.return_value = [small_pr, large_pr]

    pipeline = RecommenderPipeline(connectors=[mock_connector], skip_ai_detection=True)
    results = pipeline.run(limit=10, min_suitability=0.0)

    assert all(c.difficulty_bucket is not None for c in results)
    buckets = {c.title: c.difficulty_bucket for c in results}
    assert buckets["Tiny fix"] == DifficultyLevel.easy
    assert buckets["Major refactor"] == DifficultyLevel.hard
