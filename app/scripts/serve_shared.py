# -*- coding: utf-8 -*-
"""Ispravni podaci za sheet Serviranje + Cigare (izvor istine za Excel i JSON export)."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CORRECTIONS_PATH = ROOT / "seed" / "serve_corrections.json"

SERVE_SCORE = {"++": 3, "+": 2, "~": 1, "x": 0}
SERVE_SCORE_REV = {3: "++", 2: "+", 1: "~", 0: "x"}

# Zamjene pogrešnih cigar hint tekstova (stari Excel) -> ispravno
HINT_REPLACEMENTS: list[tuple[str, str]] = [
    (r"Barbados/Dom\.?,?\s*natural wrapper", "Srednja, Habano ili San Andres maduro"),
    (r"natural wrapper", "Srednja, Habano ili San Andres maduro"),
    (r"puna maduro.*Doorly", "Srednja, Habano ili San Andres maduro"),
    (r"Nije za cigaru.*", "Uz koktel ili highball"),
]

# Profilni redovi na vrhu Serviranje + Cigare (rum)
RUM_SERVE_PROFILES: list[dict] = [
    {
        "name": "Barbados clean (Doorly's, Foursquare, Mount Gay)",
        "neat": "++",
        "water": "++",
        "rocks": "~",
        "highball": "x",
        "cola": "x",
        "best": "Cisto / kap vode",
        "cigarHint": "Srednja, Habano ili San Andres maduro",
    },
    {
        "name": "Jamajka esterska (Hampden, Worthy Park)",
        "neat": "++",
        "water": "++",
        "rocks": "~",
        "highball": "+",
        "cola": "x",
        "best": "Kap vode (otvara estere)",
        "cigarHint": "Puna Habano/maduro cigara",
    },
    {
        "name": "Agricole (Clement, Neisson)",
        "neat": "++",
        "water": "++",
        "rocks": "~",
        "highball": "+",
        "cola": "x",
        "best": "Cisto / Ti' Punch",
        "cigarHint": "Laganija, Connecticut shade",
    },
    {
        "name": "Demerara / solera (El Dorado, Dictador)",
        "neat": "+",
        "water": "+",
        "rocks": "++",
        "highball": "+",
        "cola": "x",
        "best": "On the rocks (velika kocka)",
        "cigarHint": "Srednja do puna maduro cigara",
    },
    {
        "name": "Dosladeni / spiced (Don Papa, Malibu)",
        "neat": "+",
        "water": "+",
        "rocks": "++",
        "highball": "+",
        "cola": "+",
        "best": "Velika kocka leda ili koktel",
        "cigarHint": "Lagana-srednja, Connecticut ili lagani Habano — NE puna cigara",
    },
]


def match_tokens(name: str) -> set[str]:
    stop = {
        "the", "de", "of", "and", "rum", "ron", "estate", "reserve", "reserva", "yo",
        "vol", "gb", "giftbox", "brandy", "cognac", "whisky", "whiskey",
    }
    toks = set(
        re.findall(
            r"[a-z0-9]+",
            unicodedata.normalize("NFKD", name.lower()).encode("ascii", "ignore").decode(),
        )
    )
    return {t for t in toks if t not in stop and not (t.isdigit() and len(t) <= 2)}


def normalize_hint(hint: str | None) -> str | None:
    if not hint:
        return None
    text = str(hint).strip()
    for pattern, replacement in HINT_REPLACEMENTS:
        if re.search(pattern, text, re.I):
            return replacement
    return text


def serving_dict_to_excel(serving: dict) -> tuple[str, str, str, str, str, str]:
    sm = SERVE_SCORE_REV
    s = serving
    return (
        sm.get(s.get("neat", 0), "+"),
        sm.get(s.get("water", 0), "+"),
        sm.get(s.get("rocks", 0), "~"),
        sm.get(s.get("highball", 0), "x"),
        sm.get(s.get("cola", 0), "x"),
        s.get("best", "Cisto"),
    )


def load_corrections() -> dict:
    if CORRECTIONS_PATH.exists():
        return json.loads(CORRECTIONS_PATH.read_text(encoding="utf-8-sig"))
    return {"rum_profiles": RUM_SERVE_PROFILES, "by_name": {}}


def find_correction(name: str, corrections: dict) -> dict | None:
    by_name = corrections.get("by_name", {})
    if name in by_name:
        return by_name[name]
    tokens = match_tokens(name)
    best, best_score = None, 0
    for key, row in by_name.items():
        score = len(tokens & match_tokens(key))
        if score > best_score:
            best, best_score = row, score
    return best if best and best_score >= 2 else None


def resolve_serve_hint(name: str, style: str, style_hint_fn) -> str | None:
    """Ispravan hint iz corrections; inace genericki po stilu."""
    corr = find_correction(name, load_corrections())
    if corr and corr.get("cigarHint"):
        return normalize_hint(corr["cigarHint"])
    hint = style_hint_fn(style)
    return normalize_hint(hint)
