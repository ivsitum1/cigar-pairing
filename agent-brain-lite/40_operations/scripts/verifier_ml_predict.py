#!/usr/bin/env python3
"""Debug CLI: predict verifier action probabilities for a prompt/skill pair."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

from brain_assist.skill_rerank import rank_skills  # noqa: E402
from brain_assist.skill_verifier import verify_skill  # noqa: E402
from brain_assist.verifier_ml import blend_verify_skill, predict_action_proba  # noqa: E402
from brain_assist.verifier_registry import load_verifier_registry  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Verifier ML predict debug CLI")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--skill-id", default="")
    parser.add_argument("--blend", action="store_true")
    parser.add_argument("--json", action="store_true", default=True)
    args = parser.parse_args()

    ranked = rank_skills(args.prompt, top_k=8, dag_mode=True, include_body=False)
    sid = args.skill_id or (ranked[0]["id"] if ranked else "")
    skill = next((r for r in ranked if r.get("id") == sid), ranked[0] if ranked else {"id": sid, "score": 0.0})
    vreg = load_verifier_registry()
    heuristic = verify_skill(args.prompt, skill, verifier_reg=vreg)
    ml_probs = predict_action_proba(args.prompt, skill)
    payload = {
        "skill_id": sid,
        "heuristic": heuristic,
        "ml_probs": ml_probs,
    }
    if args.blend:
        import os

        os.environ["VERIFIER_ML_BLEND"] = "1"
        payload["blended"] = blend_verify_skill(args.prompt, skill, verifier_reg=vreg)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
