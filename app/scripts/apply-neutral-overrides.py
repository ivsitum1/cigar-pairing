#!/usr/bin/env python3
"""Primjenjuje neutralne izmjene tona/ocjena na data JSON-e (idempotentno).

Pokreni nakon svake regeneracije indeksa iz Excela:
    python3 scripts/apply-neutral-overrides.py

Izvor istine za neutralni ton je scripts/neutral_overrides.json:
- "rums"/"whiskies": per-id set polja (notes, qualityScore, pairable, ...)
- "rum_splits": kombinirani zapis -> vise zasebnih zapisa (Don Papa, Bumbu)
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"

OVR = json.loads((HERE / "neutral_overrides.json").read_text(encoding="utf-8"))


def apply_sets(items: list, overrides: dict) -> int:
    changed = 0
    by_id = {d["id"]: d for d in items}
    for id_, fields in overrides.items():
        d = by_id.get(id_)
        if d is None:
            continue
        for k, v in fields.items():
            if d.get(k) != v:
                d[k] = v
                changed += 1
    return changed


def apply_splits(items: list, splits: dict) -> list:
    out = []
    existing = {d["id"] for d in items}
    for d in items:
        reps = splits.get(d["id"])
        if reps:
            # zamijeni kombinirani zapis novima (preskoci vec postojece)
            out.extend(r for r in reps if r["id"] not in existing)
        else:
            out.append(d)
    return out


def process(fname: str, set_key: str, split_key: str | None = None) -> None:
    path = DATA / fname
    items = json.loads(path.read_text(encoding="utf-8"))
    n = apply_sets(items, OVR.get(set_key, {}))
    if split_key:
        items = apply_splits(items, OVR.get(split_key, {}))
    path.write_text(
        json.dumps(items, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(f"{fname}: {n} polja azurirano, {len(items)} zapisa")


if __name__ == "__main__":
    process("rums.json", "rums", "rum_splits")
    process("whiskies.json", "whiskies")
    sys.exit(0)
