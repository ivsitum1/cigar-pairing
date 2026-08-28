# -*- coding: utf-8 -*-
"""Scrape allez.hr spirit category listing pages (shared by gap scan + images)."""
from __future__ import annotations

import re
import time
import urllib.error
import urllib.request

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

ALLEZ_SPIRIT_LISTS: list[tuple[str, str]] = [
    ("https://allez.hr/shop/whiskey", "whiskey"),
    ("https://allez.hr/shop/rum4", "rum"),
    ("https://allez.hr/shop/gin1", "gin"),
    ("https://allez.hr/shop/tequila-mezcal", "tequila"),
    ("https://allez.hr/shop/cognac-calvados-armagnac", "cognac"),
    ("https://allez.hr/shop/absinthe-brandy-grappa-sake", "brandy"),
]


def fetch_html(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,hr;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read().decode("utf-8", "replace")


def parse_listing_page(html: str) -> list[dict]:
    """Return product rows from one Allez category page."""
    items: list[dict] = []
    for part in html.split('class="product-image"')[1:]:
        href_m = re.search(r'<a href="([^"]+)"', part)
        alt_m = re.search(r'alt="([^"]+)"', part)
        if not href_m or not alt_m:
            continue
        href = href_m.group(1)
        if not href.startswith("http"):
            href = "https://allez.hr" + href
        name = alt_m.group(1).strip()
        price_m = re.search(
            r'class="product-price"[^>]*>\s*([\d]{1,4}[.,][\d]{2})\s*€',
            part,
        )
        if not price_m:
            price_m = re.search(r"([\d]{1,4}[.,][\d]{2})\s*€", part[:8000])
        price = None
        if price_m:
            price = float(price_m.group(1).replace(",", "."))
        items.append(
            {
                "shop": "allez",
                "shopLabel": "allez.hr",
                "name": name,
                "price_eur": price,
                "url": href.split("?")[0],
                "category": None,
            }
        )
    return items


def max_page(html: str, base_path: str) -> int:
    pages = [int(p) for p in re.findall(re.escape(base_path) + r"\?page=(\d+)", html)]
    return max(pages) if pages else 1


def scrape_category(base_url: str, label: str, sleep_s: float = 0.35) -> list[dict]:
    base_path = base_url.replace("https://allez.hr", "")
    print(f"  allez: {label} …", flush=True)
    try:
        first = fetch_html(base_url)
    except urllib.error.HTTPError as e:
        print(f"    skip {label}: HTTP {e.code}", flush=True)
        return []
    except urllib.error.URLError as e:
        print(f"    skip {label}: {e}", flush=True)
        return []
    mp = max_page(first, base_path)
    out: list[dict] = []
    seen: set[str] = set()
    for page in range(1, mp + 1):
        url = base_url if page == 1 else f"{base_url}?page={page}"
        try:
            html = first if page == 1 else fetch_html(url)
        except urllib.error.HTTPError as e:
            print(f"    skip page {page}: HTTP {e.code}", flush=True)
            continue
        for item in parse_listing_page(html):
            if item["url"] in seen:
                continue
            seen.add(item["url"])
            item["category"] = label
            out.append(item)
        if page < mp:
            time.sleep(sleep_s)
    print(f"    {len(out)} stavki ({mp} str.)", flush=True)
    return out


def scrape_allez(
    categories: list[tuple[str, str]] | None = None,
    *,
    sleep_s: float = 0.35,
) -> list[dict]:
    """Crawl allez.hr spirit categories; dedupe by product URL."""
    print("allez.hr …", flush=True)
    lists = categories or ALLEZ_SPIRIT_LISTS
    all_items: list[dict] = []
    seen: set[str] = set()
    for url, label in lists:
        for item in scrape_category(url, label, sleep_s=sleep_s):
            if item["url"] in seen:
                continue
            seen.add(item["url"])
            all_items.append(item)
    print(f"  allez total {len(all_items)}", flush=True)
    return all_items
