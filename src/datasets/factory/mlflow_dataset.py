"""src/datasets/factory/mlflow_dataset.py -- MLflow evaluation dataset output."""

from __future__ import annotations

import json
from pathlib import Path

from datasets.metadata.schema import CandidateArtifact


class MLflowDatasetFactory:
    @property
    def format_name(self) -> str:
        return "mlflow"

    def create(
        self,
        candidate: CandidateArtifact,
        output_dir: Path,
        task_name: str,
    ) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{task_name}.jsonl"

        record = {
            "inputs": {
                "task_description": candidate.description,
                "title": candidate.title,
                "files": candidate.raw_data.get("files", []),
            },
            "expectations": {
                "task_completed": True,
                "files_modified": candidate.raw_data.get("files", []),
            },
            "tags": {
                "source_url": candidate.source_url,
                "source_type": candidate.source_type.value,
                "ai_generation_score": (
                    candidate.ai_detection.overall_score
                    if candidate.ai_detection
                    else None
                ),
            },
        }

        with output_path.open("w") as f:
            f.write(json.dumps(record) + "\n")

        return output_path
