"""tests/unit/test_ai_detection.py"""

from __future__ import annotations

from unittest.mock import patch

from datasets.metadata.schema import AIDetectionResult
from datasets.recommender.ai_detection import detect_ai_content, parse_judge_response


def test_parse_judge_response_high_confidence():
    response = (
        '{"score": 0.9, "reasoning": "Highly structured, uses AI-typical phrasing"}'
    )
    result = parse_judge_response(response)
    assert result == 90


def test_parse_judge_response_low_confidence():
    response = '{"score": 0.1, "reasoning": "Natural human writing style with typos"}'
    result = parse_judge_response(response)
    assert result == 10


def test_parse_judge_response_malformed():
    result = parse_judge_response("I think this is AI generated")
    assert 0 <= result <= 100


def test_detect_ai_content_per_artifact():
    """AI detection produces per-artifact scores."""
    artifacts = {
        "src/auth.py": "def check_session(session):\n    if session is None:\n        raise AuthError('No session')\n",
        "README.md": "# Auth Module\n\nThis module handles user authentication and session management.\n",
    }

    with patch("datasets.recommender.ai_detection._call_judge") as mock_judge:
        mock_judge.side_effect = [
            '{"score": 0.85, "reasoning": "Clean, structured code"}',
            '{"score": 0.2, "reasoning": "Simple human-written readme"}',
        ]
        result = detect_ai_content(artifacts, model="claude-sonnet-4-6")

    assert isinstance(result, AIDetectionResult)
    assert result.per_artifact_scores["src/auth.py"] == 85
    assert result.per_artifact_scores["README.md"] == 20
    assert 0 <= result.overall_score <= 100
    assert result.method == "llm-as-judge"
    assert result.model == "claude-sonnet-4-6"
