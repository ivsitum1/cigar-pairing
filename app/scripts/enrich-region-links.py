#!/usr/bin/env python3
"""Phase A: enrich existing cigars.json with real per-region shop links + prices.

Source: app/scripts/output/cigar_unified_catalog.json (unified scrape of all 5
shops; see docs/superpowers/specs/2026-07-21-all-shops-catalog-scrape.md).

For every existing cigar we attach `regionLinks` = { HR|EU|USA: {shop, url,
priceEUR, priceApprox} } built from the unified catalog's real product offers,
and extend `markets` to the regions where a real offer exists. Embargo rule is
enforced: Cuban-origin cigars never get USA (and any pre-existing USA tag on a
Cuban cigar is removed).

HR data stays the source of truth — HR priceUrl/vitolas are untouched; regionLinks
only *adds* EU/USA (and an explicit HR product link mirror).
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
CIGARS = DATA / "cigars.json"
UNIFIED = HERE / "output" / "cigar_unified_catalog.json"

USD_TO_EUR = 0.92  # pinned approx rate; USD offers become priceApprox
REGIONS = ("HR", "EU", "USA")
SHOP_LABEL = {
    "humidor_hr": "The Humidor",
    "havana_hr": "Havana Cigar Shop",
    "cigarworld_eu": "CigarWorld",
    "holts_us": "Holt's",
    "cigarsdaily_us": "Cigars Daily",
}


def is_cuban(country: str) -> bool:
    return "kub" in (country or "").lower() or "cuba" in (country or "").lower()


def to_eur(amount, currency):
    if amount is None:
        return None, False
    if currency == "USD":
        return round(amount * USD_TO_EUR, 2), True
    return round(float(amount), 2), False


def best_offer(offers):
    """Pick the most representative single-cigar offer: in stock first, then
    lowest sane price."""
    def key(o):
        pkg = (o.get("packaging") or {}).get("type") or ""
        single = 0 if pkg in ("single", "single_equiv") else 1
        return (0 if o.get("inStock") else 1, single, o.get("amount") or 9e9)
    return sorted(offers, key=key)[0] if offers else None


def region_links_from(unified_rec, cuban):
    links = {}
    by_region = {}
    for o in unified_rec.get("offers") or []:
        by_region.setdefault(o.get("region"), []).append(o)
    for region in REGIONS:
        if region == "USA" and cuban:
            continue  # embargo
        offers = by_region.get(region)
        if not offers:
            continue
        o = best_offer(offers)
        if not o or not o.get("url"):
            continue
        price, approx = to_eur(o.get("amount"), o.get("currency"))
        entry = {"shop": SHOP_LABEL.get(o.get("sourceShopId"), o.get("sourceShopId")), "url": o["url"]}
        if price is not None:
            entry["priceEUR"] = price
            if approx:
                entry["priceApprox"] = True
        links[region] = entry
    return links


def main():
    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    unified = json.loads(UNIFIED.read_text(encoding="utf-8"))
    by_catalog = {}
    for rec in unified["cigars"]:
        cid = rec.get("catalogId")
        if cid:
            by_catalog.setdefault(cid, []).append(rec)

    stats = {"enriched": 0, "eu_added": 0, "usa_added": 0, "embargo_fixed": 0, "no_match": 0}
    for c in cigars:
        cuban = is_cuban(c.get("country"))
        # embargo cleanup regardless of match
        if cuban and "USA" in c.get("markets", []):
            c["markets"] = [m for m in c["markets"] if m != "USA"]
            stats["embargo_fixed"] += 1
        recs = by_catalog.get(c["id"])
        if not recs:
            stats["no_match"] += 1
            continue
        # merge offers from all unified records mapped to this catalog id
        merged = {"offers": []}
        for r in recs:
            merged["offers"].extend(r.get("offers") or [])
        links = region_links_from(merged, cuban)
        if not links:
            continue
        c["regionLinks"] = links
        markets = set(c.get("markets", []))
        markets.add("WW")
        for region in links:
            if region not in markets:
                markets.add(region)
                if region == "EU":
                    stats["eu_added"] += 1
                if region == "USA":
                    stats["usa_added"] += 1
        # embargo guard again after union
        if cuban:
            markets.discard("USA")
        c["markets"] = [m for m in ["HR", "EU", "USA", "WW"] if m in markets]
        stats["enriched"] += 1

    CIGARS.write_text(json.dumps(cigars, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
