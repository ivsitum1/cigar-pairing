# -*- coding: utf-8 -*-
"""Parse product-page HTML into in-stock / out-of-stock / unknown.

Conservative: only True/False when a clear signal exists. Soft 404, preorder
and pages with no stock markup stay None — callers must not invent a shelf.
"""
from __future__ import annotations

import json
import re
from typing import Any

_SOFT_404 = re.compile(
    r"<title>[^<]*(page not found|404|stranica nije pronađena|stranica ne postoji)[^<]*</title>",
    re.I,
)

_AVAIL_URL = re.compile(
    r"https?://schema\.org/(?P<status>InStock|OutOfStock|SoldOut|Discontinued|"
    r"LimitedAvailability|InStoreOnly|OnlineOnly|PreOrder|PreSale|BackOrder)\b",
    re.I,
)

_IN_STATUSES = frozenset(
    {"instock", "limitedavailability", "instoreonly", "onlineonly"}
)
_OUT_STATUSES = frozenset({"outofstock", "soldout", "discontinued"})
# PreOrder / PreSale / BackOrder: not on the shelf, but not a firm "gone".
_UNKNOWN_STATUSES = frozenset({"preorder", "presale", "backorder"})

_OUT_CLASS = re.compile(
    r"""class=["'][^"']*\b(?:out-of-stock|outofstock|out_of_stock)\b""",
    re.I,
)
_IN_CLASS = re.compile(
    r"""class=["'][^"']*\b(?:in-stock|instock|in_stock)\b""",
    re.I,
)

_OUT_PHRASE = re.compile(
    r"\b(?:nema na zalihi|nije dostupno|rasprodano|out of stock|sold out|"
    r"nicht auf lager|currently unavailable|nicht lieferbar)\b",
    re.I,
)
# "na zalihi" is a suffix of "nema na zalihi" — only count it after out-phrases
# have been ruled out, and never when "nema " sits immediately before.
_IN_PHRASE = re.compile(
    r"(?<!nema )\bna zalihi\b|\bdostupno\b|\bin stock\b|\bsofort lieferbar\b|\bauf lager\b",
    re.I,
)

# Allez (Laravel shop): static HTML exposes add-to-cart when the SKU is orderable.
_ALLEZ_CART_FORM = re.compile(r'id=["\']add-to-cart-form["\']', re.I)
_ALLEZ_OUT = re.compile(
    r"\b(?:nema na zalihi|rasprodano|trenutno nije dostupno|notify me|"
    r"obavijesti me)\b",
    re.I,
)
_ALLEZ_DISABLED_BTN = re.compile(
    r'id=["\']add-to-cart-form["\'].*?<button[^>]*\bdisabled\b',
    re.I | re.S,
)


def _status_from_token(token: str) -> bool | None:
    key = re.sub(r"[^a-z]", "", token.lower())
    if key in _OUT_STATUSES:
        return False
    if key in _IN_STATUSES:
        return True
    if key in _UNKNOWN_STATUSES:
        return None
    return None


def _walk_json(obj: Any, found: list[bool | None]) -> None:
    if isinstance(obj, dict):
        raw = obj.get("availability")
        if isinstance(raw, str):
            m = _AVAIL_URL.search(raw) or re.search(r"([A-Za-z]+)$", raw)
            token = (
                m.group("status")
                if m and m.lastgroup == "status"
                else (m.group(1) if m else raw)
            )
            found.append(_status_from_token(token))
        for v in obj.values():
            _walk_json(v, found)
    elif isinstance(obj, list):
        for item in obj:
            _walk_json(item, found)


def _jsonld_signals(html: str) -> list[bool | None]:
    found: list[bool | None] = []
    for m in re.finditer(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.I | re.S,
    ):
        raw = m.group(1).strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        _walk_json(data, found)
    return found


def _saleor_next_data(html: str) -> bool | None:
    """eCuga (Saleor + Next.js) embeds stock in __NEXT_DATA__."""
    m = re.search(
        r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
        html,
        re.I | re.S,
    )
    if not m:
        return None
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError:
        return None

    product = (data.get("props") or {}).get("pageProps", {}).get("product")
    if not isinstance(product, dict):
        return None

    if product.get("isAvailableForPurchase") is False:
        return False

    qtys: list[int] = []
    for variant in product.get("variants") or []:
        if not isinstance(variant, dict):
            continue
        qty = variant.get("quantityAvailable")
        if isinstance(qty, int):
            qtys.append(qty)

    if qtys:
        return any(q > 0 for q in qtys)
    if product.get("isAvailableForPurchase") is True:
        return True
    return None


def _allez_signals(html: str) -> bool | None:
    if not _ALLEZ_CART_FORM.search(html):
        return None
    if _ALLEZ_OUT.search(html) or _ALLEZ_DISABLED_BTN.search(html):
        return False
    return True


def parse_stock(html: str | None) -> bool | None:
    """True = in stock, False = out of stock, None = do not claim."""
    if not html or not html.strip():
        return None
    if _SOFT_404.search(html):
        return None

    signals = list(_jsonld_signals(html))
    for m in _AVAIL_URL.finditer(html):
        signals.append(_status_from_token(m.group("status")))

    saleor = _saleor_next_data(html)
    if saleor is not None:
        signals.append(saleor)

    allez = _allez_signals(html)
    if allez is not None:
        signals.append(allez)

    if _OUT_CLASS.search(html) or _OUT_PHRASE.search(html):
        signals.append(False)
    elif _IN_CLASS.search(html) or _IN_PHRASE.search(html):
        signals.append(True)

    definite = [s for s in signals if s is not None]
    if any(s is False for s in definite):
        return False
    if any(s is True for s in definite):
        return True
    return None
