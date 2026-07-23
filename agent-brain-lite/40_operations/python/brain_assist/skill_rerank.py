"""Rank registry skills by TF-IDF similarity to user prompt (routing assist only)."""
from __future__ import annotations

import json
from pathlib import Path

from .skill_dag_rerank import apply_dag_bundle, load_pipelines
from .skill_pipeline_detect import detect_pipeline, enrich_pipeline_bundle
from .skill_rwr import rwr_expand_ranked
from .reward_decay import apply_reward_decay, load_hint_counts
from .tfidf_index import TfidfIndex

WORKSPACE = Path(__file__).resolve().parents[3]
REGISTRY = WORKSPACE / "30_system" / "SKILLS" / "registry.json"
PIPELINES = WORKSPACE / "30_system" / "docs" / "skill_pipelines_dag.json"
SKILLS_DIR = WORKSPACE / "30_system" / "SKILLS"
EVALS_DIR = SKILLS_DIR / "evals"


def _strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2]
    return text


def _skill_body_snippet(skill_id: str, max_chars: int = 2000) -> str:
    path = SKILLS_DIR / f"SKILL_{skill_id}.md"
    if not path.is_file():
        return ""
    body = _strip_frontmatter(path.read_text(encoding="utf-8"))
    return body[:max_chars]


def _eval_pass_bonus(skill_id: str) -> float:
    outputs = EVALS_DIR / f"{skill_id}_outputs.json"
    eval_file = EVALS_DIR / f"{skill_id}.json"
    if not eval_file.is_file():
        return 0.0
    if not outputs.is_file():
        return 0.02
    try:
        cases = json.loads(eval_file.read_text(encoding="utf-8")).get("cases") or []
        outs = json.loads(outputs.read_text(encoding="utf-8"))
        if not cases:
            return 0.0
        passed = sum(1 for c in cases if outs.get(c.get("id")))
        rate = passed / len(cases)
        return round(min(0.12, rate * 0.12), 4)
    except (json.JSONDecodeError, OSError):
        return 0.0


def _skill_text(entry: dict, *, include_body: bool = False) -> str:
    sid = entry.get("id", "")
    parts = [
        sid,
        entry.get("domain", ""),
        " ".join(entry.get("triggers") or []),
        entry.get("disambiguation", ""),
    ]
    if include_body:
        parts.append(_skill_body_snippet(sid))
    return " ".join(p for p in parts if p)


def rank_skills(
    prompt: str,
    *,
    registry_path: Path | None = None,
    pipelines_path: Path | None = None,
    context_files: list[str] | None = None,
    top_k: int = 5,
    min_score: float = 0.04,
    include_body: bool = False,
    include_eval_history: bool = False,
    include_reward_decay: bool = False,
    dag_mode: bool = False,
    rwr_mode: bool = False,
    auto_pipeline: bool = False,
) -> list[dict]:
    if auto_pipeline:
        detection = detect_pipeline(prompt, context_files=context_files, pipelines_path=pipelines_path)
        if detection:
            return enrich_pipeline_bundle(detection, registry_path)

    path = registry_path or REGISTRY
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    skills = data.get("skills") or []
    ids: list[str] = []
    texts: list[str] = []
    meta: dict[str, dict] = {}
    for s in skills:
        sid = s.get("id")
        if not sid:
            continue
        ids.append(sid)
        texts.append(_skill_text(s, include_body=include_body))
        meta[sid] = {
            "id": sid,
            "domain": s.get("domain", ""),
            "file": s.get("file", ""),
            "triggers": s.get("triggers") or [],
        }
    if not ids:
        return []
    index = TfidfIndex(ids, texts)
    ranked = index.rank(
        prompt,
        top_k=top_k * 2 if (include_eval_history or include_reward_decay) else top_k,
        min_score=min_score,
    )
    hint_counts = load_hint_counts() if include_reward_decay else {}
    results: list[dict] = []
    for sid, score in ranked:
        if sid not in meta:
            continue
        final = score
        eval_bonus = 0.0
        hint_penalty = 0.0
        if include_eval_history:
            eval_bonus = _eval_pass_bonus(sid)
            final = score + eval_bonus
        if include_reward_decay:
            final, hint_penalty = apply_reward_decay(final, hint_counts.get(sid, 0))
        results.append(
            {
                **meta[sid],
                "score": round(final, 4),
                "tfidf_score": round(score, 4),
                "eval_bonus": round(eval_bonus, 4) if include_eval_history else None,
                "hint_penalty": round(hint_penalty, 4) if include_reward_decay else None,
                "hint_count": hint_counts.get(sid, 0) if include_reward_decay else None,
            }
        )
    results.sort(key=lambda x: x["score"], reverse=True)
    flat = results[:top_k]

    if rwr_mode and flat:
        rwr_flat = rwr_expand_ranked(flat, data, load_pipelines(pipelines_path or PIPELINES), top_k=top_k)
        if rwr_flat:
            flat = rwr_flat

    if not dag_mode:
        return flat

    pipelines_doc = load_pipelines(pipelines_path or PIPELINES)
    bundled, dag_meta = apply_dag_bundle(flat, data, pipelines_doc, top_k=top_k)
    if bundled:
        bundled[0]["dag"] = dag_meta
    return bundled
