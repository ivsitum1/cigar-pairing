# -*- coding: utf-8 -*-
"""Rum style/region heuristics from bottle name (offline shop ingest)."""
from __future__ import annotations

import re
from typing import Any

# (regex on name, style, region, body, sweetness, tags)
STYLE_RULES: list[tuple[str, str, str, int, int, list[str]]] = [
    (r"spiced|black\s*barrel|kraken|captain\s*morgan", "spiced", "Spiced / aromatizirano", 2, 5, ["vanilija", "zacini", "karamela"]),
    (r"liqueur|liker|cream|coconut|kokos|malibu|elixir", "liqueur", "Liker (rum baza)", 1, 5, ["slatko", "voce"]),
    (r"hampden|worthy\s*park|appleton|smith\s*&?\s*cross|long\s*pond|monymusk|jamaic|ester|papalin|forsyth", "jamaica", "Jamajka", 4, 1, ["ester-funk", "tropsko-voce", "hrast"]),
    (r"cl[eé]ment|neisson|rhum\s*agricole|agricole|martinique|guadeloupe|marie[\s-]?galante|karukera|saint\s*james|jm\b|depaz|la\s*favorite", "agricole", "Agricole (Martinique)", 2, 1, ["travnato", "vegetalno", "citrus"]),
    (r"foursquare|mount\s*gay|doorly|rl\s*seale|barbados|r\.?\s*l\.?\s*seale", "barbados", "Barbados", 3, 1, ["suho-voce", "hrast", "vanilija"]),
    (r"havana\s*club|santiago\s*de\s*cuba|cuban|\bkuba\b", "cuba", "Kuba", 3, 1, ["zacini", "duhan", "citrus"]),
    (r"el\s*dorado|diamond|enmore|port\s*mourant|skeldon|demerara|guyana|gvajana", "demerara", "Gvajana (Demerara)", 4, 3, ["melasa", "tamno-voce", "karamela"]),
    (r"zacapa|botran|solera|centenario|diplomatico|dictador|barcelo|brugal|matusalem|botucal", "solera", "Solera / doslađen stil", 3, 3, ["karamela", "vanilija", "hrast"]),
    (r"flor\s*de\s*ca[nñ]a|nicaragua|nikaragva", "nicaragua-dry", "Nikaragva", 3, 1, ["hrast", "suho-voce"]),
    (r"colombian|kolumbij", "colombia", "Kolumbija", 3, 2, ["suho-voce", "vanilija"]),
    (r"chairman|admiral\s*rodney|saint\s*lucia|st\.?\s*lucia|sv\.?\s*lucij", "st-lucia", "Sv. Lucija", 3, 1, ["vanilija", "duhan", "hrast"]),
    (r"angostura|trinidad", "trinidad", "Trinidad", 3, 2, ["karamela", "hrast"]),
    (r"bacardi|don\s*q|puerto\s*rico", "puerto-rico", "Puerto Rico", 3, 1, ["hrast", "vanilija"]),
    (r"santa\s*teresa|venezuela|pampero|canaima", "venezuela", "Venezuela", 3, 2, ["karamela", "suho-voce"]),
    (r"dominic", "dominican", "Dominikanska Republika", 3, 3, ["karamela", "vanilija"]),
    (r"navy|overproof|151\b|gunpowder", "navy", "Navy / overproof", 4, 2, ["melasa", "dim", "zacini"]),
    (r"plantation|compagnie\s*des\s*indes|habitation\s*velier|clairin|trois\s*rivi", "blend", "Blend (vise regija)", 3, 2, ["suho-voce", "hrast"]),
    (r"panama|abuelo", "panama", "Panama", 3, 3, ["karamela", "vanilija"]),
    (r"reunion|savanna|mauricij|mauritius|fiji|bermuda|gosling", "other", "Otoci / ostalo", 3, 2, ["karamela", "hrast"]),
    (r"a\.?\s*h\.?\s*riise|\briise\b", "other", "Danska (spirit drink)", 3, 4, ["karamela", "vanilija"]),
]

NON_PAIRABLE = {"spiced", "liqueur", "mixing"}

SERVING = {
    "jamaica": {"neat": 3, "water": 3, "rocks": 1, "highball": 1, "cola": 0, "best": "Kap vode"},
    "agricole": {"neat": 3, "water": 3, "rocks": 1, "highball": 2, "cola": 0, "best": "Čisto / Ti' Punch"},
    "demerara": {"neat": 2, "water": 2, "rocks": 3, "highball": 1, "cola": 0, "best": "Velika kocka leda"},
    "solera": {"neat": 2, "water": 2, "rocks": 3, "highball": 1, "cola": 0, "best": "Velika kocka leda"},
    "navy": {"neat": 2, "water": 3, "rocks": 2, "highball": 1, "cola": 0, "best": "Kap vode"},
    "spiced": {"neat": 1, "water": 0, "rocks": 2, "highball": 3, "cola": 3, "best": "Koktel / highball"},
    "liqueur": {"neat": 1, "water": 0, "rocks": 2, "highball": 2, "cola": 1, "best": "Rocks / koktel"},
}


def extract_abv(name: str) -> float | None:
    m = re.search(r"(\d{1,2}(?:[.,]\d+)?)\s*%\s*(?:vol\.?)?", name, re.I)
    if not m:
        return None
    return float(m.group(1).replace(",", "."))


def detect_style_region(name: str) -> tuple[str, str, int, int, list[str]]:
    text = name or ""
    for pattern, style, region, body, sweet, tags in STYLE_RULES:
        if re.search(pattern, text, re.I):
            return style, region, body, sweet, list(tags)
    return "other", "Nepoznato", 3, 2, ["hrast", "voce"]


def estimate_quality(name: str, price: float | None, style: str) -> float:
    q = 6.0
    if style in ("jamaica", "agricole", "barbados", "demerara"):
        q = 7.5
    if style in ("spiced", "liqueur"):
        q = 5.0
    if price is not None:
        if price >= 120:
            q = max(q, 8.0)
        elif price >= 70:
            q = max(q, 7.5)
        elif price >= 40:
            q = max(q, 7.0)
        elif price < 20:
            q = min(q, 5.5)
    if re.search(r"\b(?:xo|ecs|exceptional|cask\s*strength|single\s*cask)\b", name or "", re.I):
        q = min(9.5, q + 0.5)
    return round(q, 1)


def is_pairable(style: str, quality: float) -> bool:
    if style in NON_PAIRABLE:
        return False
    return quality >= 4.0


def serving_for_style(style: str, additive: str = "unknown") -> dict[str, Any]:
    if additive in ("sweetened", "flavored") and style not in NON_PAIRABLE:
        return {"neat": 2, "water": 3, "rocks": 3, "highball": 1, "cola": 0, "best": "Velika kocka leda"}
    if style in SERVING:
        return dict(SERVING[style])
    return {"neat": 3, "water": 3, "rocks": 1, "highball": 0, "cola": 0, "best": "Čisto / kap vode"}


def additive_for_style(style: str, name: str) -> tuple[str, dict[str, str] | None]:
    if style in ("spiced", "liqueur"):
        return "flavored", {"hr": "Aromatizirano / doslađeno", "en": "Flavoured / sweetened"}
    if style == "agricole":
        return "clean", {"hr": "Bez aditiva (AOC stil)", "en": "No additives (AOC-style)"}
    if style in ("jamaica", "barbados") and re.search(r"hampden|foursquare|worthy", name or "", re.I):
        return "clean", {"hr": "Čist / vrlo nizak", "en": "Clean / very low"}
    if style == "solera":
        return "sweetened", {"hr": "Često doslađen (solera stil)", "en": "Often sweetened (solera style)"}
    return "unknown", None
