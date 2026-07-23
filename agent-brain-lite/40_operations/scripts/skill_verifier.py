#!/usr/bin/env python3
"""SkillLens verifier gate after skill_rerank --dag."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

from brain_assist.skill_verifier import verify_bundle  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="SkillLens ACCEPT/DECOMPOSE/SKIP gate.")
    parser.add_argument("--prompt", "-p", required=True)
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--dag", action="store_true", help="Use skill_rerank --dag bundle first")
    parser.add_argument("--no-eval-history", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = verify_bundle(
        args.prompt,
        top_k=args.top,
        dag_mode=args.dag,
        include_eval_history=not args.no_eval_history,
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for d in result["decisions"]:
            extra = " rewrite_pending" if d.get("rewrite_pending") else ""
            print(f"{d['action']}\t{d['id']}\tscore={d['score']}{extra}")
        if result.get("relation_tag"):
            print(f"relation_tag={result['relation_tag']}")
        if result.get("rewrites"):
            print(f"rewrites={len(result['rewrites'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
