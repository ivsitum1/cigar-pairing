# -*- coding: utf-8 -*-
"""Scrape ecuga.com spirit categories (shared by the drink-shop gap scan).

eCuga is a Saleor + Next.js storefront: category pages render client-side and
load products through GraphQL. Plain HTTP sees an empty shell, so this drives
headless Chromium (Playwright) and reads the GraphQL `products` responses —
the same technique as scrape-whisky/gin/tequila/brandy-catalog.py.

Pagination: the page loads more products on scroll. We scroll until the slug
count stops growing, then — if the last response still says `hasNextPage` —
replay the captured query with `after = endCursor` until the category is done.
That second step makes a long category (rum) independent of scroll timing.

Product URLs are emitted as `https://ecuga.com/proizvod/<slug>` because that is
the form the catalog stores (see migrate-ecuga-priceurls.py) — the gap scan
matches on exact URL, so a `/katalog/...` URL would never hit Tier A.

  python scripts/scrape-drink-shop-listings.py --shops ecuga --merge
  python scripts/scan-drink-shop-gaps.py --shops ecuga
"""
from __future__ import annotations

import copy
import json

BASE = "https://ecuga.com/katalog"

# (path candidates under /katalog, category label for suggested_category).
# The storefront has moved categories between /katalog/<x> and
# /katalog/spirits-and-liqueurs/<x>; the first path that yields products wins.
ECUGA_SPIRIT_LISTS: list[tuple[tuple[str, ...], str]] = [
    (("rum", "spirits-and-liqueurs/rum"), "rum"),
    (("whisky", "spirits-and-liqueurs/whisky"), "whisky"),
    (("spirits-and-liqueurs/gin", "gin"), "gin"),
    (("spirits-and-liqueurs/tequila", "tequila"), "tequila"),
    (("spirits-and-liqueurs/mezcal", "mezcal"), "tequila"),
    (("spirits-and-liqueurs/cognac", "cognac"), "cognac"),
    (("spirits-and-liqueurs/armagnac", "armagnac"), "cognac"),
    (("spirits-and-liqueurs/calvados", "calvados"), "cognac"),
    (("spirits-and-liqueurs/brandy", "brandy"), "brandy"),
]

# Whisky top-level page may only show a teaser; subcategories are the proven
# paths from whisky_shared.ECUGA_CATEGORIES.
ECUGA_WHISKY_SUBCATS: tuple[str, ...] = (
    "skotski-maltgrain-whisky",
    "skotski-blended-whisky",
    "irski-whiskey",
    "americki-bourbon-whiskey",
    "azijski-whisky",
    "kanadski-whisky",
    "ostalo",
)

MAX_SCROLLS = 40
MAX_REPLAY_PAGES = 30


def product_url(slug: str) -> str:
    return f"https://ecuga.com/proizvod/{slug}"


def products_from_body(body: object) -> dict | None:
    """Return the `products` connection from a GraphQL response body, if any."""
    if not isinstance(body, dict):
        return None
    products = (body.get("data") or {}).get("products")
    if isinstance(products, dict) and products.get("edges"):
        return products
    return None


def items_from_products(
    products: dict,
    category: str,
    seen: set[str],
    pending: set[str] | None = None,
) -> list[dict]:
    """Map Saleor product edges to raw listing rows; skips slugs in `seen`.

    When `pending` is set, new slugs are recorded there until the caller commits
    them into `seen` (so a failed category path does not hide products).
    """
    out: list[dict] = []
    for edge in products.get("edges") or []:
        node = (edge or {}).get("node") or {}
        slug = (node.get("slug") or "").strip()
        name = (node.get("name") or "").strip()
        if not slug or not name or slug in seen or (pending is not None and slug in pending):
            continue
        if pending is not None:
            pending.add(slug)
        else:
            seen.add(slug)
        start = ((node.get("pricing") or {}).get("priceRange") or {}).get("start") or {}
        amount = (start.get("gross") or {}).get("amount")
        try:
            price = float(amount) if amount is not None else None
        except (TypeError, ValueError):
            price = None
        out.append(
            {
                "shop": "ecuga",
                "shopLabel": "ecuga.com",
                "name": name,
                "price_eur": price,
                "url": product_url(slug),
                "category": category,
            }
        )
    return out


def next_page_payload(request_body: str | None, products: dict) -> str | None:
    """Rewrite a captured GraphQL request to fetch the page after `products`.

    Returns None when there is no next page or the query is not cursor-paged
    (no `after` variable to set), so the caller falls back to scrolling only.
    """
    info = products.get("pageInfo") or {}
    cursor = info.get("endCursor")
    if not info.get("hasNextPage") or not cursor or not request_body:
        return None
    try:
        payload = json.loads(request_body)
    except (TypeError, ValueError):
        return None
    if not isinstance(payload, dict):
        return None
    query = payload.get("query") or ""
    if "$after" not in query:
        return None
    payload = copy.deepcopy(payload)
    variables = payload.get("variables") or {}
    variables["after"] = cursor
    payload["variables"] = variables
    return json.dumps(payload)


def _accept_cookies(page) -> None:
    for sel in ('button:has-text("Dopusti sve")', 'button:has-text("Dopusti selektirane")'):
        try:
            page.locator(sel).first.click(timeout=4000)
            return
        except Exception:
            pass


def _scrape_path(page, url: str, category: str, seen: set[str]) -> list[dict]:
    path_seen: set[str] = set()
    captured: list[tuple[dict, str | None, str]] = []

    def on_response(response) -> None:
        if "graphql" not in response.url or response.status != 200:
            return
        try:
            products = products_from_body(response.json())
        except Exception:
            return
        if products is None:
            return
        try:
            post = response.request.post_data
        except Exception:
            post = None
        captured.append((products, post, response.url))

    page.on("response", on_response)
    try:
        try:
            page.goto(url, wait_until="networkidle", timeout=90000)
        except Exception:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2500)

        items: list[dict] = []
        stale = 0
        for _ in range(MAX_SCROLLS):
            before = len(seen)
            for products, _post, _u in captured:
                items.extend(items_from_products(products, category, seen, path_seen))
            captured_n = len(captured)
            page.mouse.wheel(0, 4000)
            page.wait_for_timeout(900)
            for products, _post, _u in captured[captured_n:]:
                items.extend(items_from_products(products, category, seen, path_seen))
            stale = stale + 1 if len(seen) == before else 0
            if stale >= 3:
                break

        # Cursor replay for whatever scrolling did not reach.
        if captured:
            products, post, gql_url = captured[-1]
            for _ in range(MAX_REPLAY_PAGES):
                body = next_page_payload(post, products)
                if body is None:
                    break
                resp = page.request.post(
                    gql_url, data=body, headers={"Content-Type": "application/json"}
                )
                if not resp.ok:
                    break
                nxt = products_from_body(resp.json())
                if nxt is None:
                    break
                items.extend(items_from_products(nxt, category, seen, path_seen))
                products, post = nxt, body
        seen.update(path_seen)
        return items
    finally:
        page.remove_listener("response", on_response)


def scrape_ecuga(lists: list[tuple[tuple[str, ...], str]] | None = None) -> list[dict]:
    """Crawl eCuga spirit categories; dedupe by product slug."""
    from playwright.sync_api import sync_playwright

    print("ecuga.com (Playwright + GraphQL) …", flush=True)
    lists = lists or ECUGA_SPIRIT_LISTS
    seen: set[str] = set()
    out: list[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"{BASE}/rum", wait_until="domcontentloaded", timeout=60000)
        _accept_cookies(page)
        for paths, category in lists:
            got = 0
            for path in paths:
                try:
                    batch = _scrape_path(page, f"{BASE}/{path}", category, seen)
                except Exception as exc:  # one bad category must not sink the shop
                    print(f"  skip {path}: {exc}", flush=True)
                    continue
                out.extend(batch)
                got = len(batch)
                if got:
                    break
            if category == "whisky":
                for sub in ECUGA_WHISKY_SUBCATS:
                    try:
                        batch = _scrape_path(page, f"{BASE}/whisky/{sub}", category, seen)
                    except Exception as exc:
                        print(f"  skip whisky/{sub}: {exc}", flush=True)
                        continue
                    out.extend(batch)
                    got += len(batch)
            print(f"  {category} ({paths[0]}): +{got} -> {len(out)} unique", flush=True)
        browser.close()
    print(f"  ecuga total {len(out)}", flush=True)
    return out
