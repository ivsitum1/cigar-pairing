# -*- coding: utf-8 -*-
"""Ground drink notes in YouTube caption corpus (original copy; not transcript paste).

Uses corpus_knowledge_by_topic.json for fast title/domain lookup, then loads full
caption text from output/youtube/{channelId}/videos/{videoId}.json when a dedicated
review match exists. Falls back to caller heuristics when material is thin.

Offline only — corpus bundle is gitignored.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import importlib.util
import sys

from youtube_common import OUTPUT_ROOT, load_video
from youtube_match_lib import confidence_for_key, drink_match_keys, normalize_tokens, snippet_around
from youtube_match_cigar_lib import cigar_match_keys

HERE = Path(__file__).resolve().parent
CORPUS_BUNDLE = OUTPUT_ROOT / "corpus_knowledge_by_topic.json"


def _merge_lib():
    name = "merge_drink_profile_enrichment"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, HERE / "merge-drink-profile-enrichment.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

CATEGORY_DOMAIN: dict[str, str] = {
    "rum": "rum",
    "whisky": "whisky",
    "gin": "gin",
    "tequila": "tequila",
    "brandy": "brandy",
    "digestif": "spirits",
}

REJECT_TITLE = re.compile(
    r"\b(sampler|sample pack|gift set|gift pack|variety pack|unboxing|"
    r"top\s*\d+|ranked|brands?\s+to\s+(avoid|never)|levels?\s+of\s+rum|"
    r"vs\.?|versus|comparison|trio of|flight of|blind tasting)\b",
    re.I,
)

REVIEW_TITLE = re.compile(r"\b(review|tasting|taste test|first impression|notes on)\b", re.I)

TAG_HR: dict[str, str] = {
    "dim": "dim",
    "iodin": "jod",
    "medicinski": "medicinska nota",
    "hrast": "hrast",
    "karamela": "karamela",
    "vanilija": "vanilija",
    "suho-voce": "suho voće",
    "tropsko-voce": "tropsko voće",
    "voce": "voće",
    "tamno-voce": "tamno voće",
    "citrus": "citrus",
    "zacini": "začini",
    "papar": "papar",
    "med": "med",
    "cvjetno": "cvjetne note",
    "kremasto": "kremasta tekstura",
    "kakao": "kakao",
    "orasasti": "orašasti tonovi",
    "ester-funk": "esterski funk",
    "duhan": "duhan",
    "koza": "koža",
    "borovica": "borovica",
    "melasa": "melasa",
    "kava": "kava",
    "agava": "agave",
    "zemljano": "zemlja",
    "sol": "slana nota",
    "overproof": "jači alkohol",
    "slatko": "slatko",
    "biljno": "biljno",
    "vegetalno": "vegetalno",
}

# Every TAG_HR key must have an English gloss — never emit the raw HR slug in notes.en.
TAG_EN: dict[str, str] = {
    "dim": "smoke",
    "iodin": "iodine",
    "medicinski": "medicinal note",
    "hrast": "oak",
    "karamela": "caramel",
    "vanilija": "vanilla",
    "suho-voce": "dried fruit",
    "tropsko-voce": "tropical fruit",
    "voce": "fruit",
    "tamno-voce": "dark fruit",
    "citrus": "citrus",
    "zacini": "spice",
    "papar": "pepper",
    "med": "honey",
    "cvjetno": "floral notes",
    "kremasto": "creamy texture",
    "kakao": "cocoa",
    "orasasti": "nutty tones",
    "ester-funk": "estery funk",
    "duhan": "tobacco",
    "koza": "leather",
    "borovica": "juniper",
    "melasa": "molasses",
    "kava": "coffee",
    "agava": "agave",
    "zemljano": "earth",
    "sol": "salty note",
    "overproof": "higher proof",
    "slatko": "sweet",
    "biljno": "herbal",
    "vegetalno": "vegetal",
}

# Region/country labels stored in HR on drinks; localize for EN templates.
REGION_EN: dict[str, str] = {
    "Škotska": "Scotland",
    "Irska": "Ireland",
    "Meksiko": "Mexico",
    "Jalisco": "Jalisco",
    "SAD": "USA",
    "Japan": "Japan",
    "Indija": "India",
    "Kanada": "Canada",
    "Velika Britanija": "United Kingdom",
    "Engleska": "England",
    "Wales": "Wales",
    "Francuska": "France",
    "Španjolska": "Spain",
    "Italija": "Italy",
    "Njemačka": "Germany",
    "Jamajka": "Jamaica",
    "Barbados": "Barbados",
    "Trinidad": "Trinidad",
    "Kuba": "Cuba",
    "Haiti": "Haiti",
    "Martinique": "Martinique",
    "Guadeloupe": "Guadeloupe",
    "Réunion": "Réunion",
    "Mauricijus": "Mauritius",
    "Filipini": "Philippines",
    "Nikaragva": "Nicaragua",
    "Dominikanska Republika": "Dominican Republic",
    "Dominikana": "Dominican Republic",
    "Kostarika": "Costa Rica",
    "Panama": "Panama",
    "Gvatemala": "Guatemala",
    "Venecuela": "Venezuela",
    "Brazil": "Brazil",
    "Peru": "Peru",
    "Nepoznato": "Unknown",
}

# Same HR-leak regex as app/src/data/integrity.test.ts (cigar notes.en).
EN_NOTES_HR_LEAK = re.compile(
    r"\b("
    r"Nikaragva|Meksiko|Kuba|Škotska|Njemačka|Španjolska|"
    r"kakao|zacini|začini|koza|koža|drvo|papar|hrast|kava|cvjetno|travnato|"
    r"orasasti|orašasti|zemljano|melasa|mlijeko|kremasto|vanilija|"
    r"suho-voce|tamno-voce|biljno|Okusi|pokrov"
    r")\b"
)

MIN_BLOB_CHARS = 120
MIN_TAG_COUNT = 2
MIN_NOTES_CHARS = 80

_CIGAR_SIGNAL = re.compile(
    r"\b(cedar|earth|earthy|pepper|spice|draw|smoke|wrapper|cream|creamy|coffee|"
    r"leather|cocoa|construction|burn|ash|retrohale|nose|palate|flavor)\b",
    re.I,
)


def _curate_stub_mod():
    name = "youtube_curate_stub_enrichments"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, HERE / "youtube-curate-stub-enrichments.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

_AGE_RE = re.compile(r"\b(\d{1,2})\s*(?:yo|year|years|yr|y\.o\.|ans?)\b", re.I)
_VINTAGE_RE = re.compile(r"\b((?:19|20)\d{2})\b")


def title_specific_enough(drink: dict, title: str) -> bool:
    """Reject sibling bottles that share a brand prefix (e.g. Hampden 8 vs Great House)."""
    name = drink.get("name") or ""
    title_l = title.lower()
    name_l = name.lower()

    ages = [m.group(1) for m in _AGE_RE.finditer(name_l)]
    if ages:
        return any(re.search(rf"\b{a}\b", title_l) for a in ages)

    vintages = _VINTAGE_RE.findall(name)
    if vintages:
        return any(v in title_l for v in vintages)

    toks = normalize_tokens(name)
    if len(toks) >= 3:
        for i in range(len(toks) - 1):
            phrase = f"{toks[i]} {toks[i + 1]}"
            if len(toks[i]) >= 3 and phrase in title_l:
                return True
        return False

    return True


def tags_phrase(tags: list[str], n: int = 3) -> str:
    out: list[str] = []
    for t in tags:
        s = TAG_HR.get(t, t.replace("-", " "))
        if s and s not in out:
            out.append(s)
        if len(out) >= n:
            break
    if not out:
        return "čist profil bačve"
    if len(out) == 1:
        return out[0]
    if len(out) == 2:
        return f"{out[0]} i {out[1]}"
    return f"{out[0]}, {out[1]} i {out[2]}"


def tags_phrase_en(tags: list[str], n: int = 3) -> str:
    out: list[str] = []
    for t in tags:
        s = TAG_EN.get(t)
        if s is None:
            # Never emit an unmapped HR slug into notes.en
            continue
        if s and s not in out:
            out.append(s)
        if len(out) >= n:
            break
    if not out:
        return "clean barrel profile"
    if len(out) == 1:
        return out[0]
    if len(out) == 2:
        return f"{out[0]} and {out[1]}"
    return f"{out[0]}, {out[1]} and {out[2]}"


def region_en(region: str) -> str:
    """Localize HR region/country tokens inside a region string for EN notes."""
    if not region:
        return region
    # Prefer longest keys so "Speyside, Škotska" maps both parts.
    out = region
    for hr, en in sorted(REGION_EN.items(), key=lambda kv: -len(kv[0])):
        if hr in out:
            out = out.replace(hr, en)
    return out


def _body_phrases(body: int | None) -> tuple[str, str]:
    b = body if body is not None else 3
    if b <= 2:
        return "laganije tijelo", "lighter body"
    if b >= 4:
        return "punije tijelo", "fuller body"
    return "srednje tijelo", "medium body"


def _abv_bit(drink: dict) -> str:
    abv = drink.get("abv")
    if abv is None:
        return ""
    try:
        return f" ({float(abv):g} %)"
    except (TypeError, ValueError):
        return ""


def _field_len(block: dict[str, str] | None, key: str) -> int:
    if not block:
        return 0
    return len((block.get(key) or "").strip())


def hr_notes_ok(block: dict[str, str] | None, *, min_chars: int = MIN_NOTES_CHARS) -> bool:
    """HR-in-HR checks plus minimum length on both locales (default ≥80)."""
    if not block:
        return False
    hr = (block.get("hr") or "").lower()
    hr_raw = block.get("hr") or ""
    en_raw = block.get("en") or ""
    if len(hr_raw) < min_chars or len(en_raw) < min_chars:
        return False
    if re.search(r"\bcigar\b", hr) or re.search(r"\bwrapper\b", hr):
        return False
    if "heuristika" in hr:
        return False
    return True


def en_notes_ok(block: dict[str, str] | None) -> bool:
    """Reject English notes that leak HR country/tag words (integrity.test.ts regex)."""
    if not block:
        return False
    en = block.get("en") or ""
    if not en.strip():
        return False
    return EN_NOTES_HR_LEAK.search(en) is None


def notes_block_ok(block: dict[str, str] | None, *, min_chars: int = MIN_NOTES_CHARS) -> bool:
    return hr_notes_ok(block, min_chars=min_chars) and en_notes_ok(block)


def _would_shorten(existing: dict[str, str] | None, incoming: dict[str, str] | None) -> bool:
    """True if any locale that was ≥80 would become <80 under the patch."""
    if not incoming:
        return True
    for key in ("hr", "en"):
        old_len = _field_len(existing, key)
        new_len = _field_len(incoming, key)
        if old_len >= MIN_NOTES_CHARS and new_len < MIN_NOTES_CHARS:
            return True
    return False


def _has_pairing_signal(blob: str) -> bool:
    low = blob.lower()
    return any(
        x in low
        for x in (
            "pair with",
            "pairs well",
            "pairing",
            "with a cigar",
            "beside a cigar",
            "smoke and sip",
            "cigar and",
        )
    )


def _hint_from_blob(category: str, drink: dict, blob: str, tags: list[str]) -> dict[str, str]:
    """Pairing hint — paraphrase corpus signal or category default. Both locales ≥80."""
    name = drink.get("name") or drink.get("id") or "boca"
    tag_set = set(tags)
    body = drink.get("body")
    try:
        body_i = int(body) if body is not None else 3
    except (TypeError, ValueError):
        body_i = 3

    if _has_pairing_signal(blob):
        if category == "rum" and (body_i >= 4 or "ester-funk" in tag_set):
            return {
                "hr": (
                    f"Uz {name} recenzenti drže sporiji ritam — maduro ili puni Habano "
                    f"nose esterski rub bez žurbe u dimu."
                ),
                "en": (
                    f"With {name} reviewers keep a slow rhythm — maduro or a full Habano "
                    f"carry the estery edge without rushing the puff."
                ),
            }
        if category == "whisky" and tag_set & {"dim", "iodin", "medicinski"}:
            return {
                "hr": (
                    f"Dim u profilu {name} traži maduro ili puni Habano; gutljaj neka bude "
                    f"manji i mirniji uz stol."
                ),
                "en": (
                    f"Smoke in {name} wants maduro or a full Habano; keep sips smaller "
                    f"and calmer at the table."
                ),
            }
        return {
            "hr": (
                f"Recenzenti uz {name} drže sporiji dim i gutljaj — isti tempo i za stol, "
                f"bez žurbe u srednjoj trećini."
            ),
            "en": (
                f"Reviewers keep a slower puff and sip rhythm with {name} — match that "
                f"at the table without rushing the middle third."
            ),
        }

    if category == "rum":
        if drink.get("additiveStatus") in {"flavored", "spiced"} or int(drink.get("sweetness") or 0) >= 4:
            return {
                "hr": (
                    "Ako ide uz dim, biraj kraći Connecticut ili blagi shade — šećer lako "
                    "preglasi nijanse u srednjoj trećini."
                ),
                "en": (
                    "If you pair it with smoke, pick a shorter Connecticut or mild shade — "
                    "sugar easily covers nuance in the middle third."
                ),
            }
        if body_i >= 4 or "ester-funk" in tag_set:
            return {
                "hr": (
                    "Punije tijelo ili esterski rub — maduro ili puni Habano; dim i gutljaj "
                    "u sporom ritmu do kraja."
                ),
                "en": (
                    "Fuller body or an estery edge — maduro or a full Habano; keep smoke "
                    "and sip slow through the finish."
                ),
            }
        if body_i <= 2:
            return {
                "hr": (
                    "Laganije tijelo — Connecticut ili Cameroon; prva trećina cigare često "
                    "dovoljna uz ovaj rum."
                ),
                "en": (
                    "Lighter body — Connecticut or Cameroon; the cigar’s first third is "
                    "often enough beside this rum."
                ),
            }
        return {
            "hr": (
                "Srednje tijelo — Habano robusto ili zreliji corojo kao most; drži ritam "
                "bez forsiranja snage."
            ),
            "en": (
                "Medium body — Habano robusto or a riper corojo as the bridge; keep pace "
                "without forcing strength."
            ),
        }

    if category == "whisky":
        if tag_set & {"dim", "iodin", "medicinski"}:
            return {
                "hr": (
                    "Dim u čaši traži maduro ili puni Habano — most je pepeo i zemlja, "
                    "gutljaj manji nego inače."
                ),
                "en": (
                    "Smoke in the glass wants maduro or a full Habano — bridge on ash and "
                    "earth, with smaller sips than usual."
                ),
            }
        return {
            "hr": (
                "Srednje ili laganije tijelo — Cameroon ili kraći Habano; prva trećina "
                "cigare često dovoljna uz čašu."
            ),
            "en": (
                "Medium or lighter body — Cameroon or a shorter Habano; the first third "
                "is often enough beside the glass."
            ),
        }

    if category == "gin":
        return {
            "hr": (
                "Borovica i citrus — Connecticut ili panatela; maduro je pretežak partner "
                "i lako preglasi botanike."
            ),
            "en": (
                "Juniper and citrus — Connecticut or panatela; maduro is too heavy a "
                "partner and easily covers the botanicals."
            ),
        }

    if category == "tequila":
        style = str(drink.get("style") or "").lower()
        if "blanco" in style or "silver" in style:
            return {
                "hr": (
                    "Blanco/agave — Connecticut ili kratki Habano; slatki maduro zamuti "
                    "agavu i gubi svježi rub."
                ),
                "en": (
                    "Blanco/agave — Connecticut or a short Habano; sweet maduro muddies "
                    "the agave and dulls the bright edge."
                ),
            }
        return {
            "hr": (
                "Reposado/añejo — Habano srednjeg tijela ili blagi maduro; most je hrast "
                "i miran ritam dimova."
            ),
            "en": (
                "Reposado/añejo — medium Habano or a gentle maduro; bridge on oak with "
                "a calm puff rhythm."
            ),
        }

    return {
        "hr": (
            f"Uz {name} biraj cigaru srednjeg tijela — sporiji dim neka nosi most "
            f"bez forsiranja snage."
        ),
        "en": (
            f"With {name} pick a medium-bodied cigar — a slower puff carries the bridge "
            f"without forcing strength."
        ),
    }


def draft_notes_from_material(
    drink: dict,
    category: str,
    *,
    tags: list[str],
    body: int | None,
    sweet: int | None,
) -> dict[str, str]:
    """Original bottle sentences from extracted tasting signals (not transcript paste)."""
    name = drink.get("name") or drink.get("id")
    region_hr = drink.get("region") or drink.get("style") or ""
    region_hr = str(region_hr)
    region_en_s = region_en(region_hr)
    abv = _abv_bit(drink)
    tag_hr = tags_phrase(tags)
    tag_en = tags_phrase_en(tags)
    body_hr, body_en = _body_phrases(body or drink.get("body"))

    sweet_i = sweet if sweet is not None else int(drink.get("sweetness") or 2)
    additive = str(drink.get("additiveStatus") or "")

    if category == "rum" and (additive in {"flavored", "spiced"} or sweet_i >= 4):
        hr = (
            f"{name}{abv} — {region_hr}: {tag_hr}, izraženija slatkoća. "
            f"Koktel ili desertni gutljaj; neat uz cigaru rijetko je prvi izbor."
        )
        en = (
            f"{name}{abv} — {region_en_s}: {tag_en}, higher sweetness. "
            f"Cocktail or dessert sip; neat with a cigar is rarely the first choice."
        )
    elif category == "whisky" and tags and tags[0] in {"dim", "iodin", "medicinski"}:
        peat_tags = tags_phrase([t for t in tags if t != "dim"] or tags)
        peat_en = tags_phrase_en([t for t in tags if t != "dim"] or tags)
        hr = (
            f"{name}{abv} — {region_hr}. Dimljeni profil: {peat_tags}; {body_hr}. "
            f"Čisto ili s kap vode; uz cigaru sporiji ritam gutljaja."
        )
        en = (
            f"{name}{abv} — {region_en_s}. Peated profile: {peat_en}; {body_en}. "
            f"Neat or with a drop of water; keep sips slow beside a cigar."
        )
    else:
        hr = (
            f"{name}{abv} — {region_hr}: {tag_hr}, {body_hr}. "
            f"Čisto ili s kap vode; drži ritam uz cigaru bez pretjerane slatkoće."
        )
        en = (
            f"{name}{abv} — {region_en_s}: {tag_en}, {body_en}. "
            f"Neat or with a drop of water; keeps pace with a cigar without heavy sweetness."
        )
    return {"hr": hr.strip(), "en": en.strip()}


@lru_cache(maxsize=1)
def load_corpus_entries() -> list[dict[str, Any]]:
    if not CORPUS_BUNDLE.is_file():
        return []
    payload = json.loads(CORPUS_BUNDLE.read_text(encoding="utf-8"))
    return list(payload.get("entries") or [])


def entries_for_category(category: str) -> list[dict[str, Any]]:
    domain = CATEGORY_DOMAIN.get(category, category)
    entries = load_corpus_entries()
    if not entries:
        return []
    out: list[dict[str, Any]] = []
    for e in entries:
        doms = e.get("domains") or []
        primary = e.get("primaryDomain") or ""
        if domain in doms or primary == domain:
            out.append(e)
    return out


def _title_match(drink: dict, entry: dict) -> tuple[str, float] | None:
    title = entry.get("title") or ""
    title_l = title.lower()
    if REJECT_TITLE.search(title):
        return None
    best_key = ""
    best_conf = 0.0
    for key in drink_match_keys(drink):
        if key not in title_l:
            continue
        conf = confidence_for_key(key, in_title=True)
        if conf > best_conf:
            best_conf = conf
            best_key = key
    if not best_key or best_conf < 0.85:
        return None
    if not title_specific_enough(drink, title):
        return None
    return best_key, best_conf


def _load_blob(entry: dict, matched_key: str) -> str:
    rec = load_video(str(entry.get("channelId") or ""), str(entry.get("videoId") or ""))
    text = ""
    if rec and rec.get("captionStatus") == "ok":
        text = str(rec.get("text") or "")
    if not text:
        text = str(entry.get("researchExcerpt") or "")
    if not text:
        return ""
    return snippet_around(text, matched_key, radius=420)


def _material_ok(title: str, blob: str, tags: list[str], *, matched_key: str) -> bool:
    if len(blob.strip()) < MIN_BLOB_CHARS:
        return False
    if len(tags) < MIN_TAG_COUNT:
        return False
    if matched_key.lower() not in blob.lower() and matched_key.lower() not in title.lower():
        return False
    # Require dedicated review OR rich tasting vocabulary
    if REVIEW_TITLE.search(title):
        return True
    return len(tags) >= 3


def find_corpus_match(drink: dict, category: str) -> dict[str, Any] | None:
    """Best corpus-backed match for a catalog drink, or None."""
    candidates: list[tuple[float, str, dict, str]] = []
    for entry in entries_for_category(category):
        hit = _title_match(drink, entry)
        if not hit:
            continue
        key, conf = hit
        title = entry.get("title") or ""
        # Prefer dedicated reviews
        if REVIEW_TITLE.search(title):
            conf += 0.05
        if "review" in (entry.get("themes") or []):
            conf += 0.03
        candidates.append((conf, key, entry, title))

    if not candidates:
        return None

    candidates.sort(key=lambda x: (-x[0], x[3]))
    for conf, key, entry, title in candidates[:12]:
        blob = _load_blob(entry, key)
        m = _merge_lib()
        tags = m.map_tags(blob)
        if not tags:
            tags = m.map_tags(title)
        body = m.map_body(blob) or m.map_body(title)
        sweet = m.map_sweet(blob)
        if not _material_ok(title, blob, tags, matched_key=key):
            continue
        notes = draft_notes_from_material(
            drink, category, tags=tags, body=body, sweet=sweet
        )
        hint = _hint_from_blob(category, drink, blob, tags)
        if not notes_block_ok(notes) or not notes_block_ok(hint):
            continue
        return {
            "notes": notes,
            "cigarHint": hint,
            "sourceVideoIds": [entry["videoId"]] if entry.get("videoId") else [],
            "corpusConfidence": round(conf, 2),
            "corpusTags": tags,
            "corpusBody": body,
            "corpusSweet": sweet,
            "matchedTitle": title,
        }
    return None


def apply_corpus_patch(drink: dict, match: dict[str, Any]) -> None:
    """Merge corpus enrichment into drink dict (in place). Skip unsafe overwrites."""
    notes = match.get("notes")
    hint = match.get("cigarHint")
    if not notes_block_ok(notes) or not notes_block_ok(hint):
        return
    if _would_shorten(drink.get("notes") if isinstance(drink.get("notes"), dict) else None, notes):
        return
    if _would_shorten(
        drink.get("cigarHint") if isinstance(drink.get("cigarHint"), dict) else None,
        hint,
    ):
        return
    drink["notes"] = notes
    drink["cigarHint"] = hint
    drink["youtubeCorpusEnriched"] = True
    if match.get("sourceVideoIds"):
        drink["sourceVideoIds"] = match["sourceVideoIds"]
    tags = match.get("corpusTags") or []
    if tags:
        old = list(drink.get("flavorTags") or [])
        merged = list(old)
        for t in tags:
            if t not in merged:
                merged.append(t)
        drink["flavorTags"] = merged[:6]
    if match.get("corpusBody") is not None:
        old_b = drink.get("body")
        if old_b in (None, 3) or drink.get("profileEstimated"):
            drink["body"] = match["corpusBody"]
    if match.get("corpusSweet") is not None:
        old_s = drink.get("sweetness")
        if old_s in (None, 2, 3):
            drink["sweetness"] = match["corpusSweet"]


def try_corpus_enrich(drink: dict, category: str) -> dict[str, Any] | None:
    """Return enrichment patch or None when corpus has no usable material."""
    if category not in CATEGORY_DOMAIN:
        return None
    return find_corpus_match(drink, category)


def _fold_cigar(s: str) -> str:
    import unicodedata

    nfkd = unicodedata.normalize("NFKD", s or "")
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch)).lower()


def _title_match_cigar(cigar: dict, entry: dict) -> tuple[str, float] | None:
    title = entry.get("title") or ""
    title_l = _fold_cigar(title)
    if REJECT_TITLE.search(title):
        return None
    line = _fold_cigar(cigar.get("line") or "")
    brand = _fold_cigar(cigar.get("brand") or "")
    if line and line not in title_l:
        return None
    if brand and brand not in title_l:
        return None
    best_key = ""
    best_conf = 0.0
    for key in cigar_match_keys(cigar):
        fk = _fold_cigar(key)
        if fk not in title_l:
            continue
        conf = confidence_for_key(key, in_title=True)
        if conf > best_conf:
            best_conf = conf
            best_key = key
    if not best_key or best_conf < 0.85:
        return None
    return best_key, best_conf


def _cigar_material_ok(title: str, blob: str, *, matched_key: str) -> bool:
    if len(blob.strip()) < MIN_BLOB_CHARS:
        return False
    if _fold_cigar(matched_key) not in _fold_cigar(blob) and _fold_cigar(matched_key) not in _fold_cigar(title):
        return False
    signals = len(_CIGAR_SIGNAL.findall(blob))
    if REVIEW_TITLE.search(title):
        return signals >= 1
    return signals >= 2


def find_corpus_match_cigar(cigar: dict) -> dict[str, Any] | None:
    """Best corpus-backed cigar review match, or None."""
    candidates: list[tuple[float, str, dict, str]] = []
    for entry in entries_for_category("cigar"):
        hit = _title_match_cigar(cigar, entry)
        if not hit:
            continue
        key, conf = hit
        title = entry.get("title") or ""
        if REVIEW_TITLE.search(title):
            conf += 0.05
        if "review" in (entry.get("themes") or []):
            conf += 0.03
        candidates.append((conf, key, entry, title))

    if not candidates:
        return None

    candidates.sort(key=lambda x: (-x[0], x[3]))
    cur = _curate_stub_mod()
    brand = str(cigar.get("brand") or "")
    line = str(cigar.get("line") or "")

    for conf, key, entry, title in candidates[:12]:
        blob = _load_blob(entry, key)
        if not _cigar_material_ok(title, blob, matched_key=key):
            continue
        notes = cur.draft_cigar_notes(cigar, brand, line)
        if not notes_block_ok(notes):
            continue
        return {
            "notes": notes,
            "sourceVideoIds": [entry["videoId"]] if entry.get("videoId") else [],
            "corpusConfidence": round(conf, 2),
            "matchedTitle": title,
        }
    return None


def apply_corpus_patch_cigar(cigar: dict, match: dict[str, Any]) -> None:
    notes = match.get("notes")
    if not notes_block_ok(notes):
        return
    if _would_shorten(cigar.get("notes") if isinstance(cigar.get("notes"), dict) else None, notes):
        return
    cigar["notes"] = notes
    cigar["youtubeCorpusEnriched"] = True
    if match.get("sourceVideoIds"):
        cigar["sourceVideoIds"] = match["sourceVideoIds"]
