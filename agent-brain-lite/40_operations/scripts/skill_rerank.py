#!/usr/bin/env python3
"""Rank skills from registry.json by prompt similarity (TF-IDF routing assist)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

from brain_assist.skill_rerank import rank_skills  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank skills for a user prompt.")
    parser.add_argument("--prompt", "-p", required=True)
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--body", action="store_true", help="Include SKILL body in TF-IDF corpus")
    parser.add_argument("--eval-history", action="store_true", help="Add eval pass-rate bonus")
    parser.add_argument(
        "--reward-decay",
        action="store_true",
        help="Apply Socratic hint penalty from .agent/hint_ledger.jsonl (-0.1 per hint)",
    )
    parser.add_argument(
        "--dag",
        action="store_true",
        help="Expand bundle with depends_on prerequisites and pipeline edge bonuses",
    )
    parser.add_argument(
        "--rwr",
        action="store_true",
        help="SkillLens degree-corrected random walk expansion on skill graph",
    )
    parser.add_argument(
        "--auto-pipeline",
        action="store_true",
        help="Semantic PRD/Ralph/scholarly pipeline bundle (implies --dag when TF-IDF fallback)",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    use_dag = args.dag or args.auto_pipeline
    results = rank_skills(
        args.prompt,
        top_k=args.top,
        include_body=args.body,
        include_eval_history=args.eval_history,
        include_reward_decay=args.reward_decay,
        dag_mode=use_dag,
        rwr_mode=args.rwr,
        auto_pipeline=args.auto_pipeline,
    )
    if args.json:
        payload: dict = {"skills": results}
        if results and results[0].get("pipeline_auto_load"):
            payload["pipeline_auto_load"] = results[0]["pipeline_auto_load"]
        elif use_dag and results:
            payload["dag"] = results[0].get("dag")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"{r['score']:.3f}\t{r['id']}\t({r.get('domain', '')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
