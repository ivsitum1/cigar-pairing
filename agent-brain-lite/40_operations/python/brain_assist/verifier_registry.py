"""Load and apply SkillLens verifier registry (dual-registry routing layer)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[3]
VERIFIER_REGISTRY = WORKSPACE / "30_system" / "docs" / "verifier_registry.json"


def load_verifier_registry(path: Path | None = None) -> dict[str, Any]:
    p = path or VERIFIER_REGISTRY
    if not p.is_file():
        return {"defaults": {}, "skill_policies": [], "relation_overrides": [], "pending_rewrites": []}
    return json.loads(p.read_text(encoding="utf-8"))


def save_verifier_registry(data: dict[str, Any], path: Path | None = None) -> Path:
    p = path or VERIFIER_REGISTRY
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p


def policy_for_skill(registry: dict[str, Any], skill_id: str) -> dict[str, Any]:
    defaults = registry.get("defaults") or {}
    for row in registry.get("skill_policies") or []:
        if row.get("skill_id") == skill_id:
            merged = {**defaults, **row}
            return merged
    return dict(defaults)


def pending_rewrite_ids(registry: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    for row in registry.get("pending_rewrites") or []:
        sid = row.get("skill_id")
        if sid and row.get("status", "pending") == "pending":
            out.add(sid)
    return out


def relation_boosts(registry: dict[str, Any], relation_tag: str | None) -> dict[str, float]:
    if not relation_tag:
        return {}
    boosts: dict[str, float] = {}
    for row in registry.get("relation_overrides") or []:
        if row.get("relation_tag") != relation_tag:
            continue
        bonus = float(row.get("score_bonus") or 0.0)
        for sid in row.get("boost_skill_ids") or []:
            boosts[sid] = max(boosts.get(sid, 0.0), bonus)
    return boosts


def apply_relation_boosts(ranked: list[dict], boosts: dict[str, float]) -> list[dict]:
    if not boosts:
        return ranked
    updated: list[dict] = []
    for row in ranked:
        sid = row.get("id", "")
        bonus = boosts.get(sid, 0.0)
        if bonus:
            row = {
                **row,
                "score": round(float(row.get("score") or 0.0) + bonus, 4),
                "relation_bonus": round(bonus, 4),
            }
        updated.append(row)
    updated.sort(key=lambda x: float(x.get("score") or 0.0), reverse=True)
    return updated
