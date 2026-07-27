#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Normalize leaf-origin country strings and derive isPuro.

Canonical country names match cigars.json `country` (Croatian labels).
Never invent binder/filler — callers only pass shop-sourced values.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any

# EN / DE / variants → HR catalog labels
COUNTRY_ALIASES: dict[str, str] = {
    "nicaragua": "Nikaragva",
    "nicaraguan": "Nikaragva",
    "nikaragva": "Nikaragva",
    "nikaragve": "Nikaragva",
    "honduras": "Honduras",
    "honduran": "Honduras",
    "dominican republic": "Dominikanska Republika",
    "dominican": "Dominikanska Republika",
    "dominikanische republik": "Dominikanska Republika",
    "dominikanska republika": "Dominikanska Republika",
    "dominikanska": "Dominikanska Republika",
    "dr": "Dominikanska Republika",
    "d.r.": "Dominikanska Republika",
    "cuba": "Kuba",
    "cuban": "Kuba",
    "kuba": "Kuba",
    "kubanski": "Kuba",
    "ecuador": "Ekvador",
    "ecuadorian": "Ekvador",
    "ekvador": "Ekvador",
    "mexico": "Meksiko",
    "mexican": "Meksiko",
    "meksiko": "Meksiko",
    "san andres": "Meksiko",
    "san andrés": "Meksiko",
    "san andres mexico": "Meksiko",
    "mexican san andres": "Meksiko",
    "brasil": "Brazil",
    "brazil": "Brazil",
    "brazilian": "Brazil",
    "brasilien": "Brazil",
    "usa": "SAD",
    "u.s.a.": "SAD",
    "u.s.": "SAD",
    "united states": "SAD",
    "united states of america": "SAD",
    "america": "SAD",
    "american": "SAD",
    "connecticut": "SAD",  # Connecticut shade grown in USA (origin country)
    "cameroon": "Kamerun",
    "kamerun": "Kamerun",
    "indonesia": "Indonezija",
    "indonesian": "Indonezija",
    "indonezija": "Indonezija",
    "sumatra": "Indonezija",
    "java": "Indonezija",
    "philippines": "Filipini",
    "filipini": "Filipini",
    "costa rica": "Kostarika",
    "kostarika": "Kostarika",
    "panama": "Panama",
    "peru": "Peru",
    "colombia": "Kolumbija",
    "kolumbija": "Kolumbija",
    "italy": "Italija",
    "italija": "Italija",
    "spain": "Španjolska",
    "spanjolska": "Španjolska",
    "nicaragua / honduras": "MULTI",
}


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.lower().strip()


def _clean_raw(raw: str | None) -> str | None:
    if raw is None:
        return None
    t = str(raw).strip()
    if not t or t in ("—", "-", "?", "n/a", "N/A", "undisclosed"):
        return None
    if re.search(r"not available|undisclosed|n/?a\b|unknown", t, re.I):
        return None
    return t


def is_multi_origin(raw: str) -> bool:
    """True if the string lists more than one country (blend filler etc.)."""
    t = raw.strip()
    if not re.search(r"\b(and|&|/|\+|plus)\b|,|;", t, re.I):
        return False
    parts = re.split(r"\s*(?:,|;|/|&|\band\b|\+)\s*", t, flags=re.I)
    countries: list[str] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # Avoid recursion through is_multi_origin — use alias lookup only
        folded = _fold(re.sub(r"\([^)]*\)", " ", p))
        folded = re.sub(r"\s+", " ", folded).strip()
        if folded in COUNTRY_ALIASES:
            v = COUNTRY_ALIASES[folded]
            if v != "MULTI":
                countries.append(v)
            continue
        for alias, canon in sorted(COUNTRY_ALIASES.items(), key=lambda kv: -len(kv[0])):
            if alias == "dr" or len(alias) < 4:
                continue
            if folded.startswith(alias + " ") or folded.endswith(" " + alias) or f" {alias} " in f" {folded} ":
                if canon != "MULTI":
                    countries.append(canon)
                break
    return len(set(countries)) > 1


def normalize_origin_single(raw: str | None) -> str | None:
    """Map one origin string to a single HR country, or None if unknown/multi."""
    t = _clean_raw(raw)
    if not t:
        return None
    if is_multi_origin(t):
        return None  # multi-country → not a single origin for puro

    folded = _fold(t)
    # strip variety suffixes in parentheses
    folded = re.sub(r"\([^)]*\)", " ", folded)
    folded = re.sub(r"\s+", " ", folded).strip()

    if folded in COUNTRY_ALIASES:
        v = COUNTRY_ALIASES[folded]
        return None if v == "MULTI" else v

    # "Nicaraguan Habano", "Ecuador Connecticut", "Mexican San Andres"
    for alias, canon in sorted(COUNTRY_ALIASES.items(), key=lambda kv: -len(kv[0])):
        if alias == "dr" or len(alias) < 4:
            continue
        if folded.startswith(alias + " ") or folded.endswith(" " + alias) or f" {alias} " in f" {folded} ":
            if canon == "MULTI":
                return None
            return canon

    # Exact HR labels already in catalog
    for canon in set(COUNTRY_ALIASES.values()):
        if canon != "MULTI" and _fold(canon) == folded:
            return canon

    return None


def display_leaf(raw: str | None, max_len: int = 48) -> str | None:
    """Keep shop variety/label for binder/filler/wrapper display."""
    t = _clean_raw(raw)
    if not t:
        return None
    return t[:max_len]


def leaf_from_facts(facts: dict[str, Any] | None) -> dict[str, str | None]:
    """Extract display + origin fields from CigarWorld-style facts dict."""
    facts = facts or {}
    # keys may be lowercased already
    def get(*keys: str) -> str | None:
        for k in keys:
            for fk, fv in facts.items():
                if str(fk).lower().strip() == k.lower():
                    return _clean_raw(fv)
        return None

    wrapper_display = get("wrapper", "wrapper variety", "wrapper leaf", "deckblatt")
    binder_display = get("binder", "binder variety", "umblatt")
    filler_display = get("filler", "filler variety", "einlage")

    wo = normalize_origin_single(get("wrapper origin") or wrapper_display)
    bo = normalize_origin_single(get("binder origin") or binder_display)
    fo = normalize_origin_single(get("filler origin") or filler_display)

    # If origin key missing but display is a country name, use it
    if not wo and wrapper_display:
        wo = normalize_origin_single(wrapper_display)
    if not bo and binder_display:
        bo = normalize_origin_single(binder_display)
    if not fo and filler_display:
        fo = normalize_origin_single(filler_display)

    return {
        "wrapper": display_leaf(wrapper_display),
        "binder": display_leaf(binder_display),
        "filler": display_leaf(filler_display),
        "wrapperOrigin": wo,
        "binderOrigin": bo,
        "fillerOrigin": fo,
    }


def derive_is_puro(
    wrapper_origin: str | None,
    binder_origin: str | None,
    filler_origin: str | None,
) -> bool | None:
    """true if all three equal; false if all known and differ; None if incomplete."""
    w, b, f = wrapper_origin, binder_origin, filler_origin
    if not w or not b or not f:
        return None
    if w == b == f:
        return True
    return False


def apply_cuban_default(cigar: dict[str, Any]) -> bool:
    """If manufacture country is Kuba and no contradictory origins, set all to Kuba.

    Returns True if any field was set.
    """
    if (cigar.get("country") or "").strip() != "Kuba":
        return False
    changed = False
    for key in ("wrapperOrigin", "binderOrigin", "fillerOrigin"):
        cur = cigar.get(key)
        if cur and cur != "Kuba":
            # contradictory shop data — do not override
            return False
    for key in ("wrapperOrigin", "binderOrigin", "fillerOrigin"):
        if not cigar.get(key):
            cigar[key] = "Kuba"
            changed = True
    return changed


def apply_leaf_fields(
    cigar: dict[str, Any],
    leaf: dict[str, str | None],
    *,
    prefer_existing: bool = True,
    fill_wrapper_display: bool = True,
) -> bool:
    """Merge leaf dict into cigar. Does not invent values.

    prefer_existing: keep non-empty cigar fields over incoming (CW already applied).
    """
    changed = False
    for display_key in ("wrapper", "binder", "filler"):
        incoming = leaf.get(display_key)
        if not incoming:
            continue
        if display_key == "wrapper" and not fill_wrapper_display:
            continue
        cur = (cigar.get(display_key) or "").strip()
        weak = (not cur) or cur in ("—", "-", "Natural", "?", "Maduro")
        if prefer_existing and cur and not weak and display_key != "wrapper":
            continue
        if prefer_existing and display_key == "wrapper" and cur and not weak:
            # still allow if incoming looks more specific (has origin word etc.) — keep simple
            continue
        if display_key == "wrapper" and weak and incoming:
            cigar["wrapper"] = incoming
            changed = True
        elif display_key in ("binder", "filler") and (not cur or weak):
            cigar[display_key] = incoming
            changed = True
        elif display_key in ("binder", "filler") and not prefer_existing:
            cigar[display_key] = incoming
            changed = True

    for origin_key in ("wrapperOrigin", "binderOrigin", "fillerOrigin"):
        incoming = leaf.get(origin_key)
        if not incoming:
            continue
        cur = cigar.get(origin_key)
        if prefer_existing and cur:
            continue
        cigar[origin_key] = incoming
        changed = True

    return changed


def refresh_is_puro(cigar: dict[str, Any]) -> bool | None:
    val = derive_is_puro(
        cigar.get("wrapperOrigin"),
        cigar.get("binderOrigin"),
        cigar.get("fillerOrigin"),
    )
    prev = cigar.get("isPuro")
    if val is None:
        if "isPuro" in cigar:
            del cigar["isPuro"]
            return None if prev is not None else prev
        return prev
    cigar["isPuro"] = val
    return val
