"""Failure-mode attribution tags for memory ingest (Beyond Intelligence / MemFail)."""
from __future__ import annotations

from typing import Literal

FailureMode = Literal["summary", "storage", "retrieval", "unknown"]

VALID: frozenset[str] = frozenset({"summary", "storage", "retrieval", "unknown"})


def normalize_failure_mode(value: str | None) -> FailureMode:
    v = (value or "unknown").strip().lower()
    return v if v in VALID else "unknown"  # type: ignore[return-value]


def tag_event(event: dict, *, failure_mode: str | None = None) -> dict:
    """Attach failure_mode to a memory ingest event dict."""
    out = dict(event)
    meta = dict(out.get("metadata") or {})
    meta["failure_mode"] = normalize_failure_mode(failure_mode or meta.get("failure_mode"))
    out["metadata"] = meta
    return out
