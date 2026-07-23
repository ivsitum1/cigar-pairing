"""Promote PHI-reviewed distillation traces to committed corpus cards.

Phase 1 of the Fable → md-file-system plan. See DISTILLATION_TRACE_PROTOCOL.md.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common.workspace_scope import resolve_workspace_root

from .emit import resolve_raw_dir


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(*parts: str, max_len: int = 48) -> str:
    raw = "-".join(p for p in parts if p).lower()
    raw = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return raw[:max_len].rstrip("-") or "trace"


def resolve_trace_path(trace_id: str, workspace: Path | None = None) -> Path:
    raw_dir = resolve_raw_dir(workspace)
    path = raw_dir / f"{trace_id}.json"
    if not path.is_file():
        raise FileNotFoundError(f"Trace not found: {path}")
    return path


def load_trace(trace_id: str, workspace: Path | None = None) -> dict[str, Any]:
    data = json.loads(resolve_trace_path(trace_id, workspace).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Trace {trace_id} is not a JSON object")
    return data


def list_raw_traces(workspace: Path | None = None) -> list[dict[str, Any]]:
    raw_dir = resolve_raw_dir(workspace)
    traces: list[dict[str, Any]] = []
    for path in sorted(raw_dir.glob("dtr_*.json")):
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(row, dict):
                traces.append(row)
        except (json.JSONDecodeError, OSError):
            continue
    return traces


def validate_promotable(trace: dict[str, Any], *, phi_reviewed_confirm: bool) -> tuple[bool, str]:
    if trace.get("skeleton") and trace.get("enrichment_status") == "pending":
        return False, "skeleton pending enrichment — run distillation_enrich.py first"
    if trace.get("phi_hits"):
        return False, f"phi_hits present: {trace.get('phi_hits')}"
    if not phi_reviewed_confirm:
        return False, "human PHI gate required: pass --phi-reviewed"
    if not str(trace.get("reasoning", "")).strip():
        return False, "reasoning is empty"
    if not str(trace.get("context", "")).strip():
        return False, "context is empty"
    if trace.get("promoted_to"):
        return False, f"already promoted to {trace.get('promoted_to')}"
    return True, "ok"


def card_filename(trace: dict[str, Any]) -> str:
    domain = str(trace.get("task_domain") or "general")
    tags = trace.get("tags") or []
    tag_slug = slugify(*(str(t) for t in tags if t not in {"skeleton", "auto_hook"}))
    if not tag_slug:
        tag_slug = slugify(str(trace.get("trace_id", ""))[-8:])
    return f"card_{slugify(domain)}_{tag_slug}.md"


def _title_from_trace(trace: dict[str, Any]) -> str:
    context = str(trace.get("context", "")).strip()
    first_line = context.split("\n", 1)[0].strip()
    if len(first_line) > 12:
        return first_line[:120]
    domain = str(trace.get("task_domain") or "general")
    tags = ", ".join(str(t) for t in (trace.get("tags") or [])[:3])
    return f"{domain}: {tags}" if tags else f"{domain} distillation card"


def _actions_table(actions: list[Any]) -> str:
    if not actions:
        return "_No tool actions recorded._\n"
    lines = ["| tool | intent | result |", "|------|--------|--------|"]
    for act in actions:
        if not isinstance(act, dict):
            continue
        tool = str(act.get("tool", "unknown")).replace("|", "\\|")
        intent = str(act.get("intent", "")).replace("|", "\\|") or "—"
        summary = str(act.get("result_summary", "")).replace("|", "\\|") or (
            "ok" if act.get("success", True) else "failed"
        )
        lines.append(f"| {tool} | {intent} | {summary} |")
    return "\n".join(lines) + "\n"


def _outcome_block(outcome: Any) -> str:
    if not isinstance(outcome, dict):
        return "- **success:** unknown\n"
    lines: list[str] = []
    if "success" in outcome:
        lines.append(f"- **success:** {'yes' if outcome['success'] else 'no'}")
    if outcome.get("verification"):
        lines.append(f"- **verification:** {outcome['verification']}")
    for key, value in outcome.items():
        if key in {"success", "verification"}:
            continue
        lines.append(f"- **{key}:** {value}")
    return "\n".join(lines) + "\n"


def suggest_distills_to(trace: dict[str, Any]) -> str:
    reasoning = str(trace.get("reasoning", "")).strip()
    domain = str(trace.get("task_domain") or "general")
    if not reasoning:
        return f"A `behavior_rules` or `SKILL_` entry for **{domain}** — enrich reasoning first."
    first_sentence = reasoning.split(".", 1)[0].strip()
    return (
        f"A `behavior_rules` entry or skill for **{domain}**: "
        f"when this situation recurs → {first_sentence}. "
        "Maps Context → Reasoning → Action for Phase 2 on-policy grading."
    )


def trace_to_card_markdown(trace: dict[str, Any], *, corpus_path: Path) -> str:
    tags = trace.get("tags") or []
    tag_yaml = ", ".join(str(t) for t in tags) if tags else ""
    title = _title_from_trace(trace)
    rel_corpus = corpus_path.name
    body = f"""---
trace_id: {trace.get("trace_id", "")}
source_model: {trace.get("source_model", "")}
task_domain: {trace.get("task_domain", "general")}
tags: [{tag_yaml}]
phi_reviewed: true
promotable: true
promoted_at: {_utc_now()}
corpus_file: {rel_corpus}
---

# {title}

Promoted distillation card (PHI-reviewed). Phase 1 input for `behavior_rules/` or `SKILLS/`.

## Context

{str(trace.get("context", "")).strip()}

## Reasoning

{str(trace.get("reasoning", "")).strip()}

## Action

{_actions_table(trace.get("actions") or [])}

## Outcome

{_outcome_block(trace.get("outcome"))}

## Distills to

{suggest_distills_to(trace)}
"""
    return body


def mark_trace_promoted(
    trace_id: str,
    corpus_rel: str,
    *,
    workspace: Path | None = None,
) -> None:
    path = resolve_trace_path(trace_id, workspace)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["phi_reviewed"] = True
    data["promotable"] = True
    data["promoted_to"] = corpus_rel.replace("\\", "/")
    data["promoted_at"] = _utc_now()
    if data.get("enrichment_status") == "pending":
        data["enrichment_status"] = "promoted"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def promote_trace(
    trace_id: str,
    *,
    workspace: Path | None = None,
    phi_reviewed_confirm: bool = False,
    corpus_dir: Path | None = None,
    dry_run: bool = False,
) -> Path:
    """Write corpus card and mark raw trace promoted. Returns corpus file path."""
    ws = workspace or resolve_workspace_root()
    trace = load_trace(trace_id, ws)
    ok, reason = validate_promotable(trace, phi_reviewed_confirm=phi_reviewed_confirm)
    if not ok:
        raise ValueError(reason)

    out_dir = corpus_dir or (ws / "20_knowledge" / "distillation" / "corpus")
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = card_filename(trace)
    out_path = out_dir / filename
    if out_path.exists() and not dry_run:
        stem = out_path.stem
        suffix = slugify(trace_id[-12:])
        out_path = out_dir / f"{stem}_{suffix}.md"

    rel = str(out_path.relative_to(ws)).replace("\\", "/")
    markdown = trace_to_card_markdown(trace, corpus_path=out_path)

    if dry_run:
        return out_path

    out_path.write_text(markdown, encoding="utf-8")
    mark_trace_promoted(trace_id, rel, workspace=ws)
    return out_path
