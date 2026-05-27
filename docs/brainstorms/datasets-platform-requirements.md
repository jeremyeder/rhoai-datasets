---
date: 2026-05-21
topic: datasets-platform
---

# Datasets Platform

## Summary

A dataset creation and curation platform that helps Red Hat AI teams build evaluation datasets from real project artifacts. It provides a ground truth recommender (scans Jira, GitHub, Confluence, CVE databases, compliance frameworks), AI-content analysis on source material, dataset factory tooling that outputs Harbor/SkillsBench/EvalHub-compatible formats, and a catalog of curated external datasets reviewed for applicability.

---

## Problem Frame

Component teams across RHOAI, RHEL AI, and RHAIIS need evaluation datasets to establish agent baselines and run systematic optimization. Three evaluation ecosystems exist -- Harbor (containerized agent tasks), SkillsBench (skills effectiveness), and EvalHub+MLflow (model quality/safety benchmarks) -- but no tooling exists to help teams source good ground truth candidates from their own work, flag AI-generated content in those sources, or produce datasets in the right format for each backend.

Without this, teams either skip evaluation entirely, hand-craft a few test cases that don't generalize, or adopt public benchmarks that don't reflect their domain. Earlier prototyping proved that DoE-driven optimization works (fractional factorial designs, ANOVA, Pareto frontiers), but it assumed datasets already existed. This repo addresses the upstream gap.

---

## Actors

- A1. **Component team engineer**: Wants to improve their team's agent. Needs to create a baseline dataset from their domain, run it, and iterate.
- A2. **Dataset curator (human or agent)**: Reviews recommender output, accepts/rejects candidates, enriches metadata, and publishes datasets.
- A3. **agent-eval-harness**: Downstream consumer. Picks up datasets from this repo's catalog and runs DoE experiments across factor permutations.
- A4. **Recommender agent**: Scans team artifacts, scores candidates for ground truth suitability, runs AI-content analysis, and surfaces recommendations.

---

## Key Flows

- F1. **Source and curate a new dataset**
  - **Trigger:** A component team decides to improve their agent and needs a baseline dataset.
  - **Actors:** A1, A4, A2
  - **Steps:**
    1. Engineer configures the recommender with their team's data sources (Jira project, GitHub repos, Confluence spaces, relevant CVE categories)
    2. Recommender scans sources and scores candidates on ground-truth suitability (clear before/after state, verifiable outcome, appropriate difficulty)
    3. Recommender runs AI-content analysis on each candidate and flags results
    4. Curator reviews recommendations, accepts/rejects/enriches candidates
    5. Dataset factory transforms accepted candidates into target format(s) (Harbor task, SkillsBench task, EvalHub dataset)
    6. Metadata file is generated with provenance, AI-generation scores, domain tags, difficulty classification
  - **Outcome:** A structured, metadata-rich dataset ready for agent-eval-harness consumption.
  - **Covered by:** R1, R2, R3, R4, R5, R6

- F2. **Review external datasets for applicability**
  - **Trigger:** A team wants to evaluate their agent against public benchmarks before creating custom ones.
  - **Actors:** A1, A2
  - **Steps:**
    1. Team browses the catalog of reviewed external datasets (Harbor Hub, SkillsBench tasks)
    2. Each entry includes applicability notes for Red Hat AI domains, difficulty profile, and format
    3. Team selects applicable datasets and adds them to their eval configuration
  - **Outcome:** Team has a curated set of external benchmarks relevant to their domain.
  - **Covered by:** R7, R8

- F3. **Establish baseline and feed DoE pipeline**
  - **Trigger:** Dataset exists and team is ready to run experiments.
  - **Actors:** A1, A3
  - **Steps:**
    1. Engineer points agent-eval-harness at the dataset (local path or catalog reference)
    2. agent-eval-harness runs baseline measurement with current agent+harness config
    3. agent-eval-harness uses the dataset across DoE factor permutations (model variant, harness workflow, budget, etc.)
  - **Outcome:** Baseline metrics established; DoE optimization can proceed.
  - **Covered by:** R9, R10

---

## Requirements

**Ground truth recommender**
- R1. The recommender shall scan configurable data sources (Jira issues, GitHub PRs/issues/commits, Confluence pages, CVE databases, compliance frameworks) and score each artifact on ground-truth suitability.
- R2. Suitability scoring shall consider: clarity of before/after state, verifiability of outcome, appropriate difficulty, domain relevance, and completeness of context.
- R3. The recommender shall run AI-content analysis on candidate source material and include an AI-generation confidence score in its output.
- R4. The recommender shall output a ranked list of candidates with suitability scores, AI-generation flags, source provenance, and suggested evaluation type (agent coding, model quality, safety, skills effectiveness).

**Dataset factory**
- R5. The factory shall transform accepted candidates into structured evaluation datasets in at least three formats: Harbor task (instruction + container env + test script), SkillsBench task (skills + verifier + oracle), and EvalHub/MLflow dataset (test cases with expected outputs).
- R6. Each produced dataset shall include a metadata file with: provenance (source artifact URLs), AI-generation scores per item, domain tags, difficulty classification, creation date, and curator identity.

**Dataset catalog**
- R7. The repo shall maintain a catalog of reviewed external datasets from Harbor Hub and SkillsBench, with applicability notes for Red Hat AI domains.
- R8. Each catalog entry shall include: source URL, task count, domain coverage, difficulty profile, format, and applicability assessment.

**Integration with agent-eval-harness**
- R9. Datasets produced by this repo shall be consumable by agent-eval-harness without format conversion -- the factory output is the harness input.
- R10. Dataset metadata shall be structured so agent-eval-harness can filter datasets by domain, difficulty, evaluation type, and AI-generation threshold.

**Quality and provenance**
- R11. All datasets shall track provenance back to source artifacts (Jira issue key, PR URL, CVE ID, etc.).
- R12. AI-content analysis shall use content-level classification, not just metadata signals (git co-author tags are supplementary, not sufficient).

---

## Acceptance Examples

- AE1. **Covers R1, R2, R4.** Given a Jira project with 200 closed bugs, when the recommender scans it, then it produces a ranked list where bugs with clear reproduction steps, a fix PR, and test coverage score higher than bugs closed as "won't fix" or lacking context.
- AE2. **Covers R3, R12.** Given a GitHub PR where the code was written by Claude Code (Co-Authored-By tag present) but the description was written by a human, when AI-content analysis runs, then the code files get high AI-generation scores and the PR description gets a low score -- the system distinguishes per-artifact, not per-PR.
- AE3. **Covers R5, R9.** Given an accepted bug-fix candidate, when the factory produces a Harbor task, then `harbor run` can execute it without modification; when it produces an MLflow dataset, then agent-eval-harness can load it directly.
- AE4. **Covers R10.** Given a catalog of 50 datasets spanning 4 domains, when agent-eval-harness queries for "safety" datasets with difficulty > medium and AI-generation score < 0.3, then only matching datasets are returned.

---

## Success Criteria

- A component team can go from "we want a baseline" to "we have a runnable dataset" in under a day, not weeks of manual curation.
- The recommender surfaces candidates that humans agree are good ground truths at least 70% of the time (precision over recall -- false positives waste curator time).
- AI-generation flags are accurate enough that teams trust them for provenance decisions (content analysis, not just metadata).
- agent-eval-harness can consume produced datasets without glue code.

---

## Scope Boundaries

### Deferred for later

- Automated dataset quality scoring (beyond suitability scoring of candidates) -- measuring how well a dataset discriminates between good and bad agents
- Continuous dataset refresh -- automatically re-scanning sources on a schedule to find new candidates
- Dataset versioning with diff tracking (v1 vs v2 of the same dataset)
- Integration with Harbor's registry publishing (`harbor publish`)

### Outside this product's identity

- **DoE orchestration** -- that's agent-eval-harness. This repo does not run experiments, compute ANOVA, or find Pareto frontiers.
- **Benchmark execution** -- that's Harbor/EvalHub. This repo does not execute tasks or score agent output.
- **Results storage** -- that's MLflow. This repo does not store experiment results or metrics.
- **DoE execution** -- fractional factorial design, factor permutation, ANOVA, and Pareto analysis are out of scope for this repo.

---

## Key Decisions

- **AI-content detection uses LLM-as-judge**: Simpler to integrate than Binoculars, costs per-call but avoids heavyweight model dependencies. Claude is the judge.
- **Multiple output formats, not one canonical format**: Harbor, SkillsBench, and EvalHub each have their own dataset structure. The factory produces all three rather than picking one and requiring adapters.
- **Datasets live in this repo (small) or are referenced (large)**: JSONL test cases, task descriptions, and metadata live in the repo. Container images, large repo snapshots, and corpora are referenced by URL.
- **Recommender is opinionated about quality**: It scores candidates on suitability. A bug with clear repro steps, a fix PR, and test coverage is better than an ambiguous feature request.

---

## Dependencies / Assumptions

- agent-eval-harness exists and has a defined dataset input format (or will co-evolve with this repo)
- Teams have accessible Jira projects, GitHub repos, and optionally Confluence spaces
- Harbor CLI and SkillsBench CLI are available for format validation
- ANTHROPIC_API_KEY is available for LLM-as-judge AI detection
- MLflow tracking server is available for EvalHub dataset format

---

## Outstanding Questions

### Deferred to Planning

- [Affects R5][Technical] Exact validation of Harbor task output against `harbor run` -- needs live testing
- [Affects R5][Technical] Exact validation of SkillsBench task output against `bench tasks check` -- needs live testing
- [Affects R2][Needs research] Suitability scoring weights -- current weights are heuristic, need calibration against human judgment
- [Affects R7][Needs research] Full review of all Harbor Hub and SkillsBench catalog entries for Red Hat AI applicability
