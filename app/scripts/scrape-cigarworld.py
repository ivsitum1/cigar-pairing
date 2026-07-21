# -*- coding: utf-8 -*-
"""Scrape cigar catalog from CigarWorld.de (EU shop).

Crawls paginated product listing at cigarworld.de/en/zigarren and outputs
raw catalog to app/scripts/output/cigarworld_catalog_raw.json.

Usage:
  python scripts/scrape-cigarworld.py
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

OUTFILE = OUTPUT / "cigarworld_catalog_raw.json"
BASE_URL = "https://www.cigarworld.de"
LISTING_URL = f"{BASE_URL}/en/zigarren"
ITEMS_PER_PAGE = 48
MAX_PAGES = 30
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

COUNTRY_SLUGS = [
    ("kuba", "Kuba"),
    ("nicaragua", "Nikaragva"),
    ("honduras", "Honduras"),
    ("dominikanische-republik", "Dominikana"),
    ("brasilien", "Brazil"),
    ("costa-rica", "Kostarika"),
    ("mexiko", "Meksiko"),
    ("ecuador", "Ekvador"),
    ("panama", "Panama"),
    ("indonesien", "Indonezija"),
    ("italien", "Italija"),
    ("spanien", "Španjolska"),
    ("deutschland", "Njemačka"),
    ("philippinen", "Filipini"),
    ("mosambik", "Mozambik"),
    ("kolumbien", "Kolumbija"),
]

COUNTRY_MAP = {slug: name for slug, name in COUNTRY_SLUGS}


def parse_country_from_url(href: str) -> str | None:
    m = re.search(r"/en/zigarren/([^/]+)/", href)
    if not m:
        m = re.search(r"/en/Zigarren/([^/]+)/", href, re.IGNORECASE)
    if m:
        slug = m.group(1).lower()
        return COUNTRY_MAP.get(slug, slug.replace("-", " ").title())
    return None


def parse_dimensions_from_text(text: str) -> tuple[float | None, float | None]:
    """Extract diameter (cm) and length (cm) from CigarWorld listing text."""
    diam_m = re.search(r"Ø\s*([\d.,]+)\s*cm", text)
    len_m = re.search(r"L\s*([\d.,]+)\s*cm", text)
    diam = float(diam_m.group(1).replace(",", ".")) if diam_m else None
    length = float(len_m.group(1).replace(",", ".")) if len_m else None
    return diam, length


def cm_to_ring_gauge(diam_cm: float) -> int:
    """Convert diameter in cm to ring gauge (1/64 inch)."""
    return round(diam_cm / 2.54 * 64)


def cm_to_mm(cm: float) -> int:
    return round(cm * 10)


def parse_price_eur(text: str) -> float | None:
    m = re.search(r"([\d]+[.,][\d]{2})\s*€", text)
    if m:
        return float(m.group(1).replace(",", "."))
    return None


def parse_brand_line(alt_text: str) -> tuple[str, str]:
    """Split image alt text into brand and line/vitola."""
    parts = alt_text.strip().split(" ", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return alt_text.strip(), ""


def scrape_page(session: requests.Session, page: int, country_slug: str = "") -> list[dict]:
    if country_slug:
        url = f"{LISTING_URL}/{country_slug}?p={page}&o=1&n={ITEMS_PER_PAGE}"
    else:
        url = f"{LISTING_URL}?p={page}&o=1&n={ITEMS_PER_PAGE}"

    for attempt in range(3):
        r = session.get(url, timeout=20)
        if r.status_code == 429:
            wait = 5 * (attempt + 1)
            print(f"  Rate limited (429), waiting {wait}s...")
            time.sleep(wait)
            continue
        break
    else:
        print(f"  Page {page}: rate limit exceeded")
        return []

    if r.status_code != 200:
        print(f"  Page {page}: HTTP {r.status_code}")
        return []

    soup = BeautifulSoup(r.text, "lxml")
    items = soup.select(".search-result-item")
    products = []

    for item in items:
        img = item.select_one("img")
        alt_text = img.get("alt", "").strip() if img else ""
        if not alt_text:
            continue

        link = item.select_one("a")
        href = link.get("href", "") if link else ""
        full_url = f"{BASE_URL}{href}" if href.startswith("/") else href

        full_text = item.get_text(separator=" | ", strip=True)

        price = parse_price_eur(full_text)
        diam_cm, length_cm = parse_dimensions_from_text(full_text)
        country = parse_country_from_url(href)

        ring = cm_to_ring_gauge(diam_cm) if diam_cm else None
        length_mm = cm_to_mm(length_cm) if length_cm else None

        fmt = ""
        if ring and length_mm:
            fmt = f"{ring} x {length_mm}mm"

        rating_m = re.search(r"\((\d+)\)", full_text)
        rating_count = int(rating_m.group(1)) if rating_m else None

        products.append({
            "source": "cigarworld",
            "name": alt_text,
            "url": full_url,
            "priceEUR": price,
            "currency": "EUR",
            "format": fmt,
            "ring": ring,
            "lengthMM": length_mm,
            "country": country,
            "ratingCount": rating_count,
        })

    return products


def get_max_pages(session: requests.Session, country_slug: str = "") -> int:
    path = f"{LISTING_URL}/{country_slug}" if country_slug else LISTING_URL
    r = session.get(f"{path}?p=1&o=1&n={ITEMS_PER_PAGE}", timeout=20)
    soup = BeautifulSoup(r.text, "lxml")
    for sel in soup.select("select"):
        options = sel.find_all("option")
        nums = []
        for o in options:
            txt = o.get_text(strip=True)
            if txt.isdigit():
                nums.append(int(txt))
        if nums:
            return max(nums)
    return 1


def main() -> None:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    all_products: list[dict] = []

    for slug, country_name in COUNTRY_SLUGS:
        max_pages = get_max_pages(session, slug)
        print(f"\n{country_name} ({slug}): {max_pages} pages")

        for page in range(1, min(max_pages, MAX_PAGES) + 1):
            products = scrape_page(session, page, country_slug=slug)
            for p in products:
                if not p.get("country"):
                    p["country"] = country_name
            all_products.extend(products)
            print(f"  Page {page}/{max_pages}: {len(products)} products "
                  f"(total: {len(all_products)})")
            if not products:
                break
            time.sleep(1.5)

    by_url: dict[str, dict] = {}
    for p in all_products:
        by_url[p["url"]] = p
    deduped = list(by_url.values())

    OUTFILE.write_text(json.dumps(deduped, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nDone: {len(deduped)} unique products → {OUTFILE}")


if __name__ == "__main__":
    main()
