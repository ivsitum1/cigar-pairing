"""Prompt cues for conditional memory injection (hook only — not conversational SKILL grill-me).

Canonical triggers load from ``30_system/SKILLS/registry.json`` (skills ``grill-me``,
``research-grill-me``). See ``30_system/docs/GRILL_ME_INJECTION_HEURISTIC.md``.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

# Informal variants / SKILL narrative phrases not duplicated in registry triggers.
# Registry remains the single source for user-facing skill triggers.
SUPPLEMENTAL_INJECTION_CUES: tuple[str, ...] = (
    "interview me",
    "clarify the plan",
    "grillme",
)

# Used only if registry is missing or yields no triggers (fail-safe).
_FALLBACK_INJECTION_CUES: tuple[str, ...] = (
    "grill-me",
    "grill me",
    "grillme",
    "shared understanding",
    "research grill-me",
    "scholarly alignment",
)


def _workspace_root() -> Path:
    return Path(__file__).resolve().parent.parent


@lru_cache(maxsize=1)
def _injection_cues_lowercase() -> tuple[str, ...]:
    """Lowercase substring cues: registry (grill-me, research-grill-me) + supplement + fallback."""
    registry_path = _workspace_root() / "30_system" / "SKILLS" / "registry.json"
    merged: set[str] = set()

    if registry_path.exists():
        try:
            data = json.loads(registry_path.read_text(encoding="utf-8"))
            for skill in data.get("skills", []):
                if skill.get("id") not in ("grill-me", "research-grill-me"):
                    continue
                for raw in skill.get("triggers", []):
                    if isinstance(raw, str) and raw.strip():
                        merged.add(raw.strip().lower())
        except (json.JSONDecodeError, OSError):
            pass

    merged.update(SUPPLEMENTAL_INJECTION_CUES)

    if not merged:
        merged.update(_FALLBACK_INJECTION_CUES)

    return tuple(sorted(merged))


def reload_injection_cues_cache() -> None:
    """Clear cue cache (e.g. after registry edits in long-lived processes)."""
    _injection_cues_lowercase.cache_clear()


def _walk_dict_strings(obj: Any, max_depth: int = 4) -> list[str]:
    """Collect short string values from nested dict/list (for prompt discovery)."""
    out: list[str] = []
    if max_depth < 0:
        return out
    if isinstance(obj, str) and len(obj.strip()) > 2:
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            out.extend(_walk_dict_strings(v, max_depth - 1))
    elif isinstance(obj, list):
        for item in obj[:50]:
            out.extend(_walk_dict_strings(item, max_depth - 1))
    return out


def extract_conversation_id(hook_input: dict[str, Any], payload: dict[str, Any]) -> str | None:
    for obj in (hook_input, payload):
        if not isinstance(obj, dict):
            continue
        for key in ("conversation_id", "conversationId", "chat_id", "chatId", "thread_id", "threadId"):
            val = obj.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
    return None


def extract_user_prompt(hook_input: dict[str, Any], payload: dict[str, Any]) -> str:
    """Best-effort user text from Cursor hook JSON (shape varies by hook / version)."""
    for obj in (payload, hook_input):
        if not isinstance(obj, dict):
            continue
        for key in ("prompt", "text", "userPrompt", "user_prompt", "message", "input", "query", "content"):
            val = obj.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()

    raw = hook_input.get("raw_input") or payload.get("raw_input")
    if isinstance(raw, str) and raw.strip():
        blob = raw.lstrip("\ufeff").strip()
        try:
            parsed = json.loads(blob)
            if isinstance(parsed, dict):
                for key in ("prompt", "text", "message", "input", "query"):
                    val = parsed.get(key)
                    if isinstance(val, str) and val.strip():
                        return val.strip()
                for s in _walk_dict_strings(parsed, max_depth=5):
                    if len(s) > 10 and not s.startswith("{"):
                        return s
        except json.JSONDecodeError:
            if len(blob) > 3:
                return blob
    return ""


def prompt_matches_grill_me(text: str) -> bool:
    if not text or len(text.strip()) < 3:
        return False
    low = text.lower()
    return any(cue in low for cue in _injection_cues_lowercase())


def build_injection_query(user_prompt: str) -> str:
    """Retrieval query: user words + stable anchors (not skill triggers — search helpers)."""
    cleaned = re.sub(r"\s+", " ", user_prompt).strip()
    if len(cleaned) > 280:
        cleaned = cleaned[:277] + "..."
    base = "memory alignment interview requirements PRD research context"
    if cleaned:
        return f"{cleaned} | {base}"
    return base
