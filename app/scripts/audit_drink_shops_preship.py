# -*- coding: utf-8 -*-
"""Pre-ship audit for drink shop merge/ingest.

  python scripts/audit_drink_shops_preship.py --check

Exit 1 if blockers found (CI may run with continue-on-error).
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
OUT = HERE / "output"
REGISTRY = DATA / "drinkIdRegistry.json"
HOLD = OUT / "shop_drinks_hold.json"

DRINK_FILES = (
    "rums.json",
    "whiskies.json",
    "brandies.json",
    "gins.json",
    "tequilas.json",
    "wines.json",
    "digestifs.json",
)

SHOP_HOST = {
    "allez.hr": "allez.hr",
    "tipsy.hr": "tipsy.hr",
    "cugaklik.hr": "cugaklik.hr",
    "miva.com.hr": "miva.com.hr",
    "Miva": "miva.com.hr",
    "webshop.rotodinamic.hr": "rotodinamic.hr",
    "humidor.hr": "humidor.hr",
    "ecuga.com": "ecuga.com",
}


def host_of(url: str) -> str:
    try:
        return (urlparse(url).hostname or "").lower().removeprefix("www.")
    except Exception:
        return ""


def brand_key(name: str) -> str:
    parts = (name or "").split()
    return " ".join(parts[:2]).lower() if parts else ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="Exit 1 on blockers")
    args = ap.parse_args()

    blockers: list[str] = []
    warnings: list[str] = []

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    reg_ids = set(registry.get("ids") or [])

    all_drinks: list[dict] = []
    ids: list[str] = []
    for fname in DRINK_FILES:
        path = DATA / fname
        if not path.exists():
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        for d in rows:
            all_drinks.append(d)
            ids.append(d["id"])

    dupes = [i for i, n in Counter(ids).items() if n > 1]
    if dupes:
        blockers.append(f"duplicate drink ids: {dupes[:10]}")

    missing_reg = [d["id"] for d in all_drinks if d["id"] not in reg_ids]
    if missing_reg:
        blockers.append(f"ids missing from drinkIdRegistry: {len(missing_reg)} e.g. {missing_reg[:5]}")

    # shopHR vs priceUrl host
    host_mismatch = 0
    for d in all_drinks:
        url = d.get("priceUrl") or ""
        shop = d.get("shopHR") or ""
        if not url or not shop:
            continue
        expected = SHOP_HOST.get(shop)
        if not expected:
            continue
        h = host_of(url)
        if expected not in h and h not in expected:
            host_mismatch += 1
    if host_mismatch:
        warnings.append(f"shopHR/priceUrl host mismatch: {host_mismatch}")

    # price outliers by brand key (shop-ingested only to reduce noise)
    by_brand: dict[str, list[float]] = defaultdict(list)
    for d in all_drinks:
        pe = d.get("priceEUR") or {}
        p = pe.get("min") if isinstance(pe, dict) else None
        if not isinstance(p, (int, float)):
            continue
        by_brand[brand_key(d.get("name") or "")].append(float(p))

    outliers = 0
    for d in all_drinks:
        if not d.get("shopIngest"):
            continue
        pe = d.get("priceEUR") or {}
        p = pe.get("min") if isinstance(pe, dict) else None
        if not isinstance(p, (int, float)):
            continue
        prices = by_brand.get(brand_key(d.get("name") or "")) or []
        if len(prices) < 3:
            continue
        med = statistics.median(prices)
        if med > 0 and p > 3 * med:
            outliers += 1
            warnings.append(f"price outlier {d['id']}: {p} vs median {med:.1f}")
    if outliers > 20:
        blockers.append(f"too many price outliers among shopIngest: {outliers}")

    if HOLD.exists():
        hold = json.loads(HOLD.read_text(encoding="utf-8"))
        n = len(hold.get("items") or [])
        if n > 5000:
            warnings.append(f"hold file very large: {n} items")

    print(f"drinks={len(all_drinks)} blockers={len(blockers)} warnings={len(warnings)}")
    for b in blockers:
        print(f"BLOCKER: {b}")
    for w in warnings[:20]:
        print(f"WARN: {w}")
    if len(warnings) > 20:
        print(f"WARN: ... +{len(warnings) - 20} more")

    if args.check and blockers:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
