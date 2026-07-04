#!/usr/bin/env python3
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "src/data/cigars.json").read_text(encoding="utf-8"))

ids = [c["id"] for c in data]
dupes = {k: v for k, v in Counter(ids).items() if v > 1}
print(f"total={len(data)} unique={len(set(ids))} dupes={len(dupes)}")
for id_, count in sorted(dupes.items()):
    entries = [(i, c["brand"], c["line"]) for i, c in enumerate(data) if c["id"] == id_]
    print(f"  DUPE {id_} x{count}: {entries}")

market = "HR"
q = "oliva"
pick = []
for c in data:
    if market not in c.get("markets", []):
        continue
    text = f"{c['brand']} {c['line']} {c['country']} {c['wrapper']} " + " ".join(
        v["name"] for v in c.get("vitolas", [])
    )
    if not q or q in text.lower():
        pick.append(c)

print(f"\noliva HR pickList ({len(pick)}):")
for c in pick:
    print(f"  {c['id'][:40]:40} | {c['line']}")

# key collision check for React
keys = [c["id"] for c in pick]
key_dupes = {k: v for k, v in Counter(keys).items() if v > 1}
print(f"\npickList key dupes: {key_dupes}")
