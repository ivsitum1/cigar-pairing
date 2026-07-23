"""SkillLens-style verifier gate: ACCEPT / DECOMPOSE / REWRITE / SKIP before skill body load."""
from __future__ import annotations

import json
from pathlib import Path

from .rcml_registry import detect_relation_tag
from .reward_decay import apply_reward_decay, load_hint_counts
from .skill_rerank import rank_skills
from .verifier_registry import (
    apply_relation_boosts,
    load_verifier_registry,
    pending_rewrite_ids,
    policy_for_skill,
    relation_boosts,
)

WORKSPACE = Path(__file__).resolve().parents[3]
REGISTRY = WORKSPACE / "30_system" / "SKILLS" / "registry.json"


def _trigger_overlap(prompt: str, triggers: list[str]) -> float:
    if not triggers:
        return 0.0
    prompt_l = prompt.lower()
    hits = sum(1 for t in triggers if t.lower() in prompt_l)
    return hits / len(triggers)


def verify_skill(
    prompt: str,
    skill: dict,
    *,
    verifier_reg: dict | None = None,
    pending_rewrites: set[str] | None = None,
) -> dict:
    vreg = verifier_reg or load_verifier_registry()
    pending = pending_rewrites if pending_rewrites is not None else pending_rewrite_ids(vreg)
    sid = skill.get("id", "")
    policy = policy_for_skill(vreg, sid)

    score = float(skill.get("score") or 0.0)
    triggers = skill.get("triggers") or []
    overlap = _trigger_overlap(prompt, triggers)
    granularity = skill.get("granularity", policy.get("granularity_override", "procedure"))

    accept_score = float(policy.get("accept_score", 0.12))
    decompose_score = float(policy.get("decompose_score", 0.04))
    trigger_ratio = float(policy.get("trigger_hit_ratio", policy.get("min_trigger_overlap", 0.2)))
    rewrite_band = policy.get("rewrite_score_band") or vreg.get("defaults", {}).get("rewrite_score_band") or [0.04, 0.12]

    force = policy.get("force_action")
    if force:
        action = force
    elif score >= accept_score or (score >= decompose_score and overlap >= trigger_ratio):
        action = "ACCEPT"
    elif score >= decompose_score or overlap > 0:
        action = "DECOMPOSE"
    else:
        action = "SKIP"

    if granularity == "policy" and not force:
        action = "ACCEPT"

    rewrite_on_gap = bool(policy.get("rewrite_on_gap"))
    low, high = float(rewrite_band[0]), float(rewrite_band[1])
    if (
        action in {"DECOMPOSE", "ACCEPT"}
        and rewrite_on_gap
        and sid in pending
        and low <= score <= high
    ):
        action = "REWRITE"

    out = {
        "id": sid,
        "action": action,
        "score": round(score, 4),
        "trigger_overlap": round(overlap, 4),
        "granularity": granularity,
        "dag_role": skill.get("dag_role"),
        "load_order": skill.get("load_order"),
    }
    if action == "REWRITE":
        out["rewrite_pending"] = True
    return out


def verify_bundle(
    prompt: str,
    *,
    ranked: list[dict] | None = None,
    registry_path: Path | None = None,
    verifier_registry_path: Path | None = None,
    top_k: int = 5,
    dag_mode: bool = True,
    include_eval_history: bool = True,
    include_reward_decay: bool = True,
    relation_tag: str | None = None,
) -> dict:
    vreg = load_verifier_registry(verifier_registry_path)
    rel_tag = relation_tag or detect_relation_tag(prompt)
    boosts = relation_boosts(vreg, rel_tag)
    pending = pending_rewrite_ids(vreg)
    hint_counts = load_hint_counts() if include_reward_decay else {}

    if ranked is None:
        ranked = rank_skills(
            prompt,
            registry_path=registry_path,
            top_k=top_k,
            dag_mode=dag_mode,
            include_eval_history=include_eval_history,
            include_reward_decay=include_reward_decay,
            include_body=False,
        )

    ranked = apply_relation_boosts(ranked, boosts)

    registry = json.loads((registry_path or REGISTRY).read_text(encoding="utf-8"))
    gran = {s["id"]: s.get("granularity", "procedure") for s in registry.get("skills") or []}

    enriched: list[dict] = []
    for row in ranked:
        sid = row.get("id", "")
        merged = {**row, "granularity": gran.get(sid, "procedure")}
        enriched.append(merged)

    try:
        from .verifier_ml import ml_blend_active

        use_blend = ml_blend_active()
    except Exception:
        use_blend = __import__("os").environ.get("VERIFIER_ML_BLEND", "").strip() in {"1", "true", "TRUE"}
    if use_blend:
        try:
            from .verifier_ml import blend_verify_skill

            decisions = [
                blend_verify_skill(
                    prompt,
                    s,
                    verifier_reg=vreg,
                    pending_rewrites=pending,
                    relation_tag=rel_tag,
                )
                for s in enriched
            ]
        except Exception:
            decisions = [
                verify_skill(prompt, s, verifier_reg=vreg, pending_rewrites=pending) for s in enriched
            ]
    else:
        decisions = [
            verify_skill(prompt, s, verifier_reg=vreg, pending_rewrites=pending) for s in enriched
        ]
    to_load = [d for d in decisions if d["action"] in {"ACCEPT", "DECOMPOSE", "REWRITE"}]
    rewrites = [d for d in decisions if d["action"] == "REWRITE"]

    return {
        "prompt": prompt,
        "relation_tag": rel_tag,
        "decisions": decisions,
        "to_load": to_load,
        "rewrites": rewrites,
        "dag": enriched[0].get("dag") if enriched else None,
    }
