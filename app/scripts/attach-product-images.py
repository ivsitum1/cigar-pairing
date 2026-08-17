#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build app/src/data/productImages.json from shop scrapes.

Cigar images: cigar_unified_catalog.json offers[].image (shop product photos).
Drink images: Allez listing pages (img inside .product-image), matched by priceUrl.

Does not modify cigars.json / drink JSON. Remote URLs only — not invented.
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
DATA = ROOT / "src" / "data"
OUT_JSON = DATA / "productImages.json"
DEFAULT_UNIFIED = Path("/tmp/cigar_unified_catalog.json")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

SHOP_RANK = {
    "humidor_hr": 0,
    "havana_hr": 1,
    "cigarworld_eu": 2,
    "cigarsdaily_us": 3,
    "holts_us": 4,
}

ALLEZ_LISTS = [
    ("https://allez.hr/shop/whiskey", "whiskey"),
    ("https://allez.hr/shop/rum4", "rum"),
    ("https://allez.hr/shop/gin1", "gin"),
    ("https://allez.hr/shop/tequila-mezcal", "tequila"),
    ("https://allez.hr/shop/cognac-calvados-armagnac", "cognac"),
    ("https://allez.hr/shop/absinthe-brandy-grappa-sake", "brandy"),
]


def norm_url(url: str | None) -> str:
    if not url or not isinstance(url, str):
        return ""
    u = url.split("?")[0].split("#")[0].rstrip("/").lower()
    u = u.replace("://www.", "://")
    return u


def is_http_image(url: object) -> bool:
    if not isinstance(url, str):
        return False
    u = url.strip()
    if not (u.startswith("http://") or u.startswith("https://")):
        return False
    if any(tok in u.lower() for tok in ("placeholder", "no-image", "blank.gif")):
        return False
    return True


def parse_allez_listing(html: str) -> list[tuple[str, str]]:
    """Return (product_url, image_url) pairs from an Allez category page."""
    rows: list[tuple[str, str]] = []
    for part in html.split('class="product-image"')[1:]:
        href_m = re.search(r'<a href="([^"]+)"', part)
        img_m = re.search(r'<img[^>]+src="([^"]+)"', part)
        if not href_m or not img_m:
            continue
        href = href_m.group(1)
        if not href.startswith("http"):
            href = "https://allez.hr" + href
        img = img_m.group(1)
        if img.startswith("//"):
            img = "https:" + img
        elif img.startswith("/"):
            img = "https://allez.hr" + img
        if is_http_image(img):
            rows.append((href, img))
    return rows


def allez_max_page(html: str, list_url: str) -> int:
    path = urlparse(list_url).path
    pages = [int(p) for p in re.findall(rf"{re.escape(path)}\?page=(\d+)", html)]
    return max(pages) if pages else 1


def fetch_html(url: str) -> str:
    last: Exception | None = None
    for attempt in range(5):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                return resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 500, 502, 503, 504) and attempt < 4:
                time.sleep(2 ** attempt)
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
            if attempt < 4:
                time.sleep(2 ** attempt)
                continue
            raise
    raise last or RuntimeError(url)


def scrape_allez_images() -> dict[str, str]:
    by_url: dict[str, str] = {}
    for list_url, label in ALLEZ_LISTS:
        try:
            first = fetch_html(list_url)
        except urllib.error.HTTPError as e:
            print(f"  skip {label}: HTTP {e.code}", flush=True)
            continue
        except Exception as e:
            print(f"  skip {label}: {e}", flush=True)
            continue
        max_page = allez_max_page(first, list_url)
        print(f"  allez {label}: {max_page} pages", flush=True)
        for page in range(1, max_page + 1):
            url = list_url if page == 1 else f"{list_url}?page={page}"
            try:
                html = first if page == 1 else fetch_html(url)
            except urllib.error.HTTPError as e:
                print(f"    skip {label} page {page}: HTTP {e.code}", flush=True)
                time.sleep(2)
                continue
            n_before = len(by_url)
            for href, img in parse_allez_listing(html):
                key = norm_url(href)
                if key and key not in by_url:
                    by_url[key] = img
            if page % 15 == 0 or page == max_page:
                print(f"    page {page}/{max_page} (+{len(by_url) - n_before}) total {len(by_url)}", flush=True)
            if page != max_page:
                time.sleep(0.45)
    return by_url


def cigar_urls(c: dict) -> list[str]:
    urls: list[str] = []
    if c.get("priceUrl"):
        urls.append(str(c["priceUrl"]))
    for v in c.get("vitolas") or []:
        if isinstance(v, dict) and v.get("url"):
            urls.append(str(v["url"]))
        if isinstance(v, dict):
            rl = v.get("regionLinks") or {}
            if isinstance(rl, dict):
                for rec in rl.values():
                    if isinstance(rec, dict) and rec.get("url"):
                        urls.append(str(rec["url"]))
    rl = c.get("regionLinks") or {}
    if isinstance(rl, dict):
        for rec in rl.values():
            if isinstance(rec, dict) and rec.get("url"):
                urls.append(str(rec["url"]))
    return urls


def pick_offer_image(offers: list[dict]) -> str | None:
    ranked: list[tuple[int, str]] = []
    for o in offers:
        img = o.get("image")
        if not is_http_image(img):
            continue
        shop = str(o.get("sourceShopId") or "")
        ranked.append((SHOP_RANK.get(shop, 9), str(img)))
    if not ranked:
        return None
    ranked.sort(key=lambda x: x[0])
    return ranked[0][1]


def cigar_images_from_unified(unified_path: Path, cigars: list[dict]) -> dict[str, str]:
    data = json.loads(unified_path.read_text(encoding="utf-8"))
    rows = data.get("cigars") if isinstance(data, dict) else data
    by_cid: dict[str, list[dict]] = {}
    by_url: dict[str, list[dict]] = {}
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        offers = [o for o in (row.get("offers") or []) if isinstance(o, dict)]
        cid = row.get("catalogId")
        if isinstance(cid, str) and cid:
            by_cid.setdefault(cid, []).extend(offers)
        for o in offers:
            u = norm_url(o.get("url") if isinstance(o.get("url"), str) else None)
            if u:
                by_url.setdefault(u, []).append(o)

    out: dict[str, str] = {}
    for c in cigars:
        cid = c.get("id")
        if not isinstance(cid, str):
            continue
        offers: list[dict] = []
        if cid in by_cid:
            offers.extend(by_cid[cid])
        for u in cigar_urls(c):
            offers.extend(by_url.get(norm_url(u), []))
        img = pick_offer_image(offers)
        if img:
            out[cid] = img
    return out


OG_IMAGE_RE = re.compile(r'property="og:image"\s+content="([^"]+)"', re.I)


def fill_missing_allez_product_images(drinks: list[dict], allez_map: dict[str, str]) -> None:
    """Fetch og:image for remaining allez.hr priceUrls not seen on listing pages."""
    pending: list[str] = []
    seen: set[str] = set()
    for d in drinks:
        url = d.get("priceUrl")
        if not isinstance(url, str) or "allez.hr" not in url:
            continue
        key = norm_url(url)
        if not key or key in allez_map or key in seen:
            continue
        seen.add(key)
        pending.append(url)
    print(f"  allez product-page fallback: {len(pending)} urls", flush=True)
    for i, url in enumerate(pending, 1):
        try:
            html = fetch_html(url)
        except Exception as e:
            print(f"    skip {url}: {e}", flush=True)
            time.sleep(0.4)
            continue
        m = OG_IMAGE_RE.search(html)
        if m and is_http_image(m.group(1)):
            allez_map[norm_url(url)] = m.group(1)
        if i % 10 == 0 or i == len(pending):
            print(f"    {i}/{len(pending)} map size {len(allez_map)}", flush=True)
        time.sleep(0.35)


def drink_images(drinks: list[dict], allez_map: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for d in drinks:
        did = d.get("id")
        url = d.get("priceUrl")
        if not isinstance(did, str) or not isinstance(url, str):
            continue
        img = allez_map.get(norm_url(url))
        if img:
            out[did] = img
    return out


def load_drink_lists() -> list[dict]:
    drinks: list[dict] = []
    for name in (
        "rums.json",
        "whiskies.json",
        "brandies.json",
        "gins.json",
        "wines.json",
        "coffees.json",
        "tequilas.json",
        "digestifs.json",
    ):
        path = DATA / name
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            drinks.extend(x for x in payload if isinstance(x, dict))
    return drinks


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Attach scraped product image URLs to app ids")
    p.add_argument("--unified", default=str(DEFAULT_UNIFIED))
    p.add_argument("--out", default=str(OUT_JSON))
    p.add_argument("--skip-allez", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cigars = json.loads((DATA / "cigars.json").read_text(encoding="utf-8"))
    drinks = load_drink_lists()
    unified = Path(args.unified)
    if not unified.exists():
        raise SystemExit(f"missing unified catalog: {unified}")

    cigar_map = cigar_images_from_unified(unified, cigars)
    print(f"cigars with image: {len(cigar_map)} / {len(cigars)}", flush=True)

    allez_map: dict[str, str] = {}
    if not args.skip_allez:
        print("scraping allez.hr listings for bottle photos …", flush=True)
        allez_map = scrape_allez_images()
        print(f"allez listing photos: {len(allez_map)}", flush=True)
        fill_missing_allez_product_images(drinks, allez_map)
        print(f"allez product photos: {len(allez_map)}", flush=True)
    drink_map = drink_images(drinks, allez_map)
    print(f"drinks with image: {len(drink_map)} / {len(drinks)}", flush=True)

    payload = {
        "schemaVersion": 1,
        "note": (
            "Remote product photos from shop scrapes (not invented). "
            "Keys are cigars.json / drink JSON ids. Used on the detail sheet."
        ),
        "cigars": {k: cigar_map[k] for k in sorted(cigar_map)},
        "drinks": {k: drink_map[k] for k in sorted(drink_map)},
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size // 1024} KiB)", flush=True)


if __name__ == "__main__":
    main()
