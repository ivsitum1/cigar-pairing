"""Enrich a hook-written skeleton trace with context and reasoning."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .emit import Action, CaptureRecord, capture
from .promote import load_trace, resolve_trace_path


def enrich_skeleton(
    trace_id: str,
    *,
    context: str,
    reasoning: str,
    workspace: Path | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Capture enriched trace and mark skeleton superseded. Returns new trace record."""
    skeleton = load_trace(trace_id, workspace)
    if not skeleton.get("skeleton"):
        raise ValueError(f"{trace_id} is not a skeleton trace")
    if skeleton.get("enrichment_status") not in {None, "pending", ""}:
        raise ValueError(f"{trace_id} enrichment_status={skeleton.get('enrichment_status')}")

    actions = [
        Action(
            tool=str(a.get("tool", "unknown")),
            intent=str(a.get("intent", "")),
            result_summary=str(a.get("result_summary", "")),
            success=bool(a.get("success", True)),
        )
        for a in (skeleton.get("actions") or [])
        if isinstance(a, dict)
    ]
    merged_tags = list(skeleton.get("tags") or [])
    for t in tags or []:
        if t not in merged_tags:
            merged_tags.append(t)
    for drop in ("skeleton", "auto_hook"):
        while drop in merged_tags:
            merged_tags.remove(drop)
    merged_tags.append("enriched")

    record = CaptureRecord(
        context=context.strip(),
        reasoning=reasoning.strip(),
        actions=actions,
        outcome=skeleton.get("outcome") if isinstance(skeleton.get("outcome"), dict) else {},
        task_domain=str(skeleton.get("task_domain") or "general"),
        source_model=str(skeleton.get("source_model") or "enriched-skeleton"),
        tags=merged_tags,
        skeleton=False,
        enrichment_status="enriched",
    )
    capture(record, workspace=workspace)
    enriched = record.to_record()

    # Mark skeleton superseded
    sk_path = resolve_trace_path(trace_id, workspace)
    skeleton["enrichment_status"] = "superseded"
    skeleton["enriched_trace_id"] = enriched["trace_id"]
    sk_path.write_text(json.dumps(skeleton, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return enriched
