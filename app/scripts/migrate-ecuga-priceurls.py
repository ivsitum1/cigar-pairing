#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rewrite eCuga drink `priceUrl` from `/katalog/.../<slug>` to `/proizvod/<slug>`.

Why:
  Stock parser expects eCuga product pages that embed Saleor product stock
  data (via `__NEXT_DATA__`). Those pages are under `/proizvod/`.

This script is pure data migration (no scraping). It is idempotent.

  python scripts/migrate-ecuga-priceurls.py --dry-run
  python scripts/migrate-ecuga-priceurls.py
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "src" / "data"

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


def _rewrite_ecuga_katalog(url: str) -> str | None:
    try:
        parsed = urlparse(url)
    except Exception:
        return None

    host = (parsed.hostname or "").lower()
    if host != "ecuga.com":
        return None
    if "/katalog/" not in parsed.path:
        return None
    if "/proizvod/" in parsed.path:
        return None

    slug = parsed.path.rstrip("/").split("/")[-1]
    if not slug:
        return None
    return f"https://ecuga.com/proizvod/{slug}"


def main() -> int:
    p = argparse.ArgumentParser(description="Rewrite eCuga drink priceUrl from katalog -> proizvod")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    total_changed = 0
    total_scanned = 0

    for path in DRINK_FILES:
        if not path.exists():
            continue
        drinks = _load(path)
        if not isinstance(drinks, list):
            continue

        changed = 0
        scanned = 0

        for d in drinks:
            if not isinstance(d, dict):
                continue
            scanned += 1
            if d.get("shopHR") != "ecuga.com":
                continue
            price_url = d.get("priceUrl")
            if not isinstance(price_url, str):
                continue

            new_url = _rewrite_ecuga_katalog(price_url)
            if not new_url or new_url == price_url:
                continue

            d["priceUrl"] = new_url
            changed += 1

        if changed:
            total_changed += changed
            total_scanned += scanned
            if not args.dry_run:
                _save(path, drinks)
            print(f"{path.name}: changed={changed} scanned={scanned}", flush=True)

    print(
        f"done date={date.today().isoformat()} changed={total_changed} scanned={total_scanned}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

