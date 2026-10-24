#!/usr/bin/env python3
"""Intenzitet note (flavor intensity) 1–5 za svaku liniju u cigars.json.

Treća os uz snagu i tijelo — koliko je okus *glasan*, ne koliko ima nikotina
ni koliko je dim gust. U trgovinama to često stoji kao Strength / Body / Flavor;
CigarWorld mjeri `props["aroma strength"]` (1–10).

Prioritet po liniji (prvi pogodak koji da broj pobjeduje):
  1. CigarWorld `aroma strength` → mjerenje (`flavorIntensityFromShop: true`)
  2. CigarWorld aroma-radar (prosjek tri najjače dimenzije) → mjerenje
  3. Neptune opis + bilješke kataloga + okusne oznake → izvod po tekstu
  4. Meki prior: round((snaga + tijelo) / 2) uz nudge iz pokrova/oznaka

Namjerno nije „svi 3”: skor se računa po zapisu. Idempotentno; `--check` ne piše.

Pokreni iz app/:
    python3 scripts/derive-flavor-intensity.py
    python3 scripts/derive-flavor-intensity.py --check
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
CIGARS = DATA / "cigars.json"
CW_RAW = HERE / "output" / "cw_famous_flavor_raw.json"
NEP_RAW = HERE / "output" / "neptune_raw.json"

# Oznake koje dižu / spuštaju glasnoću okusa (ne snagu).
LOUD_TAGS = {
    "papar": 2,
    "dim": 2,
    "zacini": 1,
    "kakao": 1,
    "kava": 1,
    "koza": 1,
    "zemljano": 1,
    "tamno-voce": 1,
    "duhan": 1,
}
QUIET_TAGS = {
    "kremasto": -1,
    "med": -1,
    "trava-slatka": -1,
    "cvjetno": -1,
    "orasasti": 0,
    "cedar": 0,
    "citrus": 0,
}

LOUD_NOTE = re.compile(
    r"\b(bold|intense|intense flavor|powerful flavor|full.?flavou?r|loud|"
    r"pepper|spicy|rich aroma|complex aroma|assertive|"
    r"intenziv|jak okus|pun okus|izražen|oštar|papar)\b",
    re.I,
)
MILD_NOTE = re.compile(
    r"\b(mild flavor|delicate|subtle|gentle|understated|restrained|"
    r"soft palate|light flavor|nuanced|"
    r"blag okus|nježan|suptil|diskretan)\b",
    re.I,
)
FULL_FLAVOR = re.compile(r"full.?flavou?red|full.?bodied flavor|flavor.?forward", re.I)


def clamp(v: int, lo: int = 1, hi: int = 5) -> int:
    return max(lo, min(hi, int(v)))


def cw_ten_to_five(v: float) -> int:
    """CigarWorld 1–10 → naš 1–5 (1–2→1, 3–4→2, 5–6→3, 7–8→4, 9–10→5)."""
    return clamp(int(math.ceil(float(v) / 2)))


def radar_intensity(aroma: dict) -> int | None:
    vals = [float(v) for v in aroma.values() if isinstance(v, (int, float))]
    if len(vals) < 3:
        return None
    top = sorted(vals, reverse=True)[:3]
    return cw_ten_to_five(sum(top) / len(top))


def tag_delta(tags: list) -> float:
    """Glasne vs tihe oznake → mali pomak (−0.7…+0.7), ne zbrajanje po tagu."""
    loud = quiet = 0
    for t in tags:
        key = str(t)
        w = LOUD_TAGS.get(key)
        if w and w > 0:
            loud += 1
        q = QUIET_TAGS.get(key)
        if q is not None and q < 0:
            quiet += 1
    diff = loud - quiet
    if diff >= 3:
        return 0.7
    if diff >= 1:
        return 0.35
    if diff <= -2:
        return -0.7
    if diff <= -1:
        return -0.35
    return 0.0


def text_delta(text: str) -> float:
    n = 0.0
    if LOUD_NOTE.search(text):
        n += 0.45
    if FULL_FLAVOR.search(text):
        n += 0.35
    if MILD_NOTE.search(text):
        n -= 0.55
    return max(-0.8, min(0.8, n))


def wrapper_delta(wrapper: str) -> float:
    w = (wrapper or "").lower()
    if re.search(r"oscuro|double maduro|broadleaf", w):
        return 0.45
    if re.search(r"connecticut|shade|candela|claro", w):
        return -0.45
    if re.search(r"maduro|corojo|san andr", w):
        return 0.25
    return 0.0


def resolve_factory(by_id: dict, aliases: dict):
    def resolve(cid: str):
        seen = set()
        while cid not in by_id:
            if cid in seen or cid not in aliases:
                return None
            seen.add(cid)
            cid = aliases[cid]
        return cid

    return resolve


def load_cw(resolve) -> dict[str, dict]:
    if not CW_RAW.exists():
        return {}
    out: dict[str, dict] = {}
    for row in json.loads(CW_RAW.read_text(encoding="utf-8")):
        block = row.get("cigarworld") or {}
        cid = resolve(row.get("id") or "")
        if not cid:
            continue
        out[cid] = block
    return out


def load_neptune(resolve) -> dict[str, str]:
    if not NEP_RAW.exists():
        return {}
    out: dict[str, str] = {}
    for row in json.loads(NEP_RAW.read_text(encoding="utf-8")):
        cid = resolve(row.get("id") or "")
        if not cid:
            continue
        desc = row.get("description") or ""
        if desc:
            out[cid] = str(desc)
    return out


def score_estimated(cigar: dict, nep_desc: str) -> int:
    """Izvod po zapisu — ne kopira tijelo; blagi prior + tekst/oznake/pokrov.

    Cilj raspodjele: sličan CigarWorldovu `aroma strength` (uglavnom 2–4),
    s rijetkim 1 i 5 — inače treća os opet postane „uvijek puno”.
    """
    s = int(cigar.get("strength") or 3)
    b = int(cigar.get("body") or 3)
    # Centar 3; snaga i tijelo samo blago vuku (intenzitet ≠ nikotin ≠ gustoća).
    # Malo ispod 3.0 jer katalogovo tijelo često sjedi na 4, a CigarWorldov
    # aroma strength vrhuni oko 3 (nakon 1–10 → 1–5).
    score = 2.85 + 0.22 * (b - 3) + 0.12 * (s - 3)
    notes = cigar.get("notes") or {}
    blob = " ".join(
        [
            str(notes.get("en") or ""),
            str(notes.get("hr") or ""),
            str(cigar.get("line") or ""),
            nep_desc,
        ]
    )
    score += text_delta(blob)
    score += tag_delta(list(cigar.get("flavorTags") or []))
    score += wrapper_delta(str(cigar.get("wrapper") or ""))
    return clamp(round(score))


def derive_one(cigar: dict, cw: dict | None, nep_desc: str) -> tuple[int, bool]:
    """Vrati (1–5, from_shop)."""
    if cw:
        props = cw.get("props") or {}
        raw = props.get("aroma strength")
        if isinstance(raw, (int, float)) and raw > 0:
            return cw_ten_to_five(raw), True
        radar = radar_intensity(cw.get("aroma") or {})
        if radar is not None:
            return radar, True
    return score_estimated(cigar, nep_desc), False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in cigars}
    aliases = json.loads((DATA / "cigarIdAliases.json").read_text(encoding="utf-8"))["aliases"]
    resolve = resolve_factory(by_id, aliases)
    cw_by = load_cw(resolve)
    nep_by = load_neptune(resolve)

    changed = 0
    sources = Counter()
    dist = Counter()

    for c in cigars:
        cid = c["id"]
        value, from_shop = derive_one(c, cw_by.get(cid), nep_by.get(cid, ""))
        dist[value] += 1
        sources["shop" if from_shop else "estimated"] += 1

        prev = c.get("flavorIntensity")
        prev_flag = bool(c.get("flavorIntensityFromShop"))
        if prev == value and prev_flag == from_shop:
            continue
        changed += 1
        if not args.check:
            c["flavorIntensity"] = value
            if from_shop:
                c["flavorIntensityFromShop"] = True
            else:
                c.pop("flavorIntensityFromShop", None)

    print(f"linija: {len(cigars)}")
    print(f"izvor:  {dict(sources)}")
    print(f"raspon: {dict(sorted(dist.items()))}")
    print(f"izmjena:{changed}")

    if args.check:
        if changed:
            print("--check: flavorIntensity nije usklađen", file=sys.stderr)
            return 1
        print("--check: OK")
        return 0

    if changed:
        CIGARS.write_text(
            json.dumps(cigars, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
