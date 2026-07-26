#!/usr/bin/env python3
"""Clear wrong-brand cigar URLs: slug contains another catalog brand, not this one."""
from __future__ import annotations

import json
import re
from pathlib import Path

path = Path("app/src/data/cigars.json")
cigars = json.loads(path.read_text(encoding="utf-8"))
brands = sorted(
    {re.sub(r"[^a-z0-9]+", "", b.lower()) for b in {c["brand"] for c in cigars} if len(b) >= 4},
    key=len,
    reverse=True,
)

def brand_tok(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())

fixed = 0
for c in cigars:
    own = brand_tok(c["brand"])
    line = brand_tok(c.get("line") or "")
    aliases = {own}
    # common abbreviations
    if own.startswith("ajfernandez"):
        aliases.add("ajf")
    if own == "arturofuente":
        aliases.add("fuente")
    if own == "mydad":
        aliases.add("myfather")

    def is_wrong(url: str) -> bool:
        slug = brand_tok(url)
        if any(a and a in slug for a in aliases):
            return False
        if line and len(line) >= 5 and line in slug:
            return False
        # foreign brand token present
        for b in brands:
            if b == own or len(b) < 5:
                continue
            if b in slug and b not in aliases:
                return True
        return False

    if c.get("priceUrl") and is_wrong(c["priceUrl"]):
        print(f"CLEAR priceUrl {c['id']} <- {c['priceUrl']}")
        c["priceUrl"] = None
        fixed += 1
    rl = c.get("regionLinks")
    if isinstance(rl, dict):
        hr = rl.get("HR")
        if isinstance(hr, dict) and hr.get("url") and is_wrong(hr["url"]):
            print(f"CLEAR HR {c['id']} <- {hr['url']}")
            del rl["HR"]
            fixed += 1

path.write_text(json.dumps(cigars, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"cleared={fixed}")
