"""Dataclasses used by memory engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MemoryEvent:
    lifecycle: str
    session_id: str
    project_scope: str
    payload: dict[str, Any]
    ts: str = field(default_factory=utc_now_iso)


#: Brain-inspired memory domains (see ADR memory_canonical + Synthius-Mem 2026).
#: - explicit:    stated facts, decisions, outcomes (default)
#: - implicit:    inferred patterns, preferences, recurring corrections
#: - associative: links/relations between entities or sessions
MEM_TYPES = ("explicit", "implicit", "associative")


@dataclass
class Observation:
    session_id: str
    project_scope: str
    event_hash: str
    lifecycle: str
    summary: str
    detail: str
    source_ref: str
    confidence: float = 0.8
    tags: list[str] = field(default_factory=list)
    mem_type: str = "explicit"
    ts: str = field(default_factory=utc_now_iso)

