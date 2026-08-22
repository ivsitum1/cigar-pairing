# -*- coding: utf-8 -*-
"""Match YouTube cigar videos to catalog cigar ids (proposals only)."""
from __future__ import annotations

import re
import unicodedata
from typing import Any

from youtube_match_lib import confidence_for_key, normalize_tokens, snippet_around

_TOKEN = re.compile(r"[a-z0-9]+", re.I)
_STOP = frozenset(
    {
        "the",
        "and",
        "for",
        "with",
        "from",
        "cigar",
        "cigars",
        "cigara",
        "cigare",
        "smoke",
        "smoking",
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
        "new",
        "first",
        "look",
        "live",
        "stream",
        "shorts",
        "habano",
        "puro",
        "vitola",
        "format",
        "size",
        "inch",
        "ring",
        "gauge",
        "box",
        "pack",
        "stick",
        "sticks",
    }
)


def _fold(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch)).lower()


def cigar_match_keys(cigar: dict[str, Any]) -> list[str]:
    """Return searchable phrases for a cigar catalog row (longest first)."""
    brand = (cigar.get("brand") or "").strip()
    line = (cigar.get("line") or "").strip()
    vitola = (cigar.get("vitola") or "").strip()
    keys: list[str] = []

    if brand and line:
        keys.append(_fold(f"{brand} {line}"))
    if line:
        folded_line = _fold(line)
        if len(folded_line) >= 5:
            keys.append(folded_line)
    if brand and vitola and line:
        keys.append(_fold(f"{brand} {line} {vitola}"))
    if brand:
        toks = normalize_tokens(brand)
        if len(toks) >= 2:
            keys.append(" ".join(toks[:2]))
        elif len(toks) == 1 and len(toks[0]) >= 6:
            keys.append(toks[0])

    # First 2–3 significant tokens from brand+line
    combined = normalize_tokens(f"{brand} {line}")
    if len(combined) >= 2:
        keys.append(" ".join(combined[:2]))
    if len(combined) >= 3:
        keys.append(" ".join(combined[:3]))

    keys.sort(key=len, reverse=True)
    seen: set[str] = set()
    out: list[str] = []
    for k in keys:
        k = re.sub(r"\s+", " ", k).strip()
        if k and k not in seen and len(k) >= 5:
            seen.add(k)
            out.append(k)
    return out


def match_video_to_cigars(
    *,
    video: dict[str, Any],
    cigars: list[dict[str, Any]],
    min_confidence: float = 0.65,
) -> list[dict[str, Any]]:
    title = video.get("title") or ""
    text = video.get("text") or ""
    blob = f"{title}\n{text}"
    blob_l = _fold(blob)
    title_l = _fold(title)

    proposals: list[dict[str, Any]] = []
    for cigar in cigars:
        cigar_id = cigar.get("id")
        if not cigar_id:
            continue
        for key in cigar_match_keys(cigar):
            if key not in blob_l:
                continue
            in_title = key in title_l
            conf = confidence_for_key(key, in_title=in_title)
            if conf < min_confidence:
                continue
            matched_name = f"{cigar.get('brand', '')} {cigar.get('line', '')}".strip()
            proposals.append(
                {
                    "cigarId": cigar_id,
                    "matchedName": matched_name,
                    "matchedKey": key,
                    "inTitle": in_title,
                    "videoId": video.get("videoId"),
                    "url": video.get("url"),
                    "title": title,
                    "confidence": conf,
                    "snippet": snippet_around(blob, key),
                    "suggestedFields": ["notes"],
                }
            )
            break
    proposals.sort(key=lambda p: (-p["confidence"], p["cigarId"]))
    return proposals
