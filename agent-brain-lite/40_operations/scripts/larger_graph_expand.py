#!/usr/bin/env python3
"""LARGER-style grep anchor + Graphify neighbor expansion."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

from harness.larger_graph_expand import expand_from_grep  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Lexically anchor grep hits to Graphify graph.")
    parser.add_argument("--grep-hit", required=True, help="File name, path fragment, or symbol")
    parser.add_argument("--graph", default="", help="Optional path to graph.json or merged.json")
    parser.add_argument("--max-neighbors", type=int, default=12)
    parser.add_argument("--min-weight", type=float, default=0.45)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    graph_path = Path(args.graph).expanduser() if args.graph else None
    try:
        result = expand_from_grep(
            args.grep_hit,
            graph_path=graph_path,
            max_neighbors=args.max_neighbors,
            min_weight=args.min_weight,
        )
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"anchors={len(result['anchors'])} neighbors={result['neighbor_count']}")
        for n in result["neighbors"][:8]:
            sf = n.get("source_file") or ""
            print(f"  {n['weight']:.2f}\t{n.get('relation','?')}\t{sf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
