#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build Famous brand-page URL candidates from queue + known slug fixes.

  python scripts/build-famous-brand-urls.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUEUE = HERE / "output" / "famous_exa_queue.json"
OUT = HERE / "output" / "famous_brand_urls.json"

# Known Famous slug overrides (line → brand-page slug after /brand-)
OVERRIDES = {
    "cig-alec-bradley-american-classic": "alec-bradley-american-classic-blend",
    "cig-arturo-fuente-anejo": "arturo-fuente-anejo",
    "cig-alec-bradley-maxx": "alec-bradley-maxx",
    "cig-alec-bradley-project-40": "alec-bradley-project-40",
    "cig-alec-bradley-project-40-maduro": "alec-bradley-project-40-maduro",
}


def slugify(s: str) -> str:
    s = s.lower().replace("&", " and ").replace("'", "")
    s = s.replace("ñ", "n").replace("é", "e").replace("á", "a").replace("ó", "o")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def main() -> None:
    rows = json.loads(QUEUE.read_text(encoding="utf-8"))
    out = []
    for r in rows:
        if r["id"] in OVERRIDES:
            slug = OVERRIDES[r["id"]]
        else:
            slug = slugify(f"{r['brand']} {r['line']}")
        urls = [
            f"https://www.famous-smoke.com/brand-{slug}",
            f"https://www.famous-smoke.com/brand/{slug}-cigars",
            f"https://www.famous-smoke.com/brands/{slugify(r['brand'])}-cigars/{slug}",
        ]
        out.append({**r, "urls": list(dict.fromkeys(urls))})
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(out)} -> {OUT}")
    for r in out[:5]:
        print(r["id"], r["urls"][0])


if __name__ == "__main__":
    main()
