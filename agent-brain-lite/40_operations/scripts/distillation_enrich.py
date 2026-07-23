#!/usr/bin/env python3
"""Enrich a skeleton distillation trace. See 30_system/docs/DISTILLATION_TRACE_PROTOCOL.md."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE / "40_operations" / "python"))

from distillation.enrich import enrich_skeleton  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich a hook skeleton trace with context + reasoning")
    parser.add_argument("--trace-id", required=True, help="skeleton trace_id (dtr_...)")
    parser.add_argument("--context", required=True, help="task context / prompt summary")
    parser.add_argument("--reasoning", required=True, help="why, not just what")
    parser.add_argument("--tag", action="append", default=[], dest="tags", help="extra tags (repeatable)")
    parser.add_argument("--json", action="store_true", help="emit enriched record JSON")
    args = parser.parse_args()

    try:
        enriched = enrich_skeleton(
            args.trace_id,
            context=args.context,
            reasoning=args.reasoning,
            workspace=WORKSPACE,
            tags=args.tags,
        )
    except (ValueError, FileNotFoundError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(enriched, ensure_ascii=False, indent=2))
    else:
        print(f"enriched -> {enriched['trace_id']}  (skeleton {args.trace_id} superseded)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
