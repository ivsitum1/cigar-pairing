"""SkillRAE-lite: decompose SKILL markdown into subunit operator graph."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[3]
SKILLS_DIR = WORKSPACE / "30_system" / "SKILLS"
OUTPUT_DIR = WORKSPACE / "outputs" / "skillrae"


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    body = parts[2].lstrip("\n")
    meta: dict[str, Any] = {"id": "unknown"}
    for line in parts[1].splitlines():
        if line.startswith("name:"):
            meta["id"] = line.split(":", 1)[1].strip()
        elif line.startswith("triggers:"):
            meta["triggers"] = []
        elif line.strip().startswith("- ") and "triggers" in meta:
            meta.setdefault("triggers", []).append(line.strip()[2:].strip())
        elif line.startswith("reference_files:"):
            meta["reference_files"] = []
        elif line.strip().startswith("- ") and "reference_files" in meta:
            meta.setdefault("reference_files", []).append(line.strip()[2:].strip())
    return meta, body


def decompose_skill(skill_path: Path) -> dict[str, Any]:
    text = skill_path.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(text)
    skill_id = meta.get("id") or skill_path.stem.replace("SKILL_", "")

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, str]] = []

    nodes.append({"id": "triggers", "type": "subunit", "label": "triggers"})
    for i, trig in enumerate(meta.get("triggers") or []):
        nid = f"trigger_{i}"
        nodes.append({"id": nid, "type": "trigger", "label": trig})
        edges.append({"from": "triggers", "to": nid})

    step_re = re.compile(r"^(\d+)\.\s+\*\*(.+?)\*\*", re.MULTILINE)
    steps = step_re.findall(body)
    prev = "triggers"
    for num, title in steps:
        sid = f"step_{num}"
        nodes.append({"id": sid, "type": "step", "label": title.strip()})
        edges.append({"from": prev, "to": sid})
        prev = sid

    if "## Verification" in body or "## Verification checklist" in body:
        nodes.append({"id": "verification", "type": "subunit", "label": "verification"})
        edges.append({"from": prev, "to": "verification"})

    for i, ref in enumerate(meta.get("reference_files") or []):
        rid = f"ref_{i}"
        nodes.append({"id": rid, "type": "reference", "label": ref})
        edges.append({"from": "triggers", "to": rid})

    return {
        "skill_id": skill_id,
        "source_file": str(skill_path.relative_to(WORKSPACE)).replace("\\", "/"),
        "nodes": nodes,
        "edges": edges,
    }


def decompose_by_id(skill_id: str) -> dict[str, Any]:
    path = SKILLS_DIR / f"SKILL_{skill_id}.md"
    if not path.is_file():
        raise FileNotFoundError(f"Skill not found: {path}")
    return decompose_skill(path)


def write_graph(skill_id: str) -> Path:
    graph = decompose_by_id(skill_id)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUT_DIR / f"{skill_id}_graph.json"
    out.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
