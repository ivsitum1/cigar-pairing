# -*- coding: utf-8 -*-
"""Ingest pairing-relevant Drinx SKUs missing from drink JSON.

Uses match-drinx-drinks scoring to skip bottles already covered, then adds
0.7 L spirits in €28–€220 with heuristic profiles (same pattern as AlleZ whisky
heuristic rows).

Pokretanje:
  python scripts/ingest-drinx-gaps.py           # dry-run
  python scripts/ingest-drinx-gaps.py --apply  # write JSON + registry
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
OUT_DIR = SCRIPTS / "output"
RAW = OUT_DIR / "drinx_catalog_raw.json"
REPORT_OUT = OUT_DIR / "drinx_ingest_report.json"
REGISTRY = ROOT / "src" / "data" / "drinkIdRegistry.json"

sys.path.insert(0, str(SCRIPTS))
from gin_shared import (  # noqa: E402
    detect_style_region as gin_detect,
    estimate_quality as gin_quality,
    serving_for_style as gin_serving,
)
from script_io import configure_stdio  # noqa: E402
from whisky_shared import (  # noqa: E402
    detect_style_region as whisky_detect,
    estimate_quality as whisky_quality,
    extract_abv,
    extract_age,
    slugify,
)

# Load match helpers from hyphenated module name
_spec = importlib.util.spec_from_file_location(
    "match_drinx", SCRIPTS / "match-drinx-drinks.py"
)
assert _spec and _spec.loader
match_drinx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(match_drinx)

FILE_FOR_CAT = {
    "rum": ROOT / "src" / "data" / "rums.json",
    "whisky": ROOT / "src" / "data" / "whiskies.json",
    "gin": ROOT / "src" / "data" / "gins.json",
    "tequila": ROOT / "src" / "data" / "tequilas.json",
    "cognac": ROOT / "src" / "data" / "brandies.json",
    "armagnac": ROOT / "src" / "data" / "brandies.json",
}

PREFIX = {
    "rum": "rum",
    "whisky": "wh",
    "gin": "gin",
    "tequila": "tq",
    "cognac": "br",
    "armagnac": "br",
}

SKIP_NAME = re.compile(
    r"(?i)(\badvent\b|\bmini\b|\bminiatur|\bcalendar\b|\bčaš|\bcas[ae]\b|"
    r"\bglass\b|\b2\s*ča|\bsa\s*2\b|\b3\s*l\b|\b1[,.]5\s*l\b|"
    r"\b4[,.]5\s*l\b|\b5\s*l\b|\bjeroboam\b|\bmagnum\b|"
    r"\blik\w*\b.*\brum\b|\brum\b.*\blik|\bcream\b|\brtd\b)"
)

PREFIX_STRIP = re.compile(
    r"(?i)^(rum|rhum|ron|gin|tekila|tequila|mezcal|konjak|cognac|armagnac|"
    r"škotski\s+viski|skotski\s+viski|irski\s+viski|američki\s+viski|"
    r"americki\s+viski|japanski\s+viski|japanski\s+whisky|kanadski\s+viski|"
    r"viski|whisky|whiskey)\s+"
)
TAIL_STRIP = re.compile(
    r"(?i)\s*(\+\s*gb|\+\s*wb|gb|wb)?\s*0[,.]7\s*l\s*$|\s*70\s*cl\s*$"
)


LEADING_AGE = re.compile(
    r"^(?P<age>\d{1,2}\s*(?:yo|years?(?:\s+old)?|anos)|\d{4})\s+(?P<rest>.+)$",
    re.I,
)


def clean_name(raw: str) -> str:
    s = PREFIX_STRIP.sub("", raw.strip())
    s = TAIL_STRIP.sub("", s)
    s = re.sub(r"\s*\+\s*GB\s*$", "", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip(" -+")
    s = s.replace("Italijanski", "Talijanski").replace("italijanski", "talijanski")
    # Brand first — drinkNames tests reject age/year-leading labels.
    m = LEADING_AGE.match(s)
    if m:
        s = f"{m.group('rest').strip()} {re.sub(r'\s+', ' ', m.group('age')).strip()}"
    return s


def pairing_ok(item: dict) -> bool:
    if SKIP_NAME.search(item["name"]):
        return False
    n = item["name"].lower()
    if "0,7 l" not in n and "0.7 l" not in n and "70 cl" not in n:
        return False
    p = item.get("price_eur")
    if p is None or p < 28 or p > 220:
        return False
    return True


def rum_profile(name: str) -> dict:
    low = name.lower()
    if any(x in low for x in ("agricole", "rhum", "martinique", "guadeloupe", "haiti", "clairin")):
        return {
            "style": "agricole",
            "region": "Agricole",
            "body": 2,
            "sweetness": 1,
            "flavorTags": ["travnato", "citrus", "vegetalno"],
            "additiveStatus": "clean",
        }
    if any(x in low for x in ("hampden", "worthy park", "appleton", "jamaica", "smith & cross")):
        return {
            "style": "jamaica",
            "region": "Jamajka",
            "body": 3,
            "sweetness": 1,
            "flavorTags": ["ester-funk", "tropsko-voce", "hrast"],
            "additiveStatus": "clean",
        }
    if any(x in low for x in ("el dorado", "demerara", "diamond", "port mourant", "guyana")):
        return {
            "style": "demerara",
            "region": "Demerara (Gvajana)",
            "body": 4,
            "sweetness": 3,
            "flavorTags": ["melasa", "karamela", "hrast"],
            "additiveStatus": "unknown",
        }
    if "spiced" in low:
        return {
            "style": "spiced",
            "region": "Spiced / aromatizirano",
            "body": 2,
            "sweetness": 4,
            "flavorTags": ["vanilija", "zacini", "karamela"],
            "additiveStatus": "flavored",
        }
    if any(
        x in low
        for x in (
            "dictador",
            "zacapa",
            "flor de caña",
            "flor de cana",
            "nicaragua",
            "guatemala",
            "diplomatico",
            "matusalem",
            "brugal",
            "barcelo",
        )
    ):
        return {
            "style": "solera",
            "region": "Latinska Amerika",
            "body": 3,
            "sweetness": 3,
            "flavorTags": ["karamela", "vanilija", "suho-voce"],
            "additiveStatus": "unknown",
        }
    return {
        "style": "blend",
        "region": "Blend (vise regija)",
        "body": 3,
        "sweetness": 2,
        "flavorTags": ["hrast", "vanilija", "suho-voce"],
        "additiveStatus": "unknown",
    }


def tequila_profile(name: str) -> dict:
    low = name.lower()
    if "extra" in low and ("anejo" in low or "añejo" in low):
        style, body, sweet = "extra-anejo", 5, 3
        tags = ["hrast", "kakao", "vanilija"]
    elif "anejo" in low or "añejo" in low:
        style, body, sweet = "anejo", 4, 3
        tags = ["hrast", "vanilija", "agava"]
    elif "reposado" in low:
        style, body, sweet = "reposado", 3, 2
        tags = ["agava", "vanilija", "citrus"]
    else:
        style, body, sweet = "blanco", 2, 1
        tags = ["agava", "citrus", "papar"]
    return {
        "style": style,
        "region": "Jalisco, Meksiko",
        "country": "Meksiko",
        "body": body,
        "sweetness": sweet,
        "flavorTags": tags,
    }


def brandy_profile(name: str, cat: str) -> dict:
    low = name.lower()
    if cat == "armagnac" or "armagnac" in low:
        return {
            "style": "armagnac",
            "region": "Armagnac, Francuska",
            "country": "Francuska",
            "body": 4,
            "sweetness": 2,
            "flavorTags": ["suho-voce", "hrast", "zacini"],
            "additiveStatus": "clean",
        }
    if "xo" in low or "extra" in low:
        st = "cognac-xo"
        body, sweet = 4, 3
    elif "vsop" in low:
        st = "cognac-vsop"
        body, sweet = 3, 2
    else:
        st = "cognac-vs"
        body, sweet = 2, 2
    return {
        "style": st,
        "region": "Cognac, Francuska",
        "country": "Francuska",
        "body": body,
        "sweetness": sweet,
        "flavorTags": ["suho-voce", "vanilija", "hrast"],
        "additiveStatus": "clean",
    }


def quality_from_price(price: float, age: int | None = None) -> float:
    score = 5.5
    if price >= 150:
        score += 2.0
    elif price >= 90:
        score += 1.5
    elif price >= 55:
        score += 1.0
    elif price >= 40:
        score += 0.5
    if age:
        if age >= 18:
            score += 1.0
        elif age >= 12:
            score += 0.5
    return round(min(9.4, score), 1)


def serving_spirits(best: str = "Čisto / kap vode") -> dict:
    return {
        "neat": 3,
        "water": 2,
        "rocks": 1,
        "highball": 1,
        "cola": 0,
        "best": best,
    }


def build_entry(item: dict, used_ids: set[str]) -> dict | None:
    cat = item["category"]
    display = clean_name(item["name"])
    if len(display) < 3:
        return None
    price = float(item["price_eur"])
    abv = extract_abv(item["name"])
    age = extract_age(item["name"])

    base_id = f"{PREFIX[cat]}-{slugify(display)}"
    # keep ids readable
    if len(base_id) > 90:
        base_id = base_id[:90].rstrip("-")
    drink_id = base_id
    n = 2
    while drink_id in used_ids:
        drink_id = f"{base_id}-{n}"
        n += 1
    used_ids.add(drink_id)

    notes = {
        "hr": (
            f"Orijentir iz Drinx kataloga — {display}. "
            "Profil je za sparivanje, ne lab mjerenje."
        ),
        "en": (
            f"Drinx catalogue orientation — {display}. "
            "Pairing profile, not a lab reading."
        ),
    }

    def cigar_hint(kind: str, style: str) -> dict:
        return {
            "hr": (
                f"Uz {display}: uskladi cigaru sa stilom {style} ({kind}); "
                "biraj srednje tijelo osim kad stil traži jači ili blažiji pokrov."
            ),
            "en": (
                f"With {display}: match the cigar to {style} ({kind}); "
                "prefer medium body unless the style wants a stronger or milder wrapper."
            ),
        }

    if cat == "whisky":
        style, region, body, sweet, tags = whisky_detect(item["name"])
        tag_map = {
            "iodin": "dim",
            "medicinski": "dim",
            "slane": "mineralno",
            "sol": "mineralno",
            "maple": "karamela",
        }
        tags = [tag_map.get(t, t) for t in tags]
        tags = list(dict.fromkeys(tags)) or ["hrast"]
        q = whisky_quality(item["name"], price, style, "single-malt", abv)
        # Heuristic Scotch labels → keys that scotchRegionOf understands
        if region in (
            "Peated, Škotska",
            "Sherry cask, Škotska",
            "Blended, Škotska",
            "Škotska (blended malt)",
        ):
            if style == "islay-peated" or region.startswith("Peated"):
                region = "Islay, Škotska"
            elif style == "speyside-sherry" or "Sherry" in region:
                region = "Speyside, Škotska"
            elif style.startswith("speyside"):
                region = "Speyside, Škotska"
            elif style == "highland":
                region = "Highland, Škotska"
            elif style == "campbeltown":
                region = "Campbeltown, Škotska"
            elif style == "lowland":
                region = "Lowland, Škotska"
            elif style == "island":
                region = "Orkney, Škotska"
            else:
                region = "Škotska (blend)"
        country = "World"
        if "Irska" in region or style.startswith("irish"):
            country = "Irska"
        elif "SAD" in region or style in ("bourbon", "rye", "tennessee"):
            country = "SAD"
        elif "Japan" in region or style == "japanese":
            country = "Japan"
        elif style == "canadian":
            country = "Kanada"
        elif (
            "Škotska" in region
            or style.startswith("speyside")
            or style
            in (
                "highland",
                "islay-peated",
                "island",
                "campbeltown",
                "lowland",
                "blended-scotch",
            )
        ):
            country = "Škotska"
        entry = {
            "id": drink_id,
            "category": "whisky",
            "name": display,
            "style": style,
            "region": region,
            "country": country,
            "body": body,
            "sweetness": sweet,
            "flavorTags": tags or ["hrast"],
            "additiveStatus": "clean",
            "additiveDetail": {
                "hr": "Heuristika — whisky bez doziranog šećera (E150a moguć)",
                "en": "Heuristic — whisky without dosed sugar (E150a possible)",
            },
            "additiveSource": "Drinx ingest heuristika",
            "qualityScore": q,
            "priceEUR": {"min": price, "max": price},
            "shopHR": "drinx.hr",
            "status": None,
            "pairable": True,
            "serving": serving_spirits("Čisto / kap vode"),
            "cigarHint": cigar_hint("whisky", style),
            "priceUrl": item["url"],
            "notes": notes,
        }
        if abv:
            entry["abv"] = abv
        return entry

    if cat == "gin":
        style, region, body, sweet, botanical, tags = gin_detect(item["name"])
        q = gin_quality(item["name"], price, style, botanical, abv)
        entry = {
            "id": drink_id,
            "name": display,
            "style": style,
            "region": region,
            "botanicalProfile": botanical,
            "body": body,
            "sweetness": sweet,
            "flavorTags": tags or ["citrus", "travnato"],
            "qualityScore": q,
            "priceEUR": {"min": price, "max": price},
            "shopHR": "drinx.hr",
            "priceUrl": item["url"],
            # integrity: engine scores honestly — do not gate with pairable=false
            "pairable": True,
            "serving": gin_serving(style, botanical),
            "cigarHint": cigar_hint("gin", style),
            "notes": notes,
            "category": "gin",
        }
        if abv:
            entry["abv"] = abv
        return entry

    if cat == "rum":
        prof = rum_profile(item["name"])
        add_status = prof.pop("additiveStatus")
        style = prof.get("style", "blend")
        entry = {
            "id": drink_id,
            "category": "rum",
            "name": display,
            **prof,
            "additiveStatus": add_status,
            "additiveDetail": {
                "hr": "Heuristika — nije lab mjerenje",
                "en": "Heuristic — not a lab measurement",
            },
            "additiveSource": "Drinx ingest heuristika",
            "qualityScore": quality_from_price(price, age),
            "priceEUR": {"min": price, "max": price},
            "shopHR": "drinx.hr",
            "status": None,
            "pairable": True,
            "serving": serving_spirits(
                "Koktel / highball" if add_status == "flavored" else "Čisto / kap vode"
            ),
            "cigarHint": cigar_hint("rum", style),
            "priceUrl": item["url"],
            "notes": notes,
        }
        if abv:
            entry["abv"] = abv
        return entry

    if cat == "tequila":
        prof = tequila_profile(item["name"])
        style = prof.get("style", "blanco")
        entry = {
            "id": drink_id,
            "category": "tequila",
            "name": display,
            **prof,
            "qualityScore": quality_from_price(price, age),
            "priceEUR": {"min": price, "max": price},
            "priceApprox": False,
            "shopHR": "drinx.hr",
            "priceUrl": item["url"],
            "pairable": True,
            "serving": {"neat": 3, "rocks": 2, "best": "Čisto (snifter)"},
            "cigarHint": cigar_hint("tequila", style),
            "notes": notes,
        }
        if abv:
            entry["abv"] = abv
        return entry

    # cognac / armagnac → brandies.json, category brandy
    prof = brandy_profile(item["name"], cat)
    add_status = prof.pop("additiveStatus")
    style = prof.get("style", "cognac-vs")
    entry = {
        "id": drink_id,
        "category": "brandy",
        "name": display,
        **prof,
        "additiveStatus": add_status,
        "additiveDetail": {
            "hr": "Heuristika — nije lab mjerenje",
            "en": "Heuristic — not a lab measurement",
        },
        "additiveSource": "Drinx ingest heuristika",
        "qualityScore": quality_from_price(price, age),
        "priceEUR": {"min": price, "max": price},
        "priceApprox": False,
        "shopHR": "drinx.hr",
        "status": None,
        "pairable": True,
        "serving": {"neat": 3, "water": 2, "rocks": 1, "highball": 0, "cola": 0, "best": "Čisto (snifter)"},
        "cigarHint": cigar_hint("brandy", style),
        "priceUrl": item["url"],
        "notes": notes,
    }
    if abv:
        entry["abv"] = abv
    return entry


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not RAW.exists():
        print(f"Missing {RAW}")
        return 1

    catalog = json.loads(RAW.read_text(encoding="utf-8"))
    drinks = match_drinx.load_drinks()
    existing_ids = {d["id"] for _, d in drinks}

    # Collect best unmatched candidates (one SKU per cleaned name)
    by_key: dict[str, dict] = {}
    skipped_match = 0
    for item in catalog:
        if not pairing_ok(item):
            continue
        scored = match_drinx.best_matches(item, drinks)
        if scored and scored[0][0] >= 0.5:
            # already have a solid catalogue match
            if len(scored) == 1 or scored[0][0] - scored[1][0] >= 0.05:
                skipped_match += 1
                continue
        key = f"{item['category']}:{slugify(clean_name(item['name']))}"
        prev = by_key.get(key)
        if prev is None or (item["price_eur"] or 0) < (prev["price_eur"] or 9999):
            by_key[key] = item

    candidates = sorted(by_key.values(), key=lambda x: (x["category"], x["name"]))
    print(f"candidates after match-filter: {len(candidates)} (skipped existing match {skipped_match})")

    used = set(existing_ids)
    new_by_file: dict[Path, list[dict]] = {p: [] for p in set(FILE_FOR_CAT.values())}
    built: list[dict] = []
    for item in candidates:
        entry = build_entry(item, used)
        if not entry:
            continue
        path = FILE_FOR_CAT[item["category"]]
        new_by_file[path].append(entry)
        built.append({"id": entry["id"], "name": entry["name"], "category": item["category"], "price": item["price_eur"]})

    report = {
        "added": len(built),
        "by_category": {
            c: sum(1 for b in built if b["category"] == c)
            for c in sorted({b["category"] for b in built})
        },
        "rows": built,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Would add {len(built)}: {report['by_category']}")
    print(f"Wrote {REPORT_OUT}")

    if not args.apply:
        print("Dry-run; re-run with --apply to write")
        return 0

    for path, rows in new_by_file.items():
        if not rows:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        have = {d["id"] for d in data}
        fresh = [r for r in rows if r["id"] not in have]
        if not fresh:
            print(f"Skip {path.name} (already present)")
            continue
        data.extend(fresh)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"Appended {len(fresh)} -> {path.name}")

    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    ids = list(reg.get("ids") or [])
    id_set = set(ids)
    added_reg = 0
    for b in built:
        if b["id"] not in id_set:
            ids.append(b["id"])
            id_set.add(b["id"])
            added_reg += 1
    ids.sort()
    reg["ids"] = ids
    REGISTRY.write_text(json.dumps(reg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Registry +{added_reg} ids")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
