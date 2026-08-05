#!/usr/bin/env python3
"""Merge scraped Neptune Cigar profiles into cigars.json.

Input:  scripts/output/neptune_raw.json   (built by scrape-neptune-profiles.py)
Output: app/src/data/cigars.json  (updated in place, idempotent per id)

Merge rules (per cigar record):
  - Only touches records whose id is present in neptune_raw.json
  - Never overwrites existing flavorTags / strength / wrapper with a shop value
    if the record already has them from a curated / non-market source
  - strength + body: only set if record has profileEstimated==True or has no
    strength at all; sets strengthFromShop=True
  - wrapper: only set if record currently has "—"
  - flavorTags: accumulated from description text via the standard word→tag map
    (same mapping used by merge-flavor-enrichment.py); only set when at least
    2 tags found — otherwise the text is too sparse to be useful
  - profileEstimated: set to False when tags come from Neptune shop text

Usage (run from app/):
  python scripts/merge-neptune-profiles.py
  python scripts/merge-neptune-profiles.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from taxonomy_lib import CIGARS_PATH, OUT_DIR, load_json, write_json  # noqa: E402

RAW = OUT_DIR / "neptune_raw.json"

# ---------------------------------------------------------------------------
# Flavour-tag word map (same as merge-flavor-enrichment.py)
# ---------------------------------------------------------------------------
WORD_TO_TAG: list[tuple[str, str]] = [
    (r"cocoa|chocolate|chocolat", "kakao"),
    (r"coffee|espresso|mocha", "kava"),
    (r"pepper|peppery", "papar"),
    (r"cream|creamy|creme", "kremasto"),
    (r"cedar", "cedar"),
    (r"earth|earthy|soil", "zemljano"),
    (r"nut|hazelnut|almond|walnut|pecan|cashew", "orasasti"),
    (r"leather", "koza"),
    (r"spice|spicy", "zacini"),
    (r"sweet spice", "zacini-slatki"),
    (r"honey", "med"),
    (r"caramel", "karamela"),
    (r"vanilla", "vanilija"),
    (r"citrus|lemon|orange|lime|grapefruit", "citrus"),
    (r"floral|flower|rose|jasmine", "cvjetno"),
    (r"dried fruit|dried fig|raisin", "suho-voce"),
    (r"dark fruit|dark berry|blackberry|plum", "tamno-voce"),
    (r"fruit|berry|cherry", "suho-voce"),
    (r"wood|woody|oak|cedar wood|toasted|roasted", "drvo"),
    (r"molasses", "melasa"),
    (r"grass|hay|barnyard", "trava-slatka"),
    (r"tobacco", "duhan"),
    (r"smoke|smoky", "dim"),
    (r"sweet(?:ness)?", "slatko"),
]

WRAPPER_FROM_TEXT: list[tuple[str, str]] = [
    (r"maduro|oscuro|broadleaf|san andr", "Maduro"),
    (r"corojo", "Corojo"),
    (r"sumatra", "Sumatra"),
    (r"cameroon", "Cameroon"),
    (r"connecticut|shade|claro\b", "Connecticut"),
    (r"criollo", "Criollo"),
    (r"habano|sun.?grown|sungrown", "Habano"),
]

STRENGTH_MAP_TEXT_TO_INT = {
    "mild": 2, "mild to medium": 2, "medium to mild": 2,
    "medium": 3, "medium to full": 4, "full to medium": 4, "full": 5,
    "medium-mild": 2, "mild-medium": 2, "medium-full": 4, "full-medium": 4,
    "medium/full": 4, "full/medium": 4,
}

DASH = "\u2014"

# English → Croatian country name translations (for Neptune-provided origin text)
COUNTRY_HR: dict[str, str] = {
    "nicaragua": "Nikaragva",
    "nicaraguan": "Nikaragva",
    "dominican republic": "Dominikanska Republika",
    "dominican": "Dominikanska Republika",
    "honduras": "Honduras",
    "honduran": "Honduras",
    "ecuador": "Ekvador",
    "ecuadorian": "Ekvador",
    "cuba": "Kuba",
    "cuban": "Kuba",
    "mexico": "Meksiko",
    "mexican": "Meksiko",
    "brazil": "Brazil",
    "brazilian": "Brazil",
    "peru": "Peru",
    "peruvian": "Peru",
    "colombia": "Kolumbija",
    "colombian": "Kolumbija",
    "costa rica": "Kostarika",
    "costa rican": "Kostarika",
    "cameroon": "Kamerun",
    "camerounian": "Kamerun",
    "indonesia": "Indonezija",
    "indonesian": "Indonezija",
    "sumatra": "Indonezija",
    "java": "Indonezija",
    "usa": "SAD",
    "united states": "SAD",
    "connecticut": "SAD",
    "haiti": "Haiti",
    "jamaican": "Jamajka",
    "jamaica": "Jamajka",
    "panama": "Panama",
    "panamanian": "Panama",
    "philippines": "Filipini",
    "philippine": "Filipini",
}


def _to_hr_country(text: str) -> str | None:
    """Map English country/origin text to Croatian. Returns None if unknown."""
    low = (text or "").lower().strip()
    if not low:
        return None
    # Try exact match first
    if low in COUNTRY_HR:
        return COUNTRY_HR[low]
    # Try substring match
    for key, val in COUNTRY_HR.items():
        if key in low:
            return val
    # Check if it looks like a country but in Croatian already (keep it)
    return None


def _tags_from_text(text: str) -> list[str]:
    low = (text or "").lower()
    tags: list[str] = []
    seen: set[str] = set()
    for pat, tag in WORD_TO_TAG:
        if tag not in seen and re.search(pat, low):
            tags.append(tag)
            seen.add(tag)
    return tags


def _wrapper_from_text(text: str) -> str | None:
    low = (text or "").lower()
    for pat, wrap in WRAPPER_FROM_TEXT:
        if re.search(pat, low):
            return wrap
    return None


def _format_missing(v) -> bool:
    return v is None or str(v).strip() in {"", "—", "-", "–"}


def merge_one(cigar: dict, raw: dict) -> bool:
    """Apply neptune raw data to a single cigar record. Return True if changed."""
    changed = False

    desc = raw.get("description") or ""
    wrap_text = raw.get("wrapper") or ""
    binder_text = raw.get("binder") or ""
    filler_text = raw.get("filler") or ""
    origin_text = raw.get("origin") or ""
    strength_raw = raw.get("strength")

    # ── wrapper ───────────────────────────────────────────────────────────────
    if _format_missing(cigar.get("wrapper")):
        # Try structured field first, then wrapper text from description
        new_wrapper = None
        if wrap_text and wrap_text not in ("—", "-"):
            new_wrapper = _wrapper_from_text(wrap_text) or wrap_text.strip()
        if not new_wrapper and desc:
            new_wrapper = _wrapper_from_text(desc)
        if new_wrapper:
            cigar["wrapper"] = new_wrapper
            changed = True

    # ── wrapperOrigin from wrapper spec row ───────────────────────────────────
    if not cigar.get("wrapperOrigin") and wrap_text:
        hr_country = _to_hr_country(wrap_text)
        if hr_country:
            cigar["wrapperOrigin"] = hr_country
            changed = True

    # ── binderOrigin ──────────────────────────────────────────────────────────
    if not cigar.get("binderOrigin") and binder_text:
        hr_binder = _to_hr_country(binder_text)
        if hr_binder:
            cigar["binderOrigin"] = hr_binder
            changed = True

    # ── fillerOrigin ──────────────────────────────────────────────────────────
    if not cigar.get("fillerOrigin") and filler_text:
        hr_filler = _to_hr_country(filler_text)
        if hr_filler:
            cigar["fillerOrigin"] = hr_filler
            changed = True

    # ── country (origin) ──────────────────────────────────────────────────────
    if not cigar.get("country") and origin_text:
        hr_origin = _to_hr_country(origin_text)
        if hr_origin:
            cigar["country"] = hr_origin
            changed = True

    # ── strength ──────────────────────────────────────────────────────────────
    if isinstance(strength_raw, int) and 1 <= strength_raw <= 5:
        if cigar.get("profileEstimated") or cigar.get("strength") is None:
            cigar["strength"] = strength_raw
            cigar["strengthFromShop"] = True
            changed = True

    # ── flavorTags from description ──────────────────────────────────────────
    if not cigar.get("flavorTags") and desc:
        tags = _tags_from_text(desc)
        if len(tags) >= 2:
            cigar["flavorTags"] = tags
            cigar["profileEstimated"] = False
            changed = True

    return changed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    raw_list = load_json(RAW, None)
    if raw_list is None:
        print(f"neptune_raw.json not found: {RAW}. Run scrape-neptune-profiles.py first.", file=sys.stderr)
        sys.exit(1)

    raw_by_id: dict[str, dict] = {
        item["id"]: item
        for item in raw_list
        if isinstance(item, dict) and not item.get("error")
    }
    print(f"Loaded {len(raw_by_id)} scraped records (excl. errors)")

    cigars_text = CIGARS_PATH.read_text(encoding="utf-8")
    cigars = json.loads(cigars_text)

    updated = 0
    for c in cigars:
        raw = raw_by_id.get(c["id"])
        if raw is None:
            continue
        if merge_one(c, raw):
            updated += 1

    after = json.dumps(cigars, ensure_ascii=False, indent=2) + "\n"
    changed = after != cigars_text

    print(f"Records touched: {updated}, file changed: {changed}")

    if args.dry_run:
        print("(dry-run — not writing)")
        return 0

    if changed:
        CIGARS_PATH.write_text(after, encoding="utf-8")
        print(f"Wrote {CIGARS_PATH.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
