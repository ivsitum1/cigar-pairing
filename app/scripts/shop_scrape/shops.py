from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shop_scrape.jsonld import extract_jsonld_products
from shop_scrape.sitemap import iter_sitemap_locs

from shop_scrape.http import HttpClient, iso_utc_now
from shop_scrape.woocommerce import wc_categories_text, wc_iter_products, wc_normalize_product


def _looks_like_cigar_category(text: str) -> bool:
    t = text.lower()
    keywords = (
        "cigar",
        "cigars",
        "cigare",
        "zigarre",
        "zigarren",
        "sampler",
        "samplers",
        "habanos",
    )
    return any(k in t for k in keywords)


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


def scrape_wc_shop(
    client: HttpClient,
    shop: ShopDef,
    *,
    limit: int | None,
    per_page: int = 100,
    max_pages: int = 200,
) -> dict:
    products = wc_iter_products(client, shop.base_url, per_page=per_page, max_pages=max_pages)
    items: list[dict] = []
    for p in products:
        cat_text = wc_categories_text(p)
        permalink = p.get("permalink") if isinstance(p.get("permalink"), str) else ""
        if cat_text and not _looks_like_cigar_category(cat_text) and permalink:
            # Avoid accidentally including spirits/accessories in mixed shops.
            if not _looks_like_cigar_category(permalink):
                continue
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
    return _wrap_shop(shop_final, source_kind="woocommerce-store-api", entrypoints=[entry], items=items)


def scrape_humidor_hr(client: HttpClient, *, limit: int | None) -> dict:
    return scrape_wc_shop(
        client,
        ShopDef("humidor_hr", "The Humidor", "HR", "https://humidor.hr", "EUR"),
        limit=limit,
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


SCRAPERS: dict[str, Any] = {
    "humidor_hr": scrape_humidor_hr,
    "havana_hr": scrape_havana_hr,
    "cigarsdaily_us": scrape_cigarsdaily_us,
}


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


def scrape_holts_us(client: HttpClient, *, limit: int | None) -> dict:
    shop = ShopDef("holts_us", "Holt's Cigar Company", "USA", "https://www.holts.com", "USD")
    sitemap_url = "https://www.holts.com/sitemap.xml"
    locs = iter_sitemap_locs(client.get_text(sitemap_url))

    # Candidate URLs: keep `.html` pages and let JSON-LD decide what is a Product.
    candidates = [u for u in locs if u.startswith(shop.base_url) and u.endswith(".html")]
    items: list[dict] = []
    for url in candidates:
        html = client.get_text(url)
        products = extract_jsonld_products(html)
        if not products:
            continue
        item = _normalize_jsonld_product(url, products[0])
        if item:
            items.append(item)
        if limit is not None and len(items) >= limit:
            break

    return _wrap_shop(shop, source_kind="sitemap+jsonld", entrypoints=[sitemap_url], items=items)


def scrape_cigarworld_eu(client: HttpClient, *, limit: int | None) -> dict:
    shop = ShopDef("cigarworld_eu", "Cigarworld", "EU", "https://www.cigarworld.de", "EUR")
    index_url = "https://www.cigarworld.de/sitemap.xml"
    index_locs = iter_sitemap_locs(client.get_text(index_url))

    # Prefer English sitemap if present.
    en_sitemaps = [u for u in index_locs if u.endswith("sitemap_en.xml")]
    sitemap_url = en_sitemaps[0] if en_sitemaps else index_url
    locs = iter_sitemap_locs(client.get_text(sitemap_url))

    candidates = [u for u in locs if "/en/zigarren/" in u]
    items: list[dict] = []
    for url in candidates:
        html = client.get_text(url)
        products = extract_jsonld_products(html)
        if not products:
            continue
        item = _normalize_jsonld_product(url, products[0])
        if item:
            items.append(item)
        if limit is not None and len(items) >= limit:
            break

    return _wrap_shop(shop, source_kind="sitemap+jsonld", entrypoints=[index_url, sitemap_url], items=items)


SCRAPERS.update(
    {
        "holts_us": scrape_holts_us,
        "cigarworld_eu": scrape_cigarworld_eu,
    }
)

