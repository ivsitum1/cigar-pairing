# -*- coding: utf-8 -*-
"""Scrape cigar catalog from Holts.com (USA shop).

Crawls brand pages at holts.com and parses product tables.
Output: app/scripts/output/holts_catalog_raw.json.

Usage:
  python scripts/scrape-holts.py
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "scripts" / "output"
OUTPUT.mkdir(exist_ok=True)

OUTFILE = OUTPUT / "holts_catalog_raw.json"
BASE_URL = "https://www.holts.com"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def get_brand_urls(session: requests.Session) -> list[tuple[str, str]]:
    """Discover brand URLs from the all-brands page."""
    r = session.get(f"{BASE_URL}/cigars/all-cigar-brands.html", timeout=20)
    soup = BeautifulSoup(r.text, "lxml")

    brands: list[tuple[str, str]] = []
    seen_slugs: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/cigars/all-cigar-brands/brand/" not in href:
            continue
        text = a.get_text(strip=True)
        if not text or "accessories" in href.lower():
            continue
        slug = href.rstrip("/").split("/")[-1]
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)
        full = href if href.startswith("http") else f"{BASE_URL}{href}"
        brand_name = text.replace(" Cigars", "").strip()
        brands.append((brand_name, full))

    extra_links: list[tuple[str, str]] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        if "/cigars/all-cigar-brands/" in href and "/brand/" not in href and text:
            slug = href.rstrip("/").rstrip(".html").split("/")[-1]
            if slug in seen_slugs or slug == "all-cigar-brands":
                continue
            seen_slugs.add(slug)
            full = href if href.startswith("http") else f"{BASE_URL}{href}"
            name = text.replace(" Cigars", "").strip()
            extra_links.append((name, full + (".html" if not full.endswith(".html") else "")))

    return brands + extra_links


def parse_brand_page(session: requests.Session, brand_name: str, url: str) -> list[dict]:
    """Parse product table from a brand page."""
    try:
        r = session.get(url, timeout=20)
    except requests.RequestException:
        return []

    if r.status_code != 200:
        alt_url = url.replace("/brand/", "/")
        if not alt_url.endswith(".html"):
            alt_url += ".html"
        try:
            r = session.get(alt_url, timeout=20)
        except requests.RequestException:
            return []
        if r.status_code != 200:
            return []

    soup = BeautifulSoup(r.text, "lxml")
    table = soup.select_one(".products-list-table")
    if not table:
        return []

    rows = table.find_all("tr")
    products: list[dict] = []
    current: dict | None = None

    for row in rows:
        text = row.get_text(separator=" | ", strip=True)
        dim_match = re.search(r"([\d.]+)\s*x\s*(\d+)", text)
        price_match = re.search(r"\$([\d,]+\.?\d*)", text)

        is_single_row = "Single" in text
        is_pack_row = re.search(r"Pack of \d+", text)

        if dim_match and not is_single_row and not is_pack_row:
            name_part = text.split("|")[0].strip()
            name_part = re.sub(r"\s*-\s*[\d.]+\s*x\s*\d+.*$", "", name_part).strip()
            name_part = re.sub(r"\s*\|\s*$", "", name_part).strip()

            length_in = float(dim_match.group(1))
            ring = int(dim_match.group(2))
            length_mm = round(length_in * 25.4)

            current = {
                "source": "holts",
                "brand": brand_name,
                "name": f"{brand_name} {name_part}".strip(),
                "format": f"{ring} x {length_mm}mm",
                "ring": ring,
                "lengthMM": length_mm,
                "priceUSD": None,
                "priceUSD_single": None,
                "priceUSD_box": None,
                "url": url,
                "currency": "USD",
            }

            box_match = re.search(r"Box of (\d+)", text)
            if box_match and price_match:
                current["priceUSD_box"] = float(price_match.group(1).replace(",", ""))
                box_count = int(box_match.group(1))
                current["priceUSD"] = round(
                    current["priceUSD_box"] / box_count, 2
                )

            products.append(current)

        elif is_single_row and price_match and current:
            current["priceUSD_single"] = float(price_match.group(1).replace(",", ""))
            current["priceUSD"] = current["priceUSD_single"]

    return products


def main() -> None:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    print("Discovering Holts brand pages...")
    brands = get_brand_urls(session)
    print(f"Found {len(brands)} brands")

    all_products: list[dict] = []
    for i, (brand_name, url) in enumerate(brands, 1):
        products = parse_brand_page(session, brand_name, url)
        all_products.extend(products)
        count = len(products)
        if count > 0:
            print(f"  [{i}/{len(brands)}] {brand_name}: {count} products")
        time.sleep(0.8)

    by_key: dict[str, dict] = {}
    for p in all_products:
        key = f"{p['name']}|{p['format']}"
        by_key[key] = p
    deduped = list(by_key.values())

    OUTFILE.write_text(json.dumps(deduped, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nDone: {len(deduped)} unique products → {OUTFILE}")


if __name__ == "__main__":
    main()
