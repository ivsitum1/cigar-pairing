#!/usr/bin/env python3
"""Status for Phase 3 W3 (2–4 lines) and W4 (1 line)."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from taxonomy_lib import TAXONOMY_DIR, brand_slug, load_json
from phase3_w2_status import W1

APP = Path(__file__).resolve().parent.parent
cigars = json.loads((APP / "src/data/cigars.json").read_text(encoding="utf-8"))
counts = Counter(c["brand"] for c in cigars)


def show(label: str, lo: int, hi: int) -> None:
    rows = []
    for brand, n in counts.most_common():
        if brand in W1:
            continue
        if not (lo <= n <= hi):
            continue
        fname = f"{brand_slug(brand)}.json"
        path = TAXONOMY_DIR / fname
        status = "MISSING"
        nlines = 0
        if path.exists():
            d = load_json(path, {}) or {}
            status = d.get("status") or "unknown"
            nlines = len(d.get("lines") or {})
        rows.append((n, brand, fname, status, nlines))
    done = sum(1 for r in rows if r[3] == "done")
    print(f"{label}: {len(rows)} brands  records={sum(r[0] for r in rows)}  status=done: {done}")
    for n, brand, fname, status, nlines in rows[:20]:
        print(f"  {n:3d}  {brand:<36} {fname:<32} status={status:<10} tax_lines={nlines}")
    if len(rows) > 20:
        print(f"  ... +{len(rows) - 20} more")


def main() -> None:
    show("W3", 2, 4)
    show("W4", 1, 1)


if __name__ == "__main__":
    main()
