#!/usr/bin/env python3
"""Quick structural check of Phase 3 taxonomy files (no apply)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from taxonomy_lib import TAXONOMY_DIR, brand_slug, load_json

W1 = [
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
]

RENAME_FILE = {
    "Black Label Trading Company": "black-label.json",
    "RoMa Craft Tobac": "roma.json",
    "Cavalier Genève": "cavalier.json",
    "Laura Chavin": "laura.json",
    "Gran Habano": "gh.json",
}


def main() -> None:
    rows = []
    for live in W1:
        fname = RENAME_FILE.get(live, f"{brand_slug(live)}.json")
        path = TAXONOMY_DIR / fname
        if not path.exists():
            rows.append((live, fname, "MISSING", 0, None))
            continue
        d = load_json(path, {}) or {}
        rows.append(
            (
                live,
                fname,
                d.get("status"),
                len(d.get("lines") or {}),
                len(d.get("unresolved") or []),
            )
        )
    done = sum(1 for r in rows if r[2] == "done")
    print(f"W1 files: {len(rows)}  status=done: {done}")
    for live, fname, status, nlines, nunres in rows:
        print(f"  {live:<32} {fname:<28} status={status!s:<10} lines={nlines:<4} unresolved={nunres}")


if __name__ == "__main__":
    main()
