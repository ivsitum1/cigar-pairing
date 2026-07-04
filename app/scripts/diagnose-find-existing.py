#!/usr/bin/env python3
"""Simulate find_existing fuzzy matches for Oliva YAML lines."""
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "30_system/scripts/cigars"))

try:
    import yaml
except ImportError:
    print("need pyyaml")
    sys.exit(1)

from export_cigars_to_app import (  # noqa: E402
    PAIRING_SEED,
    build_existing_index,
    find_existing,
    load_json,
    make_line_id,
)


def main() -> None:
    seed = load_json(PAIRING_SEED)
    index = build_existing_index(seed)
    oliva = yaml.safe_load((ROOT / "01_input/collections/cigars/data/brands/oliva.yaml").read_text(encoding="utf-8"))
    brand = oliva["brand"]
    print("Oliva YAML lines -> find_existing match:")
    for line in oliva.get("lines") or []:
        cid = make_line_id(brand["id"], line["id"], brand["name"], line["name"])
        ex = find_existing(index, brand["name"], line["name"], cid)
        match = f"{ex['id']} ({ex['line']})" if ex else "—"
        flag = " *** FUZZY COLLISION" if ex and ex["line"] != line["name"] else ""
        print(f"  {line['name'][:45]:45} -> {match}{flag}")


if __name__ == "__main__":
    main()
