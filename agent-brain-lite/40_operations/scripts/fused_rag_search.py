#!/usr/bin/env python3
"""Fused books_rag + wiki TGS search CLI."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
PY_ROOT = WORKSPACE / "40_operations" / "python"
sys.path.insert(0, str(WORKSPACE))
sys.path.insert(0, str(PY_ROOT))

from brain_assist.fused_rag import fused_search  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Fused books_rag + TGS wiki search")
    parser.add_argument("--query", "-q", required=True)
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = fused_search(args.query, top_k=args.top)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for r in payload["results"]:
            print(
                f"{r['fused_score']:.4f}\t{r['source']}\t{r['id']}\t"
                f"b={r['book_score']} w={r['wiki_score']} br={r['bridge_score']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
