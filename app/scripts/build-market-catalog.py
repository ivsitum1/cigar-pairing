#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build unified cigar catalog JSON from cigars.json + raw shop scrapes.

One file with everything needed for pairing + shopping:
- shops[] metadata
- catalog[] (pairing lines + shop offers)
- products[] (flat unique brand/line/vitola rows with merged details + all offers)
- unmappedShopItems[] / unmappedCrossShopDuplicates[]

Uses cigar_shop_match (sync-hr-shops + dedupe-data process).

Outputs (default):
  app/scripts/output/cigar_unified_catalog.json
  app/scripts/output/cigar_market_catalog.json  (same payload; legacy name)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent
DATA = ROOT / "src" / "data"
OUT_DIR = SCRIPTS_DIR / "output"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from cigar_shop_match import (  # noqa: E402
    build_brand_detectors,
    detect_brand,
    line_name_from_product,
    merge_duplicate_cigar_lines,
    norm,
    norm_product_url,
    parse_format_size,
    resolve_shop_product,
    shop_dedupe_key,
    unique_vitolas,
    vitola_from_product,
    vitola_name_key,
)
from shop_scrape.http import iso_utc_now  # noqa: E402


SCHEMA_VERSION = 3

REGION_FILTERS = ("HR", "EU", "USA")

SHOP_REGION = {
    "humidor_hr": "HR",
    "havana_hr": "HR",
    "cigarworld_eu": "EU",
    "holts_us": "USA",
    "cigarsdaily_us": "USA",
}

SHOP_LABEL = {
    "humidor_hr": "Humidor",
    "havana_hr": "Havana Cigar Shop",
    "cigarworld_eu": "Cigarworld",
    "holts_us": "Holt's",
    "cigarsdaily_us": "Cigars Daily",
}

PROVENANCE = {
    "policy": (
        "Shop fields (price, product URL, wrapper/binder/filler when present) come from "
        "live product-page scrapes. They are not invented. Pairing copy in cigars.json "
        "(notes, flavorTags, body) is curated for the app and may be estimated when "
        "profileEstimated is true."
    ),
    "verifiedMeans": (
        "sources[].verified === true only when the row points at a real product URL "
        "from a shop scrape (or a catalog priceUrl that is itself a shop product URL)."
    ),
    "howToUse": (
        "Prefer sources where verified===true and type==='shop-scrape'. "
        "Open sources[].url / sourceUrls[] to check the original product page."
    ),
}

DETAIL_FIELDS = (
    "wrapper",
    "binder",
    "filler",
    "origin",
    "strength",
    "burnTimeMin",
    "size",
    "ringGauge",
    "lengthIn",
    "lengthCm",
    "diameterCm",
    "boxPressed",
    "flavoured",
    "tabacalera",
    "brandLabel",
)


def load_raw_shops(out_dir: Path) -> tuple[list[dict], list[dict]]:
    """Return (flat rows, shop metadata list)."""
    rows: list[dict] = []
    shops: list[dict] = []
    for path in sorted(out_dir.glob("cigar_shop_*_raw.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        shop = data.get("shop") or {}
        shop_id = shop.get("id") or path.stem
        region = shop.get("region") or SHOP_REGION.get(shop_id)
        items = [i for i in (data.get("items") or []) if isinstance(i, dict)]
        wbf = 0
        priced = 0
        for item in items:
            d = item.get("details") if isinstance(item.get("details"), dict) else {}
            if d.get("wrapper") and d.get("binder") and d.get("filler"):
                wbf += 1
            price = item.get("price") if isinstance(item.get("price"), dict) else {}
            if price.get("amount") is not None:
                priced += 1
            rows.append(
                {
                    "sourceShopId": shop_id,
                    "region": region,
                    "scrapedAt": data.get("scrapedAt"),
                    "item": item,
                }
            )
        shops.append(
            {
                "id": shop_id,
                "name": shop.get("name"),
                "region": region,
                "baseUrl": shop.get("baseUrl"),
                "scrapedAt": data.get("scrapedAt"),
                "source": data.get("source"),
                "currency": data.get("currency"),
                "itemCount": len(items),
                "withFullWBF": wbf,
                "withPrice": priced,
            }
        )
    return rows, shops


def offer_from_raw(row: dict) -> dict:
    item = row["item"]
    price = item.get("price") if isinstance(item.get("price"), dict) else {}
    avail = item.get("availability") if isinstance(item.get("availability"), dict) else {}
    details = item.get("details") if isinstance(item.get("details"), dict) else {}
    packaging = item.get("packaging") if isinstance(item.get("packaging"), dict) else {}
    attrs = item.get("attributes") if isinstance(item.get("attributes"), dict) else {}
    details_source = item.get("detailsSource") if isinstance(item.get("detailsSource"), dict) else None
    return {
        "sourceShopId": row["sourceShopId"],
        "region": row["region"],
        "name": item.get("name"),
        "url": item.get("url"),
        "amount": price.get("amount"),
        "currency": price.get("currency"),
        "inStock": avail.get("inStock"),
        "onSale": avail.get("onSale"),
        "packaging": packaging or None,
        "attributes": attrs or None,
        "categories": [
            {"name": c.get("name"), "slug": c.get("slug")}
            for c in (item.get("categories") or [])
            if isinstance(c, dict)
        ],
        "image": next(
            (
                im.get("src")
                for im in (item.get("images") or [])
                if isinstance(im, dict) and isinstance(im.get("src"), str) and im.get("src")
            ),
            None,
        ),
        "details": details or None,
        "detailsSource": details_source,
        "scrapedAt": row.get("scrapedAt"),
    }


def _http_url(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    url = value.strip()
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return None


def _detail_provides(details: dict | None) -> list[str]:
    if not isinstance(details, dict):
        return []
    return [f for f in DETAIL_FIELDS if details.get(f) is not None and details.get(f) != ""]


def build_sources(
    *,
    offers: list[dict],
    pairing: dict | None = None,
    catalog_id: str | None = None,
    in_catalog: bool = False,
) -> tuple[list[dict], list[str], bool]:
    """Build provenance sources + flat verified URLs.

    Returns (sources, sourceUrls, hasVerifiedSource).
    """
    sources: list[dict] = []
    seen: set[str] = set()

    for o in offers:
        url = _http_url(o.get("url"))
        shop_id = o.get("sourceShopId") or ""
        ds = o.get("detailsSource") if isinstance(o.get("detailsSource"), dict) else {}
        detail_url = _http_url(ds.get("url")) or url
        key = f"shop|{shop_id}|{norm_product_url(url) or norm(str(o.get('name') or ''))}"
        if key in seen:
            continue
        seen.add(key)
        provides = ["name", "price", "productUrl"]
        provides.extend(f"details.{f}" for f in _detail_provides(o.get("details") if isinstance(o.get("details"), dict) else None))
        sources.append(
            {
                "type": "shop-scrape",
                "verified": bool(url),
                "shopId": shop_id or None,
                "label": SHOP_LABEL.get(shop_id) or shop_id or None,
                "region": o.get("region"),
                "url": url,
                "detailsUrl": detail_url if detail_url != url else None,
                "extractedFrom": ds.get("extractedFrom"),
                "scrapedAt": ds.get("extractedAt") or o.get("scrapedAt"),
                "provides": provides,
                "note": "Extracted from live shop product page / store API — not invented.",
            }
        )

    if in_catalog:
        price_url = None
        if isinstance(pairing, dict):
            price_url = _http_url(pairing.get("priceUrl"))
        provides = [
            "pairing.notes",
            "pairing.flavorTags",
            "pairing.body",
            "pairing.strength",
            "pairing.smokeTimeMin",
        ]
        estimated = bool(isinstance(pairing, dict) and pairing.get("profileEstimated"))
        sources.append(
            {
                "type": "app-catalog",
                "verified": bool(price_url),
                "shopId": None,
                "label": "App catalog (cigars.json)",
                "region": None,
                "url": price_url,
                "detailsUrl": None,
                "extractedFrom": "app/src/data/cigars.json",
                "scrapedAt": None,
                "catalogId": catalog_id,
                "provides": provides,
                "profileEstimated": estimated,
                "note": (
                    "Curated pairing fields for the app. "
                    + (
                        "profileEstimated=true: strength/body/flavor may be estimated, not shop-scraped."
                        if estimated
                        else "Not a shop scrape; use shop-scrape sources for price/WBF verification."
                    )
                ),
            }
        )

    source_urls: list[str] = []
    seen_urls: set[str] = set()
    for s in sources:
        if not s.get("verified"):
            continue
        for u in (s.get("url"), s.get("detailsUrl")):
            if isinstance(u, str) and u and u not in seen_urls:
                seen_urls.add(u)
                source_urls.append(u)
    has_verified = any(bool(s.get("verified")) and s.get("type") == "shop-scrape" for s in sources) or (
        any(bool(s.get("verified")) for s in sources)
    )
    return sources, source_urls, has_verified


def offer_id(o: dict) -> str:
    return f"{o.get('sourceShopId')}|{norm_product_url(o.get('url')) or norm(str(o.get('name') or ''))}"


def attach_offer(bucket: list[dict], seen: set[str], offer: dict) -> None:
    oid = offer_id(offer)
    if oid in seen:
        return
    seen.add(oid)
    bucket.append(offer)


def merge_details(*sources: dict | None) -> dict | None:
    """Fill detail fields preferring first non-empty value across sources."""
    out: dict = {}
    for src in sources:
        if not isinstance(src, dict):
            continue
        for field in DETAIL_FIELDS:
            if out.get(field) is None and src.get(field) is not None and src.get(field) != "":
                out[field] = src[field]
    return out or None


def prefer_offer_details(offers: list[dict]) -> dict | None:
    # Prefer Humidor, then Havana, then any with full WBF, then any with details.
    def score(o: dict) -> tuple:
        d = o.get("details") if isinstance(o.get("details"), dict) else {}
        shop = o.get("sourceShopId") or ""
        shop_rank = {"humidor_hr": 3, "havana_hr": 2, "cigarworld_eu": 1}.get(shop, 0)
        wbf = 1 if d.get("wrapper") and d.get("binder") and d.get("filler") else 0
        any_d = 1 if d else 0
        return (shop_rank, wbf, any_d)

    ordered = sorted(offers, key=score, reverse=True)
    merged: dict | None = None
    for o in ordered:
        merged = merge_details(merged, o.get("details") if isinstance(o.get("details"), dict) else None)
    return merged


def prices_by_region(offers: list[dict]) -> dict[str, list[dict]]:
    by: dict[str, list[dict]] = {}
    for o in offers:
        if o.get("amount") is None:
            continue
        region = o.get("region") or "?"
        by.setdefault(region, []).append(
            {
                "sourceShopId": o.get("sourceShopId"),
                "amount": o.get("amount"),
                "currency": o.get("currency"),
                "url": o.get("url"),
                "inStock": o.get("inStock"),
            }
        )
    for region, rows in by.items():
        rows.sort(key=lambda r: (r.get("amount") is None, r.get("amount") or 0))
    return by


def build_catalog(cigars: list[dict], raw_rows: list[dict]) -> tuple[list[dict], list[dict], dict]:
    cigars, lines_merged = merge_duplicate_cigar_lines(cigars)
    detectors = build_brand_detectors(cigars)

    offers_by_vitola: dict[str, list[dict]] = {}
    seen_by_vitola: dict[str, set[str]] = {}
    entry_offers_by_cigar: dict[str, list[dict]] = {}
    seen_entry: dict[str, set[str]] = {}
    matched_offer_ids: set[str] = set()
    unmapped_raw: list[dict] = []

    for row in raw_rows:
        item = row["item"]
        offer = offer_from_raw(row)
        details = item.get("details") if isinstance(item.get("details"), dict) else None
        name = item.get("name") if isinstance(item.get("name"), str) else ""
        url = item.get("url") if isinstance(item.get("url"), str) else None

        cigar, vitola, brand = resolve_shop_product(
            cigars,
            name,
            detectors=detectors,
            details=details,
            url=url,
        )
        if cigar and vitola:
            key = f"{cigar['id']}|{vitola_name_key(str(vitola.get('name') or ''), str(cigar.get('brand') or ''))}"
            bucket = offers_by_vitola.setdefault(key, [])
            seen = seen_by_vitola.setdefault(key, set())
            attach_offer(bucket, seen, offer)
            matched_offer_ids.add(offer_id(offer))
            continue
        if cigar and not vitola:
            cid = cigar["id"]
            bucket = entry_offers_by_cigar.setdefault(cid, [])
            seen = seen_entry.setdefault(cid, set())
            attach_offer(bucket, seen, offer)
            matched_offer_ids.add(offer_id(offer))
            continue

        unmapped_raw.append({**row, "_brand": brand, "_offer": offer})

    catalog: list[dict] = []
    for c in cigars:
        vitola_entries = []
        all_line_offers: list[dict] = []
        for v in unique_vitolas(c):
            vkey = f"{c['id']}|{vitola_name_key(str(v.get('name') or ''), str(c.get('brand') or ''))}"
            offers = offers_by_vitola.get(vkey, [])
            all_line_offers.extend(offers)
            source_ids = sorted({o["sourceShopId"] for o in offers if o.get("sourceShopId")})
            ring, mm = parse_format_size(v.get("format") if isinstance(v.get("format"), str) else None)
            parsed = {"ringGauge": ring, "lengthMm": mm}
            for o in offers:
                d = o.get("details") or {}
                if parsed["ringGauge"] is None and isinstance(d.get("ringGauge"), int):
                    parsed["ringGauge"] = d["ringGauge"]
                if parsed["lengthMm"] is None and isinstance(d.get("lengthCm"), (int, float)):
                    parsed["lengthMm"] = int(round(float(d["lengthCm"]) * 10))
                if parsed["lengthMm"] is None and isinstance(d.get("lengthIn"), (int, float)):
                    parsed["lengthMm"] = int(round(float(d["lengthIn"]) * 25.4))

            leaf = prefer_offer_details(offers)
            vitola_entries.append(
                {
                    "name": v.get("name"),
                    "format": v.get("format"),
                    "parsedSize": parsed,
                    "smokeTimeMin": v.get("smokeTimeMin"),
                    "priceEUR": v.get("priceEUR"),
                    "url": v.get("url"),
                    "details": leaf,
                    "offers": offers,
                    "pricesByRegion": prices_by_region(offers),
                    "isDuplicateAcrossSources": len(source_ids) >= 2,
                    "duplicateSources": source_ids if len(source_ids) >= 2 else [],
                }
            )

        entry_offers = entry_offers_by_cigar.get(c["id"], [])
        all_line_offers.extend(entry_offers)
        leaf_details = prefer_offer_details(all_line_offers)
        catalog_wrapper = c.get("wrapper") if c.get("wrapper") not in (None, "", "—") else None
        merged_leaf = merge_details(
            {
                "wrapper": catalog_wrapper,
                "strength": c.get("strength"),
            },
            leaf_details,
        )

        catalog.append(
            {
                "id": c.get("id"),
                "brand": c.get("brand"),
                "line": c.get("line"),
                "defaultVitola": c.get("vitola"),
                "format": c.get("format"),
                "country": c.get("country"),
                "wrapper": (merged_leaf or {}).get("wrapper"),
                "binder": (merged_leaf or {}).get("binder"),
                "filler": (merged_leaf or {}).get("filler"),
                "origin": (merged_leaf or {}).get("origin") or c.get("country"),
                "details": merged_leaf,
                "strength": c.get("strength"),
                "body": c.get("body"),
                "flavorTags": c.get("flavorTags") or [],
                "smokeTimeMin": c.get("smokeTimeMin"),
                "priceEUR": c.get("priceEUR"),
                "priceApprox": c.get("priceApprox"),
                "priceUrl": c.get("priceUrl"),
                "markets": c.get("markets") or [],
                "availabilityHR": c.get("availabilityHR") or [],
                "notes": c.get("notes") or {},
                "profileEstimated": c.get("profileEstimated"),
                "lineup": c.get("lineup"),
                "entryOffers": entry_offers,
                "vitolas": vitola_entries,
                "isDuplicateAcrossSources": any(v.get("isDuplicateAcrossSources") for v in vitola_entries)
                or len({o["sourceShopId"] for o in entry_offers}) >= 2,
            }
        )

    unmapped_groups: dict[str, dict] = {}
    for row in unmapped_raw:
        offer = row["_offer"]
        oid = offer_id(offer)
        if oid in matched_offer_ids:
            continue
        name = offer.get("name") if isinstance(offer.get("name"), str) else ""
        brand = row.get("_brand") or detect_brand(name, detectors)
        if brand:
            key = shop_dedupe_key(brand, name)
            display_line = line_name_from_product(brand, name)
            display_vitola = vitola_from_product(name, brand)
        else:
            key = f"?|{norm(name)}"
            display_line = None
            display_vitola = None
            brand = None

        group = unmapped_groups.get(key)
        if not group:
            unmapped_groups[key] = {
                "dedupeKey": key,
                "brand": brand,
                "line": display_line,
                "vitola": display_vitola,
                "name": name,
                "offers": [],
                "_seen": set(),
            }
            group = unmapped_groups[key]
        attach_offer(group["offers"], group["_seen"], offer)

    unmapped: list[dict] = []
    for g in unmapped_groups.values():
        offers = g["offers"]
        shops = sorted({o.get("sourceShopId") for o in offers if o.get("sourceShopId")})
        preferred = next((o for o in offers if o.get("sourceShopId") == "humidor_hr" and o.get("amount")), None)
        if not preferred:
            preferred = next((o for o in offers if o.get("amount")), None)
        if not preferred:
            preferred = offers[0]
        details = prefer_offer_details(offers)
        unmapped.append(
            {
                "dedupeKey": g["dedupeKey"],
                "brand": g["brand"],
                "line": g["line"],
                "vitola": g["vitola"],
                "name": preferred.get("name"),
                "url": preferred.get("url"),
                "amount": preferred.get("amount"),
                "currency": preferred.get("currency"),
                "inStock": preferred.get("inStock"),
                "details": details,
                "sourceShopId": preferred.get("sourceShopId"),
                "region": preferred.get("region"),
                "offers": offers,
                "pricesByRegion": prices_by_region(offers),
                "isDuplicateAcrossSources": len(shops) >= 2,
                "duplicateSources": shops if len(shops) >= 2 else [],
                "scrapedAt": preferred.get("scrapedAt"),
            }
        )

    unmapped.sort(key=lambda x: (x.get("brand") or "", x.get("name") or "", x.get("dedupeKey") or ""))
    catalog.sort(key=lambda x: (x.get("brand") or "", x.get("line") or "", x.get("id") or ""))
    meta = {"mergedCatalogLines": lines_merged}
    return catalog, unmapped, meta


def resolve_regions(offers: list[dict], markets: list | None = None) -> list[str]:
    """Regions for HR/EU/USA filter (ALL = no region restriction)."""
    regs: set[str] = set()
    for o in offers:
        r = o.get("region")
        if r in REGION_FILTERS:
            regs.add(r)
    for m in markets or []:
        if m in REGION_FILTERS:
            regs.add(m)
    return sorted(regs)


def _with_sources(row: dict) -> dict:
    sources, source_urls, has_verified = build_sources(
        offers=row.get("offers") or [],
        pairing=row.get("pairing"),
        catalog_id=row.get("catalogId"),
        in_catalog=bool(row.get("inCatalog")),
    )
    row["sources"] = sources
    row["sourceUrls"] = source_urls
    row["hasVerifiedSource"] = has_verified
    return row


def build_products(catalog: list[dict], unmapped: list[dict]) -> list[dict]:
    """Flat unique cigar rows (catalog vitolas + unmapped shop groups)."""
    products: list[dict] = []
    for c in catalog:
        markets = c.get("markets") or []
        for v in c.get("vitolas") or []:
            offers = v.get("offers") or []
            regions = resolve_regions(offers, markets)
            pairing = {
                "strength": c.get("strength"),
                "body": c.get("body"),
                "flavorTags": c.get("flavorTags") or [],
                "smokeTimeMin": v.get("smokeTimeMin") or c.get("smokeTimeMin"),
                "notes": c.get("notes") or {},
                "profileEstimated": c.get("profileEstimated"),
                "priceEUR": v.get("priceEUR") if v.get("priceEUR") is not None else c.get("priceEUR"),
                "priceUrl": v.get("url") or c.get("priceUrl"),
                "availabilityHR": c.get("availabilityHR") or [],
            }
            products.append(
                _with_sources(
                    {
                        "kind": "catalog",
                        "id": f"{c.get('id')}::{vitola_name_key(str(v.get('name') or ''), str(c.get('brand') or ''))}",
                        "catalogId": c.get("id"),
                        "inCatalog": True,
                        "brand": c.get("brand"),
                        "line": c.get("line"),
                        "vitola": v.get("name"),
                        "name": f"{c.get('brand')} {c.get('line')} {v.get('name')}".strip(),
                        "format": v.get("format"),
                        "parsedSize": v.get("parsedSize"),
                        "country": c.get("country"),
                        "markets": markets,
                        "regions": regions,
                        "filters": {
                            "ALL": True,
                            "HR": "HR" in regions,
                            "EU": "EU" in regions,
                            "USA": "USA" in regions,
                        },
                        "pairing": pairing,
                        "details": merge_details(v.get("details"), c.get("details")),
                        "offers": offers,
                        "pricesByRegion": v.get("pricesByRegion") or prices_by_region(offers),
                        "shops": sorted({o.get("sourceShopId") for o in offers if o.get("sourceShopId")}),
                        "isDuplicateAcrossSources": bool(v.get("isDuplicateAcrossSources")),
                        "duplicateSources": v.get("duplicateSources") or [],
                    }
                )
            )
        if c.get("entryOffers"):
            offers = c["entryOffers"]
            regions = resolve_regions(offers, markets)
            shops = sorted({o.get("sourceShopId") for o in offers if o.get("sourceShopId")})
            pairing = {
                "strength": c.get("strength"),
                "body": c.get("body"),
                "flavorTags": c.get("flavorTags") or [],
                "smokeTimeMin": c.get("smokeTimeMin"),
                "notes": c.get("notes") or {},
                "profileEstimated": c.get("profileEstimated"),
                "priceEUR": c.get("priceEUR"),
                "priceUrl": c.get("priceUrl"),
                "availabilityHR": c.get("availabilityHR") or [],
            }
            products.append(
                _with_sources(
                    {
                        "kind": "catalog-entry",
                        "id": f"{c.get('id')}::entry",
                        "catalogId": c.get("id"),
                        "inCatalog": True,
                        "brand": c.get("brand"),
                        "line": c.get("line"),
                        "vitola": c.get("defaultVitola"),
                        "name": f"{c.get('brand')} {c.get('line')}".strip(),
                        "format": c.get("format"),
                        "parsedSize": None,
                        "country": c.get("country"),
                        "markets": markets,
                        "regions": regions,
                        "filters": {
                            "ALL": True,
                            "HR": "HR" in regions,
                            "EU": "EU" in regions,
                            "USA": "USA" in regions,
                        },
                        "pairing": pairing,
                        "details": c.get("details"),
                        "offers": offers,
                        "pricesByRegion": prices_by_region(offers),
                        "shops": shops,
                        "isDuplicateAcrossSources": len(shops) >= 2,
                        "duplicateSources": shops if len(shops) >= 2 else [],
                    }
                )
            )

    for u in unmapped:
        offers = u.get("offers") or []
        regions = resolve_regions(offers)
        shops = u.get("duplicateSources") or sorted(
            {o.get("sourceShopId") for o in offers if o.get("sourceShopId")}
        )
        products.append(
            _with_sources(
                {
                    "kind": "shop",
                    "id": f"shop::{u.get('dedupeKey')}",
                    "catalogId": None,
                    "inCatalog": False,
                    "brand": u.get("brand"),
                    "line": u.get("line"),
                    "vitola": u.get("vitola"),
                    "name": u.get("name"),
                    "format": None,
                    "parsedSize": None,
                    "country": (u.get("details") or {}).get("origin") if isinstance(u.get("details"), dict) else None,
                    "markets": regions,
                    "regions": regions,
                    "filters": {
                        "ALL": True,
                        "HR": "HR" in regions,
                        "EU": "EU" in regions,
                        "USA": "USA" in regions,
                    },
                    "pairing": None,
                    "details": u.get("details"),
                    "offers": offers,
                    "pricesByRegion": u.get("pricesByRegion") or prices_by_region(offers),
                    "shops": shops,
                    "isDuplicateAcrossSources": bool(u.get("isDuplicateAcrossSources")),
                    "duplicateSources": u.get("duplicateSources") or [],
                    "dedupeKey": u.get("dedupeKey"),
                }
            )
        )

    products.sort(
        key=lambda p: (
            p.get("brand") or "",
            p.get("line") or "",
            p.get("vitola") or "",
            p.get("name") or "",
            p.get("id") or "",
        )
    )
    return products


def counts_by_filter(products: list[dict]) -> dict[str, int]:
    return {
        "ALL": len(products),
        "HR": sum(1 for p in products if (p.get("filters") or {}).get("HR")),
        "EU": sum(1 for p in products if (p.get("filters") or {}).get("EU")),
        "USA": sum(1 for p in products if (p.get("filters") or {}).get("USA")),
    }


def group_unmapped_cross_shop(unmapped: list[dict]) -> list[dict]:
    return [
        {
            "dedupeKey": u.get("dedupeKey"),
            "brand": u.get("brand"),
            "line": u.get("line"),
            "vitola": u.get("vitola"),
            "displayName": u.get("name"),
            "shops": u.get("duplicateSources") or [],
            "itemCount": len(u.get("offers") or []),
            "items": [
                {
                    "sourceShopId": o.get("sourceShopId"),
                    "region": o.get("region"),
                    "name": o.get("name"),
                    "url": o.get("url"),
                    "amount": o.get("amount"),
                    "currency": o.get("currency"),
                }
                for o in (u.get("offers") or [])
            ],
        }
        for u in unmapped
        if u.get("isDuplicateAcrossSources")
    ]


def summarize(catalog: list[dict], unmapped: list[dict], products: list[dict], shops: list[dict], meta: dict) -> dict:
    vitolas = 0
    with_offers = 0
    duplicates = 0
    with_wbf = 0
    for c in catalog:
        for v in c.get("vitolas") or []:
            vitolas += 1
            if v.get("offers"):
                with_offers += 1
            if v.get("isDuplicateAcrossSources"):
                duplicates += 1
            d = v.get("details") or {}
            if d.get("wrapper") and d.get("binder") and d.get("filler"):
                with_wbf += 1
    by_region: dict[str, int] = {}
    for u in unmapped:
        for o in u.get("offers") or [u]:
            r = o.get("region") or "?"
            by_region[r] = by_region.get(r, 0) + 1
    return {
        "shops": len(shops),
        "shopItems": sum(s.get("itemCount") or 0 for s in shops),
        "catalogLines": len(catalog),
        "catalogVitolas": vitolas,
        "vitolasWithOffers": with_offers,
        "vitolasWithFullWBF": with_wbf,
        "duplicateVitolas": duplicates,
        "products": len(products),
        "productsCatalog": sum(1 for p in products if p.get("kind") in ("catalog", "catalog-entry")),
        "productsShopOnly": sum(1 for p in products if p.get("kind") == "shop"),
        "unmappedShopItems": len(unmapped),
        "unmappedOfferRows": sum(len(u.get("offers") or []) for u in unmapped),
        "unmappedByRegion": by_region,
        "unmappedCrossShopDuplicateGroups": sum(1 for u in unmapped if u.get("isDuplicateAcrossSources")),
        "mergedCatalogLines": meta.get("mergedCatalogLines", 0),
        "countsByFilter": counts_by_filter(products),
        "withVerifiedSource": sum(1 for p in products if p.get("hasVerifiedSource")),
        "withoutVerifiedSource": sum(1 for p in products if not p.get("hasVerifiedSource")),
        "withShopScrapeUrl": sum(
            1
            for p in products
            if any(s.get("type") == "shop-scrape" and s.get("verified") for s in (p.get("sources") or []))
        ),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Build unified cigar JSON (all cigars + HR/EU/USA/ALL filters)"
    )
    p.add_argument("--cigars", default=str(DATA / "cigars.json"))
    p.add_argument("--raw-dir", default=str(OUT_DIR))
    p.add_argument("--out", default=str(OUT_DIR / "cigar_unified_catalog.json"))
    p.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON (larger). Default is compact.",
    )
    p.add_argument(
        "--write-merged-cigars",
        action="store_true",
        help="Also write merged duplicate lines back to cigars.json",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cigars_path = Path(args.cigars)
    cigars = json.loads(cigars_path.read_text(encoding="utf-8"))
    raw_rows, shops = load_raw_shops(Path(args.raw_dir))
    catalog, unmapped, meta = build_catalog(cigars, raw_rows)
    products = build_products(catalog, unmapped)
    unmapped_dupes = group_unmapped_cross_shop(unmapped)
    summary = summarize(catalog, unmapped, products, shops, meta)
    filter_counts = summary["countsByFilter"]

    out = {
        "generatedAt": iso_utc_now(),
        "schemaVersion": SCHEMA_VERSION,
        "provenance": PROVENANCE,
        "filters": {
            "values": ["ALL", "HR", "EU", "USA"],
            "description": {
                "ALL": "Sve cigare (katalog + svi shopovi)",
                "HR": "Dostupno u HR shopovima (Humidor, Havana) ili markets sadrži HR",
                "EU": "Dostupno u EU (Cigarworld) ili markets sadrži EU",
                "USA": "Dostupno u USA (Holt's, Cigars Daily) ili markets sadrži USA",
            },
            "howToFilter": "Uzmi cigars[] gdje filters[filter] === true. Za ALL uvijek true.",
            "counts": filter_counts,
        },
        "summary": {
            "totalCigars": filter_counts["ALL"],
            "inAppCatalog": summary["productsCatalog"],
            "shopOnly": summary["productsShopOnly"],
            "catalogLines": summary["catalogLines"],
            "catalogVitolas": summary["catalogVitolas"],
            "vitolasWithOffers": summary["vitolasWithOffers"],
            "vitolasWithFullWBF": summary["vitolasWithFullWBF"],
            "duplicateVitolas": summary["duplicateVitolas"],
            "crossShopUnmappedGroups": summary["unmappedCrossShopDuplicateGroups"],
            "shops": summary["shops"],
            "shopItems": summary["shopItems"],
            "countsByFilter": filter_counts,
            "withVerifiedSource": summary["withVerifiedSource"],
            "withoutVerifiedSource": summary["withoutVerifiedSource"],
            "withShopScrapeUrl": summary["withShopScrapeUrl"],
        },
        "shops": shops,
        "cigars": products,
        "unmappedCrossShopDuplicates": unmapped_dupes,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if args.pretty:
        payload = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
    else:
        payload = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    out_path.write_text(payload, encoding="utf-8")
    print(json.dumps(out["summary"], ensure_ascii=False, indent=2), flush=True)
    print(json.dumps(out["filters"]["counts"], ensure_ascii=False, indent=2), flush=True)
    print(f"wrote {out_path} ({out_path.stat().st_size // 1024} KiB)", flush=True)

    if args.write_merged_cigars:
        merged, n = merge_duplicate_cigar_lines(cigars)
        if n:
            cigars_path.write_text(
                json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(f"cigars.json: merged {n} duplicate lines -> {len(merged)} entries", flush=True)


if __name__ == "__main__":
    main()
