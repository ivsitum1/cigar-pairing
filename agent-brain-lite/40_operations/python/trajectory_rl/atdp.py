"""ATDP-lite tuple events for trajectory logging. See TRAJECTORY_EMIT_PROTOCOL.md."""
from __future__ import annotations

import hashlib
import re
from typing import Any

PHI_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("phone", re.compile(r"\b\+?\d[\d\s().-]{7,}\d\b")),
    ("long_id", re.compile(r"\b\d{7,}\b")),
    ("date_dotted", re.compile(r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b")),
]

FORBIDDEN_IN_METADATA = {"patient_name", "mrn", "oib", "free_text_note", "user_prompt"}


def scrub_phi(text: str) -> tuple[str, list[str]]:
    """Redact common PHI patterns; return cleaned text and hit categories."""
    hits: list[str] = []
    out = text
    for label, pattern in PHI_PATTERNS:
        if pattern.search(out):
            hits.append(label)
            out = pattern.sub(f"[REDACTED_{label.upper()}]", out)
    return out, hits


def truncate_observation(raw: Any, *, max_len: int = 200) -> str:
    text = scrub_phi(str(raw or ""))[0]
    if len(text) <= max_len:
        return text
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"{text[:max_len]}…[hash:{digest}]"


def build_atdp_record(
    *,
    observation: str,
    hidden_status: str,
    action: str,
    outcome: str,
    reward: float | int | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build ATDP tuple (o, h, a, y, r, m) with PHI scrub on text fields."""
    o, o_hits = scrub_phi(observation)
    h, h_hits = scrub_phi(hidden_status)
    a, _ = scrub_phi(action)
    y, y_hits = scrub_phi(outcome)
    phi_hits = sorted(set(o_hits + h_hits + y_hits))

    meta: dict[str, Any] = {}
    if metadata:
        for key, value in metadata.items():
            if key in FORBIDDEN_IN_METADATA:
                continue
            if isinstance(value, str):
                meta[key] = scrub_phi(value)[0]
            elif isinstance(value, (int, float, bool)) or value is None:
                meta[key] = value
            else:
                meta[key] = scrub_phi(str(value)[:300])[0]

    record: dict[str, Any] = {
        "o": o[:2000],
        "h": h[:1000],
        "a": a[:500],
        "y": y[:1000],
        "m": meta,
    }
    if reward is not None:
        record["r"] = reward
    if phi_hits:
        record["phi_hits"] = phi_hits
    return record
