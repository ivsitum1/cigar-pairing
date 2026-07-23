#!/usr/bin/env python3
"""Compare SkillRAE subunit graphs vs SkillDAG inter-skill metadata (SD-6)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
REGISTRY = WORKSPACE / "30_system" / "SKILLS" / "registry.json"
PIPELINES = WORKSPACE / "30_system" / "docs" / "skill_pipelines_dag.json"
OUT_JSON = WORKSPACE / "outputs" / "skillrae" / "skilldag_subunit_compare.json"
OUT_MD = WORKSPACE / "outputs" / "skillrae" / "skilldag_subunit_compare.md"

DEFAULT_SKILL_IDS = [
    "grill-me",
    "write-prd",
    "prd-to-issues",
    "ralph-loop",
    "research-grill-me",
    "write-research-spec",
    "research-spec-to-milestones",
    "scholarly-iteration-loop",
    "notebooklm-research-gate",
    "meta-analysis",
]

PY_ROOT = WORKSPACE / "40_operations" / "python"
sys.path.insert(0, str(PY_ROOT))
from brain_assist.skill_decompose import decompose_by_id  # noqa: E402


def _load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def _skill_meta(registry: dict, skill_id: str) -> dict:
    for s in registry.get("skills", []):
        if s["id"] == skill_id:
            return s
    return {}


def _pipeline_edges(pipelines_doc: dict, skill_id: str) -> list[dict]:
    out: list[dict] = []
    for pipe in pipelines_doc.get("pipelines", []):
        for edge in pipe.get("edges", []):
            if edge.get("from") == skill_id or edge.get("to") == skill_id:
                out.append(
                    {
                        "pipeline": pipe.get("id"),
                        "from": edge.get("from"),
                        "to": edge.get("to"),
                        "type": edge.get("type", "depends_on"),
                    }
                )
    return out


def build_compare(skill_ids: list[str]) -> dict:
    registry = _load_registry()
    pipelines_doc = json.loads(PIPELINES.read_text(encoding="utf-8"))
    rows: list[dict] = []

    for sid in skill_ids:
        try:
            graph = decompose_by_id(sid)
        except FileNotFoundError:
            rows.append({"skill_id": sid, "error": "skill file missing"})
            continue

        meta = _skill_meta(registry, sid)
        subunit_types = sorted({n.get("type") for n in graph.get("nodes", [])})
        rows.append(
            {
                "skill_id": sid,
                "skillrae_nodes": len(graph.get("nodes", [])),
                "skillrae_edges": len(graph.get("edges", [])),
                "skillrae_node_types": subunit_types,
                "skilldag_depends_on": meta.get("depends_on") or [],
                "pipeline_group": meta.get("pipeline_group"),
                "conflicts_with": meta.get("conflicts_with") or [],
                "pipeline_edges": _pipeline_edges(pipelines_doc, sid),
                "graph_scope": "intra-skill subunit",
                "dag_scope": "inter-skill" if meta.get("depends_on") or meta.get("pipeline_group") else "none",
            }
        )

    with_dep = sum(1 for r in rows if r.get("skilldag_depends_on"))
    gap = (
        "SkillRAE subunit graphs are intra-skill (steps/triggers); SkillDAG depends_on is inter-skill. "
        "They are complementary, not substitutable. Runtime gap: skill_rerank.py is flat TF-IDF and does not "
        "consume depends_on yet — edge-aware routing deferred to skill-dag-router / future --dag rerank."
    )

    return {
        "skill_ids": skill_ids,
        "rows": rows,
        "summary": {
            "skills_compared": len(rows),
            "with_depends_on": with_dep,
            "sd7_recommendation": "defer_full_router",
            "sd7_rationale": gap,
        },
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# SkillRAE subunit vs SkillDAG inter-skill compare (SD-6)",
        "",
        f"Skills compared: **{report['summary']['skills_compared']}** | "
        f"With `depends_on`: **{report['summary']['with_depends_on']}**",
        "",
        "| Skill | SkillRAE nodes | SkillRAE edge types | depends_on | pipeline_group | Pipeline edges |",
        "|-------|----------------|---------------------|------------|----------------|----------------|",
    ]
    for r in report.get("rows", []):
        if r.get("error"):
            lines.append(f"| {r['skill_id']} | — | — | — | — | {r['error']} |")
            continue
        types = ", ".join(r.get("skillrae_node_types") or [])
        deps = ", ".join(r.get("skilldag_depends_on") or []) or "—"
        pg = r.get("pipeline_group") or "—"
        pe = "; ".join(
            f"{e['pipeline']}: {e['from']}→{e['to']}" for e in r.get("pipeline_edges") or []
        ) or "—"
        lines.append(
            f"| {r['skill_id']} | {r['skillrae_nodes']} | {types} | {deps} | {pg} | {pe} |"
        )

    lines.extend(
        [
            "",
            "## SD-7 gate",
            "",
            report["summary"]["sd7_rationale"],
            "",
            "**Decision:** Document-only + optional `skill-dag-router` pointer skill (no `skill_rerank --dag` yet).",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output-json", default=str(OUT_JSON))
    parser.add_argument("--output-md", default=str(OUT_MD))
    parser.add_argument("--skill-id", action="append", dest="skill_ids")
    args = parser.parse_args()

    skill_ids = args.skill_ids or DEFAULT_SKILL_IDS
    report = build_compare(skill_ids)

    out_json = Path(args.output_json)
    out_md = Path(args.output_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(out_json)
        print(out_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
