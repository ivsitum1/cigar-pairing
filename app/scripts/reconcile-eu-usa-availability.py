# -*- coding: utf-8 -*-
"""Uskladi markets.EU / markets.USA s dokazom + živim CigarWorld/Holt's snapshotom.

Idempotentno. Ne izmišlja dostupnost.

Pravila:
  - tvrdi dokaz: regionLinks[region] s URL-om ILI product URL na regionalnim hostovima
  - soft keep / discovery EU: (brand, line) u CigarWorld sitemap snimci
  - soft keep USA: brand prisutan na Holt's brand listing sitemapu (SKU nema);
    discovery USA samo uz tvrdi dokaz (regionLinks/URL) — brand-level nije dovoljan za ADD
  - embargo: kubanske nikad USA
  - Cigars Daily više nije aktivni USA izvor

Pokretanje (iz app/):
  python scripts/reconcile-eu-usa-availability.py [--fetch]
  --fetch  dohvati CigarWorld + Holt's sitemap → eu_usa_catalog_snapshot.json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP = ROOT.parent
DATA = APP / "src" / "data"
OUT = ROOT / "output"
SNAPSHOT = OUT / "eu_usa_catalog_snapshot.json"
REPORT = OUT / "eu_usa_reconcile_report.json"
CIGARS = DATA / "cigars.json"

REGIONS = ("EU", "USA")
HOSTS = {
    "EU": ("cigarworld.de", "cigarworld.com"),
    # famous/neptune/daily: legacy regionLinks i dalje vrijede kao tvrdi dokaz
    "USA": ("holts.com", "famous-smoke.com", "neptunecigar.com", "cigarsdaily.com"),
}
MIN_FETCH = {"cigarworld": 500, "holts": 50}

VITOLA_TAIL = (
    "robusto grande", "double robusto", "short robusto", "petit corona",
    "double toro", "double corona", "robusto", "toro", "churchill", "corona",
    "figurado", "lonsdale", "panatela", "torpedo", "gordo", "diadema",
    "perfecto", "lancero", "belicoso",
)


def _load_fetch():
    spec = importlib.util.spec_from_file_location(
        "fetch_eu_usa", ROOT / "fetch-eu-usa-catalogs.py"
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _load_sync():
    spec = importlib.util.spec_from_file_location("sync_hr_shops", ROOT / "sync-hr-shops.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s.lower().strip())


def is_cuban(country: str | None) -> bool:
    c = (country or "").lower()
    return "kub" in c or "cuba" in c


def is_region_host_url(url: str | None, region: str) -> bool:
    if not url:
        return False
    u = url.lower()
    return any(h in u for h in HOSTS[region])


def has_hard_proof(c: dict, region: str) -> bool:
    rl = (c.get("regionLinks") or {}).get(region)
    if isinstance(rl, dict) and rl.get("url"):
        return True
    if is_region_host_url(c.get("priceUrl"), region):
        return True
    for v in c.get("vitolas") or []:
        if is_region_host_url(v.get("url"), region):
            return True
    return False


def region_link_url(c: dict, region: str) -> str | None:
    rl = (c.get("regionLinks") or {}).get(region)
    if isinstance(rl, dict) and rl.get("url"):
        return str(rl["url"])
    return None


def strip_vitola_tail(line: str) -> str:
    rest = norm(line)
    for vit in VITOLA_TAIL:
        if rest == vit:
            return ""
        if rest.endswith(" " + vit):
            return rest[: -len(vit)].strip()
    return rest


def line_from_product(brand: str, product_name: str) -> str:
    low = norm(product_name)
    b = norm(brand)
    rest = low
    if rest.startswith(b):
        rest = rest[len(b) :].strip(" -/&")
    rest = strip_vitola_tail(rest)
    return rest.title() if rest else brand


def fetch_snapshot(fetch_mod) -> dict:
    cw = fetch_mod.fetch_cigarworld_catalog()
    holts = fetch_mod.fetch_holts_brands()

    if SNAPSHOT.exists():
        prev = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        for key, fresh, floor in (
            ("cigarworld", cw, MIN_FETCH["cigarworld"]),
            ("holts", holts, MIN_FETCH["holts"]),
        ):
            before = len(prev.get(key) or [])
            now = len(fresh)
            if before and now < max(floor, int(before * 0.7)):
                raise SystemExit(
                    f"Dohvat '{key}' vratio {now} (prije {before}, prag "
                    f"{max(floor, int(before * 0.7))}). Snapshot NIJE prepisan."
                )
            if now < floor:
                raise SystemExit(
                    f"Dohvat '{key}' vratio samo {now} (< {floor}). "
                    f"Snapshot NIJE prepisan."
                )

    return fetch_mod.write_snapshot(cw, holts)


def load_snapshot() -> dict:
    if not SNAPSHOT.exists():
        raise SystemExit(f"Nedostaje snapshot: {SNAPSHOT}. Pokreni s --fetch.")
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


def build_present(
    sync,
    snapshot: dict,
    cigars: list[dict],
) -> tuple[dict[str, set[tuple[str, str]]], set[str]]:
    """EU: (brand, line) iz CW proizvoda. USA brands: norm brand s Holt's listinga."""
    detectors = sync.build_brand_detectors(cigars)
    present: dict[str, set[tuple[str, str]]] = {r: set() for r in REGIONS}
    usa_brands: set[str] = set()

    for row in snapshot.get("cigarworld") or []:
        name = row.get("name") or ""
        brand = sync.detect_brand(name, detectors)
        if not brand:
            continue
        line = line_from_product(brand, name)
        present["EU"].add((norm(brand), norm(line)))
        # fuzzy: also store brand+empty when line collapses to brand
        if norm(line) == norm(brand):
            present["EU"].add((norm(brand), ""))

    for row in snapshot.get("holts") or []:
        brand = row.get("brand") or ""
        if brand:
            usa_brands.add(norm(brand))
        # line_or_brand slug may encode brand+line — try detect against cigars
        name = sync.slugify(brand).replace("-", " ").title() if hasattr(sync, "slugify") else brand
        detected = sync.detect_brand(row.get("brand") or name, detectors)
        if detected:
            usa_brands.add(norm(detected))
            # If slug is longer than brand, treat remainder as soft line key
            slug = norm((row.get("slug") or "").replace("-", " "))
            bn = norm(detected)
            if slug.startswith(bn) and len(slug) > len(bn) + 1:
                present["USA"].add((bn, slug[len(bn) :].strip()))

    return present, usa_brands


def soft_match_pair(c: dict, present: set[tuple[str, str]]) -> bool:
    key = (norm(c.get("brand", "")), norm(c.get("line", "")))
    if key in present:
        return True
    bn, ln = key
    if not bn:
        return False
    if (bn, "") in present:
        return True
    if not ln:
        return False
    for pb, pl in present:
        if pb != bn:
            continue
        if pl and (ln in pl or pl in ln):
            return True
    return False


def soft_usa_brand(c: dict, usa_brands: set[str]) -> bool:
    return norm(c.get("brand", "")) in usa_brands


def reconcile(
    cigars: list[dict],
    present: dict[str, set[tuple[str, str]]],
    usa_brands: set[str],
) -> tuple[list[dict], list[dict]]:
    removed: list[dict] = []
    added: list[dict] = []

    for c in cigars:
        markets = list(c.get("markets") or [])
        changed = list(markets)
        cuban = is_cuban(c.get("country"))

        for region in REGIONS:
            if region == "USA" and cuban:
                if region in changed:
                    removed.append({
                        "id": c.get("id"),
                        "brand": c.get("brand"),
                        "line": c.get("line"),
                        "region": region,
                        "previous_markets": markets,
                        "reason": "embargo-cuba",
                    })
                    changed = [m for m in changed if m != region]
                continue

            hard = has_hard_proof(c, region)
            soft_pair = soft_match_pair(c, present.get(region) or set())
            soft_brand = region == "USA" and soft_usa_brand(c, usa_brands)
            # EU: product-level soft is enough to ADD. USA brand-level only KEEPS.
            soft_keep = soft_pair or soft_brand
            soft_discover = soft_pair if region == "EU" else False
            in_markets = region in changed
            link = region_link_url(c, region)

            if not in_markets:
                if link or hard:
                    changed.append(region)
                    added.append({
                        "id": c.get("id"),
                        "brand": c.get("brand"),
                        "line": c.get("line"),
                        "region": region,
                        "url": link,
                        "reason": "has_link_missing_market",
                    })
                elif soft_discover:
                    changed.append(region)
                    added.append({
                        "id": c.get("id"),
                        "brand": c.get("brand"),
                        "line": c.get("line"),
                        "region": region,
                        "reason": "snapshot-discover",
                    })
                continue

            if hard or soft_keep:
                continue

            removed.append({
                "id": c.get("id"),
                "brand": c.get("brand"),
                "line": c.get("line"),
                "region": region,
                "catalogSource": c.get("catalogSource"),
                "previous_markets": markets,
                "reason": "no-proof-no-snapshot-match",
            })
            changed = [m for m in changed if m != region]

        order = {"HR": 0, "EU": 1, "USA": 2}
        changed = sorted(set(changed), key=lambda m: (order.get(m, 9), m))
        if changed != markets:
            c["markets"] = changed

    return removed, added


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--fetch",
        action="store_true",
        help="Dohvati CigarWorld + Holt's sitemap i prepiši snapshot",
    )
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    sync = _load_sync()

    if args.fetch:
        print("Dohvat CigarWorld + Holt's kataloga…", flush=True)
        fetch_mod = _load_fetch()
        snap = fetch_snapshot(fetch_mod)
    else:
        snap = load_snapshot()

    print(
        f"Snapshot: cw={len(snap.get('cigarworld') or [])} "
        f"holts={len(snap.get('holts') or [])} at={snap.get('fetched_at')}",
        flush=True,
    )

    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    present, usa_brands = build_present(sync, snap, cigars)
    print(
        f"Present EU pairs={len(present['EU'])} USA pairs={len(present['USA'])} "
        f"USA brands={len(usa_brands)}",
        flush=True,
    )

    removed, added = reconcile(cigars, present, usa_brands)
    CIGARS.write_text(json.dumps(cigars, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "snapshot_at": snap.get("fetched_at"),
        "present_keys": {r: len(present[r]) for r in REGIONS},
        "usa_brands": len(usa_brands),
        "removed_count": len(removed),
        "added_count": len(added),
        "removed_eu": sum(1 for r in removed if r["region"] == "EU"),
        "removed_usa": sum(1 for r in removed if r["region"] == "USA"),
        "added_eu": sum(1 for a in added if a["region"] == "EU"),
        "added_usa": sum(1 for a in added if a["region"] == "USA"),
        "markets_remaining": {
            r: sum(1 for c in cigars if r in (c.get("markets") or []))
            for r in REGIONS
        },
        "removed": removed,
        "added": added,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Added EU={report['added_eu']} USA={report['added_usa']} | "
        f"Removed EU={report['removed_eu']} USA={report['removed_usa']} | "
        f"markets EU={report['markets_remaining']['EU']} "
        f"USA={report['markets_remaining']['USA']}",
        flush=True,
    )
    print(f"Report: {REPORT}", flush=True)


if __name__ == "__main__":
    main()
