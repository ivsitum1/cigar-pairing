#!/usr/bin/env python3
"""Run usage-driven verifier learning cycle (export + incremental train)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

from brain_assist.verifier_learning_cycle import run_learning_cycle  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Verifier learning cycle (usage-driven)")
    parser.add_argument("--trigger", default="manual", help="manual|sessionEnd|stop|prompt|daily")
    parser.add_argument("--force", action="store_true", help="Bypass throttle")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_learning_cycle(trigger=args.trigger, force=args.force)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
