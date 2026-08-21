# -*- coding: utf-8 -*-
"""Scrape drink shop listings (Tipsy, CugaKlik, Miva, Roto, Humidor) -> raw JSON.

Cooltura: no public product catalogue (pub / Wolt only) — skipped with a note.
Havana Cigar Shop webshop: cigars/accessories only — no bottle catalogue.

  python scripts/scrape-drink-shop-listings.py
  python scripts/scrape-drink-shop-listings.py --shops tipsy,cugaklik,miva
  python scripts/scrape-drink-shop-listings.py --shops humidor --merge
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
OUT = HERE / "output" / "drink_shop_listings_raw.json"
UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

SHOP_META = {
    "tipsy": {"label": "tipsy.hr", "host": "tipsy.hr"},
    "cugaklik": {"label": "cugaklik.hr", "host": "cugaklik.hr"},
    "miva": {"label": "Miva", "host": "miva.com.hr"},
    "roto": {"label": "webshop.rotodinamic.hr", "host": "webshop.rotodinamic.hr"},
    "humidor": {"label": "humidor.hr", "host": "humidor.hr"},
    "coolitura": {"label": "Cooltura", "host": None},  # no catalog
}

TIPSY_CATEGORIES = [
    "https://tipsy.hr/zestice/whiskey-zestice/",
    "https://tipsy.hr/zestice/rum-zestice/",
    "https://tipsy.hr/zestice/gin-zestice/",
    "https://tipsy.hr/zestice/cognac-zestice/",
    "https://tipsy.hr/zestice/likeri/",
]

# WooCommerce Store API category ids (from shop HTML / probe)
TIPSY_WC_CATEGORIES = [
    ("58", "whiskey"),
    ("61", "rum"),
]

CUGAKLIK_CATEGORIES = [
    "https://www.cugaklik.hr/kategorija/whisky/",
    "https://www.cugaklik.hr/kategorija/zestoka-cuga/rum/",
    "https://www.cugaklik.hr/kategorija/zestoka-cuga/gin/",
    "https://www.cugaklik.hr/kategorija/zestoka-cuga/cognac/",
    "https://www.cugaklik.hr/kategorija/zestoka-cuga/liker/",
]

CUGAKLIK_WC_CATEGORIES = [
    ("71", "whisky"),
]

MIVA_CATEGORIES = [
    "https://www.miva.com.hr/zestoka-pica?num_per_page=96",
    "https://www.miva.com.hr/vina?num_per_page=96",
]

ROTO_CATEGORIES = [
    "https://webshop.rotodinamic.hr/jaka-alkoholna-pica",
    "https://webshop.rotodinamic.hr/jaka-alkoholna-pica/filter/19-vrsta-jap,Whisky",
    "https://webshop.rotodinamic.hr/jaka-alkoholna-pica/filter/19-vrsta-jap,Gin",
    "https://webshop.rotodinamic.hr/jaka-alkoholna-pica/filter/19-vrsta-jap,konjak",
    "https://webshop.rotodinamic.hr/jaka-alkoholna-pica/filter/19-vrsta-jap,Liker",
]

# WooCommerce Store API — HR parent "Alkoholna pića" (id 45, 240 SKUs).
# English twin (id 57) is the same catalogue; do not scrape both.
HUMIDOR_WC_CATEGORIES = [
    ("47", "whisky"),
    ("51", "rum"),
    ("49", "brandy"),
    ("265", "gin"),
    ("275", "tequila"),
    ("271", "liqueur"),
    ("263", "wine"),
]

# Miniatures / samples are not the 0.7 L bottle in the app catalogue.
MINI_RE = re.compile(
    r"(?:0\s*[,.]\s*0[1-5]\s*l|\b50\s*ml\b|\b5\s*cl\b|\b0,05\b)",
    re.I,
)


def fetch(url: str, cookie: str | None = None) -> str:
    headers = dict(UA)
    if cookie:
        headers["Cookie"] = cookie
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read().decode("utf-8", "replace")


def fetch_json(url: str) -> list | dict:
    req = urllib.request.Request(url, headers={**UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


def parse_price(text: str | None) -> float | None:
    if not text:
        return None
    # prefer last price (sale price often last)
    nums = re.findall(r"(\d{1,5}[.,]\d{2})", text.replace("\xa0", " "))
    if not nums:
        return None
    return float(nums[-1].replace(",", "."))


def tipsy_page(html: str, category: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for card in soup.select(".product-grid-item"):
        a = card.select_one("a[href]")
        title = card.select_one(".product-title, h3")
        price_el = card.select_one(".price")
        if not a or not title:
            continue
        href = a["href"]
        if href.startswith("/"):
            href = urljoin("https://tipsy.hr", href)
        # skip pure category links
        if href.rstrip("/").count("/") < 5 and href.rstrip("/").endswith(
            ("whiskey-zestice", "rum-zestice", "gin-zestice", "cognac-zestice", "likeri")
        ):
            continue
        name = title.get_text(strip=True)
        if not name:
            continue
        items.append(
            {
                "shop": "tipsy",
                "shopLabel": SHOP_META["tipsy"]["label"],
                "name": name,
                "price_eur": parse_price(price_el.get_text(" ", strip=True) if price_el else None),
                "url": href.split("?")[0],
                "category": category,
            }
        )
    return items


def tipsy_max_page(html: str) -> int:
    pages = [int(p) for p in re.findall(r"/page/(\d+)/", html)]
    return max(pages) if pages else 1


def cugaklik_page(html: str, category: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    items = []
    seen_local: set[str] = set()
    for a in soup.select('a[href*="/proizvod/"]'):
        href = a["href"].split("?")[0]
        if href in seen_local:
            continue
        name = a.get_text(strip=True)
        if not name or name.lower() in ("pročitaj više", "procitaj vise", "read more"):
            # try title from nearby
            parent = a.find_parent(["li", "div", "article"])
            t = parent.select_one("h2, h3, .woocommerce-loop-product__title") if parent else None
            name = t.get_text(strip=True) if t else ""
        # strip glued price from title
        name = re.sub(r"\d+[.,]\d{2}\s*€?\s*$", "", name).strip()
        if not name or len(name) < 3:
            continue
        parent = a.find_parent(["li", "div", "article"])
        price_el = parent.select_one(".price, .woocommerce-Price-amount") if parent else None
        price = parse_price(price_el.get_text(" ", strip=True) if price_el else a.get_text(" ", strip=True))
        if not href.startswith("http"):
            href = urljoin("https://www.cugaklik.hr", href)
        seen_local.add(href)
        items.append(
            {
                "shop": "cugaklik",
                "shopLabel": SHOP_META["cugaklik"]["label"],
                "name": name,
                "price_eur": price,
                "url": href,
                "category": category,
            }
        )
    return items


def miva_page(html: str, category: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    items = []
    seen_local: set[str] = set()
    for a in soup.select('a[href*="/asortiman/proizvod-"]'):
        href = a["href"].split("?")[0]
        if not href.startswith("http"):
            href = urljoin("https://www.miva.com.hr", href)
        if href in seen_local:
            continue
        name = a.get_text(strip=True)
        parent = a.find_parent(["div", "li", "article", "td"])
        if not name and parent:
            t = parent.select_one("h2, h3, .title, .name")
            name = t.get_text(strip=True) if t else ""
        if not name:
            # slug fallback
            slug = href.rstrip("/").split("/")[-1]
            name = re.sub(r"^proizvod-\d+-", "", slug).replace("-", " ").strip()
        price_el = parent.select_one(".price, [itemprop=price], [ee-price]") if parent else None
        price = parse_price(price_el.get_text(" ", strip=True) if price_el else None)
        seen_local.add(href)
        items.append(
            {
                "shop": "miva",
                "shopLabel": SHOP_META["miva"]["label"],
                "name": name,
                "price_eur": price,
                "url": href,
                "category": category,
            }
        )
    return items


def scrape_miva() -> list[dict]:
    print("miva.com.hr …")
    out: list[dict] = []
    seen: set[str] = set()
    for cat in MIVA_CATEGORIES:
        # Pagination: /stranica-N?num_per_page=96 (probe 201e0564)
        base = cat.split("?")[0]
        qs = "num_per_page=96"
        for page in range(1, 40):
            if page == 1:
                url = f"{base}?{qs}"
            else:
                url = f"{base}/stranica-{page}?{qs}"
            try:
                html = fetch(url)
            except urllib.error.HTTPError:
                break
            batch = miva_page(html, cat)
            new = 0
            for it in batch:
                if it["url"] in seen:
                    continue
                seen.add(it["url"])
                out.append(it)
                new += 1
            if page > 1 and new == 0:
                break
            time.sleep(0.35)
        print(f"  {cat} -> {len(seen)} unique so far")
    print(f"  miva total {len(out)}")
    return out


def scrape_roto() -> list[dict]:
    """OpenCart SSR cards: .item.single-product (ageCheck cookie optional)."""
    print("webshop.rotodinamic.hr …")
    out: list[dict] = []
    seen: set[str] = set()
    cookie = "ageCheck=true"
    for cat in ROTO_CATEGORIES:
        for page in range(1, 25):
            url = cat if page == 1 else f"{cat}?page={page}"
            try:
                html = fetch(url, cookie=cookie)
            except urllib.error.HTTPError:
                break
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select(".item.single-product")
            if not cards:
                if page == 1:
                    print(f"  no cards on {url}")
                break
            new = 0
            for card in cards:
                a = card.select_one("a[href]")
                name_el = card.select_one("span.product-name, .product-name")
                price_el = card.select_one(".price-new") or card.select_one(".price")
                if not a:
                    continue
                href = a["href"].split("?")[0]
                name = name_el.get_text(strip=True) if name_el else a.get_text(strip=True)
                # strip glued volume suffixes like 0.7l
                name = re.sub(r"(\d)[lL]\s*$", r"\1", name)
                name = re.sub(r"(\d)[.,](\d)\s*[lL]\s*$", "", name).strip()
                if not name:
                    continue
                if href in seen:
                    continue
                seen.add(href)
                # price-new is the current price; avoid "najniža cijena" blob
                price_txt = price_el.get_text(" ", strip=True) if price_el else None
                if price_txt and "Najniža" in price_txt:
                    # take first euro amount after price-new element only — usually first match is current
                    m = re.search(r"(\d{1,5}[.,]\d{2})", price_txt)
                    price = float(m.group(1).replace(",", ".")) if m else None
                else:
                    price = parse_price(price_txt)
                out.append(
                    {
                        "shop": "roto",
                        "shopLabel": SHOP_META["roto"]["label"],
                        "name": name,
                        "price_eur": price,
                        "url": href,
                        "category": cat,
                    }
                )
                new += 1
            if new == 0:
                break
            time.sleep(0.35)
        print(f"  {cat} -> {len(seen)} unique so far")
    print(f"  roto total {len(out)}")
    return out


def scrape_wc_store(base: str, shop: str, categories: list[tuple[str, str]]) -> list[dict]:
    """WooCommerce Store API pagination."""
    out: list[dict] = []
    seen: set[str] = set()
    for cat_id, label in categories:
        page = 1
        while page <= 50:
            url = f"{base}/wp-json/wc/store/v1/products?category={cat_id}&per_page=100&page={page}"
            try:
                data = fetch_json(url)
            except urllib.error.HTTPError:
                break
            if not isinstance(data, list) or not data:
                break
            for p in data:
                href = (p.get("permalink") or "").split("?")[0]
                name = p.get("name") or ""
                if not href or not name or href in seen:
                    continue
                prices = p.get("prices") or {}
                # minor units (e.g. 5875 = 58.75 EUR)
                amount = prices.get("price") or prices.get("regular_price")
                price = None
                if amount is not None:
                    try:
                        price = float(amount) / 100.0
                    except (TypeError, ValueError):
                        price = None
                seen.add(href)
                out.append(
                    {
                        "shop": shop,
                        "shopLabel": SHOP_META[shop]["label"],
                        "name": BeautifulSoup(name, "html.parser").get_text(strip=True),
                        "price_eur": price,
                        "url": href,
                        "category": label,
                    }
                )
            page += 1
            time.sleep(0.3)
        print(f"  wc {shop} cat={cat_id} -> {len(seen)} unique so far")
    return out


def scrape_humidor() -> list[dict]:
    """HR spirits catalogue at The Humidor (WooCommerce Store API)."""
    print("humidor.hr …")
    out = scrape_wc_store("https://humidor.hr", "humidor", HUMIDOR_WC_CATEGORIES)
    kept: list[dict] = []
    skipped_mini = 0
    seen: set[str] = set()
    for it in out:
        name = it.get("name") or ""
        if MINI_RE.search(name):
            skipped_mini += 1
            continue
        url = (it.get("url") or "").split("?")[0]
        if "__trashed" in url.lower():
            skipped_mini += 1
            continue
        # Prefer /hr/ product path when the API returns /en/ twin.
        url = url.replace("/en/proizvod/", "/hr/proizvod/").replace(
            "/en/product/", "/hr/proizvod/"
        )
        if not url or url in seen:
            continue
        seen.add(url)
        it["url"] = url
        kept.append(it)
    print(f"  humidor total {len(kept)} (skipped minis={skipped_mini})")
    return kept


def scrape_tipsy() -> list[dict]:
    print("tipsy.hr …")
    # Prefer Store API for whisky/rum; HTML for other cats
    out = scrape_wc_store("https://tipsy.hr", "tipsy", TIPSY_WC_CATEGORIES)
    seen = {it["url"] for it in out}
    for cat in TIPSY_CATEGORIES:
        try:
            first = fetch(cat)
        except urllib.error.HTTPError as e:
            print(f"  skip {cat}: {e}")
            continue
        max_page = tipsy_max_page(first)
        for page in range(1, max_page + 1):
            url = cat if page == 1 else cat.rstrip("/") + f"/page/{page}/"
            html = first if page == 1 else fetch(url)
            for it in tipsy_page(html, cat):
                if it["url"] in seen:
                    continue
                seen.add(it["url"])
                out.append(it)
            time.sleep(0.35)
        print(f"  {cat} -> {len(seen)} unique so far")
    print(f"  tipsy total {len(out)}")
    return out


def scrape_cugaklik() -> list[dict]:
    print("cugaklik.hr …")
    out = scrape_wc_store("https://www.cugaklik.hr", "cugaklik", CUGAKLIK_WC_CATEGORIES)
    seen = {it["url"] for it in out}
    # Also walk HTML categories for rum/gin/etc.
    for cat in CUGAKLIK_CATEGORIES:
        page = 1
        empty_streak = 0
        while page <= 40:
            url = cat if page == 1 else cat.rstrip("/") + f"/page/{page}/"
            try:
                html = fetch(url)
            except urllib.error.HTTPError:
                break
            batch = cugaklik_page(html, cat)
            new = 0
            for it in batch:
                if it["url"] in seen:
                    continue
                seen.add(it["url"])
                out.append(it)
                new += 1
            if new == 0:
                empty_streak += 1
                if empty_streak >= 2:
                    break
            else:
                empty_streak = 0
            page += 1
            time.sleep(0.35)
        print(f"  {cat} -> {len(seen)} unique so far")
    print(f"  cugaklik total {len(out)}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--shops",
        default="tipsy,cugaklik,miva,roto,humidor",
        help="Comma list: tipsy,cugaklik,miva,roto,humidor,coolitura",
    )
    ap.add_argument(
        "--merge",
        action="store_true",
        help="Replace items of the requested shops in the existing raw JSON, keep the rest.",
    )
    args = ap.parse_args()
    wanted = [s.strip().lower() for s in args.shops.split(",") if s.strip()]

    all_items: list[dict] = []
    notes: list[str] = []
    for shop in wanted:
        if shop == "coolitura":
            notes.append("Cooltura: no public web catalogue (Wolt/pub only) — skipped")
            print(notes[-1])
            continue
        if shop == "tipsy":
            all_items.extend(scrape_tipsy())
        elif shop == "cugaklik":
            all_items.extend(scrape_cugaklik())
        elif shop == "miva":
            all_items.extend(scrape_miva())
        elif shop == "roto":
            all_items.extend(scrape_roto())
        elif shop == "humidor":
            all_items.extend(scrape_humidor())
        else:
            raise SystemExit(f"unknown shop: {shop}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    if args.merge and OUT.exists():
        prev = json.loads(OUT.read_text(encoding="utf-8"))
        old_items = prev.get("items") if isinstance(prev, dict) else prev
        old_notes = prev.get("notes") if isinstance(prev, dict) else []
        keep = [it for it in (old_items or []) if (it.get("shop") or "") not in wanted]
        all_items = keep + all_items
        notes = list(old_notes or []) + notes
    payload = {"items": all_items, "notes": notes, "count": len(all_items)}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(all_items)} items)")


if __name__ == "__main__":
    main()
