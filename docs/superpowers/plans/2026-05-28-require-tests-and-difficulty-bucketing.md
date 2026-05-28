# Require Tests + Difficulty Bucketing + Real Test Extraction

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the GitHub connector only return merged PRs that include test files, add difficulty bucketing to candidates, and have the Harbor factory extract real test files from PR diffs instead of writing placeholder stubs.

**Architecture:** Three changes across the scan → score → create pipeline: (1) the GitHub connector filters PRs to those containing test files, (2) the scorer's existing `_score_difficulty` is mapped to easy/medium/hard buckets and stored on the candidate, (3) the Harbor factory parses `patches` for test files and writes them into `tests/` instead of stubs.

**Tech Stack:** Python 3.11+, Pydantic v2, pytest, Click CLI

---

### Task 1: Filter GitHub connector to only return PRs with test files

**Files:**
- Modify: `src/datasets/connectors/github.py:58-98`
- Modify: `tests/unit/test_connectors.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/unit/test_connectors.py`:

```python
def test_github_connector_skips_prs_without_tests():
    """PRs that don't touch any test files are excluded."""
    mock_pr_with_tests = MagicMock()
    mock_pr_with_tests.number = 1
    mock_pr_with_tests.title = "Fix auth with tests"
    mock_pr_with_tests.body = "Adds test coverage"
    mock_pr_with_tests.html_url = "https://github.com/org/repo/pull/1"
    mock_pr_with_tests.state = "closed"
    mock_pr_with_tests.merged = True
    mock_pr_with_tests.get_files.return_value = [
        MagicMock(filename="src/auth.py", patch="+fix"),
        MagicMock(filename="tests/test_auth.py", patch="+def test_fix(): ..."),
    ]
    mock_pr_with_tests.get_commits.return_value = [
        MagicMock(commit=MagicMock(message="fix: auth"))
    ]

    mock_pr_without_tests = MagicMock()
    mock_pr_without_tests.number = 2
    mock_pr_without_tests.title = "Bump version"
    mock_pr_without_tests.body = "Version bump"
    mock_pr_without_tests.html_url = "https://github.com/org/repo/pull/2"
    mock_pr_without_tests.state = "closed"
    mock_pr_without_tests.merged = True
    mock_pr_without_tests.get_files.return_value = [
        MagicMock(filename="setup.py", patch="+version='2.0'"),
    ]
    mock_pr_without_tests.get_commits.return_value = [
        MagicMock(commit=MagicMock(message="chore: bump"))
    ]

    mock_repo = MagicMock()
    mock_repo.get_pulls.return_value = [mock_pr_with_tests, mock_pr_without_tests]

    with patch("datasets.connectors.github.Github") as mock_github:
        mock_github.return_value.get_repo.return_value = mock_repo
        connector = GitHubConnector(token="fake", repo="org/repo")
        candidates = connector.scan(artifact_types=["pr"], limit=10)

    assert len(candidates) == 1
    assert candidates[0].title == "Fix auth with tests"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_connectors.py::test_github_connector_skips_prs_without_tests -v`
Expected: FAIL — returns 2 candidates instead of 1

- [ ] **Step 3: Implement the filter**

In `src/datasets/connectors/github.py`, add the `_has_test_files` helper and use it in `_scan_prs`:

```python
import re

def _has_test_files(filenames: list[str]) -> bool:
    return any(
        re.search(r"(^|/)tests?[/_]|_test\.|test_", f, re.IGNORECASE)
        for f in filenames
    )
```

In `_scan_prs`, after building `files` (line 74), add:

```python
            if not _has_test_files(files):
                continue
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_connectors.py -v`
Expected: All pass

- [ ] **Step 5: Commit**

```bash
git add src/datasets/connectors/github.py tests/unit/test_connectors.py
git commit -m "feat: filter GitHub connector to only return PRs with test files"
```

---

### Task 2: Add difficulty bucketing to candidates

The existing `_score_difficulty` in `scorer.py` produces a 0-1 float. We need to map that to easy/medium/hard and store it on the candidate so the output can be bucketed. The `DifficultyLevel` enum already exists in schema.py.

**Files:**
- Modify: `src/datasets/recommender/pipeline.py:46-49`
- Modify: `src/datasets/metadata/schema.py:60-68` (add `difficulty_bucket` field to `CandidateArtifact`)
- Modify: `tests/unit/test_pipeline.py`

- [ ] **Step 1: Add `difficulty_bucket` field to CandidateArtifact**

In `src/datasets/metadata/schema.py`, add to the `CandidateArtifact` model:

```python
class CandidateArtifact(BaseModel):
    source_type: SourceType
    source_url: str
    title: str
    description: str
    raw_data: dict = Field(default_factory=dict)
    suitability: SuitabilityScore | None = None
    ai_detection: AIDetectionResult | None = None
    suggested_eval_type: EvalType | None = None
    difficulty_bucket: DifficultyLevel | None = None
```

- [ ] **Step 2: Write the failing test**

Add to `tests/unit/test_pipeline.py`:

```python
from datasets.metadata.schema import DifficultyLevel


def test_pipeline_assigns_difficulty_bucket():
    small_pr = _make_candidate(
        "Tiny fix",
        "One-liner.",
        merged=True,
        files=["src/a.py"],
        patches={"src/a.py": "+x = 1"},
    )
    large_pr = _make_candidate(
        "Major refactor",
        "Rewrites the auth system with new middleware.",
        merged=True,
        files=[f"src/{c}.py" for c in "abcdefghij"] + ["tests/test_a.py"],
        patches={f"src/{c}.py": "\n".join(f"+line{i}" for i in range(80)) for c in "abcdefghij"},
    )

    mock_connector = MagicMock(spec=SourceConnector)
    mock_connector.scan.return_value = [small_pr, large_pr]

    pipeline = RecommenderPipeline(connectors=[mock_connector], skip_ai_detection=True)
    results = pipeline.run(limit=10, min_suitability=0.0)

    assert all(c.difficulty_bucket is not None for c in results)
    buckets = {c.title: c.difficulty_bucket for c in results}
    assert buckets["Tiny fix"] == DifficultyLevel.easy
    assert buckets["Major refactor"] == DifficultyLevel.hard
```

- [ ] **Step 3: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_pipeline.py::test_pipeline_assigns_difficulty_bucket -v`
Expected: FAIL — `difficulty_bucket` is None for all candidates

- [ ] **Step 4: Implement bucketing in the pipeline**

In `src/datasets/recommender/pipeline.py`, import `DifficultyLevel` and add bucketing logic after scoring:

```python
from datasets.metadata.schema import CandidateArtifact, DifficultyLevel, EvalType, SourceType


def _bucket_difficulty(score: float) -> DifficultyLevel:
    if score < 0.35:
        return DifficultyLevel.easy
    if score < 0.65:
        return DifficultyLevel.medium
    return DifficultyLevel.hard
```

In the `run` method, after `candidate.suitability = score_candidate(candidate)`, add:

```python
            candidate.difficulty_bucket = _bucket_difficulty(candidate.suitability.difficulty)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_pipeline.py -v`
Expected: All pass

- [ ] **Step 6: Commit**

```bash
git add src/datasets/metadata/schema.py src/datasets/recommender/pipeline.py tests/unit/test_pipeline.py
git commit -m "feat: add difficulty bucketing (easy/medium/hard) to candidates"
```

---

### Task 3: Use difficulty bucket in Harbor task.toml output

**Files:**
- Modify: `src/datasets/factory/harbor.py:41-67` (`_write_toml`)
- Modify: `tests/unit/test_harbor_factory.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/unit/test_harbor_factory.py`:

```python
from datasets.metadata.schema import DifficultyLevel


def _make_hard_candidate() -> CandidateArtifact:
    return CandidateArtifact(
        source_type=SourceType.github_pr,
        source_url="https://github.com/org/repo/pull/99",
        title="Major auth refactor",
        description="Complete rewrite of auth middleware.",
        raw_data={
            "merged": True,
            "files": ["src/auth.py", "src/middleware.py", "tests/test_auth.py"],
            "patches": {"src/auth.py": "+new code", "src/middleware.py": "+new code"},
        },
        difficulty_bucket=DifficultyLevel.hard,
    )


def test_harbor_factory_uses_difficulty_bucket(tmp_path):
    factory = HarborTaskFactory()
    candidate = _make_hard_candidate()
    task_dir = factory.create(candidate, output_dir=tmp_path, task_name="hard-task")

    toml_content = (task_dir / "task.toml").read_text()
    assert 'difficulty = "hard"' in toml_content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_harbor_factory.py::test_harbor_factory_uses_difficulty_bucket -v`
Expected: FAIL — toml still says `difficulty = "medium"`

- [ ] **Step 3: Update `_write_toml` to use the bucket**

In `src/datasets/factory/harbor.py`, update `_write_toml`:

```python
    def _write_toml(
        self, task_dir: Path, candidate: CandidateArtifact, task_name: str
    ) -> None:
        difficulty = candidate.difficulty_bucket.value if candidate.difficulty_bucket else "medium"
        toml = textwrap.dedent(f"""\
            version = "1.0"

            [metadata]
            author_name = "rhai-datasets"
            author_email = ""
            difficulty = "{difficulty}"
            difficulty_explanation = "Estimated from patch size, file count, and component spread"
            category = "{candidate.source_type.value}"
            tags = ["auto-generated", "{candidate.source_type.value}"]

            [verifier]
            timeout_sec = 900.0

            [agent]
            timeout_sec = 900.0

            [environment]
            build_timeout_sec = 600.0
            cpus = 1
            memory_mb = 4096
            storage_mb = 10240
        """)
        (task_dir / "task.toml").write_text(toml)
```

Add the import at the top of `harbor.py`:

```python
from datasets.metadata.schema import CandidateArtifact, DifficultyLevel
```

(Remove the old `from datasets.metadata.schema import CandidateArtifact` import.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_harbor_factory.py -v`
Expected: All pass

- [ ] **Step 5: Commit**

```bash
git add src/datasets/factory/harbor.py tests/unit/test_harbor_factory.py
git commit -m "feat: use difficulty bucket in Harbor task.toml"
```

---

### Task 4: Extract real test files from PR diffs into Harbor tests/

Instead of writing placeholder stubs, parse `candidate.raw_data["patches"]` for files matching the test pattern and write those patches as actual test files.

**Files:**
- Modify: `src/datasets/factory/harbor.py:79-105` (`_write_tests`)
- Modify: `tests/unit/test_harbor_factory.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/unit/test_harbor_factory.py`:

```python
def _make_candidate_with_test_patch() -> CandidateArtifact:
    return CandidateArtifact(
        source_type=SourceType.github_pr,
        source_url="https://github.com/org/repo/pull/55",
        title="Add validation logic",
        description="Adds input validation with tests.",
        raw_data={
            "merged": True,
            "files": ["src/validate.py", "tests/test_validate.py"],
            "patches": {
                "src/validate.py": "@@ -0,0 +1,5 @@\n+def validate(x):\n+    if x < 0:\n+        raise ValueError('negative')\n+    return x",
                "tests/test_validate.py": "@@ -0,0 +1,10 @@\n+import pytest\n+from validate import validate\n+\n+\n+def test_validate_positive():\n+    assert validate(1) == 1\n+\n+\n+def test_validate_negative():\n+    with pytest.raises(ValueError):\n+        validate(-1)",
            },
        },
        difficulty_bucket=DifficultyLevel.medium,
    )


def test_harbor_factory_extracts_real_tests(tmp_path):
    factory = HarborTaskFactory()
    candidate = _make_candidate_with_test_patch()
    task_dir = factory.create(candidate, output_dir=tmp_path, task_name="real-tests")

    tests_dir = task_dir / "tests"
    extracted = list(tests_dir.glob("*.py"))
    filenames = {f.name for f in extracted}
    assert "test_validate.py" in filenames

    content = (tests_dir / "test_validate.py").read_text()
    assert "def test_validate_positive" in content
    assert "def test_validate_negative" in content


def test_harbor_factory_test_sh_runs_extracted_tests(tmp_path):
    factory = HarborTaskFactory()
    candidate = _make_candidate_with_test_patch()
    task_dir = factory.create(candidate, output_dir=tmp_path, task_name="real-tests")

    test_sh = (task_dir / "tests" / "test.sh").read_text()
    assert "test_validate.py" in test_sh
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_harbor_factory.py::test_harbor_factory_extracts_real_tests tests/unit/test_harbor_factory.py::test_harbor_factory_test_sh_runs_extracted_tests -v`
Expected: FAIL — tests/ contains only the placeholder `test_outputs.py`

- [ ] **Step 3: Implement test extraction**

Replace `_write_tests` in `src/datasets/factory/harbor.py`:

```python
    def _write_tests(self, task_dir: Path, candidate: CandidateArtifact) -> None:
        tests_dir = task_dir / "tests"
        tests_dir.mkdir(exist_ok=True)

        patches = candidate.raw_data.get("patches", {})
        test_files = {
            fname: patch
            for fname, patch in patches.items()
            if re.search(r"(^|/)tests?[/_]|_test\.|test_", fname, re.IGNORECASE)
        }

        extracted_names: list[str] = []
        for filepath, patch in test_files.items():
            filename = Path(filepath).name
            content = _extract_added_lines(patch)
            if content.strip():
                (tests_dir / filename).write_text(content)
                extracted_names.append(filename)

        if not extracted_names:
            (tests_dir / "test_outputs.py").write_text(textwrap.dedent("""\
                \"\"\"Auto-generated test scaffold. Requires manual enrichment.\"\"\"


                class TestOutputs:
                    def test_task_completed(self):
                        assert True, "Placeholder -- add real verification"
            """))
            extracted_names.append("test_outputs.py")

        test_targets = " ".join(f"/tests/{n}" for n in extracted_names)
        test_sh = textwrap.dedent(f"""\
            #!/bin/bash
            mkdir -p /logs/verifier
            uvx --with pytest==8.4.1 --with pytest-json-ctrf==0.3.5 \\
              pytest --ctrf /logs/verifier/ctrf.json {test_targets} -rA -v
            if [ $? -eq 0 ]; then echo 1 > /logs/verifier/reward.txt; else echo 0 > /logs/verifier/reward.txt; fi
            exit 0
        """)
        test_sh_path = tests_dir / "test.sh"
        test_sh_path.write_text(test_sh)
        test_sh_path.chmod(0o755)
```

Add a module-level helper to extract added lines from a unified diff patch:

```python
import re


def _extract_added_lines(patch: str) -> str:
    lines = []
    for line in patch.split("\n"):
        if line.startswith("@@"):
            continue
        if line.startswith("+"):
            lines.append(line[1:])
        elif not line.startswith("-"):
            lines.append(line)
    return "\n".join(lines)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_harbor_factory.py -v`
Expected: All pass

- [ ] **Step 5: Run the full test suite**

Run: `uv run pytest tests/ -v`
Expected: All pass

- [ ] **Step 6: Commit**

```bash
git add src/datasets/factory/harbor.py tests/unit/test_harbor_factory.py
git commit -m "feat: extract real test files from PR diffs in Harbor factory"
```

---

### Task 5: Print difficulty breakdown in CLI output

Show the user how candidates bucket by difficulty after scanning, so they can decide how to split datasets.

**Files:**
- Modify: `src/datasets/cli.py:152-164` (the `recommend` command output section)

- [ ] **Step 1: Update the CLI output**

In `src/datasets/cli.py`, after the per-candidate output loop (line 159), add a difficulty breakdown summary:

```python
    # After the existing per-candidate loop
    from datasets.metadata.schema import DifficultyLevel

    bucket_counts: dict[str, int] = {"easy": 0, "medium": 0, "hard": 0}
    for c in results:
        if c.difficulty_bucket:
            bucket_counts[c.difficulty_bucket.value] += 1
    click.echo(
        f"\nDifficulty breakdown: "
        f"easy={bucket_counts['easy']}  "
        f"medium={bucket_counts['medium']}  "
        f"hard={bucket_counts['hard']}"
    )
```

Also update the per-candidate line to show the difficulty bucket:

```python
        bucket = f"  [{c.difficulty_bucket.value}]" if c.difficulty_bucket else ""
        click.echo(f"  [{score:.2f}] {c.title[:55]:55s}{bucket}{ai_flag}")
```

- [ ] **Step 2: Run the full test suite**

Run: `uv run pytest tests/ -v`
Expected: All pass (CLI tests may use Click's CliRunner — verify no regressions)

- [ ] **Step 3: Commit**

```bash
git add src/datasets/cli.py
git commit -m "feat: show difficulty bucket and breakdown in recommend output"
```
