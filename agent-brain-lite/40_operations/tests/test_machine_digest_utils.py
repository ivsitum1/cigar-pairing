"""Tests for machine digest utils."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_OPS = Path(__file__).resolve().parents[1] / "python"
if str(_OPS) not in sys.path:
    sys.path.insert(0, str(_OPS))

from common.machine_digest_utils import (  # noqa: E402
    count_digest_proposals,
    count_pending_proposals,
    secondary_count_message,
)


def test_count_proposals(tmp_path: Path) -> None:
    digest = tmp_path / "machine_digest_2026-W27.md"
    digest.write_text(
        "### Proposal 1: foo\n\n### Proposal 2: bar\n",
        encoding="utf-8",
    )
    assert count_digest_proposals(digest) == 2


def test_pending_defer_count(tmp_path: Path) -> None:
    digest = tmp_path / "machine_digest_2026-W27.md"
    digest.write_text("### Proposal 1: a\n", encoding="utf-8")
    decisions = tmp_path / "machine_digest_decisions_2026-W27.json"
    decisions.write_text(
        json.dumps(
            {
                "week": "2026-W27",
                "decisions": [
                    {"proposal_id": "a", "verdict": "defer"},
                    {"proposal_id": "b", "verdict": "reject"},
                ],
            }
        ),
        encoding="utf-8",
    )
    count, name = count_pending_proposals(tmp_path, "2026-W27")
    assert count == 1
    assert name == "machine_digest_2026-W27.md"


def test_secondary_message(tmp_path: Path) -> None:
    test_pending_defer_count(tmp_path)
    msg = secondary_count_message(tmp_path)
    assert msg is not None
    assert "Secondary queue: 1" in msg
