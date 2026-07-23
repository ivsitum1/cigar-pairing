"""Socratic reward decay for skill routing eval (hint penalty)."""
from __future__ import annotations

import json
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[3]
HINT_LEDGER = WORKSPACE / ".agent" / "hint_ledger.jsonl"
DEFAULT_DECAY_PER_HINT = 0.1
MIN_SCORE_FLOOR = 0.0


def load_hint_counts(*, ledger_path: Path | None = None) -> dict[str, int]:
    """Aggregate hint counts per skill_id from ledger."""
    path = ledger_path or HINT_LEDGER
    counts: dict[str, int] = {}
    if not path.is_file():
        return counts
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        sid = rec.get("skill_id")
        if not sid:
            continue
        counts[sid] = counts.get(sid, 0) + int(rec.get("hints", 1))
    return counts


def apply_reward_decay(
    score: float,
    hint_count: int,
    *,
    decay_per_hint: float = DEFAULT_DECAY_PER_HINT,
    floor: float = MIN_SCORE_FLOOR,
) -> tuple[float, float]:
    """Return (adjusted_score, penalty_applied)."""
    penalty = round(min(score - floor, hint_count * decay_per_hint), 4)
    adjusted = max(floor, round(score - penalty, 4))
    return adjusted, penalty


def append_hint(
    skill_id: str,
    *,
    session_id: str = "",
    reason: str = "",
    hints: int = 1,
    ledger_path: Path | None = None,
) -> None:
    """Record teacher/harness hint for reward decay."""
    from datetime import datetime, timezone

    path = ledger_path or HINT_LEDGER
    path.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "skill_id": skill_id,
        "hints": hints,
        "session_id": session_id,
        "reason": reason[:200],
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
