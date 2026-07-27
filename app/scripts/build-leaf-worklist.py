#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build worklist of all catalog cigars that have a CigarWorld EU URL.

  python scripts/build-leaf-worklist.py
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
OUT = HERE / "output" / "leaf_origin_worklist.json"


def main() -> None:
    cigars = json.loads((DATA / "cigars.json").read_text(encoding="utf-8"))
    rows = []
    for c in cigars:
        eu = ((c.get("regionLinks") or {}).get("EU") or {}).get("url") or ""
        if "cigarworld.de" not in eu:
            continue
        rows.append(
            {
                "id": c["id"],
                "brand": c.get("brand"),
                "line": c.get("line"),
                "cw_url": eu,
                "has_wrapper_origin": bool(c.get("wrapperOrigin")),
                "has_binder_origin": bool(c.get("binderOrigin")),
                "has_filler_origin": bool(c.get("fillerOrigin")),
            }
        )
    # Prefer gaps first
    rows.sort(
        key=lambda r: (
            int(r["has_wrapper_origin"] and r["has_binder_origin"] and r["has_filler_origin"]),
            r["brand"] or "",
            r["line"] or "",
        )
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    gaps = sum(
        1
        for r in rows
        if not (r["has_wrapper_origin"] and r["has_binder_origin"] and r["has_filler_origin"])
    )
    print(f"wrote {len(rows)} rows ({gaps} missing full origins) -> {OUT}")


if __name__ == "__main__":
    main()
