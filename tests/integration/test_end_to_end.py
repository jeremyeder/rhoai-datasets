"""tests/integration/test_end_to_end.py -- Full pipeline test with mocked connectors."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

from datasets.connectors.base import SourceConnector
from datasets.factory.harbor import HarborTaskFactory
from datasets.factory.mlflow_dataset import MLflowDatasetFactory
from datasets.factory.skillsbench import SkillsBenchTaskFactory
from datasets.metadata.schema import CandidateArtifact, SourceType
from datasets.recommender.pipeline import RecommenderPipeline


def _make_realistic_candidates() -> list[CandidateArtifact]:
    return [
        CandidateArtifact(
            source_type=SourceType.github_pr,
            source_url="https://github.com/org/repo/pull/42",
            title="Fix NPE in session handler",
            description="## Problem\nNull pointer when session expires.\n\n## Steps\n1. Login\n2. Wait\n3. Crash\n\n## Fix\nAdded null check.",
            raw_data={
                "merged": True,
                "files": ["src/session.py", "tests/test_session.py"],
                "patches": {
                    "src/session.py": "+if not session:\n+    return redirect('/login')"
                },
                "commit_messages": [
                    "fix: handle expired session\n\nCo-Authored-By: Claude <noreply@anthropic.com>"
                ],
            },
        ),
        CandidateArtifact(
            source_type=SourceType.jira_issue,
            source_url="https://issues.redhat.com/browse/RHOAIENG-5678",
            title="Improve performance",
            description="Make it faster.",
            raw_data={"issue_type": "Story", "resolution": "Won't Fix"},
        ),
    ]


def test_full_pipeline_to_harbor(tmp_path):
    """End-to-end: scan -> score -> filter -> create Harbor tasks."""
    mock_connector = MagicMock(spec=SourceConnector)
    mock_connector.scan.return_value = _make_realistic_candidates()

    pipeline = RecommenderPipeline(connectors=[mock_connector], skip_ai_detection=True)
    results = pipeline.run(limit=10, min_suitability=0.4)

    assert len(results) >= 1
    best = results[0]
    assert best.suitability.overall > 0.5

    factory = HarborTaskFactory()
    task_dir = factory.create(best, output_dir=tmp_path, task_name="fix-session-npe")

    assert (task_dir / "instruction.md").is_file()
    assert (task_dir / "task.toml").is_file()
    assert (task_dir / "environment" / "Dockerfile").is_file()


def test_full_pipeline_to_mlflow(tmp_path):
    """End-to-end: scan -> score -> filter -> create MLflow dataset."""
    mock_connector = MagicMock(spec=SourceConnector)
    mock_connector.scan.return_value = _make_realistic_candidates()

    pipeline = RecommenderPipeline(connectors=[mock_connector], skip_ai_detection=True)
    results = pipeline.run(limit=10, min_suitability=0.4)

    factory = MLflowDatasetFactory()
    output = factory.create(
        results[0], output_dir=tmp_path, task_name="fix-session-npe"
    )

    with output.open() as f:
        record = json.loads(f.readline())
    assert "inputs" in record
    assert record["tags"]["source_type"] == "github_pr"


def test_full_pipeline_to_skillsbench(tmp_path):
    """End-to-end: scan -> score -> filter -> create SkillsBench tasks."""
    mock_connector = MagicMock(spec=SourceConnector)
    mock_connector.scan.return_value = _make_realistic_candidates()

    pipeline = RecommenderPipeline(connectors=[mock_connector], skip_ai_detection=True)
    results = pipeline.run(limit=10, min_suitability=0.4)

    factory = SkillsBenchTaskFactory()
    task_dir = factory.create(
        results[0], output_dir=tmp_path, task_name="fix-session-npe"
    )

    assert (task_dir / "environment" / "skills").is_dir()


def test_vague_candidates_filtered_out():
    """Vague candidates with low suitability are filtered."""
    mock_connector = MagicMock(spec=SourceConnector)
    mock_connector.scan.return_value = _make_realistic_candidates()

    pipeline = RecommenderPipeline(connectors=[mock_connector], skip_ai_detection=True)
    results = pipeline.run(limit=10, min_suitability=0.6)

    titles = [c.title for c in results]
    assert "Improve performance" not in titles
