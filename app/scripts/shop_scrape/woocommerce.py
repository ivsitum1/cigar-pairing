from __future__ import annotations

import html
from typing import Any
from urllib.parse import urlencode

from shop_scrape.http import HttpClient


def wc_price_to_amount(prices: dict[str, Any]) -> float | None:
    raw = prices.get("price")
    if raw is None:
        return None
    minor = int(prices.get("currency_minor_unit", 2))
    try:
        return int(raw) / (10**minor)
    except Exception:
        return None


def wc_iter_products(
    client: HttpClient,
    base_url: str,
    *,
    query: dict[str, str] | None = None,
    per_page: int = 100,
    max_pages: int = 200,
) -> list[dict]:
    out: list[dict] = []
    for page in range(1, max_pages + 1):
        q = {"per_page": str(per_page), "page": str(page)}
        if query:
            q.update(query)
        url = f"{base_url}/wp-json/wc/store/products?{urlencode(q)}"
        batch = client.get_json(url)
        if not isinstance(batch, list) or not batch:
            break
        out.extend([x for x in batch if isinstance(x, dict)])
    return out


def wc_iter_categories(
    client: HttpClient, base_url: str, *, per_page: int = 100, max_pages: int = 20
) -> list[dict]:
    out: list[dict] = []
    for page in range(1, max_pages + 1):
        url = f"{base_url}/wp-json/wc/store/products/categories?{urlencode({'per_page': str(per_page), 'page': str(page)})}"
        batch = client.get_json(url)
        if not isinstance(batch, list) or not batch:
            break
        out.extend([x for x in batch if isinstance(x, dict)])
    return out


def wc_pick_cigar_category_ids(categories: list[dict]) -> list[int]:
    """Best-effort cigar category detection by slug/name/link keywords."""
    keywords = ("cig", "cigar", "cigare", "zigar", "zigarr", "haban")
    picks: list[tuple[int, int]] = []
    for c in categories:
        cid = c.get("id")
        if not isinstance(cid, int):
            continue
        name = (c.get("name") if isinstance(c.get("name"), str) else "").lower()
        slug = (c.get("slug") if isinstance(c.get("slug"), str) else "").lower()
        link = (c.get("link") if isinstance(c.get("link"), str) else "").lower()
        text = " ".join([name, slug, link])
        if not any(k in text for k in keywords):
            continue
        # Prefer the canonical "cigare/cigars" over brand categories.
        score = 0
        if slug in ("cigare", "cigars", "habanos"):
            score += 10
        if "/product-category/" in link or "/kategorija-proizvoda/" in link:
            score += 2
        picks.append((score, cid))
    picks.sort(reverse=True)
    # Keep a few top IDs to be safe; callers can pick first.
    return [cid for _score, cid in picks[:5]]


def wc_categories_text(product: dict) -> str:
    cats = product.get("categories") or []
    if not isinstance(cats, list):
        return ""
    parts: list[str] = []
    for c in cats:
        if not isinstance(c, dict):
            continue
        name = c.get("name")
        slug = c.get("slug")
        link = c.get("link")
        for v in (name, slug, link):
            if isinstance(v, str) and v:
                parts.append(v.lower())
    return " ".join(parts)


def wc_normalize_product(product: dict) -> dict:
    prices = product.get("prices") if isinstance(product.get("prices"), dict) else {}
    currency = prices.get("currency_code") if isinstance(prices, dict) else None
    amount = wc_price_to_amount(prices) if isinstance(prices, dict) else None

    name = product.get("name") if isinstance(product.get("name"), str) else ""
    permalink = product.get("permalink") if isinstance(product.get("permalink"), str) else ""

    images: list[dict] = []
    for im in product.get("images") or []:
        if not isinstance(im, dict):
            continue
        src = im.get("src")
        alt = im.get("alt") if isinstance(im.get("alt"), str) else ""
        if isinstance(src, str) and src:
            images.append({"src": src, "alt": alt})

    categories: list[dict] = []
    for c in product.get("categories") or []:
        if not isinstance(c, dict):
            continue
        categories.append(
            {
                "name": c.get("name") if isinstance(c.get("name"), str) else "",
                "slug": c.get("slug") if isinstance(c.get("slug"), str) else "",
                "url": c.get("link") if isinstance(c.get("link"), str) else "",
            }
        )

    return {
        "id": str(product.get("id") or product.get("slug") or permalink),
        "name": html.unescape(name),
        "url": permalink,
        "price": {"amount": amount, "currency": currency} if amount is not None and currency else None,
        "availability": {
            "inStock": bool(product.get("is_in_stock")) if "is_in_stock" in product else None,
            "onSale": bool(product.get("on_sale")) if "on_sale" in product else None,
        },
        "packaging": {"type": "unknown", "count": None},
        "attributes": {
            "brand": None,
            "vitola": None,
            "dimensions": {"lengthIn": None, "ringGauge": None},
        },
        "categories": categories,
        "images": images,
        "raw": {
            "type": product.get("type"),
            "slug": product.get("slug"),
            "sku": product.get("sku"),
        },
    }

