# -*- coding: utf-8 -*-
"""Match YouTube rum videos to catalog drink ids (proposals only)."""
from __future__ import annotations

import re
from typing import Any

_TOKEN = re.compile(r"[a-z0-9]+", re.I)
_STOP = frozenset(
    {
        "the",
        "and",
        "for",
        "with",
        "from",
        "rum",
        "rhum",
        "ron",
        "aged",
        "year",
        "years",
        "yr",
        "yrs",
        "old",
        "vs",
        "review",
        "reviews",
        "tasting",
        "guide",
        "best",
        "worst",
        "under",
        "over",
        "video",
        "episode",
        "part",
        "how",
        "why",
        "what",
        "this",
        "that",
        "you",
        "your",
        "vsop",
        "xo",
        "anejo",
        "blanco",
        "dark",
        "gold",
        "white",
        "spiced",
        "bottle",
        "bottles",
    }
)


def normalize_tokens(text: str) -> list[str]:
    toks = [t.lower() for t in _TOKEN.findall(text or "")]
    return [t for t in toks if len(t) > 2 and t not in _STOP]


def drink_match_keys(drink: dict[str, Any]) -> list[str]:
    """Return searchable phrases for a rum catalog row (longest first)."""
    name = (drink.get("name") or "").strip()
    keys: list[str] = []
    if name:
        keys.append(name.lower())
    # Drop parenthetical / ECS style suffixes for softer match
    short = re.sub(r"\s*\([^)]*\)\s*", " ", name).strip().lower()
    if short and short not in keys:
        keys.append(short)
    # First 2–3 significant tokens as a phrase
    toks = normalize_tokens(name)
    if len(toks) >= 2:
        keys.append(" ".join(toks[:2]))
    if len(toks) >= 3:
        keys.append(" ".join(toks[:3]))
    # Prefer longer keys first
    keys.sort(key=len, reverse=True)
    # Dedupe preserving order
    seen: set[str] = set()
    out: list[str] = []
    for k in keys:
        k = re.sub(r"\s+", " ", k).strip()
        if k and k not in seen and len(k) >= 4:
            seen.add(k)
            out.append(k)
    return out


def confidence_for_key(key: str, *, in_title: bool) -> float:
    words = len(key.split())
    base = 0.55 + 0.1 * min(words, 3)
    if in_title:
        base += 0.2
    if len(key) >= 12:
        base += 0.05
    return round(min(base, 0.98), 2)


def snippet_around(text: str, key: str, radius: int = 80) -> str:
    low = (text or "").lower()
    idx = low.find(key.lower())
    if idx < 0:
        return (text or "")[:160]
    start = max(0, idx - radius)
    end = min(len(text), idx + len(key) + radius)
    return text[start:end].strip()


def match_video_to_rums(
    *,
    video: dict[str, Any],
    rums: list[dict[str, Any]],
    min_confidence: float = 0.65,
) -> list[dict[str, Any]]:
    title = video.get("title") or ""
    text = video.get("text") or ""
    blob = f"{title}\n{text}"
    blob_l = blob.lower()
    title_l = title.lower()

    proposals: list[dict[str, Any]] = []
    for drink in rums:
        drink_id = drink.get("id")
        if not drink_id:
            continue
        for key in drink_match_keys(drink):
            if key not in blob_l:
                continue
            in_title = key in title_l
            conf = confidence_for_key(key, in_title=in_title)
            if conf < min_confidence:
                continue
            proposals.append(
                {
                    "drinkId": drink_id,
                    "matchedName": drink.get("name"),
                    "matchedKey": key,
                    "videoId": video.get("videoId"),
                    "url": video.get("url"),
                    "title": title,
                    "confidence": conf,
                    "snippet": snippet_around(blob, key),
                    "suggestedFields": ["notes", "cigarHint"],
                }
            )
            break  # one proposal per drink per video
    proposals.sort(key=lambda p: (-p["confidence"], p["drinkId"]))
    return proposals
