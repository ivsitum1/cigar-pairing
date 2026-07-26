#!/usr/bin/env python3
"""Apply app/scripts/data/line_notes.json onto existing market cigars.json entries.

build-market-cigars.py already applies line_notes on every full rebuild (it
regenerates catalogSource=="market" entries from the unified shop catalog).
This script does the same fold for the *already-built* cigars.json, for runs
where the unified catalog input isn't available — deterministic, idempotent
(only catalogSource=="market" records are touched).

Usage:
  python scripts/apply-line-notes.py
  python scripts/apply-line-notes.py --check
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CIGARS = HERE.parent / "src" / "data" / "cigars.json"
DATADIR = HERE / "data"


def _load_build_module():
    spec = importlib.util.spec_from_file_location("build_market_cigars", HERE / "build-market-cigars.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="exit 1 if applying would change cigars.json")
    args = ap.parse_args()

    mod = _load_build_module()
    line_notes = mod.load_line_notes(DATADIR)
    cigars = mod.load_json(CIGARS)
    before = json.dumps(cigars, ensure_ascii=False, sort_keys=True)

    applied = 0
    for rec in cigars:
        if rec.get("catalogSource") != "market":
            continue
        if mod.apply_line_note(rec, rec["brand"], rec["line"], line_notes):
            applied += 1

    after = json.dumps(cigars, ensure_ascii=False, sort_keys=True)
    changed = before != after

    if args.check:
        if changed:
            raise SystemExit("line_notes not applied — run scripts/apply-line-notes.py")
        print(f"changed: false (already applied to {applied} lines)")
        return

    if changed:
        mod.write_json(CIGARS, cigars)
    print(f"applied line_notes to {applied} market line(s); changed: {changed}")


if __name__ == "__main__":
    main()
