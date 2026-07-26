#!/usr/bin/env python3
"""Flag cigar priceUrl / HR links whose slug lacks the brand token."""
from __future__ import annotations

import json
import re
from pathlib import Path

cigars = json.loads(Path("app/src/data/cigars.json").read_text(encoding="utf-8"))
bad: list[str] = []
for c in cigars:
    urls: list[tuple[str, str]] = []
    if c.get("priceUrl"):
        urls.append(("priceUrl", c["priceUrl"]))
    rl = c.get("regionLinks") or {}
    hr = rl.get("HR") if isinstance(rl, dict) else None
    if isinstance(hr, dict) and hr.get("url"):
        urls.append(("HR", hr["url"]))
    brand = re.sub(r"[^a-z0-9]+", "", (c.get("brand") or "").lower())
    for kind, url in urls:
        slug = re.sub(r"[^a-z0-9]+", "", url.lower())
        if len(brand) >= 4 and brand not in slug:
            bad.append(f"{c['id']}\t{c['brand']}\t{kind}\t{url}")

out = Path("01_work/output/url-mismatch.txt")
out.write_text("\n".join(bad), encoding="utf-8")
print(f"suspect={len(bad)} -> {out}")
for row in bad[:20]:
    print(row)
