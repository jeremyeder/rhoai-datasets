"""tests/unit/test_harbor_factory.py"""

from __future__ import annotations

from datasets.factory.harbor import HarborTaskFactory
from datasets.metadata.schema import CandidateArtifact, DifficultyLevel, SourceType


def _make_bug_fix_candidate() -> CandidateArtifact:
    return CandidateArtifact(
        source_type=SourceType.github_pr,
        source_url="https://github.com/org/repo/pull/42",
        title="Fix null pointer in auth handler",
        description="NPE when user session is missing. Added null check.",
        raw_data={
            "merged": True,
            "files": ["src/auth.py", "tests/test_auth.py"],
            "patches": {
                "src/auth.py": "+if session is None:\n+    raise AuthError()",
            },
        },
    )


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
                "src/validate.py": (
                    "@@ -0,0 +1,5 @@\n"
                    "+def validate(x):\n"
                    "+    if x < 0:\n"
                    "+        raise ValueError('negative')\n"
                    "+    return x"
                ),
                "tests/test_validate.py": (
                    "@@ -0,0 +1,10 @@\n"
                    "+import pytest\n"
                    "+from validate import validate\n"
                    "+\n"
                    "+\n"
                    "+def test_validate_positive():\n"
                    "+    assert validate(1) == 1\n"
                    "+\n"
                    "+\n"
                    "+def test_validate_negative():\n"
                    "+    with pytest.raises(ValueError):\n"
                    "+        validate(-1)"
                ),
            },
        },
        difficulty_bucket=DifficultyLevel.medium,
    )


def test_harbor_factory_creates_task_structure(tmp_path):
    factory = HarborTaskFactory()
    candidate = _make_bug_fix_candidate()
    task_dir = factory.create(candidate, output_dir=tmp_path, task_name="fix-auth-npe")

    assert (task_dir / "instruction.md").is_file()
    assert (task_dir / "task.toml").is_file()
    assert (task_dir / "environment" / "Dockerfile").is_file()
    assert (task_dir / "tests" / "test.sh").is_file()
    assert (task_dir / "solution" / "solve.sh").is_file()


def test_harbor_factory_instruction_contains_candidate_info(tmp_path):
    factory = HarborTaskFactory()
    candidate = _make_bug_fix_candidate()
    task_dir = factory.create(candidate, output_dir=tmp_path, task_name="fix-auth-npe")

    instruction = (task_dir / "instruction.md").read_text()
    assert "null pointer" in instruction.lower() or "auth" in instruction.lower()


def test_harbor_factory_toml_has_metadata(tmp_path):
    factory = HarborTaskFactory()
    candidate = _make_bug_fix_candidate()
    task_dir = factory.create(candidate, output_dir=tmp_path, task_name="fix-auth-npe")

    toml_content = (task_dir / "task.toml").read_text()
    assert "version" in toml_content
    assert "metadata" in toml_content
    assert "verifier" in toml_content


def test_harbor_factory_uses_difficulty_bucket(tmp_path):
    factory = HarborTaskFactory()
    candidate = CandidateArtifact(
        source_type=SourceType.github_pr,
        source_url="https://github.com/org/repo/pull/99",
        title="Major auth refactor",
        description="Complete rewrite of auth middleware.",
        raw_data={
            "merged": True,
            "files": ["src/auth.py", "src/middleware.py", "tests/test_auth.py"],
            "patches": {
                "src/auth.py": "+new code",
                "src/middleware.py": "+new code",
            },
        },
        difficulty_bucket=DifficultyLevel.hard,
    )
    task_dir = factory.create(candidate, output_dir=tmp_path, task_name="hard-task")

    toml_content = (task_dir / "task.toml").read_text()
    assert 'difficulty = "hard"' in toml_content


def test_harbor_factory_defaults_to_medium_without_bucket(tmp_path):
    factory = HarborTaskFactory()
    candidate = _make_bug_fix_candidate()
    task_dir = factory.create(candidate, output_dir=tmp_path, task_name="no-bucket")

    toml_content = (task_dir / "task.toml").read_text()
    assert 'difficulty = "medium"' in toml_content


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


def test_harbor_factory_test_sh_references_extracted_tests(tmp_path):
    factory = HarborTaskFactory()
    candidate = _make_candidate_with_test_patch()
    task_dir = factory.create(candidate, output_dir=tmp_path, task_name="real-tests")

    test_sh = (task_dir / "tests" / "test.sh").read_text()
    assert "test_validate.py" in test_sh


def test_harbor_factory_falls_back_to_placeholder_without_test_patches(tmp_path):
    factory = HarborTaskFactory()
    candidate = CandidateArtifact(
        source_type=SourceType.github_pr,
        source_url="https://github.com/org/repo/pull/10",
        title="Config change",
        description="Update config.",
        raw_data={
            "merged": True,
            "files": ["src/config.py"],
            "patches": {"src/config.py": "+DEBUG = True"},
        },
    )
    task_dir = factory.create(candidate, output_dir=tmp_path, task_name="no-tests")

    assert (task_dir / "tests" / "test_outputs.py").is_file()
    test_sh = (task_dir / "tests" / "test.sh").read_text()
    assert "test_outputs.py" in test_sh


def test_harbor_factory_solve_sh_contains_real_patches(tmp_path):
    factory = HarborTaskFactory()
    candidate = _make_candidate_with_test_patch()
    task_dir = factory.create(candidate, output_dir=tmp_path, task_name="oracle")

    solve_sh = (task_dir / "solution" / "solve.sh").read_text()
    assert "patch --fuzz=5 -p1" in solve_sh
    assert "src/validate.py" in solve_sh
    assert "def validate(x):" in solve_sh
    assert "test_validate.py" not in solve_sh


def test_harbor_factory_solve_sh_fallback_without_patches(tmp_path):
    factory = HarborTaskFactory()
    candidate = CandidateArtifact(
        source_type=SourceType.github_pr,
        source_url="https://github.com/org/repo/pull/10",
        title="Empty",
        description="No patches.",
        raw_data={"merged": True, "files": [], "patches": {}},
    )
    task_dir = factory.create(candidate, output_dir=tmp_path, task_name="no-oracle")

    solve_sh = (task_dir / "solution" / "solve.sh").read_text()
    assert "No source patches" in solve_sh
