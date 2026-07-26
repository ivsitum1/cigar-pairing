# -*- coding: utf-8 -*-
"""Shared helpers for tequila/mezcal catalog scrape, Excel build, and JSON export."""
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
    "detect_age_tier",
    "detect_category_type",
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

TEQUILA_STOP = {
    "the", "of", "and", "vol", "tequila", "mezcal", "agave", "giftbox", "gift",
    "box", "poklon", "kutiji", "u", "in", "gb", "limited", "edition", "l", "de",
    "la", "el", "100", "puro", "with", "glass",
}

ALLEZ_LISTS = [
    ("https://allez.hr/shop/tequila-mezcal", "tequila-mezcal"),
]

ECUGA_CATEGORIES: list[tuple[str, str, str]] = [
    ("tequila", "", "Tequila"),
    ("mezcal", "", "Mezcal"),
]

# pattern, style, region, body, sweetness, tags
STYLE_RULES: list[tuple[str, str, str, int, int, list[str]]] = [
    (r"extra\s*a[nñ]ejo|extra anejo|\bxa\b|1942|reserva de la familia", "extra-anejo", "Jalisco, Meksiko", 5, 4, ["hrast", "kakao", "vanilija", "suho-voce"]),
    (r"a[nñ]ejo|anejo", "anejo", "Jalisco, Meksiko", 4, 3, ["hrast", "vanilija", "karamela", "agava"]),
    (r"reposado", "reposado", "Jalisco, Meksiko", 3, 3, ["agava", "hrast", "vanilija", "papar"]),
    (r"blanco|plata|silver|cristalino", "blanco", "Jalisco, Meksiko", 2, 2, ["agava", "citrus", "papar", "biljno"]),
    (r"mezcal|espad[ií]n|tobala|tobala|del maguey|montana", "mezcal", "Oaxaca, Meksiko", 4, 2, ["dim", "agava", "zemljano", "papar"]),
]

NON_PAIRABLE_RE = re.compile(
    r"mixto|gold(?!\s*blanco)|flavou?r|liker|liqueur|cocktail|rtd|premix|"
    r"margarita|ready to drink|cream|coffee",
    re.I,
)

PREMIUM_BRANDS = {
    "don julio", "patrón", "patron", "herradura", "fortaleza", "clase azul",
    "casamigos", "espolón", "espolon", "olmeca altos", "codigo", "código",
    "tequila ocho", "tapatio", "tapatio", "siete leguas", "fuente", "1942",
    "del maguey", "montelobos",
}

MIXTO_HINT = re.compile(r"jose cuervo\s+especial|cuervo\s+gold|mixto|40%\s*agave", re.I)


def match_tokens(name: str) -> set[str]:
    toks = set(
        re.findall(
            r"[a-z0-9]+",
            unicodedata.normalize("NFKD", name.lower()).encode("ascii", "ignore").decode(),
        )
    )
    return {t for t in toks if t not in TEQUILA_STOP and not (t.isdigit() and len(t) <= 2)}


def token_overlap(a: str, b: str) -> int:
    return len(match_tokens(a) & match_tokens(b))


def extract_abv(name: str) -> float | None:
    m = re.search(r"(\d{2}(?:[.,]\d+)?)\s*%\s*(?:Vol|vol)?", name)
    if m:
        return float(m.group(1).replace(",", "."))
    return None


def detect_category_type(name: str, ecuga_category: str = "") -> str:
    low = f"{name} {ecuga_category}".lower()
    if re.search(r"mezcal", low):
        return "mezcal"
    if NON_PAIRABLE_RE.search(low) or MIXTO_HINT.search(low):
        return "non-pairable"
    return "tequila"


def detect_age_tier(name: str) -> str:
    low = name.lower()
    if re.search(r"extra\s*a[nñ]ejo|\bxa\b|1942", low):
        return "extra-anejo"
    if re.search(r"a[nñ]ejo|anejo", low):
        return "anejo"
    if re.search(r"reposado", low):
        return "reposado"
    if re.search(r"blanco|plata|silver", low):
        return "blanco"
    if re.search(r"mezcal", low):
        return "mezcal"
    return "unknown"


def detect_style_region(name: str, ecuga_category: str = "") -> tuple[str, str, int, int, list[str]]:
    text = f"{name} {ecuga_category}"
    for pattern, style, region, body, sweet, tags in STYLE_RULES:
        if re.search(pattern, text, re.IGNORECASE):
            return style, region, body, sweet, list(tags)
    cat = detect_category_type(name, ecuga_category)
    if cat == "mezcal":
        return "mezcal", "Oaxaca, Meksiko", 4, 2, ["dim", "agava", "zemljano"]
    return "blanco", "Jalisco, Meksiko", 2, 2, ["agava", "citrus", "papar"]


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
        return float(seed_score)
    if category == "non-pairable" or NON_PAIRABLE_RE.search(name) or MIXTO_HINT.search(name):
        return 3.5
    score = 6.0
    tier_bonus = {
        "blanco": 0.2,
        "reposado": 0.5,
        "anejo": 0.9,
        "extra-anejo": 1.4,
        "mezcal": 0.4,
        "unknown": 0.0,
    }
    score += tier_bonus.get(age_tier, 0.0)
    low = name.lower()
    for brand in PREMIUM_BRANDS:
        if brand in low:
            score += 0.8
            break
    if "100" in low and "agave" in low:
        score += 0.3
    if price:
        if price >= 180:
            score += 1.0
        elif price >= 90:
            score += 0.7
        elif price >= 55:
            score += 0.4
        elif price >= 35:
            score += 0.2
        elif price < 22:
            score -= 0.5
    if style == "mezcal":
        # sipping mezcal OK in catalog sheet; MASTER only if quality high
        score += 0.1
    return round(min(10.0, max(3.0, score)), 1)


def is_pairable(name: str, style: str, category: str, quality: float) -> bool:
    if category == "non-pairable" or NON_PAIRABLE_RE.search(name) or MIXTO_HINT.search(name):
        return False
    # Mezcal: only clear sipping profiles (quality gate)
    if style == "mezcal" or category == "mezcal":
        return quality >= 7.0
    return quality >= 5.5


def serving_for_style(style: str) -> dict[str, Any]:
    if style in ("anejo", "extra-anejo"):
        return {"neat": 3, "rocks": 2, "best": "Cisto (snifter)"}
    if style == "reposado":
        return {"neat": 3, "rocks": 2, "best": "Cisto ili velika kocka leda"}
    if style == "mezcal":
        return {"neat": 3, "rocks": 1, "best": "Cisto, sobna temperatura"}
    return {"neat": 3, "rocks": 2, "best": "Cisto / lagano ohlađeno"}


def cigar_hint_for_style(style: str) -> str:
    hints = {
        "blanco": "Connecticut / blagi Habano — čista agava",
        "reposado": "Habano srednje snage — agava + hrast",
        "anejo": "Habano / maduro — vanilija i hrast",
        "extra-anejo": "Maduro / oscuro — gusta večer",
        "mezcal": "Corojo / oscura — dim uz dim",
    }
    return hints.get(style, "Srednja cigara, balans snage")


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
