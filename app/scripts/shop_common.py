#!/usr/bin/env python3
"""Zajedničke determinističke funkcije za shop-katalog pipeline (Faza A/B/C).

Uvozi se iz enrich-region-links.py i build-market-cigars.py — bez copy-paste,
da svi agenti (Claude/Cursor) rade identično. Vidi playbook:
docs/superpowers/plans/2026-07-21-phase-b-c-execution-playbook.md
"""
from __future__ import annotations
import re
import unicodedata
from datetime import date

# Tečajevi osvježeni 2026-07-01 (ECB/Wise mid-market, zaokruženi).
# Sljedeće osvježavanje: ~2026-10-01 (kvartalno).
USD_TO_EUR = 0.91  # zakovani tečaj; USD ponude postaju priceApprox
GBP_TO_EUR = 1.19  # zakovani; GBP → EUR approx
CHF_TO_EUR = 1.06  # zakovani; CHF → EUR approx

FETCH_DATE: str = date.today().isoformat()  # YYYY-MM-DD, postavlja se kad skripta radi
REGIONS = ("HR", "EU", "USA")

SHOP_LABEL = {
    "humidor_hr": "The Humidor",
    "havana_hr": "Havana Cigar Shop",
    "cigarworld_eu": "CigarWorld",
    "cgars_uk": "C.Gars Ltd",
    "la_couronne_ch": "La Couronne",
    "holts_us": "Holt's",
    "cigarsdaily_us": "Cigars Daily",
    "famous_smoke_us": "Famous Smoke",
    "neptune_us": "Neptune Cigar",
}
SHOP_REGION = {
    "humidor_hr": "HR", "havana_hr": "HR",
    "cigarworld_eu": "EU", "cgars_uk": "EU", "la_couronne_ch": "EU",
    "holts_us": "USA", "cigarsdaily_us": "USA",
    "famous_smoke_us": "USA", "neptune_us": "USA",
}


def strip_diacritics(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(ch for ch in s if not unicodedata.combining(ch))


def slug(s: str) -> str:
    s = strip_diacritics(s).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-{2,}", "-", s)


def sort_key(c: dict):
    def f(s: str) -> str:
        return strip_diacritics(s or "").casefold()
    return (f(c.get("brand", "")), f(c.get("line", "")), f(c.get("vitola", "")), c.get("id", ""))


def is_cuban(country: str | None) -> bool:
    c = (country or "").lower()
    return "kub" in c or "cuba" in c


def to_eur(amount, currency) -> tuple[float | None, bool]:
    """Vrati (priceEUR, approx). USD/GBP/CHF -> EUR uz zakovani tečaj (approx=True)."""
    if amount is None:
        return None, False
    cur = (currency or "EUR").upper()
    if cur == "USD":
        return round(float(amount) * USD_TO_EUR, 2), True
    if cur == "GBP":
        return round(float(amount) * GBP_TO_EUR, 2), True
    if cur == "CHF":
        return round(float(amount) * CHF_TO_EUR, 2), True
    return round(float(amount), 2), False


def best_offer(offers: list[dict]) -> dict | None:
    """Najreprezentativnija single-cigar ponuda: in-stock prvo, single pakiranje,
    pa najniža cijena. Deterministički."""
    if not offers:
        return None

    def key(o):
        pkg = (o.get("packaging") or {}).get("type") or ""
        single = 0 if pkg in ("single", "single_equiv") else 1
        return (0 if o.get("inStock") else 1, single, o.get("amount") if o.get("amount") is not None else 9e9,
                o.get("url") or "")
    return sorted(offers, key=key)[0]
