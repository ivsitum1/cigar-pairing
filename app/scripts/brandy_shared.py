# -*- coding: utf-8 -*-
"""Shared helpers for brandy/cognac catalog scrape, Excel build, and JSON export."""
from __future__ import annotations

import re
import unicodedata
from typing import Any

from whisky_shared import format_price_eur, parse_price_eur, slugify

__all__ = [
    "BRANDY_STOP",
    "ECUGA_CATEGORIES",
    "STYLE_RULES",
    "catalog_index",
    "cigar_hint_for_style",
    "detect_age_tier",
    "detect_category_type",
    "detect_style_region",
    "detect_sweetening",
    "estimate_quality",
    "extract_abv",
    "find_best_catalog_match",
    "format_price_eur",
    "is_pairable",
    "match_tokens",
    "parse_price_eur",
    "serving_for_style",
    "slugify",
    "sweetening_to_additive",
    "token_overlap",
]

BRANDY_STOP = {
    "the", "of", "and", "yo", "vol", "old", "years", "year", "brandy", "cognac",
    "konjak", "vinjak", "giftbox", "gift", "box", "poklon", "kutiji", "u", "in",
    "gb", "limited", "edition", "extra", "reserve", "fine", "l", "de", "la", "le",
    "du", "des", "single", "estate", "champagne", "grande",
}

ECUGA_CATEGORIES: list[tuple[str, str, str]] = [
    ("cognac", "", "Cognac"),
    ("brandy", "", "Brandy"),
    ("armagnac", "", "Armagnac"),
    ("calvados", "", "Calvados"),
]

ALLEZ_LISTS = [
    ("https://allez.hr/shop/cognac-calvados-armagnac", "cognac-calvados-armagnac"),
    ("https://allez.hr/shop/absinthe-brandy-grappa-sake", "brandy-grappa"),
]

STYLE_RULES: list[tuple[str, str, str, int, int, list[str]]] = [
    (r"hennessy\s+vs\b|\bvs cognac|\bcognac vs\b|\bvs\b.*cognac", "cognac-vs", "Cognac, Francuska", 3, 3, ["voce", "vanilija", "hrast"]),
    (r"\bxo\b|extra old|hors d|paradis|louis xiii|richard hennessy", "cognac-xo", "Cognac, Francuska", 4, 3, ["suho-voce", "kakao", "zacini", "koza"]),
    (r"vsop|v\.s\.o\.p|1738|accord royal", "cognac-vsop", "Cognac, Francuska", 3, 3, ["voce", "vanilija", "zacini", "hrast"]),
    (r"armagnac|dartigalongue|janneau|chateau de laubade|domaine du tarriquet", "armagnac", "Armagnac, Francuska", 4, 3, ["suho-voce", "prune", "zacini", "hrast"]),
    (r"calvados|boulard|dupont|christian drouin", "calvados", "Normandija, Francuska", 3, 3, ["jabuka", "cimet", "hrast"]),
    (r"carlos i|fundador|magnifico|gran reserva|brandy de jerez|lepanto|soberano", "brandy-de-jerez", "Jerez, Španjolska", 4, 3, ["orah", "karamela", "suho-voce", "hrast"]),
    (r"torres|gran duque|reserva|spanish brandy|magnifico", "brandy-spanish", "Španjolska", 3, 3, ["karamela", "suho-voce", "hrast"]),
    (r"metaxa|tsipouro|ouzo|brandy greek", "brandy-greek", "Grčka", 3, 4, ["med", "voce", "zacini"]),
    (r"vecchia romagna|grappa|nonino|berta|poli|marchesi", "brandy-italian", "Italija", 3, 2, ["grozdje", "hrast"]),
    (r"ararat|armenian|noah", "brandy-armenian", "Armenija", 4, 3, ["suho-voce", "cokolada", "zacini"]),
    (r"asbach|weinbrand|german brandy", "brandy-german", "Njemačka", 3, 3, ["voce", "hrast", "karamela"]),
    (r"badel|vinjak|stock|maraska|lozovaca|rakija", "vinjak", "Hrvatska", 3, 3, ["grozdje", "med", "hrast"]),
    (r"jameson|irish|bushmills|paddy", "brandy-irish", "Irska", 3, 3, ["voce", "vanilija", "med"]),
    (r"martell|remy|hennessy|camus|hine|delamain|davidoff|courvoisier", "cognac-vsop", "Cognac, Francuska", 3, 3, ["voce", "vanilija", "hrast"]),
]

NON_PAIRABLE_CATEGORIES = {"grappa", "pisco", "absinthe", "sake", "liqueur", "other-spirit"}
NON_PAIRABLE_RE = re.compile(
    r"grappa|pisco|absinthe|absinthe|sake|liqueur|liker|cocktail|flavou?r|"
    r"premix|sambuca|ouzo|tsipouro|amaretto|grand marnier",
    re.I,
)

PREMIUM_BRANDS = {
    "hennessy", "remy", "martell", "camus", "delamain", "hine", "carlos",
    "fundador", "torres", "metaxa", "ararat", "boulard", "janneau",
}

AGE_TIER_RE = [
    (r"\bxo\b|extra old|hors d|paradis|louis xiii", "xo"),
    (r"vsop|v\.s\.o\.p|1738|reserve", "vsop"),
    (r"\bvs\b|v\.s\.|three star|3 star", "vs"),
    (r"\b(\d{1,2})\s*(?:yo|years?|jears?|god)\b", "age"),
]


def match_tokens(name: str) -> set[str]:
    toks = set(
        re.findall(
            r"[a-z0-9]+",
            unicodedata.normalize("NFKD", name.lower()).encode("ascii", "ignore").decode(),
        )
    )
    return {t for t in toks if t not in BRANDY_STOP and not (t.isdigit() and len(t) <= 2)}


def token_overlap(a: str, b: str) -> int:
    return len(match_tokens(a) & match_tokens(b))


def extract_abv(name: str) -> float | None:
    m = re.search(r"(\d{2}(?:[.,]\d+)?)\s*%\s*(?:Vol|vol)?", name)
    if m:
        return float(m.group(1).replace(",", "."))
    return None


def detect_category_type(name: str, ecuga_category: str = "") -> str:
    low = f"{name} {ecuga_category}".lower()
    if NON_PAIRABLE_RE.search(low):
        if re.search(r"grappa", low, re.I):
            return "grappa"
        if re.search(r"pisco", low, re.I):
            return "pisco"
        if re.search(r"absinthe", low, re.I):
            return "absinthe"
        if re.search(r"sake", low, re.I):
            return "sake"
        if re.search(r"liqueur|liker|grand marnier|amaretto", low, re.I):
            return "liqueur"
    if re.search(r"armagnac", low, re.I):
        return "armagnac"
    if re.search(r"calvados", low, re.I):
        return "calvados"
    if re.search(r"brandy de jerez|carlos i|fundador|lepanto|soberano", low, re.I):
        return "brandy-jerez"
    if re.search(r"vinjak|badel|lozovaca|maraska", low, re.I):
        return "vinjak"
    if re.search(r"cognac|hennessy|martell|remy|camus|delamain|hine|davidoff", low, re.I):
        return "cognac"
    if re.search(r"brandy|weinbrand|asbach|metaxa|torres|ararat", low, re.I):
        return "brandy-other"
    return "other"


def detect_age_tier(name: str) -> str:
    low = name.lower()
    for pattern, tier in AGE_TIER_RE:
        if re.search(pattern, low, re.I):
            if tier == "age":
                return "nas"
            return tier
    if re.search(r"\b\d{1,2}\s*(?:yo|years?|jears?)\b", low, re.I):
        return "nas"
    return "unknown"


def detect_style_region(name: str, ecuga_category: str = "") -> tuple[str, str, int, int, list[str]]:
    text = f"{name} {ecuga_category}"
    for pattern, style, region, body, sweet, tags in STYLE_RULES:
        if re.search(pattern, text, re.IGNORECASE):
            return style, region, body, sweet, list(tags)
    cat = detect_category_type(name, ecuga_category)
    cat_map = {
        "cognac": ("cognac-vsop", "Cognac, Francuska", 3, 3, ["voce", "vanilija"]),
        "armagnac": ("armagnac", "Armagnac, Francuska", 4, 3, ["suho-voce", "prune"]),
        "calvados": ("calvados", "Normandija, Francuska", 3, 3, ["jabuka", "cimet"]),
        "brandy-jerez": ("brandy-de-jerez", "Jerez, Španjolska", 4, 3, ["orah", "karamela"]),
        "vinjak": ("vinjak", "Hrvatska", 3, 3, ["grozdje", "med"]),
        "grappa": ("brandy-italian", "Italija", 2, 2, ["grozdje"]),
    }
    if cat in cat_map:
        st, reg, body, sweet, tags = cat_map[cat]
        return st, reg, body, sweet, tags
    return "brandy-spanish", "World", 3, 3, ["hrast", "voce"]


def detect_sweetening(name: str, category: str) -> str:
    low = name.lower()
    if category in ("grappa", "pisco", "absinthe", "cognac", "armagnac", "calvados", "brandy-jerez"):
        if category == "brandy-jerez":
            return "sweetened"
        if category in ("cognac", "armagnac", "calvados"):
            return "clean"
    if re.search(r"metaxa|doslad|sweet|sladk", low, re.I):
        return "sweetened"
    if re.search(r"solera|jerez|carlos|fundador", low, re.I):
        return "sweetened"
    return "unknown"


def sweetening_to_additive(sweetening: str, category: str) -> str:
    if category in NON_PAIRABLE_CATEGORIES:
        return "flavored"
    if sweetening == "clean":
        return "clean"
    if sweetening == "sweetened":
        return "moderate"
    return "unknown"


def estimate_quality(
    name: str,
    price: float | None,
    style: str,
    category: str,
    age_tier: str,
    abv: float | None,
    seed_score: float | None = None,
) -> float:
    if seed_score is not None:
        return seed_score
    if category in NON_PAIRABLE_CATEGORIES:
        return 3.5
    score = 5.5
    tier_bonus = {"vs": 0.0, "vsop": 0.5, "xo": 1.5, "hors": 2.0, "nas": 0.3, "unknown": 0.0}
    score += tier_bonus.get(age_tier, 0.0)
    low = name.lower()
    for brand in PREMIUM_BRANDS:
        if brand in low:
            score += 0.6
            break
    if price:
        if price >= 200:
            score += 1.0
        elif price >= 120:
            score += 0.7
        elif price >= 70:
            score += 0.4
        elif price >= 45:
            score += 0.2
        elif price < 25:
            score -= 0.4
    if style in ("cognac-xo", "armagnac", "brandy-de-jerez"):
        score += 0.4
    if style == "cognac-vs":
        score -= 0.5
    return round(min(10.0, max(3.0, score)), 1)


def is_pairable(category: str, style: str, quality: float) -> bool:
    if category in NON_PAIRABLE_CATEGORIES:
        return False
    if category == "grappa":
        return False
    return quality >= 4.0


def serving_for_style(style: str, abv: float | None, category: str) -> dict[str, Any]:
    if category in NON_PAIRABLE_CATEGORIES:
        return {"neat": 1, "water": 0, "rocks": 1, "highball": 2, "cola": 0, "best": "Koktel / digestif"}
    if style in ("cognac-xo", "armagnac", "brandy-de-jerez"):
        best = "Cisto (snifter)"
        neat, water, rocks = 3, 2, 1
    elif style in ("cognac-vsop", "cognac-vs"):
        best = "Cisto ili velika kocka leda"
        neat, water, rocks = 3, 2, 2
    elif style == "calvados":
        best = "Cisto / lagano ohlađeno"
        neat, water, rocks = 3, 1, 2
    elif style == "vinjak":
        best = "Cisto / on the rocks"
        neat, water, rocks = 3, 1, 3
    else:
        best = "Cisto"
        neat, water, rocks = 3, 2, 2
    return {"neat": neat, "water": water, "rocks": rocks, "highball": 0, "cola": 0, "best": best}


def cigar_hint_for_style(style: str) -> str:
    hints = {
        "cognac-vs": "Connecticut do srednje Habano — blaži konjak",
        "cognac-vsop": "Connecticut do Habano srednje snage",
        "cognac-xo": "Habano/oscuro — XO nosi jaču cigaru",
        "armagnac": "Habano/maduro — rustikalniji profil",
        "brandy-de-jerez": "Maduro/oscuro — orah i karamela",
        "brandy-spanish": "Maduro srednje snage",
        "calvados": "Connecticut/claro — jabuka + blaža cigara",
        "vinjak": "Connecticut do Habano blage-srednje",
        "brandy-greek": "Connecticut — med i začini",
        "brandy-armenian": "Habano srednje-jake",
        "brandy-italian": "Srednja cigara",
        "brandy-german": "Connecticut srednje snage",
    }
    return hints.get(style, "Srednja cigara, balans snage")


def find_best_catalog_match(name: str, catalog: list[dict]) -> dict | None:
    tokens = match_tokens(name)
    best, best_score = None, 0
    for entry in catalog:
        score = len(tokens & entry["tokens"])
        if score > best_score:
            best, best_score = entry, score
    return best if best and best_score >= 2 else None


def catalog_index(entries: list[dict]) -> list[dict]:
    out = []
    for e in entries:
        out.append({**e, "tokens": match_tokens(e["name"])})
    return out
