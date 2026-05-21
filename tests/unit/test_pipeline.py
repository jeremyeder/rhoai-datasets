"""tests/unit/test_pipeline.py"""

from __future__ import annotations

from unittest.mock import MagicMock

from datasets.connectors.base import SourceConnector
from datasets.metadata.schema import CandidateArtifact, SourceType
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
    results = pipeline.run(limit=10, min_suitability=0.5)

    assert len(results) <= 2
    assert all(c.suitability.overall >= 0.5 for c in results)
