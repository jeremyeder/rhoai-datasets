"""Suitability scoring for ground truth candidates."""

from __future__ import annotations

import re

from datasets.metadata.schema import CandidateArtifact, SuitabilityScore


def _source_files(files: list[str]) -> list[str]:
    """Filter to source files, excluding test files."""
    return [
        f
        for f in files
        if not re.search(
            r"(^|/)tests?[/_]|_test\.|test_|\btestutils\b",
            f,
            re.IGNORECASE,
        )
    ]


def _test_files(files: list[str]) -> list[str]:
    """Filter to test files only."""
    return [
        f
        for f in files
        if re.search(
            r"(^|/)tests?[/_]|_test\.|test_",
            f,
            re.IGNORECASE,
        )
    ]


def _patch_line_count(patches: dict[str, str]) -> int:
    """Count total changed lines across all patches."""
    return sum(
        sum(
            1
            for line in patch.split("\n")
            if line.startswith("+") or line.startswith("-")
        )
        for patch in patches.values()
    )


def _component_spread(files: list[str]) -> int:
    """Count distinct top-level packages touched."""
    components = set()
    for f in _source_files(files):
        parts = f.split("/")
        if len(parts) >= 2:
            components.add(
                parts[1]
                if parts[0] in ("pkg", "controllers", "components", "src")
                else parts[0]
            )
    return len(components)


def _score_clarity(candidate: CandidateArtifact) -> float:
    desc = candidate.description.lower()
    score = 30

    clarity_signals = [
        (r"(steps to reproduce|repro|how to)", 20),
        (r"(expected|actual|observed)", 15),
        (r"(problem|issue|bug|error|exception|crash)", 10),
        (r"(fix|solution|resolved|patch)", 10),
        (r"\d+\.", 5),
    ]
    for pattern, weight in clarity_signals:
        if re.search(pattern, desc):
            score += weight

    if len(desc) < 20:
        score *= 0.5
    elif len(desc) > 200:
        score = min(score + 10, 100)

    return min(score, 100)


def _score_verifiability(candidate: CandidateArtifact) -> float:
    raw = candidate.raw_data
    score = 30

    resolution = raw.get("resolution", "")
    if resolution in ("Won't Fix", "Duplicate", "Cannot Reproduce"):
        return 10

    if "merged" in raw and not raw["merged"]:
        return 0

    if raw.get("merged"):
        score += 30

    files = raw.get("files", [])
    if _test_files(files):
        score += 20

    patches = raw.get("patches", {})
    if patches:
        score += 10

    return min(score, 100)


def _score_difficulty(candidate: CandidateArtifact) -> float:
    files = candidate.raw_data.get("files", [])
    patches = candidate.raw_data.get("patches", {})
    src = _source_files(files)
    src_count = len(src)
    patch_lines = _patch_line_count(patches)
    spread = _component_spread(files)

    score = 0

    if patch_lines < 20:
        score += 10
    elif patch_lines < 100:
        score += 30
    elif patch_lines < 500:
        score += 70
    elif patch_lines < 1500:
        score += 90
    else:
        score += 60

    if src_count <= 1:
        score *= 0.7
    elif src_count <= 5:
        score *= 0.9
    elif src_count <= 15:
        score *= 1.0
    else:
        score *= 0.8

    if spread >= 3:
        score = min(score + 10, 100)

    return max(10, min(score, 100))


def _score_domain_relevance(candidate: CandidateArtifact) -> float:
    return 50


def _score_completeness(candidate: CandidateArtifact) -> float:
    score = 30
    if candidate.title and len(candidate.title) > 10:
        score += 20
    if candidate.description and len(candidate.description) > 50:
        score += 20
    if candidate.raw_data.get("files"):
        score += 15
    if candidate.raw_data.get("patches"):
        score += 15
    return min(score, 100)


def score_candidate(
    candidate: CandidateArtifact,
) -> SuitabilityScore:
    return SuitabilityScore(
        clarity=_score_clarity(candidate),
        verifiability=_score_verifiability(candidate),
        difficulty=_score_difficulty(candidate),
        domain_relevance=_score_domain_relevance(candidate),
        completeness=_score_completeness(candidate),
    )
