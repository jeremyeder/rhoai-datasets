"""Shared regex patterns for file classification."""

from __future__ import annotations

import re

TEST_FILE_RE = re.compile(r"(^|/)tests?[/_]|_test\.|test_|\btestutils\b", re.IGNORECASE)
