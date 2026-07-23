#!/usr/bin/env python3
"""Propose SkillDAG edges from skill gap / failure trajectory (P2 experimental)."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
OUT = WORKSPACE / "outputs" / "skillrae" / "proposed_edges.jsonl"
ERROR_LOG = WORKSPACE / ".cursor" / "errors" / "error_log.jsonl"


def _recent_errors(limit: int = 30) -> list[dict]:
    if not ERROR_LOG.is_file():
        return []
    rows: list[dict] = []
    for line in ERROR_LOG.read_text(encoding="utf-8", errors="replace").strip().splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Propose depends_on edges from error patterns")
    parser.add_argument("--from-skill", required=True)
    parser.add_argument("--to-skill", required=True)
    parser.add_argument("--reason", default="trajectory-derived")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    proposal = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "edge": {"from": args.from_skill, "to": args.to_skill, "type": "depends_on"},
        "reason": args.reason,
        "status": "proposed",
        "recent_errors": len(_recent_errors()),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    if not args.dry_run:
        with OUT.open("a", encoding="utf-8") as f:
            f.write(json.dumps(proposal, ensure_ascii=False) + "\n")

    print(json.dumps(proposal, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
