from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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

