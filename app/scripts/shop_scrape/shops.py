from __future__ import annotations

import json
import re
import urllib.error
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from shop_scrape.details import (
    apply_details_to_item,
    parse_cigarworld_variant_info,
    parse_holts_line_details,
    parse_holts_vitola_rows,
    parse_humidor_product_details,
    prefer_holts_pack,
)
from shop_scrape.http import HttpClient, iso_utc_now
from shop_scrape.jsonld import extract_jsonld_products
from shop_scrape.sitemap import iter_sitemap_locs
from shop_scrape.woocommerce import (
    wc_iter_categories,
    wc_iter_products,
    wc_normalize_product,
    wc_pick_cigar_category_ids,
)


@dataclass(frozen=True)
class ShopDef:
    id: str
    name: str
    region: str
    base_url: str
    currency: str | None


def _wrap_shop(shop: ShopDef, *, source_kind: str, entrypoints: list[str], items: list[dict]) -> dict:
    out_items = sorted(items, key=lambda x: (x.get("url") or "", x.get("id") or ""))
    return {
        "shop": {
            "id": shop.id,
            "name": shop.name,
            "region": shop.region,
            "baseUrl": shop.base_url,
        },
        "scrapedAt": iso_utc_now(),
        "currency": shop.currency,
        "source": {"kind": source_kind, "entrypoints": entrypoints},
        "items": out_items,
    }


def _parse_price_eur(text: str) -> float | None:
    if not text:
        return None
    m = re.search(r"([\d]+)[,\.]([\d]{2})", text.replace(" ", "").replace("\xa0", ""))
    return float(f"{m.group(1)}.{m.group(2)}") if m else None


def scrape_humidor_category_listing(client: HttpClient, *, limit: int | None) -> list[dict]:
    """List cigar products from Humidor HTML category pages."""
    base = "https://humidor.hr/hr/kategorija-proizvoda/cigare/"
    items: list[dict] = []
    seen: set[str] = set()

    for page in range(1, 201):
        url = base if page == 1 else f"{base}page/{page}/"
        try:
            html = client.get_text(url)
        except urllib.error.HTTPError as e:
            # WooCommerce category pagination ends with 404.
            if e.code == 404:
                break
            raise
        # Stop on Cloudflare challenge / empty listing.
        if "Just a moment" in html or "Attention Required" in html:
            break
        products = re.findall(
            r'<li[^>]*class="[^"]*\bproduct\b[^"]*"[^>]*>(.*?)</li>',
            html,
            re.IGNORECASE | re.DOTALL,
        )
        if not products:
            break

        for block in products:
            link_m = re.search(
                r'href="(https?://humidor\.hr/[^"]+/proizvod/[^"]+/)"',
                block,
                re.IGNORECASE,
            )
            title_m = re.search(
                r'class="woocommerce-loop-product__title"[^>]*>\s*<a[^>]*>(.*?)</a>',
                block,
                re.IGNORECASE | re.DOTALL,
            )
            if not title_m:
                title_m = re.search(
                    r'woocommerce-loop-product__title[^"]*"[^>]*>(.*?)</',
                    block,
                    re.IGNORECASE | re.DOTALL,
                )
            if not link_m or not title_m:
                continue
            product_url = link_m.group(1)
            if product_url in seen:
                continue
            seen.add(product_url)

            brand_m = re.search(
                r'class="[^"]*product-brand-label[^"]*"[^>]*>(.*?)</span>',
                block,
                re.IGNORECASE | re.DOTALL,
            )
            price_m = re.search(r'class="price"[^>]*>(.*?)</span>\s*</span>', block, re.IGNORECASE | re.DOTALL)
            price_text = price_m.group(1) if price_m else ""
            amount = _parse_price_eur(re.sub(r"<[^>]+>", " ", price_text))

            name = re.sub(r"<[^>]+>", " ", title_m.group(1))
            name = re.sub(r"\s+", " ", name).strip()

            item = {
                "id": product_url.rstrip("/").split("/")[-1],
                "name": name,
                "url": product_url,
                "price": {"amount": amount, "currency": "EUR"} if amount is not None else None,
                "availability": {
                    "inStock": "outofstock" not in block.lower(),
                    "onSale": None,
                },
                "packaging": {"type": "unknown", "count": None},
                "attributes": {
                    "brand": re.sub(r"<[^>]+>", " ", brand_m.group(1)).strip() if brand_m else None,
                    "vitola": None,
                    "dimensions": {"lengthIn": None, "ringGauge": None},
                },
                "categories": [
                    {
                        "name": "Cigare",
                        "slug": "cigare",
                        "url": base,
                    }
                ],
                "images": [],
                "raw": {"listingPage": page},
            }
            items.append(item)
            if limit is not None and len(items) >= limit:
                return items

    return items


def enrich_humidor_item(client: HttpClient, item: dict) -> None:
    url = item.get("url")
    if not isinstance(url, str) or not url:
        return
    try:
        html = client.get_text(url)
    except urllib.error.HTTPError as e:
        item["details"] = None
        item["detailsSource"] = {
            "url": url,
            "extractedFrom": "humidor-product-specs",
            "extractedAt": iso_utc_now(),
            "error": f"HTTP {e.code}",
        }
        return
    details = parse_humidor_product_details(html)
    apply_details_to_item(item, details)
    item["detailsSource"] = {
        "url": url,
        "extractedFrom": "humidor-product-specs",
        "extractedAt": iso_utc_now(),
    }


def scrape_wc_shop(
    client: HttpClient,
    shop: ShopDef,
    *,
    limit: int | None,
    per_page: int = 100,
    max_pages: int = 200,
) -> dict:
    cats = wc_iter_categories(client, shop.base_url)
    cigar_cat_ids = wc_pick_cigar_category_ids(cats)
    query = {"category": str(cigar_cat_ids[0])} if cigar_cat_ids else None
    products = wc_iter_products(
        client,
        shop.base_url,
        query=query,
        per_page=per_page,
        max_pages=max_pages if query is None else min(max_pages, 50),
    )
    items: list[dict] = []
    for p in products:
        items.append(wc_normalize_product(p))
        if limit is not None and len(items) >= limit:
            break

    currency = shop.currency
    if currency is None:
        for it in items:
            price = it.get("price") or {}
            if isinstance(price, dict) and isinstance(price.get("currency"), str) and price["currency"]:
                currency = price["currency"]
                break

    shop_final = ShopDef(shop.id, shop.name, shop.region, shop.base_url, currency)
    entry = f"{shop.base_url}/wp-json/wc/store/products"
    entrypoints = [entry]
    if cigar_cat_ids:
        entrypoints.append(f"{entry}?category={cigar_cat_ids[0]}")
    return _wrap_shop(
        shop_final,
        source_kind="woocommerce-store-api",
        entrypoints=entrypoints,
        items=items,
    )


def scrape_humidor_hr(client: HttpClient, *, limit: int | None) -> dict:
    shop = ShopDef("humidor_hr", "The Humidor", "HR", "https://humidor.hr", "EUR")
    entry = "https://humidor.hr/hr/kategorija-proizvoda/cigare/"
    items = scrape_humidor_category_listing(client, limit=limit)
    print(f"  listed {len(items)} products; enriching details…", flush=True)
    for i, item in enumerate(items, 1):
        enrich_humidor_item(client, item)
        if i % 25 == 0 or i == len(items):
            print(f"  enriched {i}/{len(items)}", flush=True)
    return _wrap_shop(
        shop,
        source_kind="html-category+product-specs",
        entrypoints=[entry],
        items=items,
    )


def scrape_havana_hr(client: HttpClient, *, limit: int | None) -> dict:
    return scrape_wc_shop(
        client,
        ShopDef("havana_hr", "Havana Shop (Camelot)", "HR", "https://havana-cigar-shop.com", "EUR"),
        limit=limit,
    )


def scrape_cigarsdaily_us(client: HttpClient, *, limit: int | None) -> dict:
    return scrape_wc_shop(
        client,
        ShopDef("cigarsdaily_us", "Cigars Daily", "USA", "https://cigarsdaily.com", "USD"),
        limit=limit,
    )


def _normalize_jsonld_offer(offer: dict) -> tuple[float | None, str | None, bool | None]:
    price = offer.get("price")
    currency = offer.get("priceCurrency")
    availability = offer.get("availability")
    amount: float | None = None
    if isinstance(price, (int, float)):
        amount = float(price)
    elif isinstance(price, str):
        try:
            amount = float(price.replace(",", ".").strip())
        except Exception:
            amount = None
    cur = currency if isinstance(currency, str) and currency else None
    in_stock: bool | None = None
    if isinstance(availability, str):
        a = availability.lower()
        if "instock" in a:
            in_stock = True
        elif "outofstock" in a:
            in_stock = False
    return amount, cur, in_stock


def _normalize_jsonld_product(url: str, product: dict) -> dict | None:
    name = product.get("name") if isinstance(product.get("name"), str) else ""
    if not name:
        return None

    offers = product.get("offers")
    offer_nodes: list[dict] = []
    if isinstance(offers, dict):
        offer_nodes = [offers]
    elif isinstance(offers, list):
        offer_nodes = [o for o in offers if isinstance(o, dict)]

    amount = None
    currency = None
    in_stock = None
    for o in offer_nodes:
        a, c, s = _normalize_jsonld_offer(o)
        if a is not None and amount is None:
            amount = a
        if c and currency is None:
            currency = c
        if s is not None and in_stock is None:
            in_stock = s

    return {
        "id": url,
        "name": name,
        "url": url,
        "price": {"amount": amount, "currency": currency} if amount is not None and currency else None,
        "availability": {"inStock": in_stock, "onSale": None},
        "packaging": {"type": "unknown", "count": None},
        "attributes": {"brand": None, "vitola": None, "dimensions": {"lengthIn": None, "ringGauge": None}},
        "categories": [],
        "images": [],
        "raw": {"jsonld": {"@type": product.get("@type"), "offers": offers}},
    }


def scrape_holts_us(
    client: HttpClient,
    *,
    limit: int | None,
    checkpoint_path: str | None = None,
) -> dict:
    """Scrape Holt's line pages and expand vitola rows (single-stick preferred)."""
    shop = ShopDef("holts_us", "Holt's Cigar Company", "USA", "https://www.holts.com", "USD")
    sitemap_url = "https://www.holts.com/sitemap.xml"
    locs = iter_sitemap_locs(client.get_text(sitemap_url))

    candidates = [
        u
        for u in locs
        if "/cigars/all-cigar-brands/" in u
        and u.endswith(".html")
        and not u.rstrip("/").endswith("all-cigar-brands.html")
    ]

    items: list[dict] = []

    def _checkpoint() -> None:
        if not checkpoint_path:
            return
        payload = _wrap_shop(
            shop,
            source_kind="sitemap+line-page+vitola-table",
            entrypoints=[sitemap_url],
            items=items,
        )
        path = Path(checkpoint_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(path)

    for url in candidates:
        try:
            html = client.get_text(url)
        except urllib.error.HTTPError:
            continue
        if "products-list-table" not in html:
            continue

        products = extract_jsonld_products(html)
        line_name = ""
        if products and isinstance(products[0].get("name"), str):
            line_name = products[0]["name"]
        if not line_name:
            title_m = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
            line_name = re.sub(r"\s*[|\-].*$", "", title_m.group(1)).strip() if title_m else url.rsplit("/", 1)[-1]

        line_details = parse_holts_line_details(html)
        vitolas = parse_holts_vitola_rows(html)
        if not vitolas:
            continue

        for vit in vitolas:
            pack = prefer_holts_pack(vit.get("packs") or [])
            amount = pack.get("price") if pack else None
            vitola_name = vit.get("name") or ""
            full_name = f"{line_name} {vitola_name}".strip()
            details = dict(line_details)
            details["size"] = vitola_name or details.get("size")
            details["lengthIn"] = vit.get("lengthIn")
            details["ringGauge"] = vit.get("ringGauge")
            if details.get("lengthIn") is not None:
                details["lengthCm"] = round(float(details["lengthIn"]) * 2.54, 2)

            item = {
                "id": f"{url}#{vitola_name}",
                "name": full_name,
                "url": url,
                "price": {"amount": amount, "currency": "USD"} if amount is not None else None,
                "availability": {"inStock": True if amount is not None else None, "onSale": None},
                "packaging": {
                    "type": (pack or {}).get("type") or "unknown",
                    "count": (pack or {}).get("count"),
                    "label": (pack or {}).get("label"),
                },
                "attributes": {
                    "brand": None,
                    "vitola": vitola_name or None,
                    "dimensions": {
                        "lengthIn": vit.get("lengthIn"),
                        "ringGauge": vit.get("ringGauge"),
                    },
                },
                "categories": [],
                "images": [],
                "raw": {
                    "lineName": line_name,
                    "vitola": vitola_name,
                    "packs": vit.get("packs") or [],
                    "jsonld": {"@type": "Product", "name": line_name} if line_name else None,
                },
            }
            apply_details_to_item(item, details)
            item["detailsSource"] = {
                "url": url,
                "extractedFrom": "holts-line-page+vitola-table",
                "extractedAt": iso_utc_now(),
            }
            items.append(item)
            if limit is not None and len(items) >= limit:
                _checkpoint()
                return _wrap_shop(
                    shop,
                    source_kind="sitemap+line-page+vitola-table",
                    entrypoints=[sitemap_url],
                    items=items,
                )

        if len(items) % 100 == 0 and items:
            print(f"  holts items {len(items)}", flush=True)
            _checkpoint()

    _checkpoint()
    return _wrap_shop(
        shop,
        source_kind="sitemap+line-page+vitola-table",
        entrypoints=[sitemap_url],
        items=items,
    )


def scrape_cigarworld_eu(
    client: HttpClient,
    *,
    limit: int | None,
    checkpoint_path: str | None = None,
) -> dict:
    shop = ShopDef("cigarworld_eu", "Cigarworld", "EU", "https://www.cigarworld.de", "EUR")
    index_url = "https://www.cigarworld.de/sitemap.xml"
    index_locs = iter_sitemap_locs(client.get_text(index_url))

    en_sitemaps = [u for u in index_locs if u.endswith("sitemap_en.xml")]
    sitemap_url = en_sitemaps[0] if en_sitemaps else index_url
    locs = iter_sitemap_locs(client.get_text(sitemap_url))

    # Prefer product-like URLs (SKU suffix) over brand/category landings.
    candidates = [u for u in locs if "/en/zigarren/" in u and re.search(r"_\d+$", u)]
    if not candidates:
        candidates = [u for u in locs if "/en/zigarren/" in u]

    items: list[dict] = []

    def _checkpoint() -> None:
        if not checkpoint_path:
            return
        payload = _wrap_shop(
            shop,
            source_kind="sitemap+jsonld+variantinfo",
            entrypoints=[index_url, sitemap_url],
            items=items,
        )
        path = Path(checkpoint_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(path)

    for url in candidates:
        try:
            html = client.get_text(url)
        except urllib.error.HTTPError:
            continue
        products = extract_jsonld_products(html)
        if not products:
            continue
        item = _normalize_jsonld_product(url, products[0])
        if not item:
            continue
        details = parse_cigarworld_variant_info(html)
        apply_details_to_item(item, details)
        item["detailsSource"] = {
            "url": url,
            "extractedFrom": "cigarworld-variantinfo",
            "extractedAt": iso_utc_now(),
        }
        items.append(item)
        if len(items) % 50 == 0:
            print(f"  cigarworld items {len(items)}", flush=True)
            _checkpoint()
        if limit is not None and len(items) >= limit:
            break

    _checkpoint()
    return _wrap_shop(
        shop,
        source_kind="sitemap+jsonld+variantinfo",
        entrypoints=[index_url, sitemap_url],
        items=items,
    )


SCRAPERS: dict[str, Any] = {
    "humidor_hr": scrape_humidor_hr,
    "havana_hr": scrape_havana_hr,
    "cigarsdaily_us": scrape_cigarsdaily_us,
    "holts_us": scrape_holts_us,
    "cigarworld_eu": scrape_cigarworld_eu,
}
