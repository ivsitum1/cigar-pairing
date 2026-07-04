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
import unicodedata
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data"
CIGARS_JSON = DATA / "cigars.json"

USER_AGENT = "Mozilla/5.0 (compatible; CigarRumSync/1.0)"
FRACTIONS = {"½": 0.5, "¼": 0.25, "¾": 0.75, "⅛": 0.125, "⅜": 0.375, "⅝": 0.625, "⅞": 0.875}
FRACTION_CHARS = "".join(FRACTIONS)


def parse_length_inches(raw: str) -> float:
    """Parsira '6', '6½', '6 ½', '6¼' u inče."""
    s = raw.strip()
    total = 0.0
    for part in s.split():
        if part in FRACTIONS:
            total += FRACTIONS[part]
            continue
        m = re.match(rf"^(\d+(?:\.\d+)?)([{FRACTION_CHARS}])?$", part)
        if not m:
            raise ValueError(f"cannot parse length: {raw!r}")
        total += float(m.group(1))
        if m.group(2):
            total += FRACTIONS[m.group(2)]
    return total


def parse_humidor_dims(name: str) -> tuple[str, int | None, int | None]:
    """'Arturo Fuente Hemingway Signature 6 x 46' -> (base, 152mm, 46)"""
    dim_re = re.compile(
        rf"^(.*?)\s+([\d\s{FRACTION_CHARS}.]+)\s*[xX]\s*(\d+)\s*$"
    )
    m = dim_re.match(name.strip())
    if not m:
        return name.strip(), None, None
    base = m.group(1).strip()
    try:
        length_in = parse_length_inches(m.group(2))
    except ValueError:
        return name.strip(), None, None
    ring = int(m.group(3))
    return base, int(round(length_in * 25.4)), ring


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s.lower().strip())


def slugify(s: str) -> str:
    s = norm(s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def parse_price(text: str) -> float | None:
    if not text:
        return None
    m = re.search(r"([\d]+)[,\.]([\d]{2})", text.replace(" ", ""))
    return float(f"{m.group(1)}.{m.group(2)}") if m else None


def wc_price(prices: dict) -> float:
    minor = int(prices.get("currency_minor_unit", 2))
    return int(prices.get("price") or 0) / (10**minor)


def parse_pack_suffix(name: str) -> tuple[str, int | None]:
    """'Montecristo No.2/25' -> ('Montecristo No.2', 25)"""
    m = re.search(r"^(.+?)/(\d+)\s*$", name.strip())
    if m:
        return m.group(1).strip(), int(m.group(2))
    return name.strip(), None


def smoke_minutes(length_mm: int | None, ring: int | None) -> int:
    if not length_mm or not ring:
        return 45
    length_in = length_mm / 25.4
    est = length_in * 10 * (0.60 + ring / 140)
    return int(round(est / 5) * 5)


# brand alias -> canonical brand name in cigars.json
BRAND_ALIASES = {
    "bundle selection by cusano": "Cusano",
    "cusano": "Cusano",
    "arturo fuente": "Arturo Fuente",
    "joya de nicaragua": "Joya de Nicaragua",
    "joya silver": "Joya de Nicaragua",
    "joya red": "Joya de Nicaragua",
    "joya black": "Joya de Nicaragua",
}

# (brand_norm, line keywords in product name) -> existing id or None (create new)
LINE_RULES: list[tuple[str, tuple[str, ...], str | None]] = [
    ("arturo fuente", ("hemingway",), "cig-arturo-fuente-hemingway"),
    ("arturo fuente", ("opus", "opusx"), "cig-fuente-opus-x"),
    ("arturo fuente", ("don carlos",), None),
    ("arturo fuente", ("anejo", "añejo"), None),
    ("arturo fuente", ("brevas",), None),
    ("arturo fuente", ("curly head",), None),
    ("arturo fuente", ("chateau",), None),
    ("arturo fuente", ("gran reserva", "exquisitos", "petit corona", "cuban corona", "cubanitos"), "cig-arturo-fuente-gran-reserva"),
    ("joya de nicaragua", ("antano 1970", "antano gran reserva", "antano ct"), "cig-joya-de-nicaragua-antano"),
    ("joya de nicaragua", ("joya red", "red robusto"), "cig-joya-red"),
    ("joya de nicaragua", ("joya silver",), None),
    ("joya de nicaragua", ("joya black",), None),
    ("joya de nicaragua", ("numero uno", "número uno"), None),
    ("joya de nicaragua", ("cuatro cinco",), None),
    ("joya de nicaragua", ("cinco decadas", "cinco décadas"), None),
    ("joya de nicaragua", ("clasico medio siglo", "clásico medio siglo"), None),
    ("joya de nicaragua", ("rosalones",), None),
    ("cusano", (), "cig-cusano"),
]


def build_brand_detectors(cigars: list[dict]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for brand in {c["brand"] for c in cigars}:
        pairs.append((norm(brand), brand))
    for alias, brand in BRAND_ALIASES.items():
        pairs.append((norm(alias), brand))
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for alias, brand in sorted(pairs, key=lambda x: -len(x[0])):
        if alias in seen:
            continue
        seen.add(alias)
        out.append((alias, brand))
    return out


def detect_brand(product_name: str, detectors: list[tuple[str, str]]) -> str | None:
    low = norm(product_name)
    for alias, brand in detectors:
        if low.startswith(alias) or f" {alias} " in f" {low} ":
            return brand
    return None


def detect_line_id(brand: str, product_name: str) -> str | None:
    bnorm = norm(brand)
    low = norm(product_name)
    for brand_key, keywords, cid in LINE_RULES:
        if brand_key != bnorm:
            continue
        if not keywords or any(kw in low for kw in keywords if kw):
            return cid
    return None


def line_name_from_product(brand: str, product_name: str) -> str:
    low = norm(product_name)
    b = norm(brand)
    rest = low
    for prefix in [b, "bundle selection by cusano", "joya de nicaragua"]:
        if rest.startswith(prefix):
            rest = rest[len(prefix) :].strip(" -/")
    rest = re.sub(r"/\d+$", "", rest).strip()
    # ukloni vitola na kraju (robusto, toro...)
    for vit in ("robusto grande", "double robusto", "short robusto", "petit corona",
                "robusto", "toro", "churchill", "corona", "figurado", "lonsdale",
                "panatela", "torpedo", "gordo", "diadema", "consul", "machito"):
        if rest.endswith(" " + vit):
            rest = rest[: -len(vit)].strip()
            break
    return rest.title() if rest else brand


def vitola_from_product(product_name: str, brand: str) -> str:
    base, pack = parse_pack_suffix(product_name)
    base, mm, ring = parse_humidor_dims(base)
    low = norm(base)
    b = norm(brand)
    if low.startswith(b):
        low = low[len(b) :].strip(" -/")
    low = re.sub(r"/\d+$", "", low).strip()
    # zadnji tokeni kao vitola
    for vit in ("Robusto Grande", "Double Robusto", "Short Robusto", "Petit Corona",
                "Gran Consul", "Gran Cónsul", "Robusto", "Toro", "Churchill", "Corona",
                "Figurado", "Lonsdale", "Panatela", "Torpedo", "Gordo", "Diadema",
                "Machito", "Signature", "Classic", "Short Story", "Best Seller",
                "Exquisitos", "Petit Corona", "Cuban Corona", "Cubanitos", "PerfecXion X"):
        if norm(vit) in low or low.endswith(norm(vit)):
            return vit
    parts = base.split()
    if len(parts) >= 2:
        return " ".join(parts[-2:]).title()
    return base.title() if base else "Standard"


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


def finalize_cigar(cigar: dict) -> None:
    vitolas = cigar.get("vitolas") or []
    if not vitolas:
        return
    vitolas.sort(key=lambda v: v.get("smokeTimeMin") or 999)
    priced = [v for v in vitolas if v.get("priceEUR")]
    if priced:
        cheapest = min(priced, key=lambda v: v["priceEUR"])
        cigar["priceEUR"] = cheapest["priceEUR"]
        cigar["priceApprox"] = False
        cigar["priceUrl"] = cheapest.get("url") or cigar.get("priceUrl")
    mid = vitolas[len(vitolas) // 2]
    cigar["vitola"] = mid["name"]
    if mid.get("format") and mid["format"] != "—":
        cigar["format"] = mid["format"]
    cigar["smokeTimeMin"] = mid.get("smokeTimeMin") or cigar.get("smokeTimeMin", 45)
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
