"""src/datasets/metadata/catalog.py -- Dataset catalog management."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class CatalogEntry(BaseModel):
    name: str
    source: str
    source_url: str
    task_count: int = Field(ge=0)
    domain: list[str] = Field(default_factory=list)
    difficulty_profile: str = "medium"
    format: str = "harbor"
    applicability: str = ""


class DatasetCatalog(BaseModel):
    entries: list[CatalogEntry] = Field(default_factory=list)

    @classmethod
    def load(cls, directory: Path) -> DatasetCatalog:
        entries: list[CatalogEntry] = []
        if not directory.is_dir():
            return cls(entries=[])
        for yaml_file in sorted(directory.glob("*.yaml")):
            with yaml_file.open() as f:
                data = yaml.safe_load(f)
            if data:
                entries.append(CatalogEntry(**data))
        return cls(entries=entries)

    def filter(
        self,
        domain: str | None = None,
        format: str | None = None,
        difficulty: str | None = None,
        min_tasks: int | None = None,
    ) -> list[CatalogEntry]:
        results = self.entries
        if domain:
            results = [e for e in results if domain in e.domain]
        if format:
            results = [e for e in results if e.format == format]
        if difficulty:
            results = [e for e in results if e.difficulty_profile == difficulty]
        if min_tasks is not None:
            results = [e for e in results if e.task_count >= min_tasks]
        return results

    def save(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        for entry in self.entries:
            path = directory / f"{entry.name}.yaml"
            with path.open("w") as f:
                yaml.dump(
                    entry.model_dump(), f, default_flow_style=False, sort_keys=False
                )
