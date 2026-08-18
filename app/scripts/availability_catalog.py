# -*- coding: utf-8 -*-
"""Collect pingable product URLs and write inStock back onto catalog records.

Does not fetch. Matching is by normalized URL so trailing slashes do not fork
two stock fields on the same SKU.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse, urlunparse

STEALTH_HOSTS = frozenset({"famous-smoke.com"})

_LISTING = (
    re.compile(r"holts\.com/cigars/all-cigar-brands/[^/?#]+\.html", re.I),
    re.compile(r"/(?:en/)?product-brand/", re.I),
    re.compile(r"famous-smoke\.com/brands?/", re.I),
    re.compile(r"famous-smoke\.com/brandgroup/", re.I),
    re.compile(r"neptunecigar\.com/cigar/", re.I),
)

_SEARCH_HINT = re.compile(
    r"[?&]s=|/search\b|catalogsearch|/find/|google\.com/search",
    re.I,
)

_REF_HOSTS = frozenset({"wine-searcher.com"})

_PINGABLE_DRINK_HOSTS = frozenset(
    {
        "allez.hr",
        "ecuga.com",
        "tipsy.hr",
        "cugaklik.hr",
        "miva.com.hr",
        "webshop.rotodinamic.hr",
        "rotodinamic.hr",
    }
)


def normalize_url(url: str | None) -> str:
    if not url:
        return ""
    raw = url.strip()
    if not raw:
        return ""
    parsed = urlparse(raw)
    path = parsed.path.rstrip("/") or ""
    return urlunparse((parsed.scheme, parsed.netloc.lower(), path, "", "", ""))


def _host(url: str) -> str:
    host = urlparse(url).hostname or ""
    return host.lower().removeprefix("www.")


def is_listing_url(url: str | None) -> bool:
    if not url:
        return False
    return any(p.search(url) for p in _LISTING)


def is_pingable_url(url: str | None) -> bool:
    if not url or not url.startswith("http"):
        return False
    if is_listing_url(url):
        return False
    if _SEARCH_HINT.search(url):
        return False
    if _host(url) in _REF_HOSTS:
        return False
    return True


def wants_stealth(url: str | None) -> bool:
    if not url:
        return False
    host = _host(url)
    return any(host == h or host.endswith(f".{h}") for h in STEALTH_HOSTS)


def _add(seen: dict[str, str], url: str | None) -> None:
    if not is_pingable_url(url):
        return
    key = normalize_url(url)
    if key and key not in seen:
        seen[key] = url.split("#", 1)[0].rstrip("/")


def collect_cigar_urls(cigar: dict) -> list[str]:
    seen: dict[str, str] = {}
    _add(seen, cigar.get("priceUrl"))
    for link in (cigar.get("regionLinks") or {}).values():
        if isinstance(link, dict):
            _add(seen, link.get("url"))
    for vitola in cigar.get("vitolas") or []:
        if not isinstance(vitola, dict):
            continue
        _add(seen, vitola.get("url"))
        for link in (vitola.get("regionLinks") or {}).values():
            if isinstance(link, dict):
                _add(seen, link.get("url"))
    return list(seen.values())


def collect_drink_urls(drink: dict) -> list[str]:
    url = drink.get("priceUrl")
    if not is_pingable_url(url):
        return []
    if _host(url) not in _PINGABLE_DRINK_HOSTS:
        return []
    return [url.split("#", 1)[0].rstrip("/")]


def _urls_match(stored: str | None, target: str) -> bool:
    return bool(stored) and normalize_url(stored) == normalize_url(target)


def _stamp(obj: dict, in_stock: bool, fetched_at: str) -> None:
    obj["inStock"] = in_stock
    obj["stockFetchedAt"] = fetched_at


def apply_stock_to_cigar(cigar: dict, url: str, in_stock: bool, fetched_at: str) -> int:
    n = 0
    if _urls_match(cigar.get("priceUrl"), url):
        _stamp(cigar, in_stock, fetched_at)
        n += 1
    for link in (cigar.get("regionLinks") or {}).values():
        if isinstance(link, dict) and _urls_match(link.get("url"), url):
            _stamp(link, in_stock, fetched_at)
            n += 1
    for vitola in cigar.get("vitolas") or []:
        if not isinstance(vitola, dict):
            continue
        if _urls_match(vitola.get("url"), url):
            _stamp(vitola, in_stock, fetched_at)
            n += 1
        for link in (vitola.get("regionLinks") or {}).values():
            if isinstance(link, dict) and _urls_match(link.get("url"), url):
                _stamp(link, in_stock, fetched_at)
                n += 1
    return n


def apply_stock_to_drink(drink: dict, url: str, in_stock: bool, fetched_at: str) -> int:
    if not _urls_match(drink.get("priceUrl"), url):
        return 0
    _stamp(drink, in_stock, fetched_at)
    return 1


def _read_stock(obj: dict | None) -> dict | None:
    if not isinstance(obj, dict):
        return None
    if obj.get("inStock") not in (True, False):
        return None
    fetched = obj.get("stockFetchedAt")
    if not fetched:
        return None
    return {"inStock": obj["inStock"], "stockFetchedAt": fetched}


def cigar_link_stock(cigar: dict, url: str) -> dict | None:
    """Return stock fields for the catalog node that owns this product URL."""
    if _urls_match(cigar.get("priceUrl"), url):
        hit = _read_stock(cigar)
        if hit:
            return hit
    for link in (cigar.get("regionLinks") or {}).values():
        if isinstance(link, dict) and _urls_match(link.get("url"), url):
            hit = _read_stock(link)
            if hit:
                return hit
    for vitola in cigar.get("vitolas") or []:
        if not isinstance(vitola, dict):
            continue
        if _urls_match(vitola.get("url"), url):
            hit = _read_stock(vitola)
            if hit:
                return hit
        for link in (vitola.get("regionLinks") or {}).values():
            if isinstance(link, dict) and _urls_match(link.get("url"), url):
                hit = _read_stock(link)
                if hit:
                    return hit
    return None


def drink_stock(drink: dict, url: str) -> dict | None:
    if not _urls_match(drink.get("priceUrl"), url):
        return None
    return _read_stock(drink)
