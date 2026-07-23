"""Edge-aware DAG bundle expansion for skill_rerank (SkillDAG P2)."""
from __future__ import annotations

import json
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[3]
PIPELINES_PATH = WORKSPACE / "30_system" / "docs" / "skill_pipelines_dag.json"

# Edge-weight bonuses applied on top of TF-IDF score.
DIRECT_PREREQ_BONUS = 0.06
PIPELINE_PATH_BONUS = 0.03
PREREQ_SYNTHETIC_RATIO = 0.55


def load_pipelines(path: Path | None = None) -> dict:
    p = path or PIPELINES_PATH
    if not p.is_file():
        return {"pipelines": []}
    return json.loads(p.read_text(encoding="utf-8"))


def depends_map(skills: list[dict]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for skill in skills:
        sid = skill["id"]
        out[sid] = list(skill.get("depends_on") or [])
    return out


def conflicts_map(skills: list[dict]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for skill in skills:
        sid = skill["id"]
        out.setdefault(sid, set())
        for other in skill.get("conflicts_with") or []:
            out[sid].add(other)
            out.setdefault(other, set()).add(sid)
    return out


def _pipeline_positions(pipelines_doc: dict) -> dict[str, list[dict]]:
    """Map skill_id -> [{pipeline_id, index, entry, exit}]."""
    index: dict[str, list[dict]] = {}
    for pipe in pipelines_doc.get("pipelines", []):
        pid = pipe.get("id", "")
        entry = pipe.get("entry")
        exit_id = pipe.get("exit")
        order: list[str] = []
        for edge in pipe.get("edges", []):
            src, dst = edge["from"], edge["to"]
            if src not in order:
                order.append(src)
            if dst not in order:
                order.append(dst)
        if entry and entry in order:
            order = [entry] + [s for s in order if s != entry]
        for i, sid in enumerate(order):
            index.setdefault(sid, []).append(
                {"pipeline_id": pid, "index": i, "entry": entry, "exit": exit_id}
            )
    return index


def prereq_chain(skill_id: str, dep_map: dict[str, list[str]]) -> list[str]:
    """Transitive prerequisites in load order (deps before dependents)."""
    chain: list[str] = []
    seen: set[str] = set()

    def visit(sid: str) -> None:
        for dep in dep_map.get(sid, []):
            if dep in seen:
                continue
            visit(dep)
            seen.add(dep)
            chain.append(dep)

    visit(skill_id)
    return chain


def _conflicts_with_any(skill_id: str, group: set[str], cmap: dict[str, set[str]]) -> bool:
    for other in group:
        if other == skill_id:
            continue
        if other in cmap.get(skill_id, set()):
            return True
    return False


def _dag_bonus(
    skill_id: str,
    anchor: str,
    dep_map: dict[str, list[str]],
    pipe_pos: dict[str, list[dict]],
    tfidf_score: float,
) -> float:
    bonus = 0.0
    if skill_id in dep_map.get(anchor, []):
        bonus += DIRECT_PREREQ_BONUS
    anchor_pipes = {p["pipeline_id"]: p["index"] for p in pipe_pos.get(anchor, [])}
    for pinfo in pipe_pos.get(skill_id, []):
        pid = pinfo["pipeline_id"]
        if pid in anchor_pipes:
            dist = abs(pinfo["index"] - anchor_pipes[pid])
            bonus += max(0.0, PIPELINE_PATH_BONUS - dist * 0.01)
    if skill_id in prereq_chain(anchor, dep_map) and skill_id != anchor:
        bonus += DIRECT_PREREQ_BONUS * 0.5
    return round(bonus, 4) if bonus else 0.0


def _meta_from_registry(skill: dict) -> dict:
    return {
        "id": skill["id"],
        "domain": skill.get("domain", ""),
        "file": skill.get("file", ""),
        "triggers": skill.get("triggers") or [],
    }


def apply_dag_bundle(
    flat_results: list[dict],
    registry: dict,
    pipelines_doc: dict | None = None,
    *,
    top_k: int = 5,
) -> tuple[list[dict], dict]:
    """Expand TF-IDF hits with prerequisite chain and pipeline edge bonuses."""
    if not flat_results:
        return [], {"anchor": None, "pipeline_id": None, "bundle_order": []}

    skills = registry.get("skills") or []
    skill_by_id = {s["id"]: s for s in skills}
    dep_map = depends_map(skills)
    cmap = conflicts_map(skills)
    pipes = pipelines_doc if pipelines_doc is not None else load_pipelines()
    pipe_pos = _pipeline_positions(pipes)

    anchor = flat_results[0]["id"]
    anchor_score = flat_results[0].get("tfidf_score") or flat_results[0].get("score", 0.0)

    prereqs = prereq_chain(anchor, dep_map)
    bundle_order: list[str] = []
    selected: set[str] = set()

    for sid in prereqs:
        if sid not in selected:
            bundle_order.append(sid)
            selected.add(sid)
    if anchor not in selected:
        bundle_order.append(anchor)
        selected.add(anchor)

    extras_slots = max(0, top_k - 1)
    extras_added = 0
    for row in flat_results[1:]:
        if extras_added >= extras_slots:
            break
        sid = row["id"]
        if sid in selected:
            continue
        if _conflicts_with_any(sid, selected, cmap):
            continue
        bundle_order.append(sid)
        selected.add(sid)
        extras_added += 1

    flat_by_id = {r["id"]: r for r in flat_results}
    pipeline_id = None
    if pipe_pos.get(anchor):
        pipeline_id = pipe_pos[anchor][0]["pipeline_id"]

    enriched: list[dict] = []
    for i, sid in enumerate(bundle_order):
        base = flat_by_id.get(sid)
        if base:
            tfidf = base.get("tfidf_score") or base.get("score", 0.0)
            eval_bonus = base.get("eval_bonus")
        else:
            tfidf = round(anchor_score * PREREQ_SYNTHETIC_RATIO, 4)
            eval_bonus = None

        dag_bonus = _dag_bonus(sid, anchor, dep_map, pipe_pos, tfidf)
        final = round(tfidf + (eval_bonus or 0.0) + dag_bonus, 4)

        if sid == anchor:
            role = "anchor"
        elif sid in prereqs:
            role = "prerequisite"
        else:
            role = "candidate"

        entry = {
            **(base or _meta_from_registry(skill_by_id[sid])),
            "score": final,
            "tfidf_score": round(tfidf, 4),
            "eval_bonus": eval_bonus,
            "dag_bonus": dag_bonus,
            "dag_role": role,
            "pipeline_id": pipeline_id if sid in (prereqs + [anchor]) or pipe_pos.get(sid) else None,
            "load_order": i + 1,
        }
        enriched.append(entry)

    dag_meta = {
        "anchor": anchor,
        "pipeline_id": pipeline_id,
        "bundle_order": bundle_order,
        "prerequisites_injected": [p for p in prereqs if p not in flat_by_id],
    }
    return enriched, dag_meta
