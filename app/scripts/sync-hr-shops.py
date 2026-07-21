# -*- coding: utf-8 -*-
"""Sinkronizira vitole + cijene iz Havana (WC API) i Humidor (crawl) u cigars.json.

Popunjava nedostajuće vitole (npr. Cusano 8 formata, Joya linije, AF Hemingway varijante).

Pokretanje:
  python scripts/sync-hr-shops.py
  python scripts/export-indexes.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from cigar_shop_match import (
    BRAND_ALIASES,
    build_brand_detectors,
    detect_brand,
    detect_line_id,
    line_name_from_product,
    norm,
    parse_humidor_dims,
    parse_pack_suffix,
    slugify,
    vitola_from_product,
)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data"
CIGARS_JSON = DATA / "cigars.json"

USER_AGENT = "Mozilla/5.0 (compatible; CigarRumSync/1.0)"


def parse_price(text: str) -> float | None:
    if not text:
        return None
    m = re.search(r"([\d]+)[,\.]([\d]{2})", text.replace(" ", ""))
    return float(f"{m.group(1)}.{m.group(2)}") if m else None


def wc_price(prices: dict) -> float:
    minor = int(prices.get("currency_minor_unit", 2))
    return int(prices.get("price") or 0) / (10**minor)


def smoke_minutes(length_mm: int | None, ring: int | None) -> int:
    if not length_mm or not ring:
        return 45
    length_in = length_mm / 25.4
    est = length_in * 10 * (0.60 + ring / 140)
    return int(round(est / 5) * 5)


def fetch_havana_catalog() -> list[dict]:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    items: list[dict] = []
    page = 1
    while page <= 50:
        url = (
            "https://havana-cigar-shop.com/wp-json/wc/store/products"
            f"?category=cigare&per_page=100&page={page}"
        )
        r = session.get(url, timeout=30)
        if r.status_code != 200:
            break
        batch = r.json()
        if not batch:
            break
        for p in batch:
            permalink = p.get("permalink", "")
            if "/en/" in permalink:
                continue
            name, _ = parse_pack_suffix(p.get("name", ""))
            items.append({
                "source": "havana",
                "name": name,
                "price": wc_price(p.get("prices") or {}),
                "url": permalink,
            })
        if page >= int(r.headers.get("X-WP-TotalPages", 1)):
            break
        page += 1
        time.sleep(0.2)
    return items


def fetch_humidor_catalog() -> list[dict]:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    items: list[dict] = []
    base = "https://humidor.hr/hr/kategorija-proizvoda/cigare/"
    page = 1
    while page <= 30:
        url = base if page == 1 else f"{base}page/{page}/"
        r = session.get(url, timeout=25)
        if r.status_code == 404:
            break
        soup = BeautifulSoup(r.text, "lxml")
        products = soup.select("li.product")
        if not products:
            break
        for li in products:
            title = li.select_one(".woocommerce-loop-product__title")
            price_el = li.select_one(".price")
            link = li.select_one("a.woocommerce-LoopProduct-link")
            if not title or not link:
                continue
            items.append({
                "source": "humidor",
                "name": title.get_text(strip=True),
                "price": parse_price(price_el.get_text() if price_el else ""),
                "url": link["href"],
            })
        page += 1
        time.sleep(0.25)
    return items


def merge_shop_rows(rows: list[dict], detectors: list[tuple[str, str]]) -> list[dict]:
    """Dedupe po brand+vitola; prefer humidor cijenu ako postoji."""
    by_key: dict[str, dict] = {}
    for row in rows:
        brand = detect_brand(row["name"], detectors)
        if not brand:
            continue
        vitola = vitola_from_product(row["name"], brand)
        key = f"{norm(brand)}|{norm(vitola)}|{norm(line_name_from_product(brand, row['name']))}"
        existing = by_key.get(key)
        if not existing:
            by_key[key] = {**row, "brand": brand, "vitola": vitola}
            continue
        if row["source"] == "humidor" and row.get("price"):
            existing["price"] = row["price"]
            existing["url"] = row["url"]
            existing["source"] = "humidor"
        elif not existing.get("price") and row.get("price"):
            existing["price"] = row["price"]
            if not existing.get("url"):
                existing["url"] = row["url"]
    return list(by_key.values())


def make_vitola_entry(row: dict) -> dict:
    base_name = row["name"]
    _, mm, ring = parse_humidor_dims(base_name)
    if mm is None:
        _, pack = parse_pack_suffix(base_name)
        mm, ring = None, None
    fmt = f"{ring} x {mm}mm" if ring and mm else row.get("format", "")
    return {
        "name": row["vitola"],
        "format": fmt or "—",
        "smokeTimeMin": smoke_minutes(mm, ring),
        "priceEUR": row.get("price"),
        "url": row.get("url"),
    }


def find_or_create_cigar(cigars: list[dict], brand: str, product_name: str) -> dict:
    cid = detect_line_id(brand, product_name)
    if cid:
        for c in cigars:
            if c["id"] == cid:
                return c
    line = line_name_from_product(brand, product_name)
    # match postojeći po brand+line
    for c in cigars:
        if c["brand"] == brand and norm(c["line"]) == norm(line):
            return c
    # fuzzy line
    for c in cigars:
        if c["brand"] != brand:
            continue
        if norm(line) in norm(c["line"]) or norm(c["line"]) in norm(line):
            return c
    # novi entry
    new_id = f"cig-{slugify(brand)}-{slugify(line)}"
    if any(c["id"] == new_id for c in cigars):
        new_id = f"{new_id}-{len(cigars)}"
    entry = {
        "id": new_id,
        "brand": brand,
        "line": line,
        "vitola": vitola_from_product(product_name, brand),
        "format": "—",
        "country": "Dominikana" if brand in ("Cusano", "Arturo Fuente") else "Nikaragva",
        "wrapper": "—",
        "strength": 3,
        "body": 3,
        "flavorTags": [],
        "smokeTimeMin": 45,
        "priceEUR": None,
        "priceApprox": False,
        "availabilityHR": ["Havana Shop", "The Humidor"],
        "notes": {"hr": f"Sinkronizirano iz HR trgovina — {line}.", "en": ""},
        "markets": ["HR", "EU", "USA", "WW"],
        "vitolas": [],
        "priceUrl": None,
    }
    cigars.append(entry)
    return entry


def upsert_vitola(cigar: dict, vitola_entry: dict) -> None:
    vitolas = cigar.setdefault("vitolas", [])
    key = norm(vitola_entry["name"])
    for v in vitolas:
        if norm(v["name"]) == key:
            if vitola_entry.get("priceEUR") is not None:
                v["priceEUR"] = vitola_entry["priceEUR"]
            if vitola_entry.get("url"):
                v["url"] = vitola_entry["url"]
            if vitola_entry.get("format") and vitola_entry["format"] != "—":
                v["format"] = vitola_entry["format"]
            if vitola_entry.get("smokeTimeMin"):
                v["smokeTimeMin"] = vitola_entry["smokeTimeMin"]
            return
    vitolas.append(vitola_entry)


def pick_default_vitola(cigar: dict) -> dict | None:
    vitolas = cigar.get("vitolas") or []
    if not vitolas:
        return None
    if len(vitolas) == 1:
        return vitolas[0]

    line = norm(cigar.get("line", ""))
    for v in vitolas:
        if norm(v.get("name", "")) == line:
            return v

    target = norm(cigar.get("vitola", ""))
    for v in vitolas:
        if norm(v.get("name", "")) == target:
            return v

    for v in vitolas:
        name = norm(v.get("name", ""))
        if line in name or name in line:
            return v

    product = [v for v in vitolas if v.get("url") and "?s=" not in v["url"]]
    priced = [v for v in product if v.get("priceEUR") is not None]
    if priced:
        humidor = [v for v in priced if "humidor.hr" in (v.get("url") or "")]
        return humidor[0] if humidor else priced[0]
    if product:
        humidor = [v for v in product if "humidor.hr" in (v.get("url") or "")]
        return humidor[0] if humidor else product[0]
    return vitolas[0]


def finalize_cigar(cigar: dict) -> None:
    vitolas = cigar.get("vitolas") or []
    if not vitolas:
        return
    vitolas.sort(key=lambda v: v.get("smokeTimeMin") or 999)
    default = pick_default_vitola(cigar)
    if default:
        if default.get("priceEUR") is not None:
            cigar["priceEUR"] = default["priceEUR"]
            cigar["priceApprox"] = False
        if default.get("url"):
            cigar["priceUrl"] = default["url"]
    elif any(v.get("priceEUR") for v in vitolas):
        priced = [v for v in vitolas if v.get("priceEUR")]
        fallback = min(priced, key=lambda v: v["priceEUR"])
        cigar["priceEUR"] = fallback["priceEUR"]
        cigar["priceApprox"] = False
        cigar["priceUrl"] = fallback.get("url") or cigar.get("priceUrl")
    mid = vitolas[len(vitolas) // 2]
    cigar["vitola"] = default["name"] if default else mid["name"]
    ref = default or mid
    if ref.get("format") and ref["format"] != "—":
        cigar["format"] = ref["format"]
    cigar["smokeTimeMin"] = ref.get("smokeTimeMin") or cigar.get("smokeTimeMin", 45)
    if "Havana Shop" not in cigar.get("availabilityHR", []):
        cigar.setdefault("availabilityHR", []).append("Havana Shop")
    if "The Humidor" not in cigar.get("availabilityHR", []):
        cigar.setdefault("availabilityHR", []).append("The Humidor")


def main() -> None:
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("Dohvat Havana kataloga...", flush=True)
    havana = fetch_havana_catalog()
    print(f"  Havana: {len(havana)} proizvoda", flush=True)

    print("Dohvat Humidor kataloga...", flush=True)
    humidor = fetch_humidor_catalog()
    print(f"  Humidor: {len(humidor)} proizvoda", flush=True)

    merged = merge_shop_rows(havana + humidor, build_brand_detectors(
        json.loads(CIGARS_JSON.read_text(encoding="utf-8"))
    ))
    cigars = json.loads(CIGARS_JSON.read_text(encoding="utf-8"))
    known_brands = {c["brand"] for c in cigars} | set(BRAND_ALIASES.values())

    touched: set[str] = set()
    added_vitolas = 0

    for row in merged:
        if row["brand"] not in known_brands:
            continue
        cigar = find_or_create_cigar(cigars, row["brand"], row["name"])
        vit = make_vitola_entry(row)
        before = len(cigar.get("vitolas") or [])
        upsert_vitola(cigar, vit)
        after = len(cigar.get("vitolas") or [])
        if after > before:
            added_vitolas += 1
        touched.add(cigar["id"])
        finalize_cigar(cigar)

    for cid in touched:
        c = next(x for x in cigars if x["id"] == cid)
        finalize_cigar(c)
        print(f"  {c['brand']} | {c['line']}: {len(c['vitolas'])} vitola", flush=True)

    CIGARS_JSON.write_text(json.dumps(cigars, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nGotovo: +{added_vitolas} vitola, {len(touched)} linija ažurirano.", flush=True)


if __name__ == "__main__":
    main()
