#!/usr/bin/env python3
"""Vraca rucno dodane zapise (seedove) u data JSON-e nakon regeneracije iz Excela.

Pokreni nakon svake regeneracije:
    python3 scripts/merge-extras.py

Idempotentno — dodaje samo zapise ciji id ne postoji:
- whiskies.json  <- seed/whiskies_classics_seed.json (klasici koje allez/ecuga ne drze
  + Starward Ginger Beer Cask, Edradour Cream, Chivas & mainstream dodaci)
- brandies.json  <- seed/brandies_extra_seed.json (grappe, Grand Marnier, Torres split)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"

MERGES = [
    ("whiskies.json", "seed/whiskies_classics_seed.json"),
    ("brandies.json", "seed/brandies_extra_seed.json"),
]


def merge(data_name: str, seed_name: str) -> None:
    data_path = DATA / data_name
    seed_path = HERE / seed_name
    cur = json.loads(data_path.read_text(encoding="utf-8"))
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    ids = {d["id"] for d in cur}
    add = [d for d in seed if d["id"] not in ids]
    cur.extend(add)
    data_path.write_text(
        json.dumps(cur, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(f"{data_name}: dodano {len(add)}, ukupno {len(cur)}")


if __name__ == "__main__":
    for data_name, seed_name in MERGES:
        merge(data_name, seed_name)
