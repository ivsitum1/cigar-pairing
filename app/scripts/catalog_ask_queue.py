# -*- coding: utf-8 -*-
"""Shared ask-queue for shop ingest (drinks + cigars).

When a scraper/matcher cannot safely auto-add or auto-match an item, it
appends a structured question here for the human to answer.

  scripts/output/catalog_ask_queue.json
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASK_PATH = HERE / "output" / "catalog_ask_queue.json"


def load_ask_queue() -> dict:
    if not ASK_PATH.exists():
        return {"updatedAt": None, "items": []}
    return json.loads(ASK_PATH.read_text(encoding="utf-8"))


def save_ask_queue(items: list[dict], *, merge: bool = True) -> Path:
    """Write ask items. If merge, keep unanswered items with distinct keys."""
    ASK_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing = load_ask_queue().get("items") or [] if merge else []
    by_key: dict[str, dict] = {}
    for it in existing:
        if it.get("answered"):
            continue
        key = it.get("key") or _fallback_key(it)
        by_key[key] = it
    for it in items:
        key = it.get("key") or _fallback_key(it)
        it = dict(it)
        it["key"] = key
        it.setdefault("askedAt", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        by_key[key] = it
    payload = {
        "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "items": sorted(by_key.values(), key=lambda x: (x.get("kind") or "", x.get("key") or "")),
    }
    ASK_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ASK_PATH


def _fallback_key(it: dict) -> str:
    return "|".join(
        str(it.get(k) or "")
        for k in ("kind", "shop", "url", "name", "brand")
    )


def ask_item(
    *,
    kind: str,
    question: str,
    name: str,
    shop: str | None = None,
    url: str | None = None,
    candidates: list[dict] | None = None,
    extra: dict | None = None,
) -> dict:
    row = {
        "kind": kind,
        "question": question,
        "name": name,
        "shop": shop,
        "url": url,
        "candidates": candidates or [],
        "answered": False,
    }
    if extra:
        row.update(extra)
    row["key"] = _fallback_key(row)
    return row
