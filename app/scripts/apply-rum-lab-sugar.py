#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply verified lab/hydrometer sugar measurements to rums.json.

Only IDs present in scripts/data/rum-lab-sugar.json are updated.
Does not invent g/L for bottles without a measurement.

Usage:
  python scripts/apply-rum-lab-sugar.py          # apply
  python scripts/apply-rum-lab-sugar.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RUMS = ROOT / "src" / "data" / "rums.json"
MAP = HERE / "data" / "rum-lab-sugar.json"
OUT = HERE / "output"


def status_for(g_l: float, keep: str | None) -> str:
    if keep:
        return keep
    if g_l <= 5:
        return "clean"
    if g_l <= 11:
        return "light"
    if g_l <= 20:
        return "moderate"
    return "sweetened"


def sweetness_for(g_l: float, keep: str | None) -> int | None:
    if keep == "flavored":
        return 5
    if g_l <= 5:
        return 1
    if g_l <= 11:
        return 2
    if g_l <= 20:
        return 3
    if g_l <= 40:
        return 4
    return 5


def detail_texts(entry: dict) -> dict:
    method = entry["method"]
    g = entry["gL"]
    g_min = entry.get("gLMin")
    g_max = entry.get("gLMax")
    lab = method == "lab"

    if g_min is not None and g_max == 5 and g_min == 0:
        hr = (
            f"Šećer ≤5 g/L ({'lab' if lab else 'hidrometar'}); tipično bez doziranog šećera"
        )
        en = (
            f"Sugar ≤5 g/L ({'lab' if lab else 'hydrometer'}); typically no dosed sugar"
        )
    elif g_max is None and g_min is not None:
        hr = f"Dodani šećer >{g_min:g} g/L ({'lab' if lab else 'hidrometar'})"
        en = f"Added sugar >{g_min:g} g/L ({'lab' if lab else 'hydrometer'})"
    else:
        hr = f"Dodani šećer ~{g:g} g/L ({'lab' if lab else 'hidrometar'})"
        en = f"Added sugar ~{g:g} g/L ({'lab' if lab else 'hydrometer'})"
    return {"hr": hr, "en": en}


def apply(dry_run: bool) -> None:
    payload = json.loads(MAP.read_text(encoding="utf-8"))
    entries: dict = payload["entries"]
    rums = json.loads(RUMS.read_text(encoding="utf-8"))
    by_id = {d["id"]: d for d in rums}

    applied = []
    missing = []
    skipped_already = []

    for rid, entry in entries.items():
        rum = by_id.get(rid)
        if rum is None:
            missing.append(rid)
            continue

        src = entry["source"]
        # Skip if already has this exact lab source (idempotent)
        if rum.get("additiveSource") == src:
            skipped_already.append(rid)
            continue

        g = float(entry["gL"])
        keep = entry.get("keepStatus")
        status = status_for(g, keep)
        sweet = sweetness_for(g, keep)
        detail = detail_texts(entry)

        rum["additiveStatus"] = status
        rum["additiveDetail"] = detail
        rum["additiveSource"] = src
        if sweet is not None:
            rum["sweetness"] = sweet
        applied.append(rid)

    print(f"apply={len(applied)} already={len(skipped_already)} missing={len(missing)}")
    for rid in applied:
        print(f"  + {rid}")
    for rid in missing:
        print(f"  ! missing {rid}")

    if dry_run:
        print("dry-run: no write")
        return

    OUT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = OUT / f"rums-before-lab-sugar-{stamp}.json"
    shutil.copy2(RUMS, backup)
    shutil.copy2(RUMS, OUT / "rums-allez-latest.json")
    RUMS.write_text(json.dumps(rums, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    shutil.copy2(RUMS, OUT / "rums-allez-latest.json")
    print(f"wrote {RUMS} (backup {backup.name})")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    apply(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
