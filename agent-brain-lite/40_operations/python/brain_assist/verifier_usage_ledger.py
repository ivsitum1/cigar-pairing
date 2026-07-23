"""Append-only usage ledger for SkillLens verifier + LARGER hook decisions."""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[3]
DEFAULT_LEDGER = WORKSPACE / ".agent" / "memory" / "verifier_usage_ledger.jsonl"

_PHI_PATTERNS = (
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\bMRN[:\s]?\d+\b", re.I),
    re.compile(r"\b\d{10,}\b"),
)


def ledger_path() -> Path:
    override = os.environ.get("VERIFIER_USAGE_LEDGER_PATH", "").strip()
    return Path(override).expanduser() if override else DEFAULT_LEDGER


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def prompt_hash(prompt: str) -> str:
    normalized = " ".join(prompt.strip().lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def sanitize_text(text: str, *, max_len: int = 400) -> str:
    out = text.strip()
    for pat in _PHI_PATTERNS:
        out = pat.sub("[REDACTED]", out)
    if len(out) > max_len:
        return out[: max_len - 3].rstrip() + "..."
    return out


def _append_row(row: dict[str, Any]) -> None:
    path = ledger_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def record_skill_lens(
    *,
    prompt: str,
    bundle: dict[str, Any],
    session_id: str | None = None,
    event: str = "beforeSubmitPrompt",
) -> None:
    if os.environ.get("VERIFIER_USAGE_LEDGER_DISABLED", "").strip() in {"1", "true", "TRUE"}:
        return
    try:
        decisions = []
        for d in bundle.get("decisions") or []:
            decisions.append(
                {
                    "id": d.get("id"),
                    "action": d.get("action"),
                    "score": d.get("score"),
                    "trigger_overlap": d.get("trigger_overlap"),
                }
            )
        to_load = [d.get("id") for d in bundle.get("to_load") or [] if d.get("id")]
        row = {
            "ts": _utc_now(),
            "event": event,
            "prompt_hash": prompt_hash(prompt),
            "prompt_preview": sanitize_text(prompt, max_len=200),
            "relation_tag": bundle.get("relation_tag"),
            "decisions": decisions,
            "to_load": to_load,
            "session_id": session_id,
        }
        _append_row(row)
    except OSError:
        pass


def record_larger(
    *,
    grep_hit: str,
    expand_result: dict[str, Any],
    session_id: str | None = None,
    event: str = "postToolUse",
) -> None:
    if os.environ.get("VERIFIER_USAGE_LEDGER_DISABLED", "").strip() in {"1", "true", "TRUE"}:
        return
    try:
        anchors = expand_result.get("anchors") or []
        neighbors = expand_result.get("neighbors") or []
        top_neighbors = []
        for n in neighbors[:8]:
            top_neighbors.append(
                {
                    "source_file": n.get("source_file") or n.get("label") or n.get("id"),
                    "relation": n.get("relation"),
                    "weight": n.get("weight"),
                }
            )
        row = {
            "ts": _utc_now(),
            "event": event,
            "grep_hit": sanitize_text(grep_hit, max_len=200),
            "anchor_count": len(anchors),
            "neighbor_count": len(neighbors),
            "top_neighbors": top_neighbors,
            "session_id": session_id,
        }
        _append_row(row)
    except OSError:
        pass


def read_rows(path: Path | None = None) -> list[dict[str, Any]]:
    p = path or ledger_path()
    if not p.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def count_gap_occurrences(
    *,
    skill_id: str,
    gap_type: str,
    path: Path | None = None,
) -> int:
    """Count ledger rows where a skill received non-ACCEPT action (proxy for gap)."""
    count = 0
    for row in read_rows(path):
        if row.get("event") != "beforeSubmitPrompt":
            continue
        for d in row.get("decisions") or []:
            if d.get("id") == skill_id and d.get("action") not in {None, "ACCEPT"}:
                if gap_type == "any" or row.get("gap_type") == gap_type:
                    count += 1
                elif gap_type == "tool_failure":
                    count += 1
    return count


def count_relation_tag(tag: str, *, path: Path | None = None) -> int:
    return sum(1 for row in read_rows(path) if row.get("relation_tag") == tag)
