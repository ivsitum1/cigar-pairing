# -*- coding: utf-8 -*-
"""Merge raw shop catalogs (EU + USA) into cigars.json.

Reads scraped catalog JSONs and:
1. Matches products to existing cigars by brand + line fuzzy match
2. Adds regionLinks for matched products
3. Updates markets[] with real availability
4. Respects Cuban embargo (Cuba → never USA)
5. Reports unmatched products (candidates for future addition)

Usage:
  python scripts/merge-shop-catalogs.py [--dry-run]
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data"
CIGARS_JSON = DATA / "cigars.json"
OUTPUT = ROOT / "scripts" / "output"

USD_TO_EUR = 0.92

SHOP_REGION = {
    "cigarworld": "EU",
    "holts": "USA",
    "cigarsdaily": "USA",
}

SHOP_NAMES = {
    "cigarworld": "CigarWorld",
    "holts": "Holt's",
    "cigarsdaily": "Cigars Daily",
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[''`]", "", s)
    return re.sub(r"\s+", " ", s.lower().strip())


def extract_brand_from_name(name: str, known_brands: list[str]) -> tuple[str, str] | None:
    """Try to match product name to a known brand. Returns (brand, remainder)."""
    low = norm(name)
    for brand in known_brands:
        brand_n = norm(brand)
        if low.startswith(brand_n + " ") or low.startswith(brand_n + "-"):
            remainder = name[len(brand_n):].strip(" -–—")
            return brand, remainder
        if brand_n in low:
            idx = low.index(brand_n)
            remainder = name[idx + len(brand_n):].strip(" -–—")
            return brand, remainder
    return None


BRAND_ALIASES: dict[str, str] = {
    "padron": "Padrón",
    "bolivar": "Bolívar",
    "san cristobal": "San Cristóbal de la Habana",
    "flor de copan": "Flor de Copán",
    "ep carrillo": "E.P. Carrillo",
    "e.p. carrillo": "E.P. Carrillo",
    "aj fernandez": "AJ Fernandez",
    "arturo fuente": "Arturo Fuente",
    "joya de nicaragua": "Joya de Nicaragua",
    "drew estate": "Drew Estate",
    "my father": "My Father",
    "oliva": "Oliva",
    "perdomo": "Perdomo",
    "rocky patel": "Rocky Patel",
    "montecristo": "Montecristo",
    "romeo y julieta": "Romeo y Julieta",
    "h. upmann": "H. Upmann",
    "h upmann": "H. Upmann",
    "partagas": "Partagás",
    "hoyo de monterrey": "Hoyo de Monterrey",
    "punch": "Punch",
    "san cristobal de la habana": "San Cristóbal de la Habana",
    "trinidad": "Trinidad",
    "cohiba": "Cohiba",
    "davidoff": "Davidoff",
    "ashton": "Ashton",
    "alec bradley": "Alec Bradley",
    "cao": "CAO",
    "camacho": "Camacho",
    "foundation": "Foundation",
    "la aroma de cuba": "La Aroma de Cuba",
    "la gloria cubana": "La Gloria Cubana",
    "macanudo": "Macanudo",
    "nub": "Nub",
    "villiger": "Villiger",
    "gurkha": "Gurkha",
    "tatuaje": "Tatuaje",
    "crowned heads": "Crowned Heads",
    "dunbarton": "Dunbarton T&T",
    "warped": "Warped",
    "vegafina": "VegaFina",
    "don tomas": "Don Tomas",
    "villa zamorano": "Villa Zamorano",
    "eiroa": "Eiroa",
    "cumpay": "Cumpay",
}

CUBAN_BRANDS = {
    "Cohiba", "Montecristo", "Partagás", "Romeo y Julieta", "H. Upmann",
    "Bolívar", "Hoyo de Monterrey", "Punch", "Fonseca", "Trinidad",
    "San Cristóbal de la Habana", "Cuaba", "Vegas Robaina",
    "Quai d'Orsay", "La Gloria Cubana", "Juan López", "Ramón Allones",
    "Por Larrañaga", "Guantanamera", "José L. Piedra", "Diplomaticos",
    "Vegueros", "Rafael González", "Sancho Panza", "El Rey del Mundo",
}


def resolve_brand(name: str, known_brands: list[str]) -> str | None:
    """Attempt to identify the brand from a product name."""
    low = norm(name)
    for alias, canonical in sorted(BRAND_ALIASES.items(), key=lambda x: -len(x[0])):
        if low.startswith(norm(alias)):
            return canonical

    sorted_brands = sorted(known_brands, key=lambda b: -len(b))
    for brand in sorted_brands:
        if low.startswith(norm(brand)):
            return brand
    return None


def stem_line(s: str) -> str:
    """Normalize line name for fuzzy comparison."""
    s = norm(s)
    s = re.sub(r"#\d+", "", s)
    s = re.sub(r"\bseries?\b", "serie", s)
    s = re.sub(r"\banniversary\b", "aniversario", s)
    s = re.sub(r"\bnatural\b", "", s)
    s = re.sub(r"\bmaduro\b", "", s)
    s = re.sub(r"\bconnecticut\b", "", s)
    s = re.sub(r"\bsungrown\b", "", s)
    s = re.sub(r"\bsun grown\b", "", s)
    s = re.sub(r"\bcorojo\b", "", s)
    s = re.sub(r"\bhabano\b", "", s)
    s = re.sub(r"\bbroadleaf\b", "", s)
    s = re.sub(r"\(.*?\)", "", s)
    return re.sub(r"\s+", " ", s).strip()


def match_cigar(product_name: str, brand: str, cigars: list[dict]) -> dict | None:
    """Find the best matching cigar entry for a product."""
    low = norm(product_name)
    brand_n = norm(brand)

    remainder = low
    if remainder.startswith(brand_n):
        remainder = remainder[len(brand_n):].strip()

    brand_cigars = [c for c in cigars if c["brand"] == brand]
    if not brand_cigars:
        return None

    remainder_stem = stem_line(remainder)

    best_match = None
    best_score = 0

    for cigar in brand_cigars:
        line_n = norm(cigar["line"])
        line_stem = stem_line(cigar["line"])
        score = 0

        if line_n == remainder:
            score = 100
        elif line_stem == remainder_stem:
            score = 95
        elif line_n in remainder:
            score = 70 + len(line_n)
        elif line_stem and line_stem in remainder_stem:
            score = 65 + len(line_stem)
        elif remainder in line_n:
            score = 50 + len(remainder)
        elif remainder_stem and remainder_stem in line_stem:
            score = 45 + len(remainder_stem)
        else:
            line_tokens = set(line_stem.split())
            rem_tokens = set(remainder_stem.split())
            if line_tokens and rem_tokens:
                common = line_tokens & rem_tokens
                if common and len(common) >= max(1, len(line_tokens) * 0.4):
                    score = 30 + len(common) * 10

        if score > best_score:
            best_score = score
            best_match = cigar

    return best_match if best_score >= 30 else None


def load_catalog(filename: str) -> list[dict]:
    path = OUTPUT / filename
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    cigars = json.loads(CIGARS_JSON.read_text(encoding="utf-8"))
    known_brands = sorted({c["brand"] for c in cigars} | set(BRAND_ALIASES.values()),
                          key=lambda b: -len(b))

    catalogs = {
        "cigarworld": load_catalog("cigarworld_catalog_raw.json"),
        "holts": load_catalog("holts_catalog_raw.json"),
        "cigarsdaily": load_catalog("cigarsdaily_catalog_raw.json"),
    }

    total_products = sum(len(v) for v in catalogs.values())
    print(f"Loaded catalogs: {', '.join(f'{k}={len(v)}' for k, v in catalogs.items())}")
    print(f"Total products: {total_products}")
    print(f"Existing cigars: {len(cigars)}")

    matched_count = 0
    unmatched: list[dict] = []
    enriched_ids: set[str] = set()

    for source, products in catalogs.items():
        region = SHOP_REGION[source]
        shop_name = SHOP_NAMES[source]

        for product in products:
            name = product.get("name", "")
            brand = resolve_brand(name, known_brands)
            if not brand:
                unmatched.append({**product, "_reason": "unknown brand"})
                continue

            if brand in CUBAN_BRANDS and region == "USA":
                continue

            cigar = match_cigar(name, brand, cigars)
            if not cigar:
                unmatched.append({**product, "_brand": brand, "_reason": "no line match"})
                continue

            matched_count += 1
            enriched_ids.add(cigar["id"])

            if region not in cigar.get("markets", []):
                cigar.setdefault("markets", []).append(region)

            price_eur = product.get("priceEUR")
            if price_eur is None and product.get("priceUSD"):
                price_eur = round(product["priceUSD"] * USD_TO_EUR, 2)

            if "regionLinks" not in cigar:
                cigar["regionLinks"] = {}
            cigar["regionLinks"][region] = {
                "shop": shop_name,
                "url": product.get("url", ""),
                "priceEUR": price_eur,
                "priceApprox": product.get("currency") == "USD",
            }

    print(f"\nMatched: {matched_count} products → {len(enriched_ids)} cigar entries")
    print(f"Unmatched: {len(unmatched)} products")

    unmatched_brands = {}
    for u in unmatched:
        brand = u.get("_brand") or u.get("_reason", "unknown")
        unmatched_brands[brand] = unmatched_brands.get(brand, 0) + 1
    print("\nTop unmatched brands/reasons:")
    for brand, count in sorted(unmatched_brands.items(), key=lambda x: -x[1])[:20]:
        print(f"  {brand}: {count}")

    markets_summary = {"HR": 0, "EU": 0, "USA": 0, "WW": 0}
    for c in cigars:
        for m in c.get("markets", []):
            markets_summary[m] = markets_summary.get(m, 0) + 1
    print(f"\nMarkets distribution: {markets_summary}")

    if not dry_run:
        CIGARS_JSON.write_text(
            json.dumps(cigars, ensure_ascii=False, indent=1),
            encoding="utf-8",
        )
        print(f"\nUpdated {CIGARS_JSON}")

        unmatched_file = OUTPUT / "unmatched_products.json"
        unmatched_file.write_text(
            json.dumps(unmatched, ensure_ascii=False, indent=1),
            encoding="utf-8",
        )
        print(f"Unmatched products → {unmatched_file}")
    else:
        print("\n[DRY RUN] No files modified.")


if __name__ == "__main__":
    main()
