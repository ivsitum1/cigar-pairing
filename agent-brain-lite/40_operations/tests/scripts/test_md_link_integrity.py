"""Regression gate for internal markdown-link integrity.

The workspace is a knowledge graph; broken relative links silently degrade
navigation and retrieval. A structural generator fix took the live-graph
breakage from ~5,300 links down to the current long tail. This test locks in
that gain: the broken-link count must not exceed the baseline below.

Ratchet policy: when link rot is repaired, lower ``BASELINE`` to the new count
so it can never climb back. Do NOT raise it to make a red build pass — fix the
link instead.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = REPO_ROOT / "40_operations" / "scripts"
sys.path.insert(0, str(SCRIPTS))

# Current known long-tail of hand-authored broken links (archive excluded).
# Ratchet: clean GitHub checkout ~713 after excluding indexes/inbox_raw/_archive.
BASELINE = 721


@pytest.mark.unit
def test_broken_links_within_baseline() -> None:
    from check_md_links import DEFAULT_EXCLUDE, find_broken

    broken = find_broken(REPO_ROOT, DEFAULT_EXCLUDE)
    sample = "\n".join(
        f"  {f.relative_to(REPO_ROOT).as_posix()} -> {t}" for f, t in broken[:20]
    )
    assert len(broken) <= BASELINE, (
        f"Broken internal markdown links rose to {len(broken)} "
        f"(baseline {BASELINE}). Fix the new broken link(s):\n{sample}"
    )
