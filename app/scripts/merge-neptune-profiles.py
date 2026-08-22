#!/usr/bin/env python3
"""Merge scraped Neptune Cigar profiles into cigars.json.

Input:  scripts/output/neptune_raw.json   (built by scrape-neptune-profiles.py)
Output: app/src/data/cigars.json  (updated in place, idempotent per id)

Merge rules (per cigar record):
  - Only touches records whose id is present in neptune_raw.json
  - Never overwrites existing flavorTags / strength / wrapper with a shop value
    if the record already has them from a curated / non-estimated source
  - strength + body: only set if record has profileEstimated==True or has no
    strength at all; sets strengthFromShop=True
  - wrapper: only set if record currently has "—"
  - flavorTags: from description text via the standard word→tag map
    (same mapping used by merge-flavor-enrichment.py); applied when the
    record has no tags OR profileEstimated==True (heuristic stubs yield to
    shop text). Requires at least 2 tags — otherwise the text is too sparse
  - notes: fill English from Neptune description when current notes are empty
    or attribute-template / market stubs (same idea as cigarNote.ts strip).
    Does not overwrite curated bilingual notes (profileEstimated==False with
    real prose). Market rows keep profileEstimated True.
  - profileEstimated: set to False when tags come from Neptune shop text
    (except catalogSource=="market", which stays estimated)

Usage (run from app/):
  python scripts/merge-neptune-profiles.py
  python scripts/merge-neptune-profiles.py --dry-run
"""
from __future__ import annotations

import argparse
import html as html_mod
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from taxonomy_lib import CIGARS_PATH, OUT_DIR, load_json, write_json  # noqa: E402

RAW = OUT_DIR / "neptune_raw.json"

# Reuse the canonical word→tag map from merge-flavor-enrichment.py
_mfe_spec = importlib.util.spec_from_file_location(
    "merge_flavor_enrichment",
    Path(__file__).resolve().parent / "merge-flavor-enrichment.py",
)
_mfe = importlib.util.module_from_spec(_mfe_spec)
assert _mfe_spec.loader is not None
_mfe_spec.loader.exec_module(_mfe)
tags_from_text = _mfe.tags_from_text


def _load_module(filename: str):
    spec = importlib.util.spec_from_file_location(
        filename.replace("-", "_").removesuffix(".py"),
        Path(__file__).resolve().parent / filename,
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


# Isti citac opisa koji je opis i napisao u neptune_raw.json, i ista heuristika
# pokrova koju katalog inace koristi — nijedan prag se ovdje ne izmislja ispocetka.
_neptune = _load_module("scrape-neptune-profiles.py")
_profile = _load_module("profile-cigars.py")
parse_profile_from_text = _neptune.parse_profile_from_text

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

# Houses whose catalog baseline is mild — Neptune description text often
# mis-labels them "medium". Never *raise* an already-mild strength via shop.
MILD_HOUSE_BRANDS = {
    "Macanudo",
    "Ashton",
    "Flor de Selva",
    "Zino",
    "Cusano",
    "Villiger",
    "Villa Zamorano",
    "Fonseca",
}

DASH = "\u2014"

NOTES_MAX = 480

# Attribute-template notes — mirror app/src/lib/cigarNote.ts GENERATED_* patterns.
_GENERATED_NOTE_RE = [
    re.compile(r"—\s*(?:vrlo lagane|lagane|srednje|jače|pune)\s+snage", re.I),
    re.compile(r"(?:pokrov|wrapper)\s*\([^)]*\);", re.I),
    re.compile(r"^Okusi:", re.I),
    re.compile(
        r"—\s*(?:very mild|mild|medium|medium-full|full)\s+in strength",
        re.I,
    ),
    re.compile(r"^Notes(?::| of)", re.I),
    re.compile(r"^Aromatizirana$", re.I),
    re.compile(r"^Flavoured/infused$", re.I),
    re.compile(r"Heuristika\s*—", re.I),
    re.compile(r"Automatski unos|Auto-added from", re.I),
]


def _clean_shop_prose(text: str) -> str:
    text = html_mod.unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\xa0", " ").replace("&nbsp;", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _truncate_prose(text: str, limit: int = NOTES_MAX) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit]
    if "." in cut:
        return cut.rsplit(".", 1)[0].rstrip() + "."
    if " " in cut:
        return cut.rsplit(" ", 1)[0].rstrip() + "…"
    return cut


def is_generated_or_thin_note(text: str | None) -> bool:
    """True when the note is empty, stub, or attribute-template prose."""
    if not text or not str(text).strip():
        return True
    bare = str(text).strip()
    if len(bare) < 40:
        return True
    return any(rx.search(bare) for rx in _GENERATED_NOTE_RE)


def notes_need_shop_prose(cigar: dict) -> bool:
    notes = cigar.get("notes") or {}
    hr = notes.get("hr") if isinstance(notes, dict) else ""
    en = notes.get("en") if isinstance(notes, dict) else ""
    if cigar.get("profileEstimated") is False:
        # Curated / previously confirmed — only fill if both sides are empty stubs.
        return is_generated_or_thin_note(hr) and is_generated_or_thin_note(en)
    return is_generated_or_thin_note(hr) and is_generated_or_thin_note(en)


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
    if low in COUNTRY_HR:
        return COUNTRY_HR[low]
    matched: list[str] = []
    for key in sorted(COUNTRY_HR, key=len, reverse=True):
        if key in low:
            val = COUNTRY_HR[key]
            if val not in matched:
                matched.append(val)
    if len(matched) == 1:
        return matched[0]
    return None


def _wrapper_from_text(text: str) -> str | None:
    low = (text or "").lower()
    for pat, wrap in WRAPPER_FROM_TEXT:
        if re.search(pat, low):
            return wrap
    return None


def _format_missing(v) -> bool:
    return v is None or str(v).strip() in {"", "—", "-", "–"}


def _house_gap(cigar: dict) -> int:
    """Koliko je tijelo punije od snage za OVAKAV pokrov, po katalogovoj heuristici.

    Maduro nosi gusto tijelo uz umjerenu snagu (+1), Connecticut je i lagan i
    blag (0), corojo vuce na snagu. Taj razmak je jedino sto imamo kad opis
    govori samo o jednoj osi — bolje nego izjednaciti ih, jer izjednacavanje
    tvrdi nesto sto nijedan izvor ne kaze.
    """
    probe = {
        "brand": cigar.get("brand", ""),
        "line": cigar.get("line", ""),
        "vitola": cigar.get("vitola", ""),
        "wrapper": cigar.get("wrapper", ""),
        "country": cigar.get("country", ""),
        "notes": cigar.get("notes", {}),
    }
    try:
        _profile.enrich(probe)
    except Exception:  # noqa: BLE001 — heuristika nikad ne smije srusiti merge
        return 0
    return int(probe.get("body", 3)) - int(probe.get("strength", 3))


def _resolve_axes(cigar: dict, raw: dict) -> tuple[int | None, int | None]:
    """(snaga, tijelo) iz Neptuneova opisa; None znaci "opis o tome ne govori"."""
    prof = raw.get("body") or raw.get("overall") or raw.get("strength")
    if prof is None:
        return None, None
    parsed = parse_profile_from_text(raw.get("description") or "")
    # neptune_raw.json je izvor; opis je uz njega, pa se citaju oba i uzima sto ima
    strength = parsed["strength"] if parsed["strength"] is not None else raw.get("strength")
    body = parsed["body"] if parsed["body"] is not None else raw.get("body")
    overall = parsed["overall"] if parsed["overall"] is not None else raw.get("overall")

    if body is None and strength is None:
        if overall is None:
            return None, None
        body = overall  # ukupan dojam je najblizi tijelu; snaga se izvodi ispod

    gap = _house_gap(cigar)
    if body is None:
        body = _profile.clamp(strength + gap)
    elif strength is None:
        strength = _profile.clamp(body - gap)
    return int(strength), int(body)


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

    # ── strength + body ───────────────────────────────────────────────────────
    # Dvije osi, dva izvora. Opis koji govori samo o jednoj ne smije odrediti
    # obje: druga se izvodi iz karaktera pokrova (razmak koji WRAPPER_BASE drzi
    # izmedu tijela i snage za tu vrstu pokrova), pa maduro ostane punijeg
    # tijela nego snage, a Connecticut obrnuto.
    if cigar.get("profileEstimated") or cigar.get("strength") is None:
        s_new, b_new = _resolve_axes(cigar, raw)
        cur = cigar.get("strength")
        brand = cigar.get("brand") or ""
        # Do not raise an already-mild house profile to "medium+" from
        # noisy shop description text (breaks agricole / mild pairing tests).
        mild_house_guard = (
            brand in MILD_HOUSE_BRANDS
            and isinstance(cur, int)
            and cur <= 2
            and s_new is not None
            and s_new > cur
        )
        if not mild_house_guard:
            if s_new is not None and cigar.get("strength") != s_new:
                cigar["strength"] = s_new
                changed = True
            if b_new is not None and cigar.get("body") != b_new:
                cigar["body"] = b_new
                changed = True
            if (s_new is not None or b_new is not None) and not cigar.get("strengthFromShop"):
                cigar["strengthFromShop"] = True
                changed = True

    # ── flavorTags from description ──────────────────────────────────────────
    # DOPUNA, NE ZAMJENA. Prije je Neptuneov popis brisao postojeci, pa se gubilo
    # ono sto blurb slucajno nije spomenuo: Macanudu Cafeu je nestala oznaka
    # `trava-slatka` (travnata slatkoca Connecticut pokrova) i s njom pao
    # kalibracijski par iz Excela — agricole rum trazi upravo tu oznaku. Ni jedan
    # izvor nije potpun: heuristika zna sto pokrov tipicno nosi, blurb zna sto je
    # pisac te cigare zapisao. Unija je bolja procjena od bilo kojeg samog, a uz
    # to je idempotentna — drugo pokretanje nema sto dodati.
    # Postojece oznake idu prve: rez na 6 tada odnosi visak, a ne temelj.
    allow_tags = (not cigar.get("flavorTags")) or cigar.get("profileEstimated") is True
    if allow_tags and desc:
        tags = tags_from_text(desc)
        if len(tags) >= 2:
            before = list(cigar.get("flavorTags") or [])
            merged = list(dict.fromkeys([*before, *tags]))[:6]
            if before != merged:
                cigar["flavorTags"] = merged
                changed = True
            # Market records are inherently shop-sourced, so their profile
            # remains "estimated" even after Neptune tag enrichment.
            if cigar.get("catalogSource") != "market":
                if cigar.get("profileEstimated") is not False:
                    cigar["profileEstimated"] = False
                    changed = True

    # ── notes from Neptune description (real shop prose) ─────────────────────
    # UI (cigarNote.ts) already hides attribute templates. Fill English from the
    # shop blurb when both languages are empty/stub; HR falls back to EN in UI
    # until a Croatian rewrite exists. Never overwrite curated bilingual notes.
    if desc and notes_need_shop_prose(cigar):
        prose = _truncate_prose(_clean_shop_prose(desc))
        if len(prose) >= 80:
            notes = dict(cigar.get("notes") or {})
            before = (notes.get("hr"), notes.get("en"))
            notes["en"] = prose
            if is_generated_or_thin_note(notes.get("hr")):
                notes["hr"] = ""
            if (notes.get("hr"), notes.get("en")) != before:
                cigar["notes"] = notes
                changed = True
            if cigar.get("catalogSource") != "market":
                if cigar.get("profileEstimated") is not False:
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
