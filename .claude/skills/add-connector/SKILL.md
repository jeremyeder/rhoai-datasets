---
name: add-connector
description: Scaffold a new source connector following the SourceConnector protocol pattern with matching tests. Use when adding support for a new data source (Confluence, CVE database, compliance framework, etc.).
---

# Add Connector

Scaffold a new source connector for the rhai-datasets recommender.

## Input

The user provides the name of the data source (e.g., "confluence", "cve", "bugzilla").

## Protocol

All connectors implement the `SourceConnector` protocol from `src/datasets/connectors/base.py`:

```python
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
```

## Steps

1. **Create the connector** at `src/datasets/connectors/{name}.py`:
   - Class named `{Name}Connector`
   - Constructor takes auth credentials and scope (e.g., space key, project)
   - `name` property returns the lowercase name
   - `scan()` method queries the API and returns `list[CandidateArtifact]`
   - Each candidate gets appropriate `SourceType` (add new enum value to schema.py if needed)
   - `raw_data` dict captures source-specific fields useful for scoring

2. **Add tests** to `tests/unit/test_connectors.py`:
   - Mock the external API client
   - Test scan returns correct CandidateArtifacts
   - Test connector name property
   - Test error handling for auth failures

3. **Update eval type heuristics** in `src/datasets/recommender/pipeline.py`:
   - Add mapping from the new SourceType to appropriate EvalType in `EVAL_TYPE_HEURISTICS`

4. **Update CLI** in `src/datasets/cli.py`:
   - Add the new source to the `--source` choice list in the `recommend` command
   - Add connector instantiation logic

5. **Run tests**: `uv run pytest tests/ -v`

## Reference: Existing Connectors

- `src/datasets/connectors/github.py` — GitHubConnector (PyGithub)
- `src/datasets/connectors/jira.py` — JiraConnector (jira library)

Follow the same patterns: constructor takes credentials + scope, scan returns CandidateArtifacts with rich raw_data.
