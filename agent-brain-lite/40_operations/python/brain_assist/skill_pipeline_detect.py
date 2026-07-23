"""Semantic detection of named skill pipelines (PRD / Ralph / scholarly spec)."""
from __future__ import annotations

import json
import re
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[3]
PIPELINES_PATH = WORKSPACE / "30_system" / "docs" / "skill_pipelines_dag.json"
REGISTRY_PATH = WORKSPACE / "30_system" / "SKILLS" / "registry.json"

# Later stages win ties (user intent closer to execution).
PIPELINE_STAGES: dict[str, list[dict]] = {
    "agentic-engineering": [
        {
            "target": "grill-me",
            "patterns": [
                r"\bgrill[- ]?me\b",
                r"\bshared understanding\b",
                r"\binterview before coding\b",
                r"\bdesign tree\b",
                r"\bclarify (the )?requirements\b",
                r"\bprvo razradimo\b",
                r"\bnemoj odmah kod\b",
            ],
            "weight": 1.0,
        },
        {
            "target": "write-prd",
            "patterns": [
                r"\bwrite prd\b",
                r"\bproduct requirements\b",
                r"\bprd\.json\b",
                r"\brequirements document\b",
                r"\bpasses flag\b",
                r"\bnapravi prd\b",
                r"\bproduct spec\b",
            ],
            "weight": 1.2,
        },
        {
            "target": "prd-to-issues",
            "patterns": [
                r"\bprd to issues\b",
                r"\bvertical slice",
                r"\bdecompose prd\b",
                r"\btracer bullet\b",
                r"\btask breakdown\b",
                r"\bissue breakdown\b",
            ],
            "weight": 1.3,
        },
        {
            "target": "ralph-loop",
            "patterns": [
                r"\bralph\s*on\b",
                r"\bralph\s*loop\b",
                r"\bpromise complete\b",
                r"\bexploration mode\b",
                r"\bautonomous execution\b",
                r"\brun ralph\b",
                r"\bexecute prd\b",
                r"\bimplement (the )?prd\b",
            ],
            "weight": 1.5,
        },
    ],
    "scholarly-spec": [
        {
            "target": "research-grill-me",
            "patterns": [
                r"\bresearch grill",
                r"\bpico interview\b",
                r"\bscholarly alignment\b",
                r"\bmanuscript scope\b",
            ],
            "weight": 1.0,
        },
        {
            "target": "write-research-spec",
            "patterns": [
                r"\bresearch[- ]spec\.json\b",
                r"\bwrite research spec\b",
                r"\bscholarly spec\b",
                r"\bmanuscript spec\b",
            ],
            "weight": 1.2,
        },
        {
            "target": "research-spec-to-milestones",
            "patterns": [
                r"\bresearch milestones\b",
                r"\bspec to milestones\b",
                r"\bchapter order\b",
            ],
            "weight": 1.3,
        },
        {
            "target": "scholarly-iteration-loop",
            "patterns": [
                r"\bloop\s*on\b",
                r"\bscholarly loop\b",
                r"\brun loop\b",
                r"\bresearch iteration loop\b",
            ],
            "weight": 1.5,
        },
    ],
}

FILE_HINTS: list[tuple[str, str, str]] = [
    (r"prd\.json$", "agentic-engineering", "write-prd"),
    (r"prd\.md$", "agentic-engineering", "write-prd"),
    (r"progress\.txt$", "agentic-engineering", "ralph-loop"),
    (r"research-spec\.json$", "scholarly-spec", "write-research-spec"),
]


def load_pipelines(path: Path | None = None) -> dict:
    p = path or PIPELINES_PATH
    if not p.is_file():
        return {"pipelines": []}
    return json.loads(p.read_text(encoding="utf-8"))


def _pipeline_order(pipeline: dict) -> list[str]:
    entry = pipeline.get("entry")
    order: list[str] = []
    for edge in pipeline.get("edges", []):
        src, dst = edge["from"], edge["to"]
        if src not in order:
            order.append(src)
        if dst not in order:
            order.append(dst)
    if entry and entry in order:
        order = [entry] + [s for s in order if s != entry]
    return order


def _pipeline_by_id(pipelines_doc: dict, pipeline_id: str) -> dict | None:
    for pipe in pipelines_doc.get("pipelines", []):
        if pipe.get("id") == pipeline_id:
            return pipe
    return None


def bundle_through_target(pipeline: dict, target_skill: str) -> list[str]:
    order = _pipeline_order(pipeline)
    if target_skill not in order:
        return order
    idx = order.index(target_skill)
    return order[: idx + 1]


def _score_stages(prompt: str) -> list[dict]:
    text = prompt.lower()
    hits: list[dict] = []
    for pipeline_id, stages in PIPELINE_STAGES.items():
        for stage in stages:
            matched = [p for p in stage["patterns"] if re.search(p, text, re.I)]
            if not matched:
                continue
            hits.append(
                {
                    "pipeline_id": pipeline_id,
                    "target_skill": stage["target"],
                    "score": stage["weight"] * len(matched),
                    "matched_patterns": matched,
                }
            )
    return hits


def _file_hints(files: list[str] | None) -> dict | None:
    if not files:
        return None
    best: dict | None = None
    for fpath in files:
        low = fpath.replace("\\", "/").lower()
        for pattern, pipeline_id, target in FILE_HINTS:
            if re.search(pattern, low):
                hint = {
                    "pipeline_id": pipeline_id,
                    "target_skill": target,
                    "score": 2.0,
                    "matched_patterns": [f"file:{pattern}"],
                    "source": "file_hint",
                }
                if not best or hint["score"] > best["score"]:
                    best = hint
    return best


def detect_pipeline(
    prompt: str,
    *,
    context_files: list[str] | None = None,
    min_score: float = 1.0,
    pipelines_path: Path | None = None,
) -> dict | None:
    """Return pipeline auto-load plan when semantic or file hints match."""
    hits = _score_stages(prompt)
    file_hit = _file_hints(context_files)
    if file_hit:
        hits.append(file_hit)

    if not hits:
        return None

    best = max(hits, key=lambda h: (h["score"], h["target_skill"]))
    if best["score"] < min_score:
        return None

    pipelines_doc = load_pipelines(pipelines_path)
    pipeline = _pipeline_by_id(pipelines_doc, best["pipeline_id"])
    if not pipeline:
        return None

    skills = bundle_through_target(pipeline, best["target_skill"])
    return {
        "pipeline_id": best["pipeline_id"],
        "pipeline_title": pipeline.get("title", best["pipeline_id"]),
        "target_skill": best["target_skill"],
        "confidence": round(min(0.98, best["score"] / 3.0), 3),
        "matched_patterns": best.get("matched_patterns", []),
        "skills": skills,
        "auto_load": True,
        "dag": True,
    }


def enrich_pipeline_bundle(
    detection: dict,
    registry_path: Path | None = None,
) -> list[dict]:
    """Turn detected skill ids into load-order rows for orchestrator/CLI."""
    path = registry_path or REGISTRY_PATH
    if not path.is_file():
        return [{"id": sid, "load_order": i + 1, "dag_role": "pipeline"} for i, sid in enumerate(detection["skills"])]

    registry = json.loads(path.read_text(encoding="utf-8"))
    index = {s["id"]: s for s in registry.get("skills", [])}
    rows: list[dict] = []
    target = detection["target_skill"]
    for i, sid in enumerate(detection["skills"]):
        meta = index.get(sid, {})
        if sid == target:
            role = "anchor"
        elif i < detection["skills"].index(target):
            role = "prerequisite"
        else:
            role = "pipeline"
        rows.append(
            {
                "id": sid,
                "domain": meta.get("domain", ""),
                "file": meta.get("file", f"SKILL_{sid}.md"),
                "triggers": meta.get("triggers") or [],
                "load_order": i + 1,
                "dag_role": role,
                "pipeline_id": detection["pipeline_id"],
                "score": round(1.0 - i * 0.05, 3),
                "auto_pipeline": True,
            }
        )
    if rows:
        rows[0]["pipeline_auto_load"] = detection
    return rows
