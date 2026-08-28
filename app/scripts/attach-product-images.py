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
import unicodedata
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
    u = u.replace("/hr/", "/").replace("/en/", "/")
    return u


BAD_IMAGE_TOKS = (
    "placeholder",
    "no-image",
    "blank.gif",
    "logo",
    "fss_share",
    "category-backgrounds",
    "payment-info",
    "store_logo",
    "facebook.com",
    "design/content",
)


def is_http_image(url: object) -> bool:
    if not isinstance(url, str):
        return False
    u = url.strip()
    if u.startswith("http://"):
        u = "https://" + u[len("http://") :]
    if not u.startswith("https://"):
        return False
    low = u.lower()
    if any(tok in low for tok in BAD_IMAGE_TOKS):
        return False
    return True


def as_https(url: str) -> str:
    url = url.strip().replace("\\u0026", "&")
    if url.startswith("http://"):
        return "https://" + url[len("http://") :]
    return url


OG_IMAGE_RE = re.compile(
    r'property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']',
    re.I,
)
OG_IMAGE_RE_REV = re.compile(
    r'content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']',
    re.I,
)
JSONLD_RE = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.I | re.S,
)


def absolutize(src: str, page_url: str) -> str:
    src = src.strip()
    if src.startswith("//"):
        return "https:" + src
    if src.startswith("/"):
        p = urlparse(page_url)
        return f"{p.scheme}://{p.netloc}{src}"
    if src.startswith("http://") or src.startswith("https://"):
        return src
    p = urlparse(page_url)
    base = f"{p.scheme}://{p.netloc}{p.path.rsplit('/', 1)[0]}/"
    return base + src


def extract_product_image(html: str, page_url: str) -> str | None:
    """Best product photo from a shop HTML page (og:image / JSON-LD / product img)."""
    cands: list[str] = []
    for rx in (OG_IMAGE_RE, OG_IMAGE_RE_REV):
        m = rx.search(html)
        if m:
            cands.append(m.group(1))
    for block in JSONLD_RE.findall(html):
        cands.extend(re.findall(r'"image"\s*:\s*"(https?://[^"]+)"', block))
        cands.extend(
            re.findall(
                r'"url"\s*:\s*"(https?://[^"]+\.(?:jpg|jpeg|png|webp)[^"]*)"',
                block,
                re.I,
            )
        )
        cands.extend(re.findall(r'"url"\s*:\s*"(/[^"]+\.(?:jpg|jpeg|png|webp)[^"]*)"', block, re.I))
    cands.extend(re.findall(r'src="([^"]*images/optimize/[^"]+)"', html, re.I))
    # eCuga Saleor: bottle photos live in __NEXT_DATA__, not og:image.
    cands.extend(
        re.findall(
            r'(https?://[^"\'\\s]+/media/thumbnails/products/[^"\'\\s]+\.(?:jpg|jpeg|png|webp))',
            html,
            re.I,
        )
    )
    cands.extend(
        re.findall(
            r'(/media/thumbnails/products/[^"\'\\s]+\.(?:jpg|jpeg|png|webp))',
            html,
            re.I,
        )
    )
    seen: set[str] = set()
    for raw in cands:
        img = as_https(absolutize(raw, page_url))
        if img in seen:
            continue
        seen.add(img)
        if is_http_image(img):
            return img
    return None


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
    headers = {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,hr;q=0.8",
    }
    for attempt in range(5):
        req = urllib.request.Request(url, headers=headers)
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


def vitola_slug(label: str) -> str:
    """Isti slug kao lib/cigarItemId.ts — ključ slike po vitoli."""
    s = unicodedata.normalize("NFKD", label)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("'", "").replace("’", "").replace("`", "")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def vitola_item_id(cigar_id: str, vitola_name: str) -> str:
    slug = vitola_slug(vitola_name)
    return f"{cigar_id}@{slug}" if slug else cigar_id


def vitola_urls(v: dict) -> list[str]:
    urls: list[str] = []
    if v.get("url"):
        urls.append(str(v["url"]))
    rl = v.get("regionLinks") or {}
    if isinstance(rl, dict):
        for rec in rl.values():
            if isinstance(rec, dict) and rec.get("url"):
                urls.append(str(rec["url"]))
    return urls


def lookup_url_image(url_map: dict[str, str], url: str) -> str | None:
    for candidate in (url, shop_fetch_url(url)):
        img = url_map.get(norm_url(candidate))
        if img:
            return img
    return None


def apply_vitola_url_images(cigars: list[dict], url_map: dict[str, str], dest: dict[str, str]) -> None:
    """Zapis `cig-x@vitola-slug` kad product URL vitole nosi sliku."""
    for c in cigars:
        cid = c.get("id")
        if not isinstance(cid, str):
            continue
        vitolas = [v for v in (c.get("vitolas") or []) if isinstance(v, dict)]
        if len(vitolas) <= 1:
            continue
        for v in vitolas:
            name = v.get("name")
            if not isinstance(name, str) or not name.strip():
                continue
            key = vitola_item_id(cid, name)
            if key in dest:
                continue
            for u in vitola_urls(v):
                found = lookup_url_image(url_map, u)
                if found:
                    dest[key] = found
                    break


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
        vitolas = [v for v in (c.get("vitolas") or []) if isinstance(v, dict)]
        if len(vitolas) > 1:
            for v in vitolas:
                name = v.get("name")
                if not isinstance(name, str) or not name.strip():
                    continue
                voffers: list[dict] = []
                for u in vitola_urls(v):
                    voffers.extend(by_url.get(norm_url(u), []))
                vimg = pick_offer_image(voffers)
                if vimg:
                    out[vitola_item_id(cid, name)] = vimg
    return out


def fetch_json(url: str) -> object:
    last: Exception | None = None
    headers = {
        "User-Agent": UA,
        "Accept": "application/json",
    }
    for attempt in range(5):
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 500, 502, 503, 504) and attempt < 4:
                time.sleep(2 ** attempt)
                continue
            raise
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            last = e
            if attempt < 4:
                time.sleep(2 ** attempt)
                continue
            raise
    raise last or RuntimeError(url)


WC_STORES = (
    ("humidor", "https://humidor.hr/wp-json/wc/store/v1/products"),
    ("havana", "https://havana-cigar-shop.com/wp-json/wc/store/v1/products"),
    ("cigarsdaily", "https://cigarsdaily.com/wp-json/wc/store/v1/products"),
)

HOST_PREF = (
    "humidor.hr",
    "havana-cigar-shop.com",
    "cigarworld.de",
    "holts.com",
    "cigarsdaily.com",
    "neptunecigar.com",
    "famous-smoke.com",
    "cgarsltd.co.uk",
    "cigarpassion.ch",
    "allez.hr",
    "ecuga.com",
    "webshop.rotodinamic.hr",
    "kavijarshop.com",
    "vivat-finavina.hr",
)


def scrape_wc_store(name: str, api: str) -> dict[str, str]:
    out: dict[str, str] = {}
    print(f"  WooCommerce {name} …", flush=True)
    for page in range(1, 201):
        url = f"{api}?per_page=100&page={page}"
        try:
            data = fetch_json(url)
        except urllib.error.HTTPError as e:
            if e.code in (400, 404):
                break
            print(f"    skip page {page}: HTTP {e.code}", flush=True)
            break
        if not isinstance(data, list) or not data:
            break
        for product in data:
            if not isinstance(product, dict):
                continue
            permalink = product.get("permalink")
            images = product.get("images") if isinstance(product.get("images"), list) else []
            src = None
            if images and isinstance(images[0], dict):
                src = images[0].get("src") or images[0].get("thumbnail")
            if isinstance(permalink, str) and is_http_image(src):
                out[norm_url(permalink)] = as_https(str(src))
        print(f"    page {page}: +{len(data)} mapped {len(out)}", flush=True)
        if len(data) < 100:
            break
        time.sleep(0.15)
    return out


def token_set(text: str) -> set[str]:
    """Tokeni za fuzzy match brand/line/vitola ↔ naslov proizvoda u dućanu."""
    s = unicodedata.normalize("NFKD", text or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    stop = {
        "cigar",
        "cigars",
        "cigara",
        "cigare",
        "the",
        "and",
        "by",
        "de",
        "la",
        "el",
        "los",
        "pack",
        "box",
        "single",
        "tube",
        "tubos",
    }
    return {t for t in s.split() if len(t) >= 2 and t not in stop}


def scrape_wc_inventory(name: str, api: str) -> list[dict]:
    """Pun inventar WooCommerce: ime + slika (za match bez product URL-a)."""
    rows: list[dict] = []
    print(f"  WooCommerce inventory {name} …", flush=True)
    for page in range(1, 201):
        url = f"{api}?per_page=100&page={page}"
        try:
            data = fetch_json(url)
        except urllib.error.HTTPError as e:
            if e.code in (400, 404):
                break
            print(f"    skip page {page}: HTTP {e.code}", flush=True)
            break
        if not isinstance(data, list) or not data:
            break
        for product in data:
            if not isinstance(product, dict):
                continue
            pname = product.get("name")
            images = product.get("images") if isinstance(product.get("images"), list) else []
            src = None
            if images and isinstance(images[0], dict):
                src = images[0].get("src") or images[0].get("thumbnail")
            if not isinstance(pname, str) or not is_http_image(src):
                continue
            rows.append(
                {
                    "name": pname,
                    "tokens": token_set(pname),
                    "image": as_https(str(src)),
                    "shop": name,
                }
            )
        print(f"    page {page}: inventory {len(rows)}", flush=True)
        if len(data) < 100:
            break
        time.sleep(0.15)
    return rows


def best_inventory_match(
    query_tokens: set[str],
    inventory: list[dict],
    *,
    min_overlap: int = 2,
) -> str | None:
    """Vrati sliku kad naslov dućana pokriva dovoljno tokena upita."""
    if len(query_tokens) < 2:
        return None
    best_img: str | None = None
    best_score = 0.0
    for row in inventory:
        tokens: set[str] = row["tokens"]
        hit = query_tokens & tokens
        if len(hit) < min_overlap:
            continue
        # brand+line moraju biti u naslovu — overlap / query
        score = len(hit) / len(query_tokens)
        # preferiraj kad gotovo svi tokeni upita postoje
        if score > best_score or (score == best_score and len(hit) > best_score):
            # odbij ako naslov ima previše suvišnih riječi (sampler paketi)
            extra = len(tokens - query_tokens)
            if extra > max(4, len(query_tokens)):
                continue
            best_score = score
            best_img = row["image"]
    if best_score >= 0.55:
        return best_img
    return None


def fill_missing_by_name_match(
    cigars: list[dict],
    inventory: list[dict],
    dest: dict[str, str],
) -> tuple[int, int]:
    """
    Treći način: bez product URL-a u katalogu, spoji po brand+line(+vitola)
    s inventarom dućana (WooCommerce name → image).
    """
    line_hits = 0
    vitola_hits = 0
    for c in cigars:
        cid = c.get("id")
        brand = c.get("brand")
        line = c.get("line")
        if not isinstance(cid, str) or not isinstance(brand, str) or not isinstance(line, str):
            continue
        base_tokens = token_set(f"{brand} {line}")
        if cid not in dest:
            img = best_inventory_match(base_tokens, inventory)
            if img:
                dest[cid] = img
                line_hits += 1
        vitolas = [v for v in (c.get("vitolas") or []) if isinstance(v, dict)]
        if len(vitolas) <= 1:
            continue
        for v in vitolas:
            name = v.get("name")
            if not isinstance(name, str) or not name.strip():
                continue
            key = vitola_item_id(cid, name)
            if key in dest:
                continue
            q = base_tokens | token_set(name)
            img = best_inventory_match(q, inventory, min_overlap=3)
            if img:
                dest[key] = img
                vitola_hits += 1
    return line_hits, vitola_hits


def apply_url_images(items: list[dict], url_fn, url_map: dict[str, str], dest: dict[str, str]) -> None:
    for item in items:
        iid = item.get("id")
        if not isinstance(iid, str) or iid in dest:
            continue
        found: str | None = None
        for u in url_fn(item):
            for candidate in (u, shop_fetch_url(u)):
                img = url_map.get(norm_url(candidate))
                if img:
                    found = img
                    break
            if found:
                dest[iid] = found
                break


def shop_fetch_url(url: str) -> str:
    """Rewrite shop URLs to a page that actually contains the product photo."""
    p = urlparse(url)
    host = p.netloc.replace("www.", "")
    if host == "ecuga.com" and "/katalog/" in p.path:
        slug = p.path.rstrip("/").split("/")[-1]
        if slug:
            return f"https://ecuga.com/proizvod/{slug}"
    return url


def preferred_url(urls: list[str]) -> str | None:
    ranked: list[tuple[int, str]] = []
    for u in urls:
        host = urlparse(u).netloc.replace("www.", "")
        try:
            rank = HOST_PREF.index(host)
        except ValueError:
            rank = 50
        ranked.append((rank, u))
    if not ranked:
        return None
    ranked.sort(key=lambda x: x[0])
    return ranked[0][1]


def load_cache(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return {k: v for k, v in data.items() if isinstance(k, str) and is_http_image(v)}


def save_cache(path: Path, cache: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fetch_page_images(urls: list[str], cache: dict[str, str]) -> dict[str, str]:
    """Fetch product pages and extract a photo. Cache by normalized URL."""
    out: dict[str, str] = {}
    pending: list[str] = []
    seen: set[str] = set()
    for url in urls:
        key = norm_url(url)
        if not key or key in seen:
            continue
        seen.add(key)
        if key in cache:
            out[key] = cache[key]
        else:
            pending.append(url)
    print(f"  product pages: {len(out)} cached, {len(pending)} to fetch", flush=True)
    for i, url in enumerate(pending, 1):
        key = norm_url(url)
        try:
            html = fetch_html(url)
            img = extract_product_image(html, url)
        except Exception as e:
            print(f"    skip {url}: {e}", flush=True)
            img = None
        if img:
            cache[key] = img
            out[key] = img
        if i % 25 == 0 or i == len(pending):
            print(f"    fetched {i}/{len(pending)} hits {len(out)}", flush=True)
            save_cache(SCRIPTS / ".cache" / "shop-page-images.json", cache)
        time.sleep(0.22)
    return out


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
        img = extract_product_image(html, url)
        if img:
            allez_map[norm_url(url)] = img
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


def drink_urls(d: dict) -> list[str]:
    url = d.get("priceUrl")
    return [str(url)] if isinstance(url, str) and url else []


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Attach scraped product image URLs to app ids")
    p.add_argument("--unified", default=str(DEFAULT_UNIFIED))
    p.add_argument("--out", default=str(OUT_JSON))
    p.add_argument("--skip-allez", action="store_true")
    p.add_argument("--skip-wc", action="store_true")
    p.add_argument("--skip-pages", action="store_true")
    p.add_argument(
        "--skip-search",
        action="store_true",
        help="Skip name-match fill against WooCommerce inventory",
    )
    p.add_argument("--limit", type=int, default=0, help="Max product pages to fetch (0 = all)")
    return p.parse_args()


def merge_keep(dest: dict[str, str], extra: dict[str, str]) -> None:
    for k, v in extra.items():
        if k not in dest and is_http_image(v):
            dest[k] = v


def main() -> None:
    args = parse_args()
    cigars = json.loads((DATA / "cigars.json").read_text(encoding="utf-8"))
    drinks = load_drink_lists()
    cigar_map: dict[str, str] = {}
    drink_map: dict[str, str] = {}
    url_map: dict[str, str] = {}

    existing = Path(args.out)
    if existing.exists():
        prev = json.loads(existing.read_text(encoding="utf-8"))
        merge_keep(cigar_map, prev.get("cigars") or {})
        merge_keep(drink_map, prev.get("drinks") or {})
        print(f"existing map: cigars {len(cigar_map)} drinks {len(drink_map)}", flush=True)

    unified = Path(args.unified)
    if unified.exists():
        merge_keep(cigar_map, cigar_images_from_unified(unified, cigars))
        print(f"after unified: cigars {len(cigar_map)}", flush=True)
    else:
        print(f"no unified catalog at {unified} — skipping", flush=True)

    if not args.skip_wc:
        print("scraping WooCommerce stores …", flush=True)
        for name, api in WC_STORES:
            try:
                url_map.update(scrape_wc_store(name, api))
            except Exception as e:
                print(f"  {name} failed: {e}", flush=True)
        apply_url_images(cigars, cigar_urls, url_map, cigar_map)
        print(f"after WooCommerce: cigars {len(cigar_map)}", flush=True)

    apply_vitola_url_images(cigars, url_map, cigar_map)
    vitola_after_wc = sum(1 for k in cigar_map if "@" in k)
    print(f"vitola-scoped keys after WC/unified: {vitola_after_wc}", flush=True)

    if not args.skip_allez:
        print("scraping allez.hr listings for bottle photos …", flush=True)
        allez_map = scrape_allez_images()
        fill_missing_allez_product_images(drinks, allez_map)
        apply_url_images(drinks, drink_urls, allez_map, drink_map)
        print(f"after allez: drinks {len(drink_map)}", flush=True)

    if not args.skip_pages:
        cache_path = SCRIPTS / ".cache" / "shop-page-images.json"
        cache = load_cache(cache_path)
        missing_urls: list[str] = []
        for c in cigars:
            cid = c.get("id")
            if not isinstance(cid, str):
                continue
            if cid not in cigar_map:
                pref = preferred_url(cigar_urls(c))
                if pref:
                    missing_urls.append(shop_fetch_url(pref))
            vitolas = [v for v in (c.get("vitolas") or []) if isinstance(v, dict)]
            if len(vitolas) > 1:
                for v in vitolas:
                    name = v.get("name")
                    if not isinstance(name, str) or not name.strip():
                        continue
                    vid = vitola_item_id(cid, name)
                    if vid in cigar_map:
                        continue
                    pref = preferred_url(vitola_urls(v))
                    if pref:
                        missing_urls.append(shop_fetch_url(pref))
        for d in drinks:
            did = d.get("id")
            if not isinstance(did, str) or did in drink_map:
                continue
            pref = preferred_url(drink_urls(d))
            if pref:
                missing_urls.append(shop_fetch_url(pref))
        if args.limit:
            missing_urls = missing_urls[: args.limit]
        page_map = fetch_page_images(missing_urls, cache)
        save_cache(cache_path, cache)
        url_map.update(page_map)
        apply_url_images(cigars, cigar_urls, page_map, cigar_map)
        apply_vitola_url_images(cigars, url_map, cigar_map)
        apply_url_images(drinks, drink_urls, page_map, drink_map)
        print(f"after product pages: cigars {len(cigar_map)} drinks {len(drink_map)}", flush=True)

    apply_vitola_url_images(cigars, url_map, cigar_map)
    vitola_total = sum(1 for k in cigar_map if "@" in k)
    print(f"vitola-scoped cigar images: {vitola_total}", flush=True)

    if not args.skip_search:
        print("name-match fill against WooCommerce inventory …", flush=True)
        inventory: list[dict] = []
        for name, api in WC_STORES:
            try:
                inventory.extend(scrape_wc_inventory(name, api))
            except Exception as e:
                print(f"  inventory {name} failed: {e}", flush=True)
        before = len(cigar_map)
        line_n, vitola_n = fill_missing_by_name_match(cigars, inventory, cigar_map)
        print(
            f"after name-match: +{len(cigar_map) - before} "
            f"(lines {line_n}, vitolas {vitola_n}); inventory {len(inventory)}",
            flush=True,
        )

    known_lines = {c["id"] for c in cigars if isinstance(c.get("id"), str)}

    def keep_cigar_key(key: str) -> bool:
        line_id = key.split("@", 1)[0]
        return line_id in known_lines

    known_drinks: set[str] = set()
    for fname in (
        "rums.json",
        "whiskies.json",
        "gins.json",
        "tequilas.json",
        "brandies.json",
        "wines.json",
        "digestifs.json",
        "coffees.json",
    ):
        path = DATA / fname
        if not path.exists():
            continue
        for row in json.loads(path.read_text(encoding="utf-8")):
            if isinstance(row, dict) and isinstance(row.get("id"), str):
                known_drinks.add(row["id"])

    def keep_drink_key(key: str) -> bool:
        return key in known_drinks

    payload = {
        "schemaVersion": 1,
        "note": (
            "Remote product photos from shop scrapes (not invented). "
            "Keys: cigars.json line id, or cig-x@vitola-slug when the shop "
            "has a per-vitola product page. Used on detail/line sheets."
        ),
        "cigars": {k: cigar_map[k] for k in sorted(cigar_map) if keep_cigar_key(k)},
        "drinks": {k: drink_map[k] for k in sorted(drink_map) if keep_drink_key(k)},
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"wrote {out} cigars={len(payload['cigars'])}/{len(cigars)} "
        f"drinks={len(payload['drinks'])}/{len(drinks)} ({out.stat().st_size // 1024} KiB)",
        flush=True,
    )


if __name__ == "__main__":
    main()
