#!/usr/bin/env python3
"""Shared helpers for brand → line → vitola taxonomy scripts."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

APP = Path(__file__).resolve().parent.parent
CIGARS_PATH = APP / "src/data/cigars.json"
BRANDS_PATH = APP / "src/data/brands.json"
ALIASES_PATH = APP / "src/data/cigarIdAliases.json"
TAXONOMY_DIR = APP / "scripts/data/taxonomy"
WORKLIST_DIR = TAXONOMY_DIR / "_worklist"
OUT_DIR = APP / "scripts/output"
LEXICON_PATH = APP / "scripts/data/vitola_lexicon.json"
LINE_MAP_PATH = APP / "scripts/data/line_map.json"
LINE_MERGES_PATH = APP / "scripts/data/line_merge_decisions.json"

DIM_IN_LINE_RE = re.compile(
    r"""(?ix)
    (?:\d+\s*[x×]\s*\d+)
    | \d+\s*(?:mm|")
    | \b\d+\s*1\s*[⁄/]\s*\d+\b
    """
)
# Trailing "… 6 X 50" / "… 6 1/4 x 52" / "… 6 ½ X 52" at end of a line name.
TRAILING_DIM_RE = re.compile(
    r"""(?ix)
    ^(.+?)\s+
    (
      \d+
      (?:\s+\d+\s*[⁄/]\s*\d+ | \s*[¼½¾⅓⅔⅛⅜⅝⅞])?
    )
    \s*[x×]\s*
    (\d+)\s*$
    """
)
# Same idea as TRAILING_DIM_RE, but for shop titles whose separator was lost in
# scraping: `1502 XO Torpedo 6"1/2 * 52` reaches us as `xo 61 2 52`, and
# `… Lancero 7" * 40` as `xo 7 40`. What survives is a run of bare numbers at
# the end of the line, so the run is re-read as (length inches, ring gauge).
BARE_DIM_TAIL_RE = re.compile(r"^(.+?)((?:\s+\d{1,3}){2,6})\s*$")
RING_MIN, RING_MAX = 26, 90
LEN_IN_MIN, LEN_IN_MAX = 3.0, 12.0
FRAC_MAP = {
    "¼": "1/4",
    "½": "1/2",
    "¾": "3/4",
    "⅓": "1/3",
    "⅔": "2/3",
    "⅛": "1/8",
    "⅜": "3/8",
    "⅝": "5/8",
    "⅞": "7/8",
    "⁄": "/",
}


def load_json(path: Path, default=None):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def strip_diacritics(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(ch for ch in s if not unicodedata.combining(ch))


def slug(s: str) -> str:
    s = strip_diacritics(s).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-{2,}", "-", s)


def brand_slug(brand: str) -> str:
    return slug(brand)


def cigar_id(brand: str, line: str) -> str:
    return "cig-" + slug(f"{brand} {line}")


def toks(s: str) -> list[str]:
    return [t for t in re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).split() if t]


ROMAN = {"i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5", "vi": "6", "vii": "7", "viii": "8", "ix": "9", "x": "10"}


def normalize_line_key(s: str) -> str:
    """Case/diacritic/punct/roman fold for duplicate-line detection."""
    parts = []
    for t in toks(strip_diacritics(s)):
        parts.append(ROMAN.get(t, t))
    return " ".join(parts)


# Line display casing. Shop imports arrive lower-cased and stripped of
# punctuation ("blue eyed jack s revenge"), which is how a third of the catalog
# ended up reading like a slug instead of a product name.
LINE_ACRONYMS = {
    "xo": "XO",
    "le": "LE",
    "taa": "TAA",
    "pca": "PCA",
    "ihk": "IHK",
    "obs": "OBS",
    "kb": "KB",
    "xl": "XL",
    "usa": "USA",
    "uk": "UK",
    "bcn": "BCN",
    "anb": "ANB",
    "jrs": "JRS",
    "afr": "AFR",
    "adv": "ADV",
    "gt": "GT",
    "ec": "EC",
    "no": "No.",
    "mr": "Mr.",
}
LINE_ROMANS = {"ii", "iii", "iv", "vi", "vii", "viii", "ix", "xi", "xii", "xiii", "xiv", "xv", "xx"}
LINE_SMALL_WORDS = {
    "a", "an", "and", "at", "by", "for", "from", "in", "of", "on", "or", "the",
    "to", "vs", "with",
}


def title_case_line(line: str) -> str:
    """Title-case a slug-shaped line name without inventing words.

    Only touches lines that carry no capitals at all — a line someone already
    spelled ("Aniversario 10", "ART-56 Claro") is left exactly as it is.
    """
    s = (line or "").strip()
    if not s or not re.search(r"[a-z]", s) or re.search(r"[A-Z]", s):
        return line
    words = s.split()
    out: list[str] = []
    shapes = shape_words()
    letter_hosts = {"serie", "series", "capa", "edicion", "edición", "edicao"}
    for i, w in enumerate(words):
        # lone "s" is a lost possessive: "devil s night" → "Devil's Night"
        # BUT not when it is a letter designation before a shape (Serie S Gordo)
        # or after serie/series/capa — those stay as "S".
        if w == "s" and out and re.search(r"[A-Za-z]$", out[-1]):
            prev = out[-1].lower()
            nxt = words[i + 1].lower() if i + 1 < len(words) else ""
            if prev in letter_hosts or nxt in shapes:
                out.append("S")
            else:
                out[-1] += "'s"
            continue
        # lone "d" before a vowel is an elision: "fume d amour" → "Fume d'Amour"
        if w == "d" and i + 1 < len(words) and words[i + 1][:1] in "aeiou":
            out.append("d'" + words[i + 1][0].upper() + words[i + 1][1:])
            words[i + 1] = ""
            continue
        if not w:
            continue
        if w in LINE_ACRONYMS:
            out.append(LINE_ACRONYMS[w])
        elif w in LINE_ROMANS:
            out.append(w.upper())
        elif re.fullmatch(r"\d+xl", w):  # 3xl → 3XL
            out.append(w.upper())
        elif re.fullmatch(r"[a-z]\d+", w):  # f55 → F55
            out.append(w.upper())
        elif len(w) == 1 and w.isalpha():  # Serie R, B Positive
            out.append(w.upper())
        elif w in LINE_SMALL_WORDS and i > 0:
            out.append(w)
        elif w[0].isalpha():
            out.append(w[0].upper() + w[1:])
        else:
            out.append(w)
    return " ".join(out)


def shape_words() -> set[str]:
    lex = load_json(LEXICON_PATH, {}) or {}
    words: set[str] = set()
    for name, meta in (lex.get("vitolas") or {}).items():
        words.add(name.lower())
        for syn in meta.get("syn") or []:
            words.add(str(syn).lower())
    # bare last tokens commonly used as shape ends
    for w in list(words):
        last = w.split()[-1]
        if len(last) >= 4:
            words.add(last)
    return words


_VITOLA_LEXICON: dict | None = None


def vitola_lexicon() -> dict:
    global _VITOLA_LEXICON
    if _VITOLA_LEXICON is None:
        _VITOLA_LEXICON = (load_json(LEXICON_PATH, {}) or {}).get("vitolas") or {}
    return _VITOLA_LEXICON


def shape_canon_index() -> dict[str, str]:
    """Every lexicon synonym (and bare last token) → its canonical vitola."""
    lex = vitola_lexicon()
    index: dict[str, str] = {}
    for canon, meta in lex.items():
        index[canon.lower()] = canon
        for syn in meta.get("syn") or []:
            index[str(syn).lower()] = canon
    for canon in lex:
        last = canon.lower().split()[-1]
        if len(last) >= 4:
            index.setdefault(last, canon)
    return index


def shape_fits_dims(canon: str | None, ring: int | None, length_mm: int | None) -> bool | None:
    """Do these dimensions fall inside the canonical vitola's box? None = unknown."""
    meta = vitola_lexicon().get(canon or "")
    if not meta or ring is None or length_mm is None:
        return None
    len_lo, len_hi = meta.get("lenMM") or (None, None)
    ring_lo, ring_hi = meta.get("ring") or (None, None)
    if None in (len_lo, len_hi, ring_lo, ring_hi):
        return None
    return len_lo <= length_mm <= len_hi and ring_lo <= ring <= ring_hi


def line_has_dimensions(line: str) -> bool:
    return bool(DIM_IN_LINE_RE.search(line or ""))


def split_trailing_dimensions(line: str) -> tuple[str, str] | None:
    """If line ends with a dimension group, return (line_without_dims, format_hint)."""
    m = TRAILING_DIM_RE.match((line or "").strip())
    if not m:
        return None
    base = m.group(1).strip()
    if not base:
        return None
    length_part = re.sub(r"\s+", " ", m.group(2).strip())
    for a, b in FRAC_MAP.items():
        length_part = length_part.replace(a, b)
    fmt = f"{length_part} x {m.group(3)}"
    return base, fmt


def _dim_from_run(run: list[str]) -> tuple[float, int] | None:
    """Read a bare number run as (length_inches, ring). None when implausible."""
    nums = [int(t) for t in run]
    if len(run) == 2:
        a, b = nums
        if LEN_IN_MIN <= a <= LEN_IN_MAX and RING_MIN <= b <= RING_MAX:
            return float(a), b
        # reversed, as some shops title "… 50 5" (ring first)
        if RING_MIN <= a <= RING_MAX and LEN_IN_MIN <= b <= LEN_IN_MAX:
            return float(b), a
        return None
    if len(run) == 3:
        # `6 1/2` lost its slash and space: "61 2" == 6 + 1/2
        a, den, ring = nums
        whole, num = divmod(a, 10)
        if (
            10 <= a <= 99
            and 2 <= den <= 16
            and 1 <= num < den
            and LEN_IN_MIN <= whole <= LEN_IN_MAX
            and RING_MIN <= ring <= RING_MAX
        ):
            return whole + num / den, ring
        return None
    if len(run) == 4:
        whole, num, den, ring = nums
        if (
            LEN_IN_MIN <= whole <= LEN_IN_MAX
            and 2 <= den <= 16
            and 1 <= num < den
            and RING_MIN <= ring <= RING_MAX
        ):
            return whole + num / den, ring
    return None


def split_bare_dimension_tail(line: str) -> tuple[str, str] | None:
    """Strip a separator-less dimension tail: `xo 61 2 52` → ("xo", "52 x 165mm").

    Only the longest trailing run that reads as a real (length, ring) pair is
    taken, so product names that merely end in a number ("Project 40", "Asylum
    13", "Domaine 50") are left alone.
    """
    m = BARE_DIM_TAIL_RE.match((line or "").strip())
    if not m:
        return None
    head = m.group(1).strip()
    run = m.group(2).split()
    for take in range(min(4, len(run)), 1, -1):
        dims = _dim_from_run(run[-take:])
        if not dims:
            continue
        base = " ".join([head, *run[:-take]]).strip()
        if not base:
            return None
        inches, ring = dims
        return base, f"{ring} x {round(inches * 25.4)}mm"
    return None


def line_ends_with_shape(line: str, shapes: set[str] | None = None) -> str | None:
    shapes = shapes if shapes is not None else shape_words()
    low = (line or "").strip().lower()
    if not low:
        return None
    # longest match at end
    best = None
    for sh in shapes:
        if low == sh or low.endswith(" " + sh):
            if best is None or len(sh) > len(best):
                best = sh
    return best


def is_sampler_line(line: str, vitola: str = "") -> bool:
    hay = f"{line} {vitola}".lower()
    return bool(re.search(r"\b(sampler|gift)\b", hay))


def vitola_repeats_line_tokens(line: str, vitola_name: str) -> bool:
    lt = toks(line)
    vt = toks(vitola_name)
    if not lt or not vt:
        return False
    # leading run of line tokens on vitola
    i = 0
    while i < len(lt) and i < len(vt) and lt[i] == vt[i]:
        i += 1
    return i > 0 and (i < len(vt) or len(vt) == len(lt))


def format_missing(fmt) -> bool:
    if fmt is None:
        return True
    s = str(fmt).strip()
    return (not s) or s in {"—", "-", "–", "n/a", "N/A"}


def parse_format(fmt: str | None) -> tuple[int | None, int | None]:
    """Parse '50 x 127mm' / '6 1/4 x 52' into (ring, lengthMM). Never invent."""
    if format_missing(fmt):
        return None, None
    s = str(fmt)
    for a, b in FRAC_MAP.items():
        s = s.replace(a, b)
    s = s.replace("×", "x").replace("X", "x")
    # ring x lengthMM already in mm
    m = re.search(r"(\d+)\s*x\s*(\d+)\s*mm", s, re.I)
    if m:
        return int(m.group(1)), int(m.group(2))
    # inches: length x ring  OR ring x length — shop strings vary
    m = re.search(r"(\d+)(?:\s+(\d+)/(\d+))?\s*x\s*(\d+)", s, re.I)
    if m:
        whole = int(m.group(1))
        num = m.group(2)
        den = m.group(3)
        other = int(m.group(4))
        inches = whole + (int(num) / int(den) if num and den else 0.0)
        # Heuristic: ring is typically 30–70; length in inches 3–10
        if 30 <= other <= 70 and inches <= 12:
            ring = other
            length_mm = int(round(inches * 25.4))
            return ring, length_mm
        if 30 <= whole <= 70 and other <= 12:
            ring = whole
            length_mm = int(round(other * 25.4))
            return ring, length_mm
    return None, None


def normalize_format_string(fmt: str | None) -> str | None:
    if format_missing(fmt):
        return fmt
    s = str(fmt)
    for a, b in FRAC_MAP.items():
        s = s.replace(a, b)
    s = re.sub(r"\s*[xX×]\s*", " x ", s)
    return s.strip()


def taxonomy_brand_files() -> list[Path]:
    if not TAXONOMY_DIR.exists():
        return []
    return sorted(
        p
        for p in TAXONOMY_DIR.glob("*.json")
        if p.is_file() and not p.name.startswith("_")
    )


def load_taxonomy_files(*, applyable_only: bool = False) -> list[dict]:
    out = []
    for p in taxonomy_brand_files():
        data = load_json(p, {})
        if not isinstance(data, dict):
            continue
        data["_file"] = p.name
        if applyable_only:
            status = data.get("status") or "todo"
            if status not in ("done", "brand-only"):
                continue
        out.append(data)
    return out
