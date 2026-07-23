#!/usr/bin/env python3
"""Record a teacher/harness hint for Socratic reward decay."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

from brain_assist.reward_decay import append_hint  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Record skill hint for reward decay")
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--session-id", default="")
    parser.add_argument("--reason", default="")
    parser.add_argument("--hints", type=int, default=1)
    args = parser.parse_args()
    append_hint(args.skill_id, session_id=args.session_id, reason=args.reason, hints=args.hints)
    print(f"Recorded {args.hints} hint(s) for {args.skill_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
