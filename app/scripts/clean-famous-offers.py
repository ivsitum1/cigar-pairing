#!/usr/bin/env python3
"""Clean Famous Smoke inventory lines and keep only catalog matches.

Strips pack/box tails, then keeps an offer only if:
  - cleaned line equals an existing catalog line for that brand, or
  - the product URL contains both brand and line slugs.

Writes scripts/output/famous_smoke_cleaned.json (no new catalog lines).
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
CIGARS = HERE.parent / "src" / "data" / "cigars.json"
RAW = HERE / "output" / "famous_smoke_catalog_raw.json"
OUT = HERE / "output" / "famous_smoke_cleaned.json"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s.lower()).strip()


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", norm(s)).strip("-")


def clean_line(line: str, brand: str, vitola: str | None) -> str:
    s = line or ""
    s = re.sub(r"\b(box|pack|tin|bundle)\s+of\s+\d+\b", " ", s, flags=re.I)
    s = re.sub(r"\bof\s+\d+\b", " ", s, flags=re.I)
    s = re.sub(r"\b\d+\s*-?\s*packs?\b", " ", s, flags=re.I)
    s = re.sub(r"\b\d+pk\b", " ", s, flags=re.I)
    s = re.sub(r"\bcigars?\b", " ", s, flags=re.I)
    s = re.sub(
        r"\b(natural|maduro|connecticut|habano|corojo|oscuro)\b", " ", s, flags=re.I
    )
    if brand and s.lower().startswith(brand.lower()):
        s = s[len(brand) :].strip(" -/")
    if vitola:
        s = re.sub(rf"\b{re.escape(vitola)}\b", " ", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip(" -/")
    if s:
        s = " ".join(w[:1].upper() + w[1:] if w else w for w in s.split())
    return s


def main() -> None:
    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    by_brand: dict[str, list[dict]] = {}
    for c in cigars:
        by_brand.setdefault(norm(c["brand"]), []).append(c)

    raw = json.loads(RAW.read_text(encoding="utf-8"))
    kept: list[dict] = []
    stats = {"exact": 0, "url_slug": 0, "skip": 0}
    for o in raw.get("offers") or []:
        brand = o.get("brand") or ""
        line = clean_line(o.get("line") or "", brand, o.get("vitola"))
        url = (o.get("url") or "").lower()
        cands = by_brand.get(norm(brand), [])
        match = None
        how = None
        nl = norm(line)
        for c in cands:
            if nl and norm(c["line"]) == nl:
                match, how = c, "exact"
                break
        if not match:
            for c in cands:
                ls = slug(c["line"])
                bs = slug(c["brand"])
                if ls and len(ls) >= 4 and ls in url and (bs in url or slug(brand) in url):
                    match, how = c, "url_slug"
                    break
        if not match:
            stats["skip"] += 1
            continue
        stats[how] += 1
        out = dict(o)
        out["line"] = match["line"]
        kept.append(out)

    OUT.write_text(
        json.dumps({"shop": "famous_smoke_us", "offers": kept}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(stats, "kept", len(kept), "->", OUT)


if __name__ == "__main__":
    main()
