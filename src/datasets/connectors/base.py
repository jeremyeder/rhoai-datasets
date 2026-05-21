"""src/datasets/connectors/base.py -- SourceConnector protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from datasets.metadata.schema import CandidateArtifact


@runtime_checkable
class SourceConnector(Protocol):
    @property
    def name(self) -> str: ...

    def scan(
        self,
        artifact_types: list[str] | None = None,
        state: str | None = None,
        limit: int = 100,
        **kwargs: str,
    ) -> list[CandidateArtifact]: ...
