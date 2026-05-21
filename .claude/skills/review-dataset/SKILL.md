---
name: review-dataset
description: Review a generated dataset directory for quality — checks instruction clarity, Dockerfile completeness, test coverage, and solution viability. Use after running `datasets create` to validate output before sharing with teams.
---

# Review Dataset

Review a generated evaluation dataset for quality and completeness.

## Input

The user provides a path to a generated dataset directory (output of `datasets create`).

## Steps

1. **Detect format** — Check for Harbor (instruction.md + task.toml + environment/Dockerfile) or SkillsBench (same + environment/skills/) or MLflow (.jsonl file).

2. **Check completeness** — Verify all required files exist:
   - Harbor/SkillsBench: instruction.md, task.toml, environment/Dockerfile, tests/test.sh, tests/test_outputs.py, solution/solve.sh
   - MLflow: .jsonl file with valid JSON records containing inputs, expectations, tags

3. **Review instruction.md** — Check:
   - Is the task description clear enough for an agent to understand what to do?
   - Are files involved listed?
   - Is there a concrete success criterion?

4. **Review task.toml** — Check:
   - Are timeouts reasonable (not default placeholder)?
   - Is difficulty classification accurate?
   - Are tags meaningful?

5. **Review Dockerfile** — Check:
   - Is the base image appropriate for the task?
   - Are necessary dependencies installed?
   - Is WORKDIR set?

6. **Review tests** — Check:
   - Does test_outputs.py have real assertions (not just placeholder `assert True`)?
   - Does test.sh write reward.txt correctly?

7. **Review solution** — Check:
   - Does solve.sh contain a real oracle solution (not just placeholder)?

8. **Report findings** — Output a summary with:
   - Pass/fail per check
   - Specific issues found
   - Suggested improvements (with diffs where possible)

## Key Principle

Generated datasets always need human enrichment. The factories produce scaffolds with placeholder tests and solutions. This review identifies what still needs manual work before the dataset is usable.
