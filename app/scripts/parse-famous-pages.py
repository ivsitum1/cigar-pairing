#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse Famous Smoke product HTML/markdown into flavor facts.

Reads scripts/output/famous_product_pages.json:
  [{ "id", "url", "html"|"markdown", ... }]

Writes/updates famous fields in cw_famous_flavor_raw.json.

  python scripts/parse-famous-pages.py
"""
from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGES = HERE / "output" / "famous_product_pages.json"
RAW = HERE / "output" / "cw_famous_flavor_raw.json"


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", unescape(s)).strip()


def parse_html(html: str) -> dict:
    facts: dict[str, str] = {}
    for k, v in re.findall(r'data-th="([^"]+)"[^>]*>([^<]+)', html, re.I):
        key = strip_tags(k.replace("&#x20;", " ")).lower()
        val = strip_tags(v)
        if key and val and len(val) < 120:
            facts[key] = val
    for k, v in re.findall(r"<th[^>]*>([^<]+)</th>\s*<td[^>]*>(.*?)</td>", html, re.S | re.I):
        key = strip_tags(k).lower()
        val = strip_tags(v)
        if key and val and len(val) < 120:
            facts.setdefault(key, val)

    desc = ""
    m = re.search(
        r'(?:itemprop="description"|Description</h\d>)\s*(.*?)(?:</div>|Specifications|<h\d)',
        html,
        re.S | re.I,
    )
    if m:
        desc = strip_tags(m.group(1))[:2000]
    if not desc:
        m = re.search(r"###?\s*Description\s*(.+?)(?:###|Specifications|\| Brand)", html, re.S | re.I)
        if m:
            desc = re.sub(r"\s+", " ", m.group(1)).strip()[:2000]

    title = ""
    tm = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)
    if tm:
        title = strip_tags(tm.group(1))
    if not title:
        tm = re.search(r"^#\s+(.+)$", html, re.M)
        if tm:
            title = tm.group(1).strip()

    # normalize wrapper key
    if facts.get("wrapper leaf") and not facts.get("wrapper"):
        facts["wrapper"] = facts["wrapper leaf"]

    return {
        "title": title,
        "facts": facts,
        "description": desc,
        "ok": bool(facts or (desc and len(desc) > 60)),
    }


def parse_markdown(md: str) -> dict:
    # reuse html parser on markdown-ish tables
    return parse_html(md)


def main() -> None:
    if not PAGES.exists():
        print(f"missing {PAGES}")
        return
    pages = json.loads(PAGES.read_text(encoding="utf-8"))
    prior = {r["id"]: r for r in json.loads(RAW.read_text(encoding="utf-8"))} if RAW.exists() else {}

    ok_n = 0
    for p in pages:
        body = p.get("html") or p.get("markdown") or p.get("text") or ""
        if not body:
            continue
        parsed = parse_html(body) if "<" in body[:200] else parse_markdown(body)
        parsed["product_url"] = p.get("url")
        parsed["search_url"] = p.get("search_url")
        entry = prior.get(p["id"]) or {
            "id": p["id"],
            "brand": p.get("brand"),
            "line": p.get("line"),
            "cigarworld": {"ok": False},
            "famous": {"ok": False},
        }
        entry["famous"] = parsed
        prior[p["id"]] = entry
        if parsed["ok"]:
            ok_n += 1
            print(f"ok {p['id']} wrap={parsed['facts'].get('wrapper')} strength={parsed['facts'].get('strength')}")

    RAW.write_text(json.dumps(list(prior.values()), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"parsed={len(pages)} famous_ok={ok_n} -> {RAW}")


if __name__ == "__main__":
    main()
