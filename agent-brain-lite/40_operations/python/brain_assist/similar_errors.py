"""Find past error_log entries similar to current task (TF-IDF assist)."""

from __future__ import annotations

import json
from pathlib import Path

from .tfidf_index import TfidfIndex

WORKSPACE = Path(__file__).resolve().parents[3]
ERROR_LOG = WORKSPACE / ".cursor" / "errors" / "error_log.jsonl"


def _entry_text(row: dict) -> str:
    parts = [
        row.get("ctx", ""),
        row.get("err", ""),
        row.get("fix", ""),
        row.get("cat", ""),
        " ".join(row.get("tags") or []),
    ]
    return " ".join(p for p in parts if p)


def find_similar_errors(
    prompt: str,
    *,
    error_log: Path | None = None,
    top_k: int = 5,
    min_score: float = 0.05,
) -> list[dict]:
    path = error_log or ERROR_LOG
    if not path.is_file() or not prompt.strip():
        return []
    rows: list[dict] = []
    ids: list[str] = []
    texts: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        eid = row.get("id") or f"row_{len(rows)}"
        text = _entry_text(row)
        if len(text) < 20:
            continue
        ids.append(eid)
        texts.append(text)
        rows.append(row)
    if not ids:
        return []
    index = TfidfIndex(ids, texts)
    ranked = index.rank(prompt, top_k=top_k, min_score=min_score)
    id_to_row = {ids[i]: rows[i] for i in range(len(rows))}
    out: list[dict] = []
    for eid, score in ranked:
        row = id_to_row.get(eid)
        if not row:
            continue
        out.append(
            {
                "id": eid,
                "score": round(score, 4),
                "cat": row.get("cat"),
                "sev": row.get("sev"),
                "ctx": row.get("ctx"),
                "err": row.get("err"),
                "fix": row.get("fix"),
                "promoted": row.get("promoted"),
            }
        )
    return out
