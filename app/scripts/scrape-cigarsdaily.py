# -*- coding: utf-8 -*-
"""Scrape cigar catalog from CigarsDaily.com (USA shop).

Uses WooCommerce Store REST API to fetch all products.
Output: app/scripts/output/cigarsdaily_catalog_raw.json.

Usage:
  python scripts/scrape-cigarsdaily.py
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "scripts" / "output"
OUTPUT.mkdir(exist_ok=True)

OUTFILE = OUTPUT / "cigarsdaily_catalog_raw.json"
API_BASE = "https://cigarsdaily.com/wp-json/wc/store/products"
PER_PAGE = 100
MAX_PAGES = 200
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

SKIP_CATEGORIES = {
    "promotional", "uncategorized", "accessories", "apparel",
    "gift cards", "memberships", "subscriptions",
}


def wc_price_to_float(prices: dict) -> float | None:
    minor = int(prices.get("currency_minor_unit", 2))
    raw = prices.get("price")
    if raw is None:
        return None
    return int(raw) / (10 ** minor)


def parse_dimensions(name: str) -> tuple[int | None, int | None]:
    """Try to extract ring x length from product name like '6x54' or '6 x 54'."""
    m = re.search(r"(\d+\.?\d*)\s*[xX×]\s*(\d+)", name)
    if not m:
        return None, None
    length_in = float(m.group(1))
    ring = int(m.group(2))
    length_mm = round(length_in * 25.4)
    return ring, length_mm


def is_cigar_product(product: dict) -> bool:
    """Filter out non-cigar products (accessories, memberships, etc.)."""
    cats = {c.get("name", "").lower() for c in product.get("categories", [])}
    if cats & SKIP_CATEGORIES:
        return False
    name_lower = product.get("name", "").lower()
    skip_keywords = ["t-shirt", "hat ", "lighter", "cutter", "humidor",
                     "ashtray", "membership", "gift card", "subscription"]
    return not any(kw in name_lower for kw in skip_keywords)


def fetch_page(session: requests.Session, page: int) -> tuple[list[dict], int]:
    url = f"{API_BASE}?per_page={PER_PAGE}&page={page}"
    r = session.get(url, timeout=30)
    if r.status_code != 200:
        return [], 0
    total_pages = int(r.headers.get("X-WP-TotalPages", 1))
    return r.json(), total_pages


def clean_html(text: str) -> str:
    text = re.sub(r"&#\d+;", " ", text)
    text = re.sub(r"&\w+;", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def main() -> None:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    print("Fetching CigarsDaily catalog via WC Store API...")

    all_products: list[dict] = []
    page = 1
    total_pages = 1

    while page <= min(total_pages, MAX_PAGES):
        batch, tp = fetch_page(session, page)
        if not batch:
            break
        if page == 1:
            total_pages = tp
            print(f"  Total pages: {total_pages}")

        for p in batch:
            if not is_cigar_product(p):
                continue

            name = clean_html(p.get("name", ""))
            permalink = p.get("permalink", "")
            prices = p.get("prices", {})
            price_usd = wc_price_to_float(prices)
            categories = [c.get("name", "") for c in p.get("categories", [])]
            ring, length_mm = parse_dimensions(name)

            fmt = ""
            if ring and length_mm:
                fmt = f"{ring} x {length_mm}mm"

            images = p.get("images", [])
            image_url = images[0].get("src", "") if images else ""

            all_products.append({
                "source": "cigarsdaily",
                "name": name,
                "url": permalink,
                "priceUSD": price_usd,
                "currency": "USD",
                "format": fmt,
                "ring": ring,
                "lengthMM": length_mm,
                "categories": categories,
                "imageUrl": image_url,
            })

        print(f"  Page {page}/{total_pages}: {len(batch)} raw, "
              f"{len(all_products)} cigars total")
        page += 1
        time.sleep(0.5)

    by_url: dict[str, dict] = {}
    for p in all_products:
        by_url[p["url"]] = p
    deduped = list(by_url.values())

    OUTFILE.write_text(json.dumps(deduped, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nDone: {len(deduped)} unique cigar products → {OUTFILE}")


if __name__ == "__main__":
    main()
