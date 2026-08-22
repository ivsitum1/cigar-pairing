# -*- coding: utf-8 -*-
"""Filter and rank cigar YouTube match proposals for human review."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from youtube_common import OUTPUT_ROOT


def note_lengths(cigar: dict) -> tuple[int, int]:
    notes = cigar.get("notes") or {}
    return len((notes.get("en") or "").strip()), len((notes.get("hr") or "").strip())


def is_stub_note(en_len: int, hr_len: int, *, stub_en_max: int) -> bool:
    if en_len == 0 and hr_len == 0:
        return True
    return en_len <= stub_en_max


def collect_proposals(
    *,
    min_confidence: float,
    min_key_len: int,
    require_in_title: bool,
    output_root: Path = OUTPUT_ROOT,
) -> dict[str, dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for path in sorted(output_root.glob("*/cigar_match_proposals.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        channel_id = payload.get("channelId") or path.parent.name
        for prop in payload.get("proposals") or []:
            conf = float(prop.get("confidence") or 0)
            if conf < min_confidence:
                continue
            key = (prop.get("matchedKey") or "").strip()
            if len(key) < min_key_len:
                continue
            in_title = prop.get("inTitle")
            if in_title is None:
                title_l = (prop.get("title") or "").lower()
                in_title = key.lower() in title_l
            if require_in_title and not in_title:
                continue
            cid = prop.get("cigarId")
            if not cid:
                continue
            row = {**prop, "channelId": channel_id}
            prev = best.get(cid)
            if prev is None or conf > float(prev.get("confidence") or 0):
                best[cid] = row
            elif conf == float(prev.get("confidence") or 0) and row.get("inTitle") and not prev.get("inTitle"):
                best[cid] = row
    return best


def build_queue(
    proposals: dict[str, dict[str, Any]],
    cigars_by_id: dict[str, dict],
    *,
    stub_en_max: int,
    prefer_stubs: bool,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for cid, prop in proposals.items():
        cigar = cigars_by_id.get(cid)
        if not cigar:
            continue
        en_len, hr_len = note_lengths(cigar)
        stub = is_stub_note(en_len, hr_len, stub_en_max=stub_en_max)
        if prefer_stubs and not stub:
            continue
        rows.append(
            {
                "cigarId": cid,
                "brand": cigar.get("brand"),
                "line": cigar.get("line"),
                "matchedName": prop.get("matchedName"),
                "matchedKey": prop.get("matchedKey"),
                "confidence": prop.get("confidence"),
                "inTitle": prop.get("inTitle"),
                "channelId": prop.get("channelId"),
                "videoId": prop.get("videoId"),
                "url": prop.get("url"),
                "videoTitle": prop.get("title"),
                "snippet": (prop.get("snippet") or "")[:240],
                "notesEnLen": en_len,
                "notesHrLen": hr_len,
                "isStubNote": stub,
                "suggestedFields": prop.get("suggestedFields") or ["notes"],
            }
        )
    rows.sort(
        key=lambda r: (
            0 if r["isStubNote"] else 1,
            r["notesEnLen"],
            -float(r["confidence"] or 0),
            r["cigarId"],
        )
    )
    return rows
