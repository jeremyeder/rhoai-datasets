"""tests/unit/test_mlflow_factory.py"""

from __future__ import annotations

import json

from datasets.factory.mlflow_dataset import MLflowDatasetFactory
from datasets.metadata.schema import CandidateArtifact, SourceType


def _make_candidate() -> CandidateArtifact:
    return CandidateArtifact(
        source_type=SourceType.github_pr,
        source_url="https://github.com/org/repo/pull/42",
        title="Fix auth handler NPE",
        description="Fix null pointer when session expires. Added null check before session access.",
        raw_data={
            "merged": True,
            "files": ["src/auth.py", "tests/test_auth.py"],
            "patches": {"src/auth.py": "+if session is None:\n+    raise AuthError()"},
        },
    )


def test_mlflow_factory_creates_jsonl(tmp_path):
    factory = MLflowDatasetFactory()
    candidate = _make_candidate()
    output_path = factory.create(
        candidate, output_dir=tmp_path, task_name="fix-auth-npe"
    )

    assert output_path.suffix == ".jsonl"
    assert output_path.is_file()

    with output_path.open() as f:
        lines = f.readlines()
    assert len(lines) >= 1

    record = json.loads(lines[0])
    assert "inputs" in record
    assert "expectations" in record
    assert "tags" in record


def test_mlflow_factory_record_structure(tmp_path):
    factory = MLflowDatasetFactory()
    candidate = _make_candidate()
    output_path = factory.create(
        candidate, output_dir=tmp_path, task_name="fix-auth-npe"
    )

    with output_path.open() as f:
        record = json.loads(f.readline())

    assert "task_description" in record["inputs"]
    assert "source_url" in record["tags"]
    assert "source_type" in record["tags"]


def test_mlflow_factory_format_name():
    factory = MLflowDatasetFactory()
    assert factory.format_name == "mlflow"
