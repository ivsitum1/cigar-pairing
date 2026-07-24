#!/usr/bin/env python3
"""List Phase 3 W2 brands: live records in [5, 19], excluding W1."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from taxonomy_lib import TAXONOMY_DIR, brand_slug, load_json

W1 = {
    "Oscar Valladares",
    "Rocky Patel",
    "Perdomo",
    "Gurkha",
    "Villiger",
    "E.P. Carrillo",
    "La Galera",
    "Drew Estate",
    "Davidoff",
    "Alec Bradley",
    "Arturo Fuente",
    "La Aurora",
    "My Father",
    "Padilla",
    "Kristoff",
    "Tatuaje",
    "Black Label Trading Company",
    "Padrón",
    "RoMa Craft Tobac",
    "Aganorsa Leaf",
    "PDR",
    "Casdagli",
    "Caldwell",
    "CAO",
    "Ashton",
    "Joya de Nicaragua",
    "Montecristo",
    "Oliva",
    "Camacho",
    "Eiroa",
    "Flor de Selva",
    "Plasencia",
    "1502",
    "Artista",
    "Casa Turrent",
    "Cavalier Genève",
    "La Aroma de Cuba",
    "Laura Chavin",
    "Leonel",
    "Gran Habano",
}

APP = Path(__file__).resolve().parent.parent
cigars = json.loads((APP / "src/data/cigars.json").read_text(encoding="utf-8"))
counts = Counter(c["brand"] for c in cigars)

w2 = []
for brand, n in counts.most_common():
    if brand in W1:
        continue
    if 5 <= n <= 19:
        fname = f"{brand_slug(brand)}.json"
        path = TAXONOMY_DIR / fname
        status = "MISSING"
        nlines = 0
        if path.exists():
            d = load_json(path, {}) or {}
            status = d.get("status") or "unknown"
            nlines = len(d.get("lines") or {})
        w2.append((n, brand, fname, status, nlines))

print(f"W2 brands: {len(w2)}  records: {sum(n for n, *_ in w2)}")
for n, brand, fname, status, nlines in w2:
    print(f"  {n:3d}  {brand:<36} {fname:<32} status={status:<10} tax_lines={nlines}")
