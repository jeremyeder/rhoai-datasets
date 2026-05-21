"""src/datasets/factory/base.py -- DatasetFactory protocol."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from datasets.metadata.schema import CandidateArtifact


@runtime_checkable
class DatasetFactory(Protocol):
    @property
    def format_name(self) -> str: ...

    def create(
        self,
        candidate: CandidateArtifact,
        output_dir: Path,
        task_name: str,
    ) -> Path: ...
