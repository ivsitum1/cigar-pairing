#!/usr/bin/env python3
"""Build structured gap report from trajectory.jsonl for skill_gap_ingest."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

from trajectory_rl.gap_report import build_gap_report  # noqa: E402

WORKSPACE = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser(description="Trajectory skill-gap report")
    parser.add_argument("--trace", default="", help="Path to trajectory.jsonl")
    parser.add_argument("--skill-id", default="", help="Target skill for suggested eval case")
    parser.add_argument("--prompt", default="", help="Optional task prompt context")
    parser.add_argument("--output", "-o", default="", help="Write JSON report path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    trace = Path(args.trace).expanduser() if args.trace else None
    report = build_gap_report(
        trace_path=trace,
        skill_id=args.skill_id or None,
        prompt=args.prompt or None,
    )

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(str(out))

    if args.json or not args.output:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("error") != "no_trajectory_found" else 1


if __name__ == "__main__":
    raise SystemExit(main())
