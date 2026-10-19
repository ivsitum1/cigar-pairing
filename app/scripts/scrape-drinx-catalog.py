# -*- coding: utf-8 -*-
"""Scrape spirit catalogues from drinx.hr (Odoo eCommerce).

Categories: rum, whisky, gin, tequila, cognac, armagnac.

Output: app/scripts/output/drinx_catalog_raw.json

Pokretanje: python scripts/scrape-drinx-catalog.py
            python scripts/scrape-drinx-catalog.py --category rum
"""
from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from script_io import configure_stdio

OUT_DIR = Path(__file__).resolve().parent / "output"
OUT_JSON = OUT_DIR / "drinx_catalog_raw.json"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
BASE = "https://drinx.hr"

# Canonical category list paths (Odoo may redirect to longer slugs).
CATEGORIES: dict[str, str] = {
    "rum": "/shop/category/zestoka-pica-rum-1371",
    "whisky": "/shop/category/zestoka-pica-viski-1364",
    "gin": "/shop/category/zestoka-pica-gin-1384",
    "tequila": "/shop/category/zestoka-pica-tekila-1392",
    "cognac": "/shop/category/zestoka-pica-cognac-1379",
    "armagnac": "/shop/category/zestoka-pica-armagnac-1374",
}

CART_RE = re.compile(
    r'<form[^>]*class="[^"]*oe_product_cart[^"]*"[^>]*aria-label="([^"]+)"[^>]*>'
    r"(.*?)</form>",
    re.S | re.I,
)
HREF_RE = re.compile(r'href="(/shop/[^"]+)"')
PRICE_RE = re.compile(r'oe_currency_value">\s*([\d]+[.,][\d]{2})')
PAGE_RE = re.compile(r"/page/(\d+)")


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", "replace")


def abs_url(path: str) -> str:
    if path.startswith("http"):
        return path
    return BASE + path


def parse_price(raw: str) -> float | None:
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        return None


def is_product_path(path: str) -> bool:
    if "/category/" in path:
        return False
    if any(x in path for x in ("/cart", "wishlist", "all-brands", "/checkout")):
        return False
    # /shop/<category-or-path>/<product-slug-id>
    segs = [s for s in path.split("/") if s]
    return len(segs) >= 3 and segs[0] == "shop"


def scrape_page(html: str, category: str) -> list[dict]:
    items: list[dict] = []
    for m in CART_RE.finditer(html):
        name = html_lib.unescape(m.group(1)).strip()
        block = m.group(2)
        hrefs = [h for h in HREF_RE.findall(block) if is_product_path(h)]
        if not hrefs:
            continue
        url = abs_url(hrefs[0])
        price_m = PRICE_RE.search(block)
        price = parse_price(price_m.group(1)) if price_m else None
        items.append(
            {
                "name": name,
                "price_eur": price,
                "shop": "drinx.hr",
                "url": url,
                "source": "drinx",
                "category": category,
            }
        )
    return items


def max_page(html: str) -> int:
    pages = [int(p) for p in PAGE_RE.findall(html)]
    return max(pages) if pages else 1


def scrape_category(category: str, path: str) -> list[dict]:
    list_url = abs_url(path)
    print(f"Scraping drinx.hr {category}...")
    try:
        first = fetch_html(list_url)
    except urllib.error.HTTPError as exc:
        # Fallback short slug (e.g. /shop/category/whisky-1364)
        alt = path.replace("zestoka-pica-viski", "whisky").replace(
            "zestoka-pica-tekila", "tequila"
        )
        if alt == path:
            raise
        print(f"  {exc.code} on {path}, trying {alt}")
        list_url = abs_url(alt)
        first = fetch_html(list_url)

    # Prefer redirected canonical category path for pagination
    canon_m = re.search(r'href="(/shop/category/[^"]+/page/\d+)"', first)
    base_path = path
    if canon_m:
        base_path = re.sub(r"/page/\d+$", "", canon_m.group(1))
    else:
        # detect from product links
        for h in HREF_RE.findall(first):
            if "/category/" in h:
                continue
            # /shop/zestoka-pica-rum-1371/product…
            parts = h.strip("/").split("/")
            if len(parts) >= 3 and parts[0] == "shop":
                base_path = f"/shop/category/{parts[1]}"
                break

    n_pages = max_page(first)
    print(f"  pages: {n_pages} (base {base_path})")
    all_items: list[dict] = []
    seen: set[str] = set()
    for page in range(1, n_pages + 1):
        if page == 1:
            html = first
            page_url = abs_url(base_path) if base_path.startswith("/shop/category/") else list_url
            if page == 1 and base_path.startswith("/shop/category/"):
                # first page already fetched via list_url; keep it
                page_url = list_url
        else:
            page_url = abs_url(f"{base_path}/page/{page}")
            html = fetch_html(page_url)
        batch = scrape_page(html, category)
        for item in batch:
            if item["url"] in seen:
                continue
            seen.add(item["url"])
            all_items.append(item)
        if page % 5 == 0 or page == n_pages:
            print(f"  page {page}/{n_pages} -> {len(all_items)} unique")
        time.sleep(0.35)
    print(f"drinx.hr {category}: {len(all_items)} stavki")
    return all_items


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--category",
        choices=sorted(CATEGORIES.keys()),
        help="Scrape only one category",
    )
    args = parser.parse_args()

    cats = (
        {args.category: CATEGORIES[args.category]}
        if args.category
        else CATEGORIES
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    entries: list[dict] = []
    for cat, path in cats.items():
        try:
            entries.extend(scrape_category(cat, path))
        except Exception as exc:
            print(f"WARNING: {cat} scrape failed: {exc}")

    OUT_JSON.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {OUT_JSON} ({len(entries)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
