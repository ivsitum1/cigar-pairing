#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build hybrid market catalog JSON from cigars.json + raw shop scrapes.

Output: app/scripts/output/cigar_market_catalog.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent
DATA = ROOT / "src" / "data"
OUT_DIR = SCRIPTS_DIR / "output"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from shop_scrape.http import iso_utc_now  # noqa: E402


SHOP_REGION = {
    "humidor_hr": "HR",
    "havana_hr": "HR",
    "cigarworld_eu": "EU",
    "holts_us": "USA",
    "cigarsdaily_us": "USA",
}


def normalize_url(url: str | None) -> str | None:
    if not url or not isinstance(url, str):
        return None
    u = unquote(url.strip())
    # Drop fragments/query for matching product pages.
    parsed = urlparse(u)
    path = parsed.path.rstrip("/")
    if not path:
        return None
    host = (parsed.netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]
    return f"{parsed.scheme}://{host}{path}".lower()


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


def parse_format(fmt: str | None) -> dict:
    if not fmt or not isinstance(fmt, str) or fmt.strip() in ("", "—", "-"):
        return {"ringGauge": None, "lengthMm": None}
    # "50 x 152mm" or "50 x 152 mm"
    m = re.search(r"(\d+)\s*[x×]\s*(\d+)\s*mm", fmt, re.IGNORECASE)
    if m:
        return {"ringGauge": int(m.group(1)), "lengthMm": int(m.group(2))}
    return {"ringGauge": None, "lengthMm": None}


def normalize_name(s: str | None) -> str:
    if not s or not isinstance(s, str):
        return ""
    s = s.casefold()
    # Drop common shop pack / size noise before tokenizing.
    s = re.sub(r"\([^)]*\d+\s*[x×]\s*\d+[^)]*\)", " ", s)
    s = re.sub(r"/\s*\d+\*?", " ", s)
    s = re.sub(r"\b\d+\s*[x×]\s*\d+(\.\d+)?\b", " ", s)
    s = re.sub(r"\bbox\s*pressed\b", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def candidate_name_keys(brand: str, line: str, vitola_name: str) -> list[str]:
    keys: list[str] = []
    for raw in (
        f"{brand} {line} {vitola_name}",
        f"{brand} {vitola_name}",
        f"{brand} {line}",
        vitola_name,
    ):
        n = normalize_name(raw)
        if n and n not in keys:
            keys.append(n)
    return keys


def shop_name_keys(name: str | None) -> list[str]:
    """Index keys for a shop product title (full + stripped pack suffixes)."""
    if not name or not isinstance(name, str):
        return []
    keys: list[str] = []
    full = normalize_name(name)
    if full:
        keys.append(full)
    # Also index without trailing vitola-ish last token collisions handled by full string.
    return keys


def build_catalog(cigars: list[dict], raw_rows: list[dict]) -> tuple[list[dict], list[dict]]:
    offers_by_url: dict[str, list[dict]] = {}
    offers_by_name: dict[str, list[dict]] = {}
    for row in raw_rows:
        item = row["item"]
        offer = offer_from_raw(row)
        nurl = normalize_url(item.get("url"))
        if nurl:
            offers_by_url.setdefault(nurl, []).append(offer)
        for nname in shop_name_keys(item.get("name") if isinstance(item.get("name"), str) else ""):
            offers_by_name.setdefault(nname, []).append(offer)

    matched_urls: set[str] = set()
    matched_offer_ids: set[str] = set()
    catalog: list[dict] = []

    def offer_id(o: dict) -> str:
        return f"{o.get('sourceShopId')}|{normalize_url(o.get('url')) or o.get('name')}"

    for c in cigars:
        brand = c.get("brand") if isinstance(c.get("brand"), str) else ""
        line = c.get("line") if isinstance(c.get("line"), str) else ""
        vitola_entries = []
        for v in c.get("vitolas") or []:
            if not isinstance(v, dict):
                continue
            nurl = normalize_url(v.get("url"))
            offers: list[dict] = []
            seen_local: set[str] = set()

            def add_offers(cands: list[dict]) -> None:
                for o in cands:
                    oid = offer_id(o)
                    if oid in seen_local:
                        continue
                    seen_local.add(oid)
                    offers.append(o)
                    matched_offer_ids.add(oid)
                    ou = normalize_url(o.get("url"))
                    if ou:
                        matched_urls.add(ou)

            if nurl:
                add_offers(offers_by_url.get(nurl, []))
            # Secondary: exact normalized name keys.
            for key in candidate_name_keys(brand, line, v.get("name") if isinstance(v.get("name"), str) else ""):
                add_offers(offers_by_name.get(key, []))

            source_ids = sorted({o["sourceShopId"] for o in offers if o.get("sourceShopId")})
            fmt = v.get("format")
            parsed = parse_format(fmt if isinstance(fmt, str) else None)
            for o in offers:
                d = o.get("details") or {}
                if parsed["ringGauge"] is None and isinstance(d.get("ringGauge"), int):
                    parsed["ringGauge"] = d["ringGauge"]
                if parsed["lengthMm"] is None and isinstance(d.get("lengthCm"), (int, float)):
                    parsed["lengthMm"] = int(round(float(d["lengthCm"]) * 10))

            vitola_entries.append(
                {
                    "name": v.get("name"),
                    "format": fmt,
                    "parsedSize": parsed,
                    "smokeTimeMin": v.get("smokeTimeMin"),
                    "priceEUR": v.get("priceEUR"),
                    "url": v.get("url"),
                    "offers": offers,
                    "isDuplicateAcrossSources": len(source_ids) >= 2,
                    "duplicateSources": source_ids if len(source_ids) >= 2 else [],
                }
            )

        entry_offers: list[dict] = []
        entry_nurl = normalize_url(c.get("priceUrl"))
        if entry_nurl and entry_nurl not in matched_urls and entry_nurl in offers_by_url:
            for o in offers_by_url[entry_nurl]:
                oid = offer_id(o)
                if oid in matched_offer_ids:
                    continue
                entry_offers.append(o)
                matched_offer_ids.add(oid)
            matched_urls.add(entry_nurl)

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

    unmapped: list[dict] = []
    for row in raw_rows:
        offer = offer_from_raw(row)
        oid = f"{offer.get('sourceShopId')}|{normalize_url(offer.get('url')) or offer.get('name')}"
        if oid in matched_offer_ids:
            continue
        unmapped.append(
            {
                "sourceShopId": row["sourceShopId"],
                "region": row["region"],
                "name": offer.get("name"),
                "url": offer.get("url"),
                "amount": offer.get("amount"),
                "currency": offer.get("currency"),
                "inStock": offer.get("inStock"),
                "details": offer.get("details"),
                "categories": row["item"].get("categories") or [],
                "attributes": row["item"].get("attributes") or {},
                "scrapedAt": row.get("scrapedAt"),
            }
        )

    unmapped.sort(key=lambda x: (x.get("sourceShopId") or "", x.get("url") or "", x.get("name") or ""))
    catalog.sort(key=lambda x: (x.get("brand") or "", x.get("line") or "", x.get("id") or ""))
    return catalog, unmapped


def group_unmapped_cross_shop(unmapped: list[dict]) -> list[dict]:
    """Same normalized product name appearing in 2+ shops (not in cigars.json)."""
    by_name: dict[str, list[dict]] = {}
    for u in unmapped:
        key = normalize_name(u.get("name") if isinstance(u.get("name"), str) else "")
        if not key:
            continue
        by_name.setdefault(key, []).append(u)
    groups: list[dict] = []
    for key, items in by_name.items():
        shops = sorted({i.get("sourceShopId") for i in items if i.get("sourceShopId")})
        if len(shops) < 2:
            continue
        groups.append(
            {
                "normalizedName": key,
                "displayName": items[0].get("name"),
                "shops": shops,
                "itemCount": len(items),
                "items": [
                    {
                        "sourceShopId": i.get("sourceShopId"),
                        "region": i.get("region"),
                        "name": i.get("name"),
                        "url": i.get("url"),
                        "amount": i.get("amount"),
                        "currency": i.get("currency"),
                    }
                    for i in items
                ],
            }
        )
    groups.sort(key=lambda g: (-g["itemCount"], g["normalizedName"]))
    return groups


def summarize(catalog: list[dict], unmapped: list[dict], unmapped_dupes: list[dict]) -> dict:
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
        r = u.get("region") or "?"
        by_region[r] = by_region.get(r, 0) + 1
    return {
        "catalogLines": len(catalog),
        "catalogVitolas": vitolas,
        "vitolasWithOffers": with_offers,
        "duplicateVitolas": duplicates,
        "unmappedShopItems": len(unmapped),
        "unmappedByRegion": by_region,
        "unmappedCrossShopDuplicateGroups": len(unmapped_dupes),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build hybrid cigar market catalog JSON")
    p.add_argument("--cigars", default=str(DATA / "cigars.json"))
    p.add_argument("--raw-dir", default=str(OUT_DIR))
    p.add_argument("--out", default=str(OUT_DIR / "cigar_market_catalog.json"))
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cigars = json.loads(Path(args.cigars).read_text(encoding="utf-8"))
    raw_rows = load_raw_shops(Path(args.raw_dir))
    catalog, unmapped = build_catalog(cigars, raw_rows)
    unmapped_dupes = group_unmapped_cross_shop(unmapped)
    summary = summarize(catalog, unmapped, unmapped_dupes)
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


if __name__ == "__main__":
    main()
