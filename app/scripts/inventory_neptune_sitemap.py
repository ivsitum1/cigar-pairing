#!/usr/bin/env python3
"""Fast Neptune inventory from sitemap.xml matched to catalog brands."""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

from shop_common import slug

HERE = Path(__file__).resolve().parent
CIGARS = HERE.parent / "src" / "data" / "cigars.json"
OUT = HERE / "output" / "neptune_catalog_raw.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

VITOLAS = (
    "robusto", "toro", "churchill", "corona", "gordo", "belicoso", "torpedo",
    "lancero", "perfecto", "lonsdale", "panetela", "presidente", "figurado",
    "petit corona", "double corona", "half corona", "gigante",
)


def guess_vitola(text: str) -> str | None:
    low = f" {text.lower()} "
    for v in sorted(VITOLAS, key=len, reverse=True):
        if f" {v} " in low:
            return " ".join(w.capitalize() for w in v.split())
    return None


def line_from(brand: str, path: str, vitola: str | None) -> str:
    title = path.replace("-", " ")
    name = re.sub(re.escape(brand), " ", title, flags=re.I)
    name = re.sub(r"\bcigars?\b", " ", name, flags=re.I)
    if vitola:
        name = re.sub(rf"\b{re.escape(vitola)}\b", " ", name, flags=re.I)
    name = re.sub(r"\b(sampler|collection|fresh pack|tubo|tubos)\b", " ", name, flags=re.I)
    name = re.sub(r"\s+", " ", name).strip(" -/")
    return name or (vitola or "Classic")


def main() -> None:
    print("fetch sitemap...", flush=True)
    req = urllib.request.Request(
        "https://www.neptunecigar.com/sitemap.xml",
        headers={"User-Agent": UA},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        xml = r.read().decode("utf-8", "replace")
    locs = re.findall(r"<loc>(https://www\.neptunecigar\.com/cigars/[^<]+)</loc>", xml)
    print(f"sitemap products: {len(locs)}", flush=True)

    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    brands = sorted({c["brand"] for c in cigars}, key=lambda b: (-len(slug(b)), b.casefold()))
    brand_slugs = [(slug(b), b) for b in brands]

    # known brand+line for better line naming
    lines_by_brand: dict[str, list[str]] = {}
    for c in cigars:
        lines_by_brand.setdefault(c["brand"], []).append(c["line"])

    offers = []
    seen = set()
    unmatched = 0
    for url in locs:
        if url in seen or "sampler" in url.lower():
            continue
        path = url.rstrip("/").split("/")[-1]
        matched = None
        for bs, bname in brand_slugs:
            if not bs:
                continue
            if path == bs or path.startswith(bs + "-"):
                matched = bname
                break
        if not matched:
            unmatched += 1
            continue
        seen.add(url)
        title = path.replace("-", " ")
        vitola = guess_vitola(title)
        # prefer catalog line if slug contains it
        line = None
        for ln in sorted(lines_by_brand.get(matched, []), key=lambda x: -len(slug(x))):
            ls = slug(ln)
            if ls and ls in path:
                line = ln
                break
        if not line:
            line = line_from(matched, path, vitola)
        offers.append(
            {
                "sourceShopId": "neptune_us",
                "brand": matched,
                "line": line,
                "vitola": vitola,
                "ring": None,
                "lengthMM": None,
                "amount": None,
                "currency": "USD",
                "url": url,
                "country": None,
                "wrapper": None,
                "inStock": True,
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps({"shop": "neptune_us", "offers": offers, "unmatched_urls": unmatched}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT} offers={len(offers)} unmatched={unmatched}", flush=True)


if __name__ == "__main__":
    main()
