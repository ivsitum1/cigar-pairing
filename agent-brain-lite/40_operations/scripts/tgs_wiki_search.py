#!/usr/bin/env python3
"""TGS multi-hop wiki RAG CLI (text-graph synergy + orphan bridging)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

from brain_assist.tgs_rag import tgs_search  # noqa: E402
from brain_assist.hybrid_retrieve import hybrid_search  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="TGS wiki RAG search")
    parser.add_argument("--query", "-q", required=True)
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--multihop", action="store_true", help="Use full TGS (default)")
    parser.add_argument("--pilot", action="store_true", help="1-hop hybrid pilot only")
    parser.add_argument("--max-hops", type=int, default=3)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.pilot:
        results = hybrid_search(args.query, top_k=args.top)
        payload = {"mode": "pilot", "results": results}
    else:
        results = tgs_search(args.query, top_k=args.top, max_hops=args.max_hops)
        payload = {"mode": "tgs_multihop", "results": results}

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for r in results:
            if "graph_score" in r:
                print(f"{r['score']:.4f}\t{r['page_id']}\tt={r['text_score']} g={r['graph_score']} b={r['bridge_score']}")
            else:
                print(f"{r['score']:.4f}\t{r['page_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
