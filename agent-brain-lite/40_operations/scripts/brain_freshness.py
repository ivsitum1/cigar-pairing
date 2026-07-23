#!/usr/bin/env python3
"""Freshness SLO monitor for the autonomous brain.

The brain's autonomy runs as scheduled jobs (arXiv scout, AI-news feed, dreaming
daemon, memory maintenance). When a scheduled task silently stops firing, the
system keeps answering but stops *learning* — the failure is invisible. This
monitor makes staleness loud: it inspects the freshness signals and exits
non-zero when any exceeds its SLO, so it can gate a scheduled run or a dashboard.

Signals checked:
  * weekly task artifacts (.agent/task/*)          -> ingestion / digest is live
  * self-harness approval loop (self_harness_state) -> self-improvement is closing
  * memory maintenance archives (.agent/memory)     -> logs stay bounded
  * memory.db size                                  -> DB not ballooning
"""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENT = REPO_ROOT / ".agent"
DAY = 86400.0


@dataclass
class Signal:
    name: str
    age_days: float | None
    slo_days: float
    detail: str

    @property
    def stale(self) -> bool:
        return self.age_days is None or self.age_days > self.slo_days

    def line(self) -> str:
        status = "STALE" if self.stale else "ok"
        age = "never" if self.age_days is None else f"{self.age_days:.1f}d"
        return f"  [{status:^5}] {self.name:<26} age={age:<7} slo={self.slo_days:g}d  {self.detail}"


def _newest_mtime(paths: list[Path]) -> float | None:
    mtimes = [p.stat().st_mtime for p in paths if p.exists()]
    return max(mtimes) if mtimes else None


def _age_days(mtime: float | None, now: float) -> float | None:
    return None if mtime is None else (now - mtime) / DAY


def collect(now: float) -> list[Signal]:
    signals: list[Signal] = []

    task_dir = AGENT / "task"
    task_files = list(task_dir.glob("*.json")) + list(task_dir.glob("*.md")) if task_dir.exists() else []
    newest = max(task_files, key=lambda p: p.stat().st_mtime, default=None)
    signals.append(Signal(
        "weekly task artifacts", _age_days(_newest_mtime(task_files), now), 10.0,
        f"newest={newest.name}" if newest else "no artifacts",
    ))

    state_file = AGENT / "self_harness_state.json"
    approved_age = None
    detail = "no state file"
    if state_file.exists():
        try:
            st = json.loads(state_file.read_text(encoding="utf-8"))
            detail = f"iter={st.get('iteration')} approved={st.get('approved_count')}"
            ts = st.get("last_approved_at")
            if ts:
                parsed = time.strptime(ts.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S%z") \
                    if "T" in ts else None
                if parsed:
                    approved_age = (now - time.mktime(parsed)) / DAY
        except (ValueError, OSError):
            detail = "unreadable state file"
    signals.append(Signal("self-harness approval", approved_age, 30.0, detail))

    archive_dir = AGENT / "memory" / "archive"
    archives = list(archive_dir.glob("*.gz")) if archive_dir.exists() else []
    signals.append(Signal(
        "memory maintenance", _age_days(_newest_mtime(archives), now), 14.0,
        f"{len(archives)} archives" if archives else "never run",
    ))

    return signals


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db-max-mb", type=float, default=250.0, help="Alert if memory.db exceeds this.")
    ap.add_argument("--strict", action="store_true", help="Exit 1 if any signal is stale.")
    args = ap.parse_args()

    now = time.time()
    signals = collect(now)

    db = AGENT / "memory" / "memory.db"
    db_mb = db.stat().st_size / 1e6 if db.exists() else 0.0
    db_over = db_mb > args.db_max_mb

    print("Brain freshness report")
    for s in signals:
        print(s.line())
    print(f"  [{'STALE' if db_over else 'ok':^5}] {'memory.db size':<26} "
          f"{db_mb:.1f}MB (max {args.db_max_mb:g}MB)")

    stale = [s.name for s in signals if s.stale] + (["memory.db size"] if db_over else [])
    if stale:
        print(f"\nSTALE signals: {', '.join(stale)}")
    else:
        print("\nAll freshness signals within SLO.")

    return 1 if (args.strict and stale) else 0


if __name__ == "__main__":
    raise SystemExit(main())
