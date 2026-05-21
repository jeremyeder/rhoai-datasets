"""tests/unit/test_scorer.py"""

from __future__ import annotations

from datasets.metadata.schema import CandidateArtifact, SourceType
from datasets.recommender.scorer import score_candidate


def test_bug_with_clear_context_scores_high():
    """Bug with repro steps, fix PR, and test coverage scores high."""
    candidate = CandidateArtifact(
        source_type=SourceType.github_pr,
        source_url="https://github.com/org/repo/pull/42",
        title="Fix null pointer in auth handler",
        description="## Problem\nNPE when session expires.\n\n## Steps to reproduce\n1. Login\n2. Wait 30 min\n3. Click link\n\n## Fix\nAdded null check before session access.",
        raw_data={
            "merged": True,
            "files": ["src/auth.py", "tests/test_auth.py"],
            "patches": {"src/auth.py": "+if session is None:\n+    raise AuthError()"},
        },
    )
    score = score_candidate(candidate)
    assert score.clarity >= 0.7
    assert score.verifiability >= 0.7
    assert score.overall >= 0.6


def test_vague_feature_request_scores_low():
    """Vague feature request with no acceptance criteria scores low."""
    candidate = CandidateArtifact(
        source_type=SourceType.jira_issue,
        source_url="https://issues.redhat.com/browse/RHOAIENG-9999",
        title="Improve performance",
        description="The system should be faster.",
        raw_data={"issue_type": "Story", "status": "Closed", "resolution": "Won't Fix"},
    )
    score = score_candidate(candidate)
    assert score.clarity < 0.5
    assert score.overall < 0.4


def test_wontfix_penalizes_verifiability():
    candidate = CandidateArtifact(
        source_type=SourceType.jira_issue,
        source_url="https://issues.redhat.com/browse/TEST-1",
        title="Something",
        description="Detailed description with steps and expected behavior.",
        raw_data={"resolution": "Won't Fix"},
    )
    score = score_candidate(candidate)
    assert score.verifiability < 0.3
