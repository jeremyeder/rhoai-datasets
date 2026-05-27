# rhai-datasets

Dataset creation and curation platform for Red Hat AI evaluation.

## Setup
- `uv sync` -- install dependencies
- `uv sync --extra all` -- install all optional dependencies (github, jira, mlflow)
- Set `ANTHROPIC_API_KEY` for AI-content detection (required unless --skip-ai-detection)
- Set `GITHUB_TOKEN` for GitHub connector

## Commands
- `uv run pytest` -- run tests
- `uv run ruff check src/ tests/` -- lint
- `uv run mypy src/` -- type check
- `uv run datasets recommend --source github --repo org/repo` -- scan for candidates
- `uv run datasets recommend --source github --repo org/repo --since 2025-01-01` -- scan with date filter
- `uv run datasets create --from-file candidates.json --format harbor` -- create datasets
- `uv run datasets catalog list` -- browse external dataset catalog

## Workflow
1. Scan source for candidates: `uv run datasets recommend --source github --repo org/name -o candidates.json`
2. Review/filter candidates.json (edit or process externally)
3. Create datasets: `uv run datasets create --from-file candidates.json --format harbor -o output/`

## Architecture
- `src/datasets/connectors/` -- pluggable source connectors (GitHub, Jira)
  - Protocol-based: all implement `SourceConnector` (name, scan method)
  - GitHubConnector scans PRs/issues, JiraConnector scans tickets
- `src/datasets/recommender/` -- suitability scoring + AI-content detection pipeline
  - Pipeline: orchestrates scoring → AI detection → ranking
  - Scorer: 5 dimensions (clarity, verifiability, difficulty, domain_relevance, completeness)
  - AI detection: LLM-as-judge pattern using Claude API (requires ANTHROPIC_API_KEY)
- `src/datasets/factory/` -- format-specific output (Harbor, SkillsBench, MLflow)
  - Protocol-based: all implement `DatasetFactory` (format_name, create method)
  - Each factory transforms CandidateArtifact → format-specific output
- `src/datasets/metadata/` -- Pydantic schemas and catalog management
  - CandidateArtifact: core data model for candidates
  - SuitabilityScore, AIDetectionResult: scoring models
- `catalog/external/` -- YAML entries for reviewed external datasets

## Conventions
- Python 3.11+, strict mypy, ruff for formatting
- Use `uv` not `pip`
- Pydantic v2 for all data models
- Tests in `tests/unit/` and `tests/integration/`

## Gotchas
- ANTHROPIC_API_KEY required for AI detection (skip with --skip-ai-detection)
- Always use `uv run datasets`, not bare `datasets` or `python -m datasets`
- Connectors and factories use Protocol pattern (runtime_checkable) not inheritance
  - Exception: SkillsBenchTaskFactory inherits from HarborTaskFactory (shared structure)
- Scoring is multi-dimensional: overall = weighted avg of 5 signals
- GitHub connector filters out PRs when scanning issues
- Enums use StrEnum (Python 3.11+), not `str, enum.Enum`
- 10 E501 line-length violations remain in string literals (intentional — shell scripts and prompts)
- 8 mypy errors remain (missing stubs for yaml, untyped jira call, Any return, PyGithub annotations, cli arg-type)
