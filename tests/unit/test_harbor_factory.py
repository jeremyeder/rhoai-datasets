"""tests/unit/test_harbor_factory.py"""

from __future__ import annotations

from datasets.factory.harbor import HarborTaskFactory
from datasets.metadata.schema import CandidateArtifact, SourceType


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


def test_harbor_factory_creates_task_structure(tmp_path):
    factory = HarborTaskFactory()
    candidate = _make_bug_fix_candidate()
    task_dir = factory.create(candidate, output_dir=tmp_path, task_name="fix-auth-npe")

    assert (task_dir / "instruction.md").is_file()
    assert (task_dir / "task.toml").is_file()
    assert (task_dir / "environment" / "Dockerfile").is_file()
    assert (task_dir / "tests" / "test.sh").is_file()
    assert (task_dir / "tests" / "test_outputs.py").is_file()
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
