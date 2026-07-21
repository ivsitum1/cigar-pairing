#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build hybrid market catalog JSON from cigars.json + raw shop scrapes.

Uses the project's established cigar dedupe/match process (cigar_shop_match /
sync-hr-shops / dedupe-data): brand aliases, LINE_RULES, fuzzy line match,
vitola name + ring±8mm, uniqueVitolas, merge_duplicate_cigar_lines, and
cross-shop merge_shop_rows keys.

Output: app/scripts/output/cigar_market_catalog.json
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


SHOP_REGION = {
    "humidor_hr": "HR",
    "havana_hr": "HR",
    "cigarworld_eu": "EU",
    "holts_us": "USA",
    "cigarsdaily_us": "USA",
}


def load_raw_shops(out_dir: Path) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(out_dir.glob("cigar_shop_*_raw.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        shop = data.get("shop") or {}
        shop_id = shop.get("id") or path.stem
        region = shop.get("region") or SHOP_REGION.get(shop_id)
        for item in data.get("items") or []:
            if not isinstance(item, dict):
                continue
            rows.append(
                {
                    "sourceShopId": shop_id,
                    "region": region,
                    "scrapedAt": data.get("scrapedAt"),
                    "item": item,
                }
            )
    return rows


def offer_from_raw(row: dict) -> dict:
    item = row["item"]
    price = item.get("price") if isinstance(item.get("price"), dict) else {}
    avail = item.get("availability") if isinstance(item.get("availability"), dict) else {}
    details = item.get("details") if isinstance(item.get("details"), dict) else {}
    return {
        "sourceShopId": row["sourceShopId"],
        "region": row["region"],
        "name": item.get("name"),
        "url": item.get("url"),
        "amount": price.get("amount"),
        "currency": price.get("currency"),
        "inStock": avail.get("inStock"),
        "details": details or None,
        "scrapedAt": row.get("scrapedAt"),
    }


def offer_id(o: dict) -> str:
    return f"{o.get('sourceShopId')}|{norm_product_url(o.get('url')) or norm(str(o.get('name') or ''))}"


def attach_offer(bucket: list[dict], seen: set[str], offer: dict) -> None:
    oid = offer_id(offer)
    if oid in seen:
        return
    seen.add(oid)
    bucket.append(offer)


def build_catalog(cigars: list[dict], raw_rows: list[dict]) -> tuple[list[dict], list[dict], dict]:
    # Resolve same line under two names before attaching shop offers.
    cigars, lines_merged = merge_duplicate_cigar_lines(cigars)
    detectors = build_brand_detectors(cigars)

    # Per vitola identity: cigarId|vitolaName
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
            # Matched line but not a specific vitola — keep as entry-level offer.
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
        for v in unique_vitolas(c):
            vkey = f"{c['id']}|{vitola_name_key(str(v.get('name') or ''), str(c.get('brand') or ''))}"
            offers = offers_by_vitola.get(vkey, [])
            source_ids = sorted({o["sourceShopId"] for o in offers if o.get("sourceShopId")})
            ring, mm = parse_format_size(v.get("format") if isinstance(v.get("format"), str) else None)
            parsed = {"ringGauge": ring, "lengthMm": mm}
            for o in offers:
                d = o.get("details") or {}
                if parsed["ringGauge"] is None and isinstance(d.get("ringGauge"), int):
                    parsed["ringGauge"] = d["ringGauge"]
                if parsed["lengthMm"] is None and isinstance(d.get("lengthCm"), (int, float)):
                    parsed["lengthMm"] = int(round(float(d["lengthCm"]) * 10))

            vitola_entries.append(
                {
                    "name": v.get("name"),
                    "format": v.get("format"),
                    "parsedSize": parsed,
                    "smokeTimeMin": v.get("smokeTimeMin"),
                    "priceEUR": v.get("priceEUR"),
                    "url": v.get("url"),
                    "offers": offers,
                    "isDuplicateAcrossSources": len(source_ids) >= 2,
                    "duplicateSources": source_ids if len(source_ids) >= 2 else [],
                }
            )

        entry_offers = entry_offers_by_cigar.get(c["id"], [])
        leaf_details = None
        for ve in vitola_entries:
            for o in ve.get("offers") or []:
                if o.get("details"):
                    leaf_details = o["details"]
                    break
            if leaf_details:
                break

        catalog.append(
            {
                "id": c.get("id"),
                "brand": c.get("brand"),
                "line": c.get("line"),
                "defaultVitola": c.get("vitola"),
                "format": c.get("format"),
                "country": c.get("country"),
                "wrapper": c.get("wrapper"),
                "binder": (leaf_details or {}).get("binder") if leaf_details else None,
                "filler": (leaf_details or {}).get("filler") if leaf_details else None,
                "origin": (leaf_details or {}).get("origin") if leaf_details else None,
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

    # Unmapped: collapse same cigar under two shop names via merge_shop_rows key.
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
        # Prefer Humidor / first priced as display row (same preference as sync-hr-shops).
        preferred = next((o for o in offers if o.get("sourceShopId") == "humidor_hr" and o.get("amount")), None)
        if not preferred:
            preferred = next((o for o in offers if o.get("amount")), None)
        if not preferred:
            preferred = offers[0]
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
                "details": preferred.get("details"),
                "sourceShopId": preferred.get("sourceShopId"),
                "region": preferred.get("region"),
                "offers": [{k: v for k, v in o.items()} for o in offers],
                "isDuplicateAcrossSources": len(shops) >= 2,
                "duplicateSources": shops if len(shops) >= 2 else [],
                "scrapedAt": preferred.get("scrapedAt"),
            }
        )

    unmapped.sort(key=lambda x: (x.get("brand") or "", x.get("name") or "", x.get("dedupeKey") or ""))
    catalog.sort(key=lambda x: (x.get("brand") or "", x.get("line") or "", x.get("id") or ""))
    meta = {"mergedCatalogLines": lines_merged}
    return catalog, unmapped, meta


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


def summarize(catalog: list[dict], unmapped: list[dict], meta: dict) -> dict:
    vitolas = 0
    with_offers = 0
    duplicates = 0
    for c in catalog:
        for v in c.get("vitolas") or []:
            vitolas += 1
            if v.get("offers"):
                with_offers += 1
            if v.get("isDuplicateAcrossSources"):
                duplicates += 1
    by_region: dict[str, int] = {}
    for u in unmapped:
        for o in u.get("offers") or [u]:
            r = o.get("region") or "?"
            by_region[r] = by_region.get(r, 0) + 1
    return {
        "catalogLines": len(catalog),
        "catalogVitolas": vitolas,
        "vitolasWithOffers": with_offers,
        "duplicateVitolas": duplicates,
        "unmappedShopItems": len(unmapped),
        "unmappedOfferRows": sum(len(u.get("offers") or []) for u in unmapped),
        "unmappedByRegion": by_region,
        "unmappedCrossShopDuplicateGroups": sum(1 for u in unmapped if u.get("isDuplicateAcrossSources")),
        "mergedCatalogLines": meta.get("mergedCatalogLines", 0),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build hybrid cigar market catalog JSON")
    p.add_argument("--cigars", default=str(DATA / "cigars.json"))
    p.add_argument("--raw-dir", default=str(OUT_DIR))
    p.add_argument("--out", default=str(OUT_DIR / "cigar_market_catalog.json"))
    p.add_argument(
        "--write-merged-cigars",
        action="store_true",
        help="Also write merged duplicate lines back to cigars.json (dedupe-data merge)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cigars_path = Path(args.cigars)
    cigars = json.loads(cigars_path.read_text(encoding="utf-8"))
    raw_rows = load_raw_shops(Path(args.raw_dir))
    catalog, unmapped, meta = build_catalog(cigars, raw_rows)
    unmapped_dupes = group_unmapped_cross_shop(unmapped)
    summary = summarize(catalog, unmapped, meta)
    out = {
        "generatedAt": iso_utc_now(),
        "summary": summary,
        "catalog": catalog,
        "unmappedShopItems": unmapped,
        "unmappedCrossShopDuplicates": unmapped_dupes,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    print(f"wrote {out_path}", flush=True)

    if args.write_merged_cigars:
        merged, n = merge_duplicate_cigar_lines(cigars)
        if n:
            # Preserve existing cigars.json indent (2) + trailing newline.
            cigars_path.write_text(
                json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(f"cigars.json: merged {n} duplicate lines -> {len(merged)} entries", flush=True)


if __name__ == "__main__":
    main()
