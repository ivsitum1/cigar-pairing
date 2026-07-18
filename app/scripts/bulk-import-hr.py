# -*- coding: utf-8 -*-
"""Bulk import: fetches all HR shop products, adds missing ones to cigars.json.

Workflow:
  1. Fetch humidor.hr + havana-cigar-shop catalogs
  2. Detect brand for each product
  3. Find products not yet in cigars.json
  4. Create entries (without profiles — those come later)
  5. Save updated cigars.json

Usage:
  python3 scripts/bulk-import-hr.py
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
BRANDS_JSON = DATA / "brands.json"
CURATED_BACKUP = ROOT / "scripts" / "output" / "curated_profiles_backup.json"

USER_AGENT = "Mozilla/5.0 (compatible; CigarBulkImport/1.0)"
FRACTIONS = {"½": 0.5, "¼": 0.25, "¾": 0.75, "⅛": 0.125, "⅜": 0.375, "⅝": 0.625, "⅞": 0.875}
FRACTION_CHARS = "".join(FRACTIONS)

BRAND_MAP: dict[str, tuple[str, str]] = {
    "accomplice": ("Accomplice", "Honduras"),
    "accomplice classic": ("Accomplice", "Honduras"),
    "aging room": ("Aging Room", "Dominikana"),
    "aging room quattro": ("Aging Room", "Nikaragva"),
    "aj fernandez": ("AJ Fernandez", "Nikaragva"),
    "ajf": ("AJ Fernandez", "Nikaragva"),
    "alec bradley": ("Alec Bradley", "Honduras"),
    "ambasciator italico": ("Ambasciator Italico", "Italija"),
    "artista harvest": ("Artista", "Nikaragva"),
    "artista midnight": ("Artista", "Nikaragva"),
    "arturo fuente": ("Arturo Fuente", "Dominikana"),
    "a. fuente": ("Arturo Fuente", "Dominikana"),
    "ashton": ("Ashton", "Dominikana"),
    "asylum 13": ("Asylum 13", "Nikaragva"),
    "asylum": ("Asylum 13", "Nikaragva"),
    "bellas artes": ("Bellas Artes", "Honduras"),
    "blend 15": ("Blend 15", "Nikaragva"),
    "bolivar": ("Bolívar", "Kuba"),
    "buffalo ten": ("Buffalo Ten", "Nikaragva"),
    "bundle selection by cusano": ("Cusano", "Dominikana"),
    "bundle selection": ("Cusano", "Dominikana"),
    "cao": ("CAO", "Nikaragva"),
    "camacho": ("Camacho", "Honduras"),
    "casa 1910": ("Casa 1910", "Nikaragva"),
    "chateau diadem": ("Chateau Diadem", "Nikaragva"),
    "cle": ("CLE", "Honduras"),
    "cohiba": ("Cohiba", "Kuba"),
    "cuaba": ("Cuaba", "Kuba"),
    "cumpay": ("Cumpay", "Dominikana"),
    "cusano": ("Cusano", "Dominikana"),
    "davidoff": ("Davidoff", "Dominikana"),
    "dias de gloria": ("AJ Fernandez", "Nikaragva"),
    "don kiki": ("Don Kiki", "Nikaragva"),
    "don tomas": ("Don Tomas", "Honduras"),
    "drew estate": ("Drew Estate", "Nikaragva"),
    "dunbarton": ("Dunbarton T&T", "Nikaragva"),
    "e.p. carrillo": ("E.P. Carrillo", "Dominikana"),
    "ep carrillo": ("E.P. Carrillo", "Dominikana"),
    "eiroa": ("Eiroa", "Honduras"),
    "el criollito": ("PDR", "Dominikana"),
    "el pulpo": ("El Pulpo", "Nikaragva"),
    "el vinyet": ("El Vinyet", "Nikaragva"),
    "eladio diaz": ("Eladio Diaz", "Dominikana"),
    "enclave": ("Enclave", "Nikaragva"),
    "flor de copan": ("Flor de Copán", "Honduras"),
    "flor de selva": ("Flor de Selva", "Honduras"),
    "fonseca": ("Fonseca", "Kuba"),
    "foundation": ("Foundation Cigar Company", "Nikaragva"),
    "guantanamera": ("Guantanamera", "Kuba"),
    "gurkha": ("Gurkha", "Dominikana"),
    "h. upmann": ("H. Upmann", "Kuba"),
    "h.upmann": ("H. Upmann", "Kuba"),
    "hoyo de monterrey": ("Hoyo de Monterrey", "Kuba"),
    "illusione": ("Illusione", "Nikaragva"),
    "jfr": ("JFR", "Nikaragva"),
    "jose l. piedra": ("José L. Piedra", "Kuba"),
    "jose l.piedra": ("José L. Piedra", "Kuba"),
    "joya de nicaragua": ("Joya de Nicaragua", "Nikaragva"),
    "joya red": ("Joya de Nicaragua", "Nikaragva"),
    "joya silver": ("Joya de Nicaragua", "Nikaragva"),
    "joya black": ("Joya de Nicaragua", "Nikaragva"),
    "juan lopez": ("Juan López", "Kuba"),
    "k by karen berger": ("K by Karen Berger", "Dominikana"),
    "k-fire by karen berger": ("K by Karen Berger", "Dominikana"),
    "kintsugi": ("Kintsugi", "Nikaragva"),
    "la aroma del caribe": ("La Aroma del Caribe", "Nikaragva"),
    "la aroma de cuba": ("La Aroma del Caribe", "Nikaragva"),
    "la aurora": ("La Aurora", "Dominikana"),
    "la flor dominicana": ("La Flor Dominicana", "Dominikana"),
    "la galera": ("La Galera", "Dominikana"),
    "la gloria cubana": ("La Gloria Cubana", "Kuba"),
    "la instructora": ("La Instructora", "Nikaragva"),
    "la ley": ("La Ley", "Nikaragva"),
    "last call": ("Last Call", "Nikaragva"),
    "leaf by oscar": ("Leaf by Oscar", "Honduras"),
    "liga privada": ("Liga Privada", "Nikaragva"),
    "lunatic": ("JFR", "Nikaragva"),
    "lunatic perfecto": ("JFR", "Nikaragva"),
    "macanudo": ("Macanudo", "Dominikana"),
    "maestranza": ("Maestranza", "Kuba"),
    "montecristo": ("Montecristo", "Kuba"),
    "muestras de saka": ("Dunbarton T&T", "Nikaragva"),
    "my father": ("My Father", "Nikaragva"),
    "new world": ("AJ Fernandez", "Nikaragva"),
    "nub": ("Nub", "Nikaragva"),
    "oliva": ("Oliva", "Nikaragva"),
    "omar ortez": ("Omar Ortez", "Nikaragva"),
    "oscar valladares": ("Oscar Valladares", "Honduras"),
    "padilla": ("Padilla", "Nikaragva"),
    "padron": ("Padrón", "Nikaragva"),
    "paradiso": ("Paradiso", "Honduras"),
    "partagas": ("Partagás", "Kuba"),
    "pdr": ("PDR", "Dominikana"),
    "perdomo": ("Perdomo", "Nikaragva"),
    "plasencia": ("Plasencia", "Honduras"),
    "por larranaga": ("Por Larrañaga", "Kuba"),
    "pulita": ("Pulita", "Nikaragva"),
    "punch": ("Punch", "Kuba"),
    "puro ambar": ("Puro Ambar", "Nikaragva"),
    "quai d'orsay": ("Quai d'Orsay", "Kuba"),
    "quai dorsay": ("Quai d'Orsay", "Kuba"),
    "quintero": ("Quintero", "Kuba"),
    "rafael gonzalez": ("Rafael Gonzalez", "Kuba"),
    "ramon allones": ("Ramón Allones", "Kuba"),
    "rey del mundo": ("Rey del Mundo", "Kuba"),
    "rocky patel": ("Rocky Patel", "Honduras"),
    "romeo y julieta": ("Romeo y Julieta", "Kuba"),
    "saga": ("Saga", "Nikaragva"),
    "san cristobal": ("San Cristóbal de la Habana", "Kuba"),
    "san lotano": ("San Lotano", "Honduras"),
    "sancho panza": ("Sancho Panza", "Kuba"),
    "sin compromiso": ("Sin Compromiso", "Nikaragva"),
    "tabernacle": ("Foundation Cigar Company", "Nikaragva"),
    "tailgate by karen berger": ("K by Karen Berger", "Dominikana"),
    "tatuaje": ("Tatuaje", "Nikaragva"),
    "the aviator": ("The Aviator", "Dominikana"),
    "the oscar": ("The Oscar", "Honduras"),
    "trinidad": ("Trinidad", "Kuba"),
    "undercrown": ("Drew Estate", "Nikaragva"),
    "vegafina": ("VegaFina", "Dominikana"),
    "vegas robaina": ("Vegas Robaina", "Kuba"),
    "vegueros": ("Vegueros", "Kuba"),
    "villa zamorano": ("Villa Zamorano", "Honduras"),
    "villiger": ("Villiger", "Dominikana"),
    "viva la vida": ("Viva La Vida", "Nikaragva"),
    "warped": ("Warped", "Nikaragva"),
    "zino": ("Zino", "Honduras"),
    "1502": ("1502", "Honduras"),
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s.lower().strip())


def slugify(s: str) -> str:
    s = norm(s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def parse_length_inches(raw: str) -> float:
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


def parse_dims(name: str) -> tuple[str, int | None, int | None]:
    dim_re = re.compile(
        rf"^(.*?)\s+([\d\s{FRACTION_CHARS}.]+)\s*[xX×]\s*(\d+)\s*$"
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


def smoke_minutes(length_mm: int | None, ring: int | None) -> int:
    if not length_mm or not ring:
        return 45
    length_in = length_mm / 25.4
    est = length_in * 10 * (0.60 + ring / 140)
    return int(round(est / 5) * 5)


def parse_price(text: str) -> float | None:
    if not text:
        return None
    m = re.search(r"([\d]+)[,\.]([\d]{2})", text.replace(" ", ""))
    return float(f"{m.group(1)}.{m.group(2)}") if m else None


def detect_brand(product_name: str) -> tuple[str, str] | None:
    low = norm(product_name)
    for alias in sorted(BRAND_MAP, key=len, reverse=True):
        alias_norm = norm(alias)
        if low.startswith(alias_norm + " ") or low == alias_norm:
            return BRAND_MAP[alias]
    return None


def extract_line(brand: str, product_name: str) -> str:
    low = norm(product_name)
    for alias in sorted(BRAND_MAP, key=len, reverse=True):
        alias_norm = norm(alias)
        if low.startswith(alias_norm):
            low = low[len(alias_norm):].strip(" -/")
            break

    low = re.sub(r"/\d+\s*(pak\.?)?\s*$", "", low).strip()
    for vit in ("robusto grande", "double robusto", "short robusto", "petit corona",
                "robusto", "toro", "churchill", "corona", "figurado", "lonsdale",
                "panatela", "torpedo", "gordo", "diadema", "lancero", "belicoso",
                "perfecto", "short corona", "half corona"):
        if low.endswith(" " + vit):
            low = low[: -len(vit)].strip()
            break

    low = re.sub(rf"\s+[\d\s{FRACTION_CHARS}.]+\s*[xX×]\s*\d+\s*$", "", low).strip()
    return low.title() if low else brand


def extract_vitola(product_name: str, brand: str) -> str:
    base, mm, ring = parse_dims(product_name)
    low = norm(base)
    for alias in sorted(BRAND_MAP, key=len, reverse=True):
        alias_norm = norm(alias)
        if low.startswith(alias_norm):
            low = low[len(alias_norm):].strip(" -/")
            break

    for vit in ("Robusto Grande", "Double Robusto", "Short Robusto", "Petit Corona",
                "Gran Consul", "Robusto", "Toro", "Churchill", "Corona",
                "Figurado", "Lonsdale", "Panatela", "Torpedo", "Gordo", "Diadema",
                "Machito", "Signature", "Classic", "Short Story", "Best Seller",
                "Exquisitos", "Cuban Corona", "Cubanitos", "Lancero", "Belicoso",
                "Half Corona", "Short Corona", "Perfecto", "Infante"):
        if norm(vit) in low or low.endswith(norm(vit)):
            return vit
    parts = base.split()
    if len(parts) >= 2:
        return " ".join(parts[-2:]).title()
    return base.title() if base else "Standard"


def detect_wrapper_from_name(name: str) -> str:
    low = norm(name)
    if "maduro" in low or "oscuro" in low:
        return "Maduro"
    if "connecticut" in low or "conn." in low:
        return "Connecticut"
    if "habano" in low or "sun grown" in low or "sungrown" in low:
        return "Habano"
    if "corojo" in low:
        return "Corojo"
    if "cameroon" in low:
        return "Cameroon"
    if "broadleaf" in low:
        return "Broadleaf"
    if "rosado" in low:
        return "Rosado"
    if "criollo" in low:
        return "Criollo"
    if "brazil" in low:
        return "Brazil"
    return "Natural"


def fetch_humidor() -> list[dict]:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    items: list[dict] = []
    base = "https://humidor.hr/hr/kategorija-proizvoda/cigare/"
    page = 1
    while page <= 30:
        url = base if page == 1 else f"{base}page/{page}/"
        try:
            r = session.get(url, timeout=25)
        except Exception as e:
            print(f"  [error] humidor page {page}: {e}")
            break
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
                "name": title.get_text(strip=True),
                "price": parse_price(price_el.get_text() if price_el else ""),
                "url": link["href"],
                "source": "humidor",
            })
        print(f"  humidor page {page}: {len(products)} products (total: {len(items)})")
        page += 1
        time.sleep(0.3)
    return items


def fetch_havana() -> list[dict]:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    items: list[dict] = []
    page = 1
    while page <= 50:
        url = (
            "https://havana-cigar-shop.com/wp-json/wc/store/products"
            f"?category=cigare&per_page=100&page={page}"
        )
        try:
            r = session.get(url, timeout=30)
        except Exception as e:
            print(f"  [error] havana page {page}: {e}")
            break
        if r.status_code != 200:
            break
        batch = r.json()
        if not batch:
            break
        for p in batch:
            permalink = p.get("permalink", "")
            if "/en/" in permalink:
                continue
            name = re.sub(r"/\d+\s*$", "", p.get("name", "")).strip()
            minor = int(p.get("prices", {}).get("currency_minor_unit", 2))
            price_raw = int(p.get("prices", {}).get("price") or 0)
            price = price_raw / (10 ** minor) if price_raw else None
            items.append({
                "name": name,
                "price": price,
                "url": permalink,
                "source": "havana",
            })
        if page >= int(r.headers.get("X-WP-TotalPages", 1)):
            break
        page += 1
        time.sleep(0.2)
    return items


def product_in_catalog(product: dict, cigars: list[dict], all_urls: set[str]) -> bool:
    url = product.get("url", "")
    if url and norm(url.rstrip("/")) in all_urls:
        return True

    sn = norm(product["name"])

    for c in cigars:
        cid = c["id"].replace("cig-", "").replace("-", " ")
        if len(cid) > 12 and (norm(cid) in sn or sn in norm(cid)):
            return True
        bl = norm(f"{c['brand']} {c['line']}")
        if len(bl) > 12 and bl == sn:
            return True
        for v in c.get("vitolas", []):
            v_url = v.get("url") or ""
            if v_url and url:
                if norm(v_url.rstrip("/")) == norm(url.rstrip("/")):
                    return True
                slug_a = v_url.rstrip("/").split("/")[-1]
                slug_b = url.rstrip("/").split("/")[-1]
                if slug_a and slug_b and norm(slug_a) == norm(slug_b):
                    return True

    return False


def find_matching_curated(brand: str, wrapper: str, line: str,
                          curated: dict, cigars: list[dict]) -> dict | None:
    line_n = norm(line)
    for cid, prof in curated.items():
        if prof["brand"] != brand:
            continue
        if norm(prof.get("wrapper", "")) == norm(wrapper) and norm(prof.get("line", "")) == line_n:
            return prof

    for cid, prof in curated.items():
        if prof["brand"] != brand:
            continue
        if norm(prof.get("wrapper", "")) == norm(wrapper):
            return prof

    for c in cigars:
        if c["brand"] != brand:
            continue
        if not c.get("profileEstimated", False):
            return {
                "wrapper": c.get("wrapper", ""),
                "strength": c["strength"],
                "body": c["body"],
                "flavorTags": c["flavorTags"],
            }

    return None


def is_sampler_or_pack(name: str) -> bool:
    low = norm(name)
    return any(kw in low for kw in ("sampler", "gift pack", "gift set", "fresh pack", "display refill"))


def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    cigars = json.loads(CIGARS_JSON.read_text(encoding="utf-8"))
    curated = json.loads(CURATED_BACKUP.read_text(encoding="utf-8")) if CURATED_BACKUP.exists() else {}
    existing_ids = {c["id"] for c in cigars}

    all_urls: set[str] = set()
    for c in cigars:
        for v in c.get("vitolas", []):
            u = v.get("url")
            if u:
                all_urls.add(norm(u.rstrip("/")))
        pu = c.get("priceUrl")
        if pu:
            all_urls.add(norm(pu.rstrip("/")))

    print(f"Existing catalog: {len(cigars)} cigars, {len(existing_ids)} IDs\n")

    print("=== Fetching Humidor catalog ===")
    humidor = fetch_humidor()
    print(f"  Total: {len(humidor)}\n")

    print("=== Fetching Havana catalog ===")
    havana = fetch_havana()
    print(f"  Total: {len(havana)}\n")

    all_products = humidor + havana
    seen: set[str] = set()
    unique: list[dict] = []
    for p in all_products:
        key = norm(p["name"])
        if key not in seen:
            seen.add(key)
            unique.append(p)

    print(f"Unique shop products: {len(unique)}")

    missing: list[dict] = []
    no_brand: list[str] = []

    for p in unique:
        if is_sampler_or_pack(p["name"]):
            continue
        if product_in_catalog(p, cigars, all_urls):
            continue

        brand_info = detect_brand(p["name"])
        if not brand_info:
            no_brand.append(p["name"])
            continue

        p["brand"], p["country"] = brand_info
        missing.append(p)

    print(f"Missing (non-sampler): {len(missing)}")
    if no_brand:
        print(f"Unrecognized brands ({len(no_brand)}):")
        for n in sorted(no_brand):
            print(f"  ? {n}")

    added = 0
    added_to_existing = 0

    for p in missing:
        brand = p["brand"]
        country = p["country"]
        name = p["name"]
        line = extract_line(brand, name)
        vitola = extract_vitola(name, brand)
        wrapper = detect_wrapper_from_name(name)
        _, length_mm, ring = parse_dims(name)
        fmt = f"{ring} x {length_mm}mm" if ring and length_mm else "—"
        stime = smoke_minutes(length_mm, ring)

        line_n = norm(line)
        existing_match = None
        for c in cigars:
            if c["brand"] == brand and norm(c.get("line", "")) == line_n:
                existing_match = c
                break
            if c["brand"] == brand and line_n and line_n in norm(c.get("line", "")):
                existing_match = c
                break

        if existing_match:
            vit_entry = {
                "name": vitola,
                "format": fmt,
                "smokeTimeMin": stime,
                "priceEUR": p.get("price"),
                "url": p.get("url"),
            }
            existing_names = {norm(v["name"]) for v in existing_match.get("vitolas", [])}
            if norm(vitola) not in existing_names:
                existing_match.setdefault("vitolas", []).append(vit_entry)
                added_to_existing += 1
                shop = "Havana Shop" if p["source"] == "havana" else "The Humidor"
                if shop not in existing_match.get("availabilityHR", []):
                    existing_match.setdefault("availabilityHR", []).append(shop)
            continue

        cig_id = f"cig-{slugify(brand)}-{slugify(line)}"
        if not line or slugify(line) == slugify(brand):
            cig_id = f"cig-{slugify(brand)}-{slugify(vitola)}"
        if cig_id in existing_ids:
            cig_id = f"{cig_id}-{slugify(vitola)}"
        if cig_id in existing_ids:
            cig_id = f"{cig_id}-{added}"

        prof = find_matching_curated(brand, wrapper, line, curated, cigars)

        shop = "Havana Shop" if p["source"] == "havana" else "The Humidor"
        markets = ["HR", "WW"]
        if country == "Kuba":
            markets = ["HR", "EU"]

        entry = {
            "id": cig_id,
            "brand": brand,
            "line": line if line != brand else vitola,
            "vitola": vitola,
            "format": fmt,
            "country": country,
            "wrapper": wrapper,
            "strength": prof["strength"] if prof else 3,
            "body": prof["body"] if prof else 3,
            "flavorTags": list(prof["flavorTags"]) if prof else [],
            "smokeTimeMin": stime,
            "priceEUR": p.get("price"),
            "priceApprox": False if p.get("price") else True,
            "availabilityHR": [shop],
            "notes": {"hr": "", "en": ""},
            "markets": markets,
            "vitolas": [
                {
                    "name": vitola,
                    "format": fmt,
                    "smokeTimeMin": stime,
                    "priceEUR": p.get("price"),
                    "url": p.get("url"),
                }
            ],
            "priceUrl": p.get("url"),
            "profileEstimated": True,
            "_needsProfile": True,
        }
        cigars.append(entry)
        existing_ids.add(cig_id)
        added += 1

    cigars.sort(key=lambda c: (c["brand"].lower(), c.get("line", "").lower()))

    CIGARS_JSON.write_text(json.dumps(cigars, ensure_ascii=False, indent=1), encoding="utf-8")

    needs_profile = sum(1 for c in cigars if c.get("_needsProfile"))
    print(f"\n=== DONE ===")
    print(f"New entries added: {added}")
    print(f"Vitolas added to existing entries: {added_to_existing}")
    print(f"Total cigars now: {len(cigars)}")
    print(f"Entries needing profile research: {needs_profile}")

    if needs_profile:
        print(f"\nEntries needing profiles:")
        for c in cigars:
            if c.get("_needsProfile"):
                print(f"  {c['brand']} | {c['line']} | {c['vitola']} | {c['wrapper']}")


if __name__ == "__main__":
    main()
