#!/usr/bin/env python3
"""Prune stale, low-confidence observations from the canonical memory store.

Addresses the "stale facts never pruned" failure mode named in 2026 agent-memory
research: memory that is both old and low-confidence degrades retrieval quality.
High-confidence facts survive regardless of age.

Wire into the weekly Windows task `AgentRules-MemoryWeeklyMaintenance`:
    python 40_operations/scripts/memory_prune.py            # prune
    python 40_operations/scripts/memory_prune.py --dry-run  # report only

Thresholds come from memory_engine.config (env-overridable):
    AGENT_MEMORY_OBS_TTL_DAYS (default 180)
    AGENT_MEMORY_PRUNE_MIN_CONFIDENCE (default 0.2)
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from memory_engine.config import load_config  # noqa: E402
from memory_engine.store import MemoryStore  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Prune stale low-confidence memory observations")
    parser.add_argument("--dry-run", action="store_true", help="Report candidates without deleting")
    parser.add_argument("--ttl-days", type=int, default=None, help="Override observation TTL in days")
    parser.add_argument("--min-confidence", type=float, default=None, help="Override min-confidence floor")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    cfg = load_config()
    if not cfg.sqlite_path.is_file():
        print(f"No memory store at {cfg.sqlite_path}; nothing to prune.")
        return 0

    ttl_days = args.ttl_days if args.ttl_days is not None else cfg.observation_ttl_days
    min_conf = args.min_confidence if args.min_confidence is not None else cfg.prune_min_confidence
    cutoff = (datetime.now(timezone.utc) - timedelta(days=ttl_days)).isoformat()

    store = MemoryStore(cfg.sqlite_path)
    result = store.prune_stale(cutoff, min_confidence=min_conf, dry_run=args.dry_run)
    payload = {
        "dry_run": args.dry_run,
        "cutoff": cutoff,
        "ttl_days": ttl_days,
        "min_confidence": min_conf,
        **result,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        verb = "would prune" if args.dry_run else "pruned"
        print(f"[memory_prune] {verb} {result['candidates']} stale obs "
              f"(<{min_conf} conf, older than {ttl_days}d)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
