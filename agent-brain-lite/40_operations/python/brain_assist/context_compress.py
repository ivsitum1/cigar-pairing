"""Opt-in context compression before prompt submit (Headroom-inspired MVP)."""
from __future__ import annotations

import re
from typing import Any


def _dedupe_lines(text: str) -> str:
    seen: set[str] = set()
    out: list[str] = []
    for line in text.splitlines():
        key = line.strip()
        if not key:
            out.append(line)
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append(line)
    return "\n".join(out)


def _collapse_blank_runs(text: str) -> str:
    return re.sub(r"\n{4,}", "\n\n\n", text)


def _truncate_repeated_blocks(text: str, min_repeat: int = 3, max_block: int = 400) -> str:
    lines = text.splitlines()
    if len(lines) < min_repeat * 2:
        return text
    i = 0
    out: list[str] = []
    while i < len(lines):
        block = lines[i : i + 3]
        if not block:
            i += 1
            continue
        repeat = 1
        j = i + 3
        while j + 3 <= len(lines) and lines[j : j + 3] == block:
            repeat += 1
            j += 3
        if repeat >= min_repeat:
            snippet = "\n".join(block)
            if len(snippet) > max_block:
                snippet = snippet[:max_block] + "..."
            out.append(snippet)
            out.append(f"[... repeated {repeat - 1} similar blocks omitted ...]")
            i = j
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out)


def compress_context(text: str, *, max_chars: int = 12000) -> dict[str, Any]:
    """Compress injected context; returns text and stats."""
    original_len = len(text)
    if original_len <= max_chars:
        return {
            "text": text,
            "original_chars": original_len,
            "compressed_chars": original_len,
            "ratio": 1.0,
            "applied": False,
        }
    staged = _collapse_blank_runs(_dedupe_lines(_truncate_repeated_blocks(text)))
    if len(staged) > max_chars:
        staged = staged[: max_chars - 80] + "\n\n[... context truncated by context_compress ...]"
    compressed_len = len(staged)
    return {
        "text": staged,
        "original_chars": original_len,
        "compressed_chars": compressed_len,
        "ratio": round(compressed_len / original_len, 4) if original_len else 1.0,
        "applied": True,
    }
