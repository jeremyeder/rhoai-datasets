"""src/datasets/factory/skillsbench.py -- SkillsBench task output format."""

from __future__ import annotations

from pathlib import Path

from datasets.factory.harbor import HarborTaskFactory
from datasets.metadata.schema import CandidateArtifact


class SkillsBenchTaskFactory(HarborTaskFactory):
    @property
    def format_name(self) -> str:
        return "skillsbench"

    def create(
        self,
        candidate: CandidateArtifact,
        output_dir: Path,
        task_name: str,
    ) -> Path:
        task_dir = super().create(candidate, output_dir, task_name)

        skills_dir = task_dir / "environment" / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)

        return task_dir
