"""Rcml relation registry: detect relation tags and export training-ready datasets."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[3]
RCML_REGISTRY = WORKSPACE / "30_system" / "docs" / "rcml_relation_registry.json"

RELATION_KEYWORDS: dict[str, list[str]] = {
    "causality": ["bug", "fix", "regression", "root cause", "failure", "error", "debug", "uzrok"],
    "dependency": ["refactor", "import", "module", "coupling", "architecture", "depends", "ovisnost"],
    "assumption_chain": ["assumption", "sap", "protocol", "test selection", "methods", "pretpostavk"],
    "evidence_strength": ["manuscript", "claim", "cite", "evidence", "grade", "swiss", "literature"],
    "procedure_reuse": ["skill", "pipeline", "workflow", "reuse", "procedure", "ralph"],
}


def load_rcml_registry(path: Path | None = None) -> dict[str, Any]:
    p = path or RCML_REGISTRY
    if not p.is_file():
        return {"relations": []}
    return json.loads(p.read_text(encoding="utf-8"))


def detect_relation_tag(prompt: str, registry: dict[str, Any] | None = None) -> str | None:
    reg = registry or load_rcml_registry()
    prompt_l = prompt.lower()
    best_id: str | None = None
    best_score = 0

    for rel in reg.get("relations") or []:
        rid = rel.get("id", "")
        score = 0
        for tag in rel.get("harness_tags") or []:
            if tag.lower() in prompt_l:
                score += 2
        for kw in RELATION_KEYWORDS.get(rid, []):
            if kw in prompt_l:
                score += 1
        for tt in rel.get("task_types") or []:
            if tt.lower() in prompt_l:
                score += 1
        if score > best_score:
            best_score = score
            best_id = rid

    return best_id if best_score > 0 else None


def relation_by_id(registry: dict[str, Any], relation_id: str) -> dict[str, Any] | None:
    for rel in registry.get("relations") or []:
        if rel.get("id") == relation_id:
            return rel
    return None


def export_contrastive_jsonl(registry: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rel in registry.get("relations") or []:
        rid = rel.get("id")
        desc = rel.get("description_nl", "")
        for ex in rel.get("examples") or []:
            rows.append(
                {
                    "relation_id": rid,
                    "relation_nl": desc,
                    "anchor": ex.get("anchor", ""),
                    "positive": ex.get("positive", ""),
                    "negative": ex.get("negative", ""),
                    "modality": ",".join(rel.get("modalities") or ["text"]),
                    "many_to_many": (rel.get("training_schema") or {}).get("many_to_many", False),
                }
            )
        if not rel.get("examples"):
            rows.append(
                {
                    "relation_id": rid,
                    "relation_nl": desc,
                    "anchor": "",
                    "positive": rel.get("routing_hint", ""),
                    "negative": "",
                    "modality": ",".join(rel.get("modalities") or ["text"]),
                    "many_to_many": (rel.get("training_schema") or {}).get("many_to_many", False),
                }
            )
    return rows


def export_instruction_jsonl(registry: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rel in registry.get("relations") or []:
        rid = rel.get("id")
        desc = rel.get("description_nl", "")
        hint = rel.get("routing_hint", "")
        rows.append(
            {
                "relation_id": rid,
                "instruction": f"Route the agent under relation [{rid}]: {desc}",
                "input": "{{user_prompt}}",
                "output": hint,
            }
        )
    return rows
