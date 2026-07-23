"""Write cleaned Context→Reasoning→Action→Outcome distillation traces.

One captured trace = one solved task, structured so Phase 1 can author it into
a behavior_rule or SKILL and Phase 2 can grade a student's attempt against the
recorded ``outcome``. Raw traces land in a gitignored per-workspace dir; they
carry content and must be PHI-reviewed before promotion to the committed corpus.

See 30_system/docs/DISTILLATION_TRACE_PROTOCOL.md.
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_OPS_PYTHON = Path(__file__).resolve().parents[1]
if str(_OPS_PYTHON) not in sys.path:
    sys.path.insert(0, str(_OPS_PYTHON))

from common.workspace_scope import resolve_workspace_root  # noqa: E402

from .clean import clean_text, scrub_phi  # noqa: E402

SCHEMA_VERSION = 1


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _enabled() -> bool:
    return os.environ.get("DISTILLATION_CAPTURE_DISABLED", "").strip() not in {"1", "true", "TRUE"}


def resolve_raw_dir(workspace: Path | None = None) -> Path:
    """Gitignored landing dir for content-bearing raw traces."""
    root = workspace or resolve_workspace_root()
    raw = root / ".agent" / "distillation" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    return raw


@dataclass
class Action:
    """One tool call inside the reasoning→action loop."""

    tool: str
    intent: str = ""
    result_summary: str = ""
    success: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool": self.tool,
            "intent": self.intent,
            "result_summary": self.result_summary,
            "success": self.success,
        }


@dataclass
class CaptureRecord:
    """A single Fable-solved task, ready to distill.

    context   — the situation / prompt the task started from.
    reasoning — the reasoning trace (why, not just what).
    actions   — ordered tool calls with intent + result summary.
    outcome   — did it work, and how was that verified (the on-policy target).
    """

    context: str
    reasoning: str = ""
    actions: list[Action] = field(default_factory=list)
    outcome: dict[str, Any] = field(default_factory=dict)
    task_domain: str = "general"
    source_model: str = "claude-fable-5"
    tags: list[str] = field(default_factory=list)
    trace_id: str = ""
    ts: str = ""
    skeleton: bool = False
    enrichment_status: str = ""

    def _clean_and_scrub(self, text: str) -> tuple[str, list[str]]:
        return scrub_phi(clean_text(text))

    def to_record(self) -> dict[str, Any]:
        """Clean + PHI-scrub every text field and assemble the JSON record."""
        phi_hits: list[str] = []

        def process(text: str) -> str:
            cleaned, hits = self._clean_and_scrub(text)
            for h in hits:
                if h not in phi_hits:
                    phi_hits.append(h)
            return cleaned

        context = process(self.context)
        reasoning = process(self.reasoning)
        actions: list[dict[str, Any]] = []
        for act in self.actions:
            actions.append(
                {
                    "tool": act.tool,
                    "intent": process(act.intent),
                    "result_summary": process(act.result_summary),
                    "success": act.success,
                }
            )
        outcome = dict(self.outcome)
        if isinstance(outcome.get("verification"), str):
            outcome["verification"] = process(outcome["verification"])

        if not self.trace_id:
            self.trace_id = _new_trace_id()
        if not self.ts:
            self.ts = _utc_now()

        row: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "trace_id": self.trace_id,
            "ts": self.ts,
            "source_model": self.source_model,
            "task_domain": self.task_domain,
            "tags": list(self.tags),
            "context": context,
            "reasoning": reasoning,
            "actions": actions,
            "outcome": outcome,
            "clean": True,
            "phi_hits": phi_hits,
            # A trace with PHI hits (or unknown status) must not be auto-promoted.
            "phi_reviewed": False,
            "promotable": not phi_hits and not self.skeleton,
        }
        if self.skeleton:
            row["skeleton"] = True
            row["enrichment_status"] = self.enrichment_status or "pending"
        return row


def _new_trace_id() -> str:
    return f"dtr_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"


def capture(record: CaptureRecord, *, workspace: Path | None = None) -> Path:
    """Clean, scrub, and append one trace to the raw landing log. Returns its path.

    No-op path (returns the intended file) when DISTILLATION_CAPTURE_DISABLED=1.
    """
    raw_dir = resolve_raw_dir(workspace)
    log_path = raw_dir / "traces.jsonl"
    if not _enabled():
        return log_path

    data = record.to_record()
    per_trace = raw_dir / f"{data['trace_id']}.json"
    per_trace.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with open(log_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(data, ensure_ascii=False) + "\n")
    return log_path
