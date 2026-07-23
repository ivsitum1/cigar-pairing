#!/usr/bin/env python3
"""Wiki hybrid search CLI (text + wikilink graph pilot)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

from brain_assist.hybrid_retrieve import hybrid_search  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Hybrid wiki search")
    parser.add_argument("--query", "-q", required=True)
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    results = hybrid_search(args.query, top_k=args.top)
    if args.json:
        print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"{r['score']:.4f}\t{r['page_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
