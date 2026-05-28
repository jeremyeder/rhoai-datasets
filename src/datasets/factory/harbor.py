"""src/datasets/factory/harbor.py -- Harbor task output format."""

from __future__ import annotations

import base64
import re
import shlex
import textwrap
from pathlib import Path

from datasets.metadata.schema import CandidateArtifact
from datasets.patterns import TEST_FILE_RE

_SAFE_FILENAME_RE = re.compile(r"^[A-Za-z0-9_.\-]+$")


def _extract_added_lines(patch: str) -> str:
    """Extract only added lines from a unified diff patch."""
    lines = []
    for line in patch.split("\n"):
        if line.startswith("@@"):
            continue
        if line.startswith("+"):
            lines.append(line[1:])
        elif not line.startswith("-"):
            lines.append(line)
    return "\n".join(lines)


class HarborTaskFactory:
    @property
    def format_name(self) -> str:
        return "harbor"

    def create(
        self,
        candidate: CandidateArtifact,
        output_dir: Path,
        task_name: str,
    ) -> Path:
        task_dir = output_dir / task_name
        task_dir.mkdir(parents=True, exist_ok=True)

        self._write_instruction(task_dir, candidate)
        self._write_toml(task_dir, candidate, task_name)
        self._write_dockerfile(task_dir)
        self._write_tests(task_dir, candidate)
        self._write_solution(task_dir, candidate)

        return task_dir

    def _write_instruction(self, task_dir: Path, candidate: CandidateArtifact) -> None:
        content = f"# {candidate.title}\n\n{candidate.description}\n"
        if candidate.raw_data.get("files"):
            content += "\n## Files involved\n"
            for f in candidate.raw_data["files"]:
                content += f"- `{f}`\n"
        (task_dir / "instruction.md").write_text(content)

    def _write_toml(
        self, task_dir: Path, candidate: CandidateArtifact, task_name: str
    ) -> None:
        difficulty = (
            candidate.difficulty_bucket.value
            if candidate.difficulty_bucket
            else "medium"
        )
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

    def _write_dockerfile(self, task_dir: Path) -> None:
        env_dir = task_dir / "environment"
        env_dir.mkdir(exist_ok=True)
        dockerfile = textwrap.dedent("""\
            FROM python:3.12-slim
            ENV DEBIAN_FRONTEND=noninteractive
            WORKDIR /root
        """)
        (env_dir / "Dockerfile").write_text(dockerfile)

    def _write_tests(self, task_dir: Path, candidate: CandidateArtifact) -> None:
        tests_dir = task_dir / "tests"
        tests_dir.mkdir(exist_ok=True)

        patches = candidate.raw_data.get("patches", {})
        test_patches = {
            fname: patch
            for fname, patch in patches.items()
            if TEST_FILE_RE.search(fname)
        }

        extracted_names: list[str] = []
        seen_names: set[str] = set()
        for filepath, patch in test_patches.items():
            filename = Path(filepath).name
            if not _SAFE_FILENAME_RE.fullmatch(filename):
                continue
            if filename in seen_names:
                stem = Path(filename).stem
                suffix = Path(filename).suffix
                counter = 1
                while f"{stem}_{counter}{suffix}" in seen_names:
                    counter += 1
                filename = f"{stem}_{counter}{suffix}"
            content = _extract_added_lines(patch)
            if content.strip():
                seen_names.add(filename)
                (tests_dir / filename).write_text(content)
                extracted_names.append(filename)

        if not extracted_names:
            (tests_dir / "test_outputs.py").write_text(
                textwrap.dedent("""\
                \"\"\"Auto-generated test scaffold. Requires manual enrichment.\"\"\"


                class TestOutputs:
                    def test_task_completed(self):
                        assert True, "Placeholder -- add real verification"
            """)
            )
            extracted_names.append("test_outputs.py")

        test_targets = " ".join(shlex.quote(f"/tests/{n}") for n in extracted_names)
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

    def _write_solution(self, task_dir: Path, candidate: CandidateArtifact) -> None:
        solution_dir = task_dir / "solution"
        solution_dir.mkdir(exist_ok=True)

        patches = candidate.raw_data.get("patches", {})
        source_patches = {
            fname: patch
            for fname, patch in patches.items()
            if not TEST_FILE_RE.search(fname) and patch.strip()
        }

        if source_patches:
            combined_patch = ""
            for fname, patch in source_patches.items():
                combined_patch += f"--- a/{fname}\n+++ b/{fname}\n{patch}\n"
            patch_b64 = base64.b64encode(combined_patch.encode()).decode()

            solve_sh = (
                "#!/bin/bash\n"
                "set -e\n"
                f"printf '%s' '{patch_b64}'"
                " | base64 -d > /tmp/solution.patch\n"
                "cd /testbed\n"
                "patch --fuzz=5 -p1 -i /tmp/solution.patch\n"
            )
        else:
            solve_sh = textwrap.dedent("""\
                #!/bin/bash
                set -e
                echo "No source patches available for oracle solution"
            """)

        solve_path = solution_dir / "solve.sh"
        solve_path.write_text(solve_sh)
        solve_path.chmod(0o755)
