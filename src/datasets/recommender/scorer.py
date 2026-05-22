"""Suitability scoring for ground truth candidates."""

from __future__ import annotations

import re

from datasets.metadata.schema import CandidateArtifact, SuitabilityScore


def _score_clarity(candidate: CandidateArtifact) -> float:
    desc = candidate.description.lower()
    score = 0.3

    clarity_signals = [
        (r"(steps to reproduce|repro|how to)", 0.2),
        (r"(expected|actual|observed)", 0.15),
        (r"(problem|issue|bug|error|exception|crash)", 0.1),
        (r"(fix|solution|resolved|patch)", 0.1),
        (r"\d+\.", 0.05),  # numbered steps
    ]
    for pattern, weight in clarity_signals:
        if re.search(pattern, desc):
            score += weight

    if len(desc) < 20:
        score *= 0.5
    elif len(desc) > 200:
        score = min(score + 0.1, 1.0)

    return min(score, 1.0)


def _score_verifiability(candidate: CandidateArtifact) -> float:
    raw = candidate.raw_data
    score = 0.3

    resolution = raw.get("resolution", "")
    if resolution in ("Won't Fix", "Duplicate", "Cannot Reproduce"):
        return 0.1

    if "merged" in raw and not raw["merged"]:
        return 0.0

    if raw.get("merged"):
        score += 0.3

    files = raw.get("files", [])
    has_tests = any("test" in f.lower() for f in files)
    if has_tests:
        score += 0.2

    patches = raw.get("patches", {})
    if patches:
        score += 0.1

    return min(score, 1.0)


def _score_difficulty(candidate: CandidateArtifact) -> float:
    files = candidate.raw_data.get("files", [])
    desc_len = len(candidate.description)

    if len(files) <= 1 and desc_len < 100:
        return 0.3  # too easy
    elif len(files) > 10 or desc_len > 2000:
        return 0.3  # too hard / too complex
    else:
        return 0.7  # goldilocks


def _score_domain_relevance(candidate: CandidateArtifact) -> float:
    return 0.5  # default; enriched by pipeline with domain config


def _score_completeness(candidate: CandidateArtifact) -> float:
    score = 0.3
    if candidate.title and len(candidate.title) > 10:
        score += 0.2
    if candidate.description and len(candidate.description) > 50:
        score += 0.2
    if candidate.raw_data.get("files"):
        score += 0.15
    if candidate.raw_data.get("patches"):
        score += 0.15
    return min(score, 1.0)


def score_candidate(candidate: CandidateArtifact) -> SuitabilityScore:
    return SuitabilityScore(
        clarity=_score_clarity(candidate),
        verifiability=_score_verifiability(candidate),
        difficulty=_score_difficulty(candidate),
        domain_relevance=_score_domain_relevance(candidate),
        completeness=_score_completeness(candidate),
    )
