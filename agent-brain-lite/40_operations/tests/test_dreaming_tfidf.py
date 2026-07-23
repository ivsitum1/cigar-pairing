"""TF-IDF clustering in dreaming daemon."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "40_operations" / "scripts"))

from dreaming_daemon import extract_patterns  # noqa: E402


def test_tfidf_clusters_similar_outcomes() -> None:
    events = [
        {"tool": "Grep", "outcome": "found memory_engine store search filter"},
        {"tool": "Grep", "outcome": "found memory_engine store search cross"},
        {"tool": "Shell", "outcome": "pytest passed all tests"},
    ]
    patterns = extract_patterns(events, similarity_threshold=0.5)
    titles = " ".join(p["title"] for p in patterns)
    assert "Grep" in titles or "Similar" in titles or "Repeated" in titles
