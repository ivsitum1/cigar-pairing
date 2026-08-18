#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge stock_overlay.json onto the current catalog by normalized product URL.

Use after pulling master when a prior stock ping wrote overlay but catalog JSON
was reset. Does not fetch; only copies inStock/stockFetchedAt onto matching URLs.

  python scripts/apply-stock-overlay.py --dry-run
  python scripts/apply-stock-overlay.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from availability_catalog import apply_stock_to_cigar, apply_stock_to_drink, normalize_url  # noqa: E402

ROOT = HERE.parent
DATA = ROOT / "src" / "data"
OVERLAY = HERE / "output" / "stock_overlay.json"
CIGARS_JSON = DATA / "cigars.json"
DRINK_FILES = (
    DATA / "rums.json",
    DATA / "whiskies.json",
    DATA / "brandies.json",
    DATA / "gins.json",
    DATA / "tequilas.json",
    DATA / "digestifs.json",
    DATA / "wines.json",
    DATA / "coffees.json",
)


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _apply_overlay_to_cigars(cigars: list, overlay: dict[str, dict]) -> int:
    applied = 0
    for c in cigars:
        candidates: list[tuple[str, dict]] = []
        if c.get("priceUrl"):
            candidates.append((c["priceUrl"], c))
        for link in (c.get("regionLinks") or {}).values():
            if isinstance(link, dict) and link.get("url"):
                candidates.append((link["url"], link))
        for vitola in c.get("vitolas") or []:
            if not isinstance(vitola, dict):
                continue
            if vitola.get("url"):
                candidates.append((vitola["url"], vitola))
            for link in (vitola.get("regionLinks") or {}).values():
                if isinstance(link, dict) and link.get("url"):
                    candidates.append((link["url"], link))
        for url, obj in candidates:
            rec = overlay.get(normalize_url(url))
            if not rec:
                continue
            in_stock = rec.get("inStock")
            fetched_at = rec.get("stockFetchedAt")
            if in_stock not in (True, False) or not fetched_at:
                continue
            if obj.get("stockFetchedAt") == fetched_at and obj.get("inStock") == in_stock:
                continue
            obj["inStock"] = in_stock
            obj["stockFetchedAt"] = fetched_at
            applied += 1
    return applied


def _apply_overlay_to_drinks(records: list, overlay: dict[str, dict]) -> int:
    applied = 0
    for d in records:
        url = d.get("priceUrl")
        if not url:
            continue
        rec = overlay.get(normalize_url(url))
        if not rec:
            continue
        in_stock = rec.get("inStock")
        fetched_at = rec.get("stockFetchedAt")
        if in_stock not in (True, False) or not fetched_at:
            continue
        if d.get("stockFetchedAt") == fetched_at and d.get("inStock") == in_stock:
            continue
        d["inStock"] = in_stock
        d["stockFetchedAt"] = fetched_at
        applied += 1
    return applied


def main() -> int:
    p = argparse.ArgumentParser(description="Apply stock overlay onto catalog JSON.")
    p.add_argument("--overlay", type=Path, default=OVERLAY)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if not args.overlay.is_file():
        print(f"missing overlay: {args.overlay}", file=sys.stderr)
        return 1

    overlay_raw = json.loads(args.overlay.read_text(encoding="utf-8"))
    overlay: dict[str, dict] = {}
    for key, rec in overlay_raw.items():
        norm = normalize_url(key)
        if norm and isinstance(rec, dict) and "inStock" in rec:
            overlay[norm] = rec

    cigars = _load(CIGARS_JSON)
    drink_payloads: list[tuple[Path, list]] = []
    for path in DRINK_FILES:
        if path.exists():
            payload = _load(path)
            if isinstance(payload, list):
                drink_payloads.append((path, payload))

    applied = _apply_overlay_to_cigars(cigars, overlay)
    for _path, records in drink_payloads:
        applied += _apply_overlay_to_drinks(records, overlay)

    print(f"overlay={len(overlay)} applied={applied}", flush=True)
    if args.dry_run:
        return 0

    _save(CIGARS_JSON, cigars)
    print(f"wrote {CIGARS_JSON}", flush=True)
    for path, records in drink_payloads:
        _save(path, records)
        print(f"wrote {path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
