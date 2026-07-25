# -*- coding: utf-8 -*-
"""Uskladi availabilityHR / markets.HR s živim HR katalogom (idempotentno).

Ulaz: scripts/output/hr_catalog_snapshot.json (havana + humidor proizvodi).
Matcher: sync-hr-shops.detect_brand / line_name_from_product / norm.

Pravila:
  - catalogSource == "market" → ne diraj (HR već iz scrapanih ponuda)
  - tvrdi dokaz (regionLinks.HR ili URL na humidor/havana) → zadrži HR
  - inače: availabilityHR = presjek sa stvarno prisutnim (brand, line);
    bez poklapanja → availabilityHR=[] i makni "HR" iz markets

Pokretanje (iz app/):
  python scripts/reconcile-hr-availability.py [--fetch]
  --fetch  ponovno dohvati kataloge i prepiši snapshot
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP = ROOT.parent
DATA = APP / "src" / "data"
OUT = ROOT / "output"
SNAPSHOT = OUT / "hr_catalog_snapshot.json"
REPORT = OUT / "hr_reconcile_report.json"
CIGARS = DATA / "cigars.json"

HR_HOSTS = ("humidor.hr", "havana-cigar-shop.com")
SHOP_FROM_SOURCE = {
    "humidor": "The Humidor",
    "havana": "Havana Shop",
}


def _load_sync():
    spec = importlib.util.spec_from_file_location("sync_hr_shops", ROOT / "sync-hr-shops.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def fetch_snapshot(sync) -> dict:
    havana = sync.fetch_havana_catalog()
    humidor = sync.fetch_humidor_catalog()
    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "havana": havana,
        "humidor": humidor,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def load_snapshot() -> dict:
    if not SNAPSHOT.exists():
        raise SystemExit(f"Nedostaje snapshot: {SNAPSHOT}. Pokreni s --fetch.")
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


def is_hr_url(url: str | None) -> bool:
    if not url:
        return False
    u = url.lower()
    return any(h in u for h in HR_HOSTS)


def has_hard_hr_proof(c: dict) -> bool:
    rl = (c.get("regionLinks") or {}).get("HR")
    if isinstance(rl, dict) and is_hr_url(rl.get("url")):
        return True
    if is_hr_url(c.get("priceUrl")):
        return True
    for v in c.get("vitolas") or []:
        if is_hr_url(v.get("url")):
            return True
    return False


def build_present(sync, snapshot: dict, cigars: list[dict]) -> dict[tuple[str, str], set[str]]:
    """(brand_norm, line_norm) -> set shop display names."""
    detectors = sync.build_brand_detectors(cigars)
    present: dict[tuple[str, str], set[str]] = {}
    for src_key in ("havana", "humidor"):
        shop = SHOP_FROM_SOURCE[src_key]
        for row in snapshot.get(src_key) or []:
            name = row.get("name") or ""
            brand = sync.detect_brand(name, detectors)
            if not brand:
                continue
            line = sync.line_name_from_product(brand, name)
            key = (sync.norm(brand), sync.norm(line))
            present.setdefault(key, set()).add(shop)
    return present


def match_shops(c: dict, present: dict[tuple[str, str], set[str]], sync) -> set[str]:
    key = (sync.norm(c.get("brand", "")), sync.norm(c.get("line", "")))
    shops = set(present.get(key) or ())
    # fuzzy: line containment within same brand (isto kao find_or_create_cigar)
    if not shops:
        bn = key[0]
        ln = key[1]
        for (pb, pl), sh in present.items():
            if pb != bn:
                continue
            if ln and pl and (ln in pl or pl in ln):
                shops |= sh
    return shops


def reconcile(cigars: list[dict], present: dict, sync) -> list[dict]:
    removed: list[dict] = []
    for c in cigars:
        prev_av = list(c.get("availabilityHR") or [])
        prev_markets = list(c.get("markets") or [])
        is_market = c.get("catalogSource") == "market"

        if is_market:
            # Market HR mora imati dokaz; inače makni HR (očiti integritetni bug).
            if "HR" in prev_markets and not has_hard_hr_proof(c) and not prev_av:
                removed.append({
                    "id": c.get("id"),
                    "brand": c.get("brand"),
                    "line": c.get("line"),
                    "previous_availabilityHR": prev_av,
                    "previous_markets": prev_markets,
                    "reason": "market-HR-without-source",
                })
                c["markets"] = [m for m in prev_markets if m != "HR"]
            elif "HR" in prev_markets and has_hard_hr_proof(c) and not prev_av:
                # Vitola/price URL dokazuje HR, ali availabilityHR prazan → popuni.
                shops = match_shops(c, present, sync) or {"The Humidor", "Havana Shop"}
                c["availabilityHR"] = sorted(shops)
            continue

        if "HR" not in prev_markets and not prev_av:
            continue

        if has_hard_hr_proof(c):
            # zadrži HR; normaliziraj availability ako prazan a ima dokaz
            if not c.get("availabilityHR"):
                shops = match_shops(c, present, sync) or {"The Humidor", "Havana Shop"}
                c["availabilityHR"] = sorted(shops)
            if "HR" not in c.get("markets", []):
                c.setdefault("markets", []).append("HR")
            continue

        shops = match_shops(c, present, sync)
        if shops:
            new_av = sorted(shops)
            c["availabilityHR"] = new_av
            if "HR" not in c.get("markets", []):
                c.setdefault("markets", []).append("HR")
        else:
            if prev_av or "HR" in prev_markets:
                removed.append({
                    "id": c.get("id"),
                    "brand": c.get("brand"),
                    "line": c.get("line"),
                    "previous_availabilityHR": prev_av,
                    "previous_markets": prev_markets,
                    "reason": "no-snapshot-match",
                })
            c["availabilityHR"] = []
            c["markets"] = [m for m in (c.get("markets") or []) if m != "HR"]
    return removed


def integrity_count(cigars: list[dict]) -> int:
    bad = [
        c for c in cigars
        if "HR" in (c.get("markets") or [])
        and not (c.get("regionLinks") or {}).get("HR")
        and not c.get("availabilityHR")
    ]
    return len(bad)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="Ponovno dohvati HR kataloge")
    args = ap.parse_args()

    sync = _load_sync()
    if args.fetch:
        print("Dohvat HR kataloga...", flush=True)
        snap = fetch_snapshot(sync)
    else:
        snap = load_snapshot()
    print(
        f"Snapshot: havana={len(snap.get('havana') or [])} "
        f"humidor={len(snap.get('humidor') or [])} "
        f"at={snap.get('fetched_at')}",
        flush=True,
    )

    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    present = build_present(sync, snap, cigars)
    print(f"Prisutni (brand,line) ključevi: {len(present)}", flush=True)

    removed = reconcile(cigars, present, sync)
    CIGARS.write_text(json.dumps(cigars, ensure_ascii=False, indent=1), encoding="utf-8")

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "snapshot_at": snap.get("fetched_at"),
        "present_keys": len(present),
        "removed_count": len(removed),
        "hr_without_source": integrity_count(cigars),
        "hr_markets_remaining": sum(1 for c in cigars if "HR" in (c.get("markets") or [])),
        "removed": removed,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"Maknuto HR: {report['removed_count']} | "
        f"HR bez izvora: {report['hr_without_source']} | "
        f"HR markets preostalo: {report['hr_markets_remaining']}",
        flush=True,
    )
    print(f"Report: {REPORT}", flush=True)


if __name__ == "__main__":
    main()
