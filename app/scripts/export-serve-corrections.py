#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generira seed/serve_corrections.json iz ispravljenih app JSON podataka."""
from __future__ import annotations

import json
from pathlib import Path

from serve_shared import RUM_SERVE_PROFILES, normalize_hint, serving_dict_to_excel

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data"
OUT = Path(__file__).resolve().parent / "seed" / "serve_corrections.json"


def drink_row(d: dict) -> dict:
    neat, water, rocks, highball, cola, best = serving_dict_to_excel(d.get("serving") or {})
    hint = d.get("cigarHint")
    if isinstance(hint, dict):
        hint = hint.get("hr")
    existing = {}
    if OUT.exists():
        existing = json.loads(OUT.read_text(encoding="utf-8-sig")).get("by_name", {})
    if not hint and d["name"] in existing:
        hint = existing[d["name"]].get("cigarHint")
    return {
        "neat": neat,
        "water": water,
        "rocks": rocks,
        "highball": highball,
        "cola": cola,
        "best": best,
        "cigarHint": normalize_hint(hint),
        "style": d.get("style"),
        "category": d.get("category"),
    }


def main() -> None:
    by_name: dict[str, dict] = {}
    for fname in ("rums.json", "brandies.json", "whiskies.json", "gins.json", "wines.json"):
        path = DATA / fname
        if not path.exists():
            continue
        for d in json.loads(path.read_text(encoding="utf-8-sig")):
            if not d.get("name"):
                continue
            by_name[d["name"]] = drink_row(d)

    payload = {
        "rum_profiles": RUM_SERVE_PROFILES,
        "by_name": by_name,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(by_name)} stavki, {len(RUM_SERVE_PROFILES)} rum profila)")


if __name__ == "__main__":
    main()
