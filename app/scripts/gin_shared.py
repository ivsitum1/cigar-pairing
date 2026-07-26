# -*- coding: utf-8 -*-
"""Shared helpers for gin catalog scrape, Excel build, and JSON export."""
from __future__ import annotations

import re
import unicodedata
from typing import Any

from whisky_shared import (
    catalog_entry_tokens,
    format_price_eur,
    is_bare_category_url,
    numeric_age_tokens,
    parse_price_eur,
    slugify,
)

__all__ = [
    "ALLEZ_LISTS",
    "ECUGA_CATEGORIES",
    "catalog_index",
    "cigar_hint_for_style",
    "detect_botanical",
    "detect_style_region",
    "estimate_quality",
    "extract_abv",
    "find_best_catalog_match",
    "format_price_eur",
    "is_pairable",
    "match_tokens",
    "parse_price_eur",
    "serving_for_style",
    "slugify",
    "token_overlap",
]

GIN_STOP = {
    "the", "of", "and", "vol", "gin", "dry", "london", "giftbox", "gift", "box",
    "poklon", "kutiji", "u", "in", "gb", "limited", "edition", "l", "de", "la",
    "le", "du", "des", "with", "glass", "casa", "bottle",
}

ALLEZ_LISTS = [
    ("https://allez.hr/shop/gin1", "gin"),
]

# ecuga spirits tree — gin usually under spirits-and-liqueurs/gin
ECUGA_CATEGORIES: list[tuple[str, str, str]] = [
    ("gin", "", "Gin"),
]

# pattern, style, region, body, sweetness, botanicalProfile, tags
STYLE_RULES: list[tuple[str, str, str, int, int, str, list[str]]] = [
    (r"plymouth|black friars", "plymouth", "Plymouth, Engleska", 3, 2, "classic-juniper", ["travnato", "biljno", "citrus"]),
    (r"beefeater|tanqueray|bombay|broker|sipsmith|no\.?\s*3|fords|hayman's|city of london", "london-dry", "Engleska", 3, 2, "classic-juniper", ["travnato", "citrus", "biljno"]),
    (r"hendrick|monkey 47|botanist|roku|ki\s*no\s*bi|kinobi|malfy|gin mare|nordes|elephant|citadelle|g'?vine|silent pool|the illusionist|copperhead|aviation|bathtub|bobby", "contemporary", "World", 3, 2, "botanical", ["cvjetno", "citrus", "zacini"]),
    (r"gin mare|nordés|nordes|malfy|portofino|mediterranean", "contemporary", "Mediteran", 3, 2, "mediterranean", ["biljno", "citrus", "travnato"]),
    (r"roku|ki no bi|kinobi|nikka|etsu|japanese", "contemporary", "Japan", 3, 2, "botanical", ["cvjetno", "citrus", "zacini"]),
    (r"aura|maraska|badel|croati|istra|dalma|hrvatsk", "croatian", "Hrvatska", 3, 2, "botanical", ["biljno", "citrus", "zacini"]),
    (r"tanqueray\s+no|no\.?\s*ten|ten\b|sipsmith v\.?j\.?o\.?p|premium", "premium-dry", "Engleska", 3, 2, "classic-juniper", ["travnato", "citrus", "cvjetno"]),
]

NON_PAIRABLE_RE = re.compile(
    r"sloe|pink|flavou?r|liker|liqueur|rtd|cocktail|premix|watermelon|peach|"
    r"june\b|candy|strawberry|raspberry|passion|mango|coconut|cream",
    re.I,
)

PREMIUM_BRANDS = {
    "monkey 47", "hendrick", "botanist", "gin mare", "sipsmith", "tanqueray",
    "roku", "ki no bi", "citadelle", "copperhead", "silent pool", "no. 3",
    "plymouth", "malfy", "elephant",
}


def match_tokens(name: str) -> set[str]:
    toks = set(
        re.findall(
            r"[a-z0-9]+",
            unicodedata.normalize("NFKD", name.lower()).encode("ascii", "ignore").decode(),
        )
    )
    return {t for t in toks if t not in GIN_STOP and not (t.isdigit() and len(t) <= 2)}


def token_overlap(a: str, b: str) -> int:
    return len(match_tokens(a) & match_tokens(b))


def extract_abv(name: str) -> float | None:
    m = re.search(r"(\d{2}(?:[.,]\d+)?)\s*%\s*(?:Vol|vol)?", name)
    if m:
        return float(m.group(1).replace(",", "."))
    return None


def detect_style_region(name: str, ecuga_category: str = "") -> tuple[str, str, int, int, str, list[str]]:
    text = f"{name} {ecuga_category}"
    for pattern, style, region, body, sweet, botanical, tags in STYLE_RULES:
        if re.search(pattern, text, re.IGNORECASE):
            # refine mediterranean override after contemporary catch-all
            if style == "contemporary" and re.search(
                r"gin mare|nordés|nordes|malfy|portofino|mediterranean", text, re.I
            ):
                return "contemporary", "Mediteran", body, sweet, "mediterranean", ["biljno", "citrus", "travnato"]
            return style, region, body, sweet, botanical, list(tags)
    if re.search(r"london\s*dry|dry gin", text, re.I):
        return "london-dry", "Engleska", 3, 2, "classic-juniper", ["travnato", "citrus", "biljno"]
    return "contemporary", "World", 3, 2, "botanical", ["cvjetno", "citrus", "zacini"]


def detect_botanical(name: str, style: str = "", botanical: str = "") -> str:
    if botanical:
        return botanical
    _, _, _, _, bot, _ = detect_style_region(name)
    return bot


def estimate_quality(
    name: str,
    price: float | None,
    style: str,
    botanical: str,
    abv: float | None,
    seed_score: float | None = None,
) -> float:
    if seed_score is not None:
        return float(seed_score)
    if NON_PAIRABLE_RE.search(name):
        return 3.5
    score = 6.2
    low = name.lower()
    for brand in PREMIUM_BRANDS:
        if brand in low:
            score += 0.9
            break
    if style in ("premium-dry", "plymouth"):
        score += 0.4
    if style == "croatian":
        score += 0.2
    if botanical == "mediterranean":
        score += 0.2
    if price:
        if price >= 55:
            score += 0.8
        elif price >= 40:
            score += 0.5
        elif price >= 28:
            score += 0.3
        elif price < 18:
            score -= 0.5
    if abv and abv >= 45:
        score += 0.2
    return round(min(10.0, max(3.0, score)), 1)


def is_pairable(name: str, style: str, quality: float) -> bool:
    if NON_PAIRABLE_RE.search(name):
        return False
    if quality < 5.5:
        return False
    return True


def serving_for_style(style: str, botanical: str = "") -> dict[str, Any]:
    if style in ("london-dry", "premium-dry", "plymouth"):
        return {
            "neat": 2,
            "tonic": 3,
            "martini": 3,
            "highball": 2,
            "best": "Martini ili G&T",
        }
    if botanical == "mediterranean" or style == "croatian":
        return {
            "neat": 2,
            "tonic": 3,
            "martini": 2,
            "highball": 2,
            "best": "G&T s mediteranskim tonikom",
        }
    return {
        "neat": 3,
        "tonic": 2,
        "martini": 3,
        "highball": 2,
        "best": "Cisti ili martini",
    }


def cigar_hint_for_style(style: str, botanical: str = "") -> str:
    if botanical == "mediterranean":
        return "Connecticut / blagi Habano — biljno-citrusni gin"
    if style in ("london-dry", "premium-dry", "plymouth"):
        return "Connecticut — klasična borovica uz blagu cigaru"
    if style == "croatian":
        return "Connecticut do blage Habano — lokalni terroir"
    return "Connecticut / blagi Habano — gusta botanika"


def find_best_catalog_match(name: str, catalog: list[dict]) -> dict | None:
    tokens = match_tokens(name)
    age_nums = numeric_age_tokens(name)
    best, best_score = None, 0
    for entry in catalog:
        url = entry.get("url", "")
        if is_bare_category_url(url):
            continue
        score = len(tokens & entry["tokens"])
        if score <= best_score:
            continue
        if age_nums and not age_nums.issubset(catalog_entry_tokens(entry, match_tokens)):
            continue
        best, best_score = entry, score
    return best if best and best_score >= 3 else None


def catalog_index(entries: list[dict]) -> list[dict]:
    return [{**e, "tokens": match_tokens(e["name"])} for e in entries]
