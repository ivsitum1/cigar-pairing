#!/usr/bin/env python3
"""Vraca klasike (seed) u whiskies.json nakon regeneracije iz Excela.

Stari kurirani klasici (Talisker 10, Ardbeg 10, Springbank 10, bourboni...)
nisu u allez/ecuga katalogu pa ih regeneracija brise. Ovaj merge ih vraca:
    python3 scripts/merge-whisky-classics.py
Idempotentno: dodaje samo zapise ciji id ne postoji.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data" / "whiskies.json"
SEED = HERE / "seed" / "whiskies_classics_seed.json"

cur = json.loads(DATA.read_text(encoding="utf-8"))
seed = json.loads(SEED.read_text(encoding="utf-8"))
ids = {d["id"] for d in cur}
add = [d for d in seed if d["id"] not in ids]
cur.extend(add)
DATA.write_text(json.dumps(cur, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"dodano {len(add)} klasika; ukupno {len(cur)}")
