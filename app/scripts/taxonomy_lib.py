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
