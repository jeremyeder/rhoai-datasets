"""tests/unit/test_skillsbench_factory.py"""

from __future__ import annotations

from datasets.factory.skillsbench import SkillsBenchTaskFactory
from datasets.metadata.schema import CandidateArtifact, SourceType


def _make_candidate() -> CandidateArtifact:
    return CandidateArtifact(
        source_type=SourceType.github_pr,
        source_url="https://github.com/org/repo/pull/42",
        title="Fix auth handler",
        description="Fix null pointer when session expires.",
        raw_data={"merged": True, "files": ["src/auth.py"]},
    )


def test_skillsbench_factory_creates_structure(tmp_path):
    factory = SkillsBenchTaskFactory()
    candidate = _make_candidate()
    task_dir = factory.create(candidate, output_dir=tmp_path, task_name="fix-auth")

    assert (task_dir / "instruction.md").is_file()
    assert (task_dir / "task.toml").is_file()
    assert (task_dir / "environment" / "Dockerfile").is_file()
    assert (task_dir / "environment" / "skills").is_dir()
    assert (task_dir / "tests" / "test.sh").is_file()
    assert (task_dir / "tests" / "test_outputs.py").is_file()
    assert (task_dir / "solution" / "solve.sh").is_file()


def test_skillsbench_factory_format_name():
    factory = SkillsBenchTaskFactory()
    assert factory.format_name == "skillsbench"
