#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert cw_famous_flavor_raw.json → cigarworld_flavor_raw.json for merge script."""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "output" / "cw_famous_flavor_raw.json"
DST = HERE / "output" / "cigarworld_flavor_raw.json"


def main() -> None:
    rows = json.loads(SRC.read_text(encoding="utf-8"))
    out = []
    for r in rows:
        cw = r.get("cigarworld") or {}
        fam = r.get("famous") or {}
        facts = dict(cw.get("facts") or {})
        # Normalize CW fields for merge
        if facts.get("wrapper variety") and not facts.get("wrapper"):
            facts["wrapper"] = facts["wrapper variety"]
        for k, v in (cw.get("aroma") or {}).items():
            facts[f"aroma {k}"] = str(v)
        for k, v in (cw.get("props") or {}).items():
            facts[f"prop {k}"] = str(v)
        for k, v in (fam.get("facts") or {}).items():
            # Famous shop facts win over CW for shared keys
            if v and not re.search(r"not available|undisclosed", str(v), re.I):
                facts[k] = str(v).strip()
        if facts.get("wrapper leaf") and (
            not facts.get("wrapper")
            or facts.get("wrapper") in ("—", "-", "Natural", "?", "Nicaragua", "Honduras")
            or re.search(r"not available|undisclosed", str(facts.get("wrapper") or ""), re.I)
        ):
            facts["wrapper"] = str(facts["wrapper leaf"]).strip()
        # drop useless wrapper placeholders
        if re.search(r"not available|undisclosed", str(facts.get("wrapper") or ""), re.I):
            facts.pop("wrapper", None)
        # Prefer Famous tasting prose; CW aroma radar only as fallback tag fuel
        fam_desc = (fam.get("description") or "").strip()
        aroma_bits = [
            f"{n}"
            for n, v in sorted((cw.get("aroma") or {}).items(), key=lambda kv: -int(kv[1] or 0))
            if int(v or 0) >= 5
        ]
        bits = " ".join((cw.get("flavour_bits") or []) + aroma_bits)
        if fam_desc and len(fam_desc) > 60:
            desc = fam_desc
        else:
            desc_parts = [cw.get("description") or "", bits]
            desc = " ".join(p for p in desc_parts if p).strip()
        strength = (cw.get("props") or {}).get("strength")
        if strength is not None and not facts.get("strength"):
            facts["strength"] = str(strength)
        ok = bool(cw.get("ok") or fam.get("ok"))
        out.append(
            {
                "id": r["id"],
                "url": cw.get("url") or fam.get("product_url") or fam.get("search_url"),
                "ok": ok,
                "title": cw.get("title") or fam.get("title") or "",
                "facts": facts,
                "description": desc[:2500],
                "sources": {
                    "cigarworld": bool(cw.get("ok")),
                    "famous": bool(fam.get("ok")),
                },
            }
        )
    DST.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"converted={len(out)} ok={sum(1 for x in out if x['ok'])} -> {DST}")


if __name__ == "__main__":
    main()
