"""HORMA-inspired memory hierarchy for .agent/memory_hierarchy/."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AGENT = Path(__file__).resolve().parents[3] / ".agent"
MEMORY_HIERARCHY = AGENT / "memory_hierarchy"
INDEX_PATH = MEMORY_HIERARCHY / "index.json"
SUMMARIES_DIR = MEMORY_HIERARCHY / "summaries"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower().strip())[:40].strip("-")
    return s or "lemma"


def load_index() -> dict[str, Any]:
    if not INDEX_PATH.is_file():
        return {"nodes": [], "version": "1.0", "updated_at": _utc_now()}
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def save_index(data: dict[str, Any]) -> None:
    MEMORY_HIERARCHY.mkdir(parents=True, exist_ok=True)
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = _utc_now()
    INDEX_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def bootstrap(*, force: bool = False) -> dict[str, Any]:
    """Create memory_hierarchy layout if missing."""
    if INDEX_PATH.is_file() and not force:
        return load_index()
    data: dict[str, Any] = {"version": "1.0", "nodes": [], "updated_at": _utc_now()}
    save_index(data)
    (MEMORY_HIERARCHY / "raw").mkdir(parents=True, exist_ok=True)
    return data


def add_lemma_node(
    *,
    subgoal: str,
    summary: str,
    provenance: str = "",
    solved_lemmas_line: int | None = None,
) -> dict[str, Any]:
    """Add summary node from a folded lemma; returns the new node record."""
    bootstrap()
    index = load_index()
    nodes: list[dict[str, Any]] = list(index.get("nodes") or [])
    node_id = f"lemma-{len(nodes) + 1:03d}"
    slug = _slugify(subgoal)
    summary_path = f"summaries/{node_id}-{slug}.md"
    summary_file = MEMORY_HIERARCHY / summary_path
    prov_list: list[str] = []
    if provenance:
        prov_list.append(provenance)
    if solved_lemmas_line is not None:
        prov_list.append(f".agent/solved_lemmas.jsonl#L{solved_lemmas_line}")

    body = (
        f"---\n"
        f"id: {node_id}\n"
        f"memory_op: write\n"
        f"schema_version: \"1.0\"\n"
        f"subgoal: {subgoal[:200]}\n"
        f"provenance: {json.dumps(prov_list)}\n"
        f"updated_at: {_utc_now()}\n"
        f"---\n\n"
        f"{summary}\n"
    )
    summary_file.write_text(body, encoding="utf-8")

    token_estimate = max(1, len(summary.split()) + len(subgoal.split()))
    node = {
        "id": node_id,
        "title": subgoal[:200],
        "summary_path": summary_path.replace("\\", "/"),
        "provenance": prov_list,
        "token_estimate": token_estimate,
        "updated_at": _utc_now(),
    }
    nodes.append(node)
    index["nodes"] = nodes
    save_index(index)
    return node


def sync_from_solved_lemmas(solved_lemmas_path: Path | None = None) -> int:
    """Bootstrap index entries for lemmas not yet in hierarchy. Returns count added."""
    path = solved_lemmas_path or (AGENT / "solved_lemmas.jsonl")
    if not path.is_file():
        return 0
    bootstrap()
    index = load_index()
    existing_titles = {n.get("title", "") for n in index.get("nodes") or []}
    added = 0
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        subgoal = rec.get("subgoal", "")
        if subgoal in existing_titles:
            continue
        add_lemma_node(
            subgoal=subgoal,
            summary=rec.get("summary", ""),
            provenance=rec.get("provenance", ""),
            solved_lemmas_line=line_no,
        )
        existing_titles.add(subgoal)
        added += 1
    return added
