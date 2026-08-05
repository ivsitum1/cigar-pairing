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
    # ── Brand-specific rules (most specific first) ──────────────────────────────
    # Monkey 47: 47 botanicals incl. blackberries, lingonberries, spruce (producer)
    (r"monkey\s*47", "contemporary", "Schwarzwald, Njema\u010dka", 3, 1, "botanical", ["borovica", "tamno-voce", "zacini"]),
    # Hendrick's: rose, cucumber, chamomile, elderflower (producer)
    (r"hendrick", "contemporary", "\u0160kotska", 3, 3, "botanical", ["cvjetno", "kamilica", "biljno"]),
    # The Botanist: 22 Islay botanicals (producer)
    (r"botanist", "contemporary", "Islay, \u0160kotska", 3, 2, "botanical", ["biljno", "cvjetno", "citrus"]),
    # Ki No Bi: yuzu, sansho pepper, ginger, green tea (Kyoto Distillery)
    (r"ki\s*no\s*bi|kinobi", "contemporary", "Kyoto, Japan", 3, 2, "botanical", ["citrus", "papar", "biljno"]),
    # Roku: sakura, yuzu, sansho pepper (Suntory)
    (r"\broku\b", "contemporary", "Japan", 3, 2, "botanical", ["cvjetno", "citrus", "papar"]),
    # Nikka Coffey Gin: grain-forward, Japanese citrus (Nikka)
    (r"nikka.*coffey.*gin|nikka.*gin", "contemporary", "Japan", 3, 2, "botanical", ["citrus", "travnato", "kamilica"]),
    # Silent Pool editions
    (r"silent pool.*rose", "contemporary", "World", 3, 3, "botanical", ["cvjetno", "kamilica", "slatko"]),
    (r"silent pool.*rare citrus|silent pool.*citrus", "contemporary", "World", 2, 2, "botanical", ["citrus", "cvjetno", "kamilica"]),
    (r"silent pool", "contemporary", "World", 3, 3, "botanical", ["cvjetno", "kamilica", "med"]),
    # Copperhead editions
    (r"copperhead.*barrel", "contemporary", "World", 4, 2, "botanical", ["zacini", "hrast", "citrus"]),
    (r"copperhead.*black batch", "contemporary", "World", 3, 2, "botanical", ["zacini", "citrus", "biljno"]),
    (r"copperhead.*alchemist", "contemporary", "World", 3, 2, "botanical", ["citrus", "zacini", "biljno"]),
    (r"copperhead", "contemporary", "World", 3, 2, "botanical", ["zacini", "citrus", "korijen"]),
    # Citadelle Reserve: aged (producer)
    (r"citadelle.*reserve", "contemporary", "Francuska", 4, 2, "botanical", ["anis", "hrast", "citrus"]),
    (r"citadelle", "contemporary", "Francuska", 3, 2, "botanical", ["anis", "biljno", "citrus"]),
    # Aviation: lavender, sarsaparilla, rose petal (producer)
    (r"aviation", "contemporary", "SAD", 3, 2, "botanical", ["cvjetno", "biljno", "korijen"]),
    # Elephant Gin editions
    (r"elephant.*orange", "contemporary", "World", 3, 3, "botanical", ["citrus", "kakao", "zacini"]),
    (r"elephant", "contemporary", "World", 3, 2, "botanical", ["biljno", "suho-voce", "zacini"]),
    # Amuerte Coca Leaf editions
    (r"amuerte.*red", "contemporary", "World", 3, 3, "botanical", ["tamno-voce", "biljno", "zacini"]),
    (r"amuerte.*black", "contemporary", "World", 4, 2, "botanical", ["biljno", "zacini", "citrus"]),
    (r"amuerte.*orange", "contemporary", "World", 3, 2, "botanical", ["citrus", "biljno", "cvjetno"]),
    (r"amuerte.*yellow", "contemporary", "World", 2, 2, "botanical", ["citrus", "cvjetno", "biljno"]),
    (r"amuerte.*blue", "contemporary", "World", 3, 2, "botanical", ["biljno", "anis", "citrus"]),
    (r"amuerte.*green", "contemporary", "World", 3, 1, "botanical", ["biljno", "travnato", "citrus"]),
    (r"amuerte.*white", "contemporary", "World", 3, 2, "botanical", ["borovica", "citrus", "biljno"]),
    (r"amuerte", "contemporary", "World", 3, 2, "botanical", ["biljno", "citrus", "zacini"]),
    # Sipsmith editions
    (r"sipsmith.*v\.?j\.?o\.?p|sipsmith.*vjop", "premium-dry", "London, UK", 4, 1, "classic-juniper", ["borovica", "citrus", "zacini"]),
    (r"sipsmith.*zesty|sipsmith.*orange", "london-dry", "Engleska", 3, 2, "classic-juniper", ["citrus", "biljno", "travnato"]),
    (r"sipsmith", "london-dry", "London, UK", 3, 2, "classic-juniper", ["borovica", "citrus", "travnato"]),
    # Gin Mare: olive, rosemary, thyme, basil (producer)
    (r"gin mare", "contemporary", "Mediteran", 3, 2, "mediterranean", ["biljno", "travnato", "zacini"]),
    # Malfy editions
    (r"malfy.*arancia|malfy.*orange", "contemporary", "Mediteran", 2, 2, "mediterranean", ["citrus", "voce", "biljno"]),
    (r"malfy.*limone|malfy.*lemon", "contemporary", "Mediteran", 2, 2, "mediterranean", ["citrus", "biljno", "cvjetno"]),
    (r"malfy", "contemporary", "Mediteran", 3, 2, "mediterranean", ["citrus", "biljno", "travnato"]),
    # Four Pillars: Australian botanicals, Tassie pepperberry (producer)
    (r"four pillars", "contemporary", "Australija", 3, 2, "botanical", ["biljno", "papar", "citrus"]),
    # ── Plymouth (root spice recipe) ──────────────────────────────────────────
    (r"plymouth.*navy", "plymouth", "Plymouth, UK", 4, 1, "classic-juniper", ["borovica", "korijen", "zacini"]),
    (r"plymouth|black friars", "plymouth", "Plymouth, UK", 3, 2, "classic-juniper", ["borovica", "korijen", "biljno"]),
    # ── London Dry & variants ─────────────────────────────────────────────────
    # Beefeater 24: green tea + standard botanicals (producer)
    (r"beefeater.*24", "london-dry", "London, UK", 3, 2, "classic-juniper", ["travnato", "citrus", "cvjetno"]),
    # Beefeater standard: traditional recipe incl. coriander, licorice, angelica
    (r"beefeater", "london-dry", "London, UK", 3, 2, "classic-juniper", ["borovica", "citrus", "zacini"]),
    # Tanqueray No. Ten: grapefruit, lime blossom, chamomile (producer)
    (r"tanqueray\s+no\.?\s*ten|tanqueray\s+n\.?\s*ten|tanqueray.*10", "premium-dry", "London, UK", 3, 2, "classic-juniper", ["citrus", "cvjetno", "travnato"]),
    # Tanqueray standard: classic London dry
    (r"tanqueray", "london-dry", "Engleska", 3, 2, "classic-juniper", ["borovica", "citrus", "travnato"]),
    # No. 3: angelica root, cardamom, coriander (producer)
    (r"no\.?\s*3\b|number\s*three", "london-dry", "Engleska", 3, 2, "classic-juniper", ["borovica", "korijen", "citrus"]),
    # Windspiel editions
    (r"windspiel.*pfeffer|windspiel.*kampot", "premium-dry", "Njema\u010dka", 3, 2, "botanical", ["papar", "biljno", "citrus"]),
    (r"windspiel.*kaffee|windspiel.*caxambu", "premium-dry", "Njema\u010dka", 3, 2, "botanical", ["kava", "zacini", "biljno"]),
    (r"windspiel", "premium-dry", "Njema\u010dka", 3, 2, "classic-juniper", ["borovica", "citrus", "biljno"]),
    # Scapegrace Gold: navy-strength premium NZ dry
    (r"scapegrace.*gold", "premium-dry", "Engleska", 4, 1, "classic-juniper", ["borovica", "citrus", "zacini"]),
    # Akori, Roby Marton: Italian premium dry
    (r"akori", "premium-dry", "Engleska", 3, 2, "classic-juniper", ["biljno", "borovica", "travnato"]),
    (r"roby\s*marton", "premium-dry", "Italija", 3, 2, "classic-juniper", ["biljno", "borovica", "citrus"]),
    # Generic premium-dry fallback
    (r"premium.*dry|dry.*premium", "premium-dry", "Engleska", 3, 2, "classic-juniper", ["borovica", "citrus", "biljno"]),
    # ── Mediterranean ────────────────────────────────────────────────────────
    (r"nordes", "contemporary", "Galicija, \u0160panjolska", 3, 2, "mediterranean", ["biljno", "citrus", "travnato"]),
    (r"nordes|nordés|portofino|mediterranean", "contemporary", "Mediteran", 3, 2, "mediterranean", ["biljno", "citrus", "travnato"]),
    # ── Japanese ──────────────────────────────────────────────────────────────
    (r"roku|ki no bi|kinobi|nikka|etsu|japanese", "contemporary", "Japan", 3, 2, "botanical", ["cvjetno", "citrus", "papar"]),
    # ── Croatian ──────────────────────────────────────────────────────────────
    # Aura Karbun: navy strength, charcoal (producer)
    (r"aura.*karbun", "croatian", "Istra, Hrvatska", 4, 1, "botanical", ["biljno", "borovica", "citrus"]),
    (r"aura|maraska|badel|croati|istra|dalma|hrvatsk|dugave|dalmatian|dalmatinski|old pilot", "croatian", "Hrvatska", 3, 2, "botanical", ["biljno", "citrus", "zacini"]),
    # Old Pilot's Dalmatian: Dalmatian lavender, rosemary (producer)
    (r"old pilot|dalmatian.*gin", "croatian", "Hrvatska", 3, 2, "mediterranean", ["biljno", "cvjetno", "travnato"]),
    # ── Generic London dry fallback ───────────────────────────────────────────
    (r"london\s*dry|dry gin|bombay|broker|fords|hayman|city of london|gordons|gordon's", "london-dry", "Engleska", 3, 2, "classic-juniper", ["borovica", "citrus", "travnato"]),
    # ── Generic contemporary fallback ─────────────────────────────────────────
    (r"contemporary|g'?vine|the illusionist|bathtub|bobby", "contemporary", "World", 3, 2, "botanical", ["cvjetno", "citrus", "zacini"]),
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
