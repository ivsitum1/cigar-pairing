#!/usr/bin/env python3
"""Process verifier_usage_ledger.jsonl into dual-registry evolution (scheduled bridge)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

WORKSPACE = Path(__file__).resolve().parents[2]
LEDGER = WORKSPACE / ".agent" / "memory" / "verifier_usage_ledger.jsonl"
OUT = WORKSPACE / "outputs" / "harness" / "verifier_evolution_batch.json"


def _read_ledger(limit: int = 200) -> list[dict]:
    if not LEDGER.is_file():
        return []
    lines = LEDGER.read_text(encoding="utf-8", errors="replace").strip().splitlines()
    rows: list[dict] = []
    for line in lines[-limit:]:
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch verifier ledger into gap reports")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--apply", action="store_true", help="Run evolve_dual_registry on SKIP failures")
    args = parser.parse_args()

    rows = _read_ledger(args.limit)
    skips = [r for r in rows if str(r.get("action", "")).upper() == "SKIP"]
    batch = {
        "ledger_entries": len(rows),
        "skip_count": len(skips),
        "gap_reports": [
            {
                "prompt": r.get("prompt", "")[:300],
                "skill_id": r.get("skill_id"),
                "action": r.get("action"),
                "failure_text": f"Verifier SKIP for {r.get('skill_id')}",
            }
            for r in skips[:20]
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(batch, indent=2), encoding="utf-8")

    if args.apply and skips:
        from brain_assist.dual_registry_evolve import process_gap_report

        for report in batch["gap_reports"]:
            process_gap_report(report, propose_rewrite=False, evolve_verifier=True)

    print(json.dumps({"output": str(args.output), "skips": len(skips)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
