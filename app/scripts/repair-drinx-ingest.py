# -*- coding: utf-8 -*-
"""One-shot repair for Drinx heuristic rows after ingest-drinx-gaps.py.

Fixes country/region/cigarHint/notes length and common name-order issues so
catalog integrity tests pass. Safe to re-run.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from script_io import configure_stdio

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data"

FILES = {
    "rum": DATA / "rums.json",
    "whisky": DATA / "whiskies.json",
    "gin": DATA / "gins.json",
    "tequila": DATA / "tequilas.json",
    "brandy": DATA / "brandies.json",
}

# Age/year leading the name → move to end (keeps brand first for drinkNames tests).
LEADING_AGE = re.compile(
    r"^(?P<age>\d{1,2}\s*(?:yo|years?(?:\s+old)?|anos)|\d{4})\s+(?P<rest>.+)$",
    re.I,
)


def is_drinx_heuristic(d: dict) -> bool:
    notes = d.get("notes") or {}
    hr = notes.get("hr") if isinstance(notes, dict) else ""
    return "Heuristika (Drinx" in (hr or "") or (
        d.get("shopHR") == "drinx.hr" and d.get("cigarHint") is None
    )


def hint_for(cat: str, name: str, style: str) -> dict:
    if cat == "gin":
        hr = (
            f"Uz {name}: srednja cigara s citrusnim ili biljnim pokrovom; "
            f"stil {style} traži čist draw i ne prejaku snagu."
        )
        en = (
            f"With {name}: a medium cigar with citrus or herbal wrapper; "
            f"{style} wants a clean draw and moderate strength."
        )
    elif cat == "tequila":
        hr = (
            f"Uz {name}: agava ide uz blagi do srednji pokrov; stil {style} "
            f"ne voli pretjerano slatke ili jako dimne cigare."
        )
        en = (
            f"With {name}: agave suits a mild-to-medium wrapper; {style} "
            f"dislikes overly sweet or heavily smoked cigars."
        )
    elif cat == "rum":
        hr = (
            f"Uz {name}: biraj cigaru po tijelu ruma ({style}); "
            f"slatke linije vole maduro, suhe esterne vole Connecticut."
        )
        en = (
            f"With {name}: pick the cigar by rum body ({style}); "
            f"sweet lines like maduro, dry esters like Connecticut."
        )
    elif cat == "brandy":
        hr = (
            f"Uz {name}: konjak/armagnac traži sporije dimljenje i srednje tijelo; "
            f"stil {style} ide uz Habano ili blagi maduro."
        )
        en = (
            f"With {name}: brandy wants a slower smoke and medium body; "
            f"{style} suits Habano or a mild maduro."
        )
    else:  # whisky
        hr = (
            f"Uz {name}: uskladi snagu cigare sa stilom {style}; "
            f"treset traži puniji pokrov, voćni speyside blažeg."
        )
        en = (
            f"With {name}: match cigar strength to {style}; "
            f"peat wants a fuller wrapper, fruity Speyside a milder one."
        )
    return {"hr": hr, "en": en}


def ensure_notes(d: dict, name: str) -> None:
    notes = d.get("notes")
    if not isinstance(notes, dict):
        notes = {}
    hr = notes.get("hr") or ""
    en = notes.get("en") or ""
    if len(hr) < 40:
        hr = f"Heuristika (Drinx katalog) — {name}. Profil je orijentir za sparivanje, ne lab mjerenje."
    if len(en) < 40:
        en = f"Heuristic profile (Drinx catalogue) — {name}. Orientation for pairing, not a lab reading."
    d["notes"] = {"hr": hr, "en": en}


def whisky_country(style: str, region: str) -> str:
    r = region or ""
    s = style or ""
    if "Irska" in r or s.startswith("irish"):
        return "Irska"
    if "SAD" in r or s in ("bourbon", "rye", "tennessee"):
        return "SAD"
    if "Japan" in r or s == "japanese":
        return "Japan"
    if s == "canadian" or "Kanada" in r or "Canada" in r:
        return "Kanada"
    if (
        "Škotska" in r
        or "Skotska" in r
        or s.startswith("speyside")
        or s
        in (
            "highland",
            "islay-peated",
            "island",
            "campbeltown",
            "lowland",
            "blended-scotch",
        )
    ):
        return "Škotska"
    if "Tajvan" in r or "Taiwan" in r:
        return "Tajvan"
    if "Indija" in r or "India" in r:
        return "Indija"
    if "Austral" in r:
        return "Australija"
    return "World"


def normalize_whisky_region(style: str, region: str) -> str:
    """Map heuristic Scotch labels to keys scotchRegionOf understands."""
    r = region or ""
    if r in (
        "Peated, Škotska",
        "Sherry cask, Škotska",
        "Blended, Škotska",
        "Škotska (blended malt)",
    ):
        if style == "islay-peated" or r.startswith("Peated"):
            return "Islay, Škotska"
        if style == "speyside-sherry" or "Sherry" in r:
            return "Speyside, Škotska"
        if style.startswith("speyside"):
            return "Speyside, Škotska"
        if style == "highland":
            return "Highland, Škotska"
        if style == "campbeltown":
            return "Campbeltown, Škotska"
        if style == "lowland":
            return "Lowland, Škotska"
        if style == "island":
            return "Orkney, Škotska"
        # blends / blended malt — intentionally regionless
        return "Škotska (blend)"
    return r


def fix_leading_age_name(name: str) -> str:
    m = LEADING_AGE.match(name.strip())
    if not m:
        return name
    rest = m.group("rest").strip()
    age = re.sub(r"\s+", " ", m.group("age")).strip()
    # Prefer brand-first: "Macallan 12 Years Old TRIPLE CASK"
    return f"{rest} {age}"


def repair_file(path: Path, category: str) -> int:
    rows = json.loads(path.read_text(encoding="utf-8"))
    n = 0
    for d in rows:
        if not is_drinx_heuristic(d):
            # Still fix numeric-leading Drinx names that already have cigarHint
            if d.get("shopHR") == "drinx.hr":
                fixed = fix_leading_age_name(d.get("name", ""))
                if fixed != d.get("name"):
                    d["name"] = fixed
                    n += 1
            continue
        name = fix_leading_age_name(d.get("name") or "")
        if name != d.get("name"):
            d["name"] = name
        style = d.get("style") or "world"
        if category == "whisky":
            region = normalize_whisky_region(style, d.get("region") or "")
            d["region"] = region
            d["country"] = whisky_country(style, region)
        ensure_notes(d, name)
        hint = d.get("cigarHint")
        if not isinstance(hint, dict) or len(hint.get("hr") or "") < 40:
            d["cigarHint"] = hint_for(category, name, style)
        n += 1
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return n


def main() -> int:
    configure_stdio()
    total = 0
    for cat, path in FILES.items():
        c = repair_file(path, cat)
        print(f"{path.name}: repaired {c}")
        total += c
    print(f"total touched ~{total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
