#!/usr/bin/env python3
"""Surface similar past errors from error_log.jsonl (TF-IDF assist)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

from brain_assist.similar_errors import find_similar_errors  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Find similar error_log entries.")
    parser.add_argument("--prompt", "-p", required=True)
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    results = find_similar_errors(args.prompt, top_k=args.top)
    if args.json:
        print(json.dumps({"errors": results}, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"{r['score']:.3f}\t{r['id']}\t[{r.get('cat')}] {str(r.get('err', ''))[:80]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
