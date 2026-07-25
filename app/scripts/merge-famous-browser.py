#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge browser-scraped Famous brand pages into cw_famous_flavor_raw.json.

Expects scripts/output/famous_browser_scrape.json:
  [{ id, url, ok, title, facts, description, blocked?, error? }]
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "output" / "famous_browser_scrape.json"
RAW = HERE / "output" / "cw_famous_flavor_raw.json"


def main() -> None:
    pages = json.loads(SRC.read_text(encoding="utf-8"))
    prior = {r["id"]: r for r in json.loads(RAW.read_text(encoding="utf-8"))} if RAW.exists() else {}
    ok_n = 0
    for p in pages:
        entry = prior.get(p["id"]) or {
            "id": p["id"],
            "brand": p.get("brand"),
            "line": p.get("line"),
            "cigarworld": {"ok": False},
            "famous": {"ok": False},
        }
        facts = dict(p.get("facts") or {})
        if facts.get("wrapper leaf") and not facts.get("wrapper"):
            facts["wrapper"] = facts["wrapper leaf"]
        fam = {
            "ok": bool(p.get("ok")),
            "title": p.get("title") or "",
            "facts": facts,
            "description": (p.get("description") or "")[:2000],
            "product_url": p.get("url"),
            "search_url": p.get("url"),
            "blocked": bool(p.get("blocked")),
        }
        if p.get("error"):
            fam["error"] = p["error"]
        entry["famous"] = fam
        if p.get("brand"):
            entry["brand"] = p["brand"]
        if p.get("line"):
            entry["line"] = p["line"]
        prior[p["id"]] = entry
        if fam["ok"]:
            ok_n += 1
            print(f"ok {p['id']} wrap={facts.get('wrapper')} str={facts.get('strength')}")
    RAW.write_text(json.dumps(list(prior.values()), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"merged={len(pages)} famous_ok={ok_n} -> {RAW}")


if __name__ == "__main__":
    main()
