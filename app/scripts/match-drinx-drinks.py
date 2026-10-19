# -*- coding: utf-8 -*-
"""Match drinx_catalog_raw.json to existing drink JSON and apply buy-link updates.

Rules:
- Prefer Drinx product URL when drink has no priceUrl, or URL is not a product page.
- Do not overwrite a verified AlleZ / Ecuga product URL.
- Update priceEUR from Drinx when applying a new primary link.
- Write report + unmatched pairing-relevant candidates (no auto-ingest of new bottles).

Pokretanje:
  python scripts/match-drinx-drinks.py           # dry-run report
  python scripts/match-drinx-drinks.py --apply  # write JSON updates
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

from script_io import configure_stdio

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = Path(__file__).resolve().parent / "output"
RAW = OUT_DIR / "drinx_catalog_raw.json"
REPORT = OUT_DIR / "drinx_match_report.json"

DRINK_FILES = {
    "rum": ROOT / "src" / "data" / "rums.json",
    "whisky": ROOT / "src" / "data" / "whiskies.json",
    "gin": ROOT / "src" / "data" / "gins.json",
    "tequila": ROOT / "src" / "data" / "tequilas.json",
    "cognac": ROOT / "src" / "data" / "brandies.json",
    "armagnac": ROOT / "src" / "data" / "brandies.json",
}

# Map scrape category → drink.category values in JSON
CAT_TO_JSON = {
    "rum": "rum",
    "whisky": "whisky",
    "gin": "gin",
    "tequila": "tequila",
    "cognac": "brandy",
    "armagnac": "brandy",
}

# Expression-grade words: overlap on these alone must not pair different houses.
GENERIC_BOTTLE = frozenset(
    {
        "xo",
        "original",
        "dark",
        "gold",
        "premium",
        "cask",
        "anejo",
        "silver",
        "blanco",
        "reposado",
        "plata",
        "cristalino",
        "rare",
        "superior",
        "classic",
        "black",
        "white",
        "spiced",
        "dry",
        "oak",
        "oaks",
        "no",
        "num",
        "yo",
    }
)

STOP = {
    "rum",
    "rhum",
    "ron",
    "whisky",
    "whiskey",
    "gin",
    "tequila",
    "mezcal",
    "cognac",
    "armagnac",
    "brandy",
    "liker",
    "liqueur",
    "vol",
    "abv",
    "yo",
    "year",
    "years",
    "old",
    "gb",
    "gift",
    "box",
    "giftbox",
    "poklon",
    "kutija",
    "kutiji",
    "reserve",
    "reserva",
    "edition",
    "limited",
    "the",
    "and",
    "de",
    "du",
    "des",
    "la",
    "le",
    "les",
    "single",
    "malt",
    "scotch",
    "estate",
    "distillery",
    "collection",
}

SKIP_NAME = re.compile(
    r"(?i)(\badvent\b|\bmini\b|\bminiatur|\bcalendar\b|\bčaš|\bcas[ae]\b|"
    r"\bglass\b|\b2\s*ča|\bsa\s*2\b|\bset\b.*\bča|\b3\s*l\b|\b1[,.]5\s*l\b|"
    r"\b4[,.]5\s*l\b|\b5\s*l\b|\bjeroboam\b|\bmagnum\b)"
)

VOL_RE = re.compile(
    r"(?i)\b\d+[.,]?\d*\s*(?:l|cl|ml)\b|\b\d+\s*cl\b|\+\s*gb\b|\bgb\b"
)
AGE_RE = re.compile(r"\b(\d{1,2})\s*(?:yo|y\.?o\.?|god(?:ina|ine)?|ans?|años?)\b", re.I)
NON_ALNUM = re.compile(r"[^a-z0-9]+")


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()


def tokens(name: str) -> set[str]:
    s = fold(name)
    s = VOL_RE.sub(" ", s)
    s = NON_ALNUM.sub(" ", s)
    out = set()
    for t in s.split():
        if t in STOP:
            continue
        if t.isdigit():
            if len(t) <= 2:
                out.add(t)
            continue
        if len(t) < 2:
            continue
        out.add(t)
    return out


def short_numbers(name: str) -> set[str]:
    return set(re.findall(r"\b(\d{1,2})\b", fold(name)))


def plausible_drinx_price(price: float | None, drink: dict) -> bool:
    if price is None:
        return False
    if price < 12:
        return False
    old = drink.get("priceEUR")
    if isinstance(old, dict):
        prev = old.get("min") or old.get("max")
        if isinstance(prev, (int, float)) and prev > 0 and price < prev * 0.25:
            return False
    return True


def age_of(name: str) -> str | None:
    m = AGE_RE.search(fold(name))
    return m.group(1) if m else None


def is_product_url(url: str | None) -> bool:
    if not url:
        return False
    u = url.lower()
    if "drinx.hr" in u:
        if "/shop/category/" in u:
            return False
        # /shop/<path>/<product-slug>
        path = u.split("drinx.hr", 1)[-1].split("?", 1)[0]
        segs = [s for s in path.split("/") if s]
        return len(segs) >= 3 and segs[0] == "shop" and segs[1] != "category"
    if "/svi-proizvodi/" in u or "/proizvod/" in u:
        return True
    if "/katalog/" in u:
        segs = [s for s in u.split("?")[0].split("/") if s]
        # host + katalog + cat + sub + product
        try:
            i = segs.index("katalog")
            return len(segs) - i >= 4
        except ValueError:
            return False
    return False


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    return inter / len(a | b)


def load_drinks() -> list[tuple[str, dict]]:
    """Return list of (file_key, drink) — brandies loaded once."""
    loaded: dict[Path, list[dict]] = {}
    rows: list[tuple[str, dict]] = []
    for cat, path in DRINK_FILES.items():
        if path not in loaded:
            loaded[path] = json.loads(path.read_text(encoding="utf-8"))
        json_cat = CAT_TO_JSON[cat]
        for d in loaded[path]:
            if d.get("category") != json_cat and cat in ("cognac", "armagnac"):
                # brandies.json mixes cognac/armagnac/other under category brandy
                pass
            if cat in ("cognac", "armagnac"):
                name = fold(d.get("name", ""))
                style = fold(str(d.get("style", "")))
                region = fold(str(d.get("region", "")))
                if cat == "cognac" and "armagnac" in name + style + region:
                    continue
                if cat == "armagnac" and "armagnac" not in name + style + region and "cognac" in name + style:
                    continue
            rows.append((cat, d))
    # Deduplicate brandies appearing under both cognac and armagnac passes
    seen: set[str] = set()
    uniq: list[tuple[str, dict]] = []
    for cat, d in rows:
        did = d["id"]
        if did in seen:
            continue
        seen.add(did)
        uniq.append((cat, d))
    return uniq


def best_matches(
    item: dict, drinks: list[tuple[str, dict]]
) -> list[tuple[float, dict, str]]:
    itoks = tokens(item["name"])
    iage = age_of(item["name"])
    cat = item["category"]
    scored: list[tuple[float, dict, str]] = []
    for dcat, d in drinks:
        if dcat != cat and not (
            cat in ("cognac", "armagnac") and dcat in ("cognac", "armagnac")
        ):
            # cognac/armagnac both live in brandies — allow cross within brandy file
            if CAT_TO_JSON.get(cat) != CAT_TO_JSON.get(dcat):
                continue
        dtoks = tokens(d["name"])
        # also use id slug tokens
        id_toks = tokens(d["id"].replace("-", " "))
        anchor = (itoks & id_toks) - GENERIC_BOTTLE
        if not anchor:
            continue
        inums = short_numbers(item["name"])
        dnums = short_numbers(d["name"])
        if inums and dnums and inums.isdisjoint(dnums):
            continue
        score = max(jaccard(itoks, dtoks), jaccard(itoks, dtoks | id_toks) * 0.95)
        dage = age_of(d["name"])
        if iage and dage and iage != dage:
            score *= 0.35
        elif iage and dage and iage == dage:
            score += 0.08
        overlap = (itoks & dtoks) - GENERIC_BOTTLE
        if len(overlap) < 1 and score < 0.62:
            continue
        if score >= 0.42:
            scored.append((score, d, dcat))
    scored.sort(key=lambda x: -x[0])
    return scored


def decide_update(drink: dict, drinx: dict) -> str:
    """Return action: apply_primary | skip_has_product | skip_packaging."""
    if SKIP_NAME.search(drinx["name"]):
        return "skip_packaging"
    url = drink.get("priceUrl")
    if not is_product_url(url):
        return "apply_primary"
    # keep allez/ecuga product URLs
    u = (url or "").lower()
    if "allez.hr" in u or "ecuga.com" in u:
        return "skip_has_product"
    if "drinx.hr" in u:
        return "apply_primary"  # refresh price
    return "skip_has_product"


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not RAW.exists():
        print(f"Missing {RAW}; run scrape-drinx-catalog.py first")
        return 1

    catalog = json.loads(RAW.read_text(encoding="utf-8"))
    drinks = load_drinks()
    by_id = {d["id"]: d for _, d in drinks}

    # Prefer standard 0.7l bottles over odd volumes when multiple Drinx SKUs match
    def volume_penalty(name: str) -> float:
        n = fold(name)
        if re.search(r"\b0[,.]7\s*l\b|\b70\s*cl\b", n):
            return 0.0
        if re.search(r"\b0[,.]05\s*l\b|\b5\s*cl\b|\bmini", n):
            return 0.3
        if re.search(r"\b[2-9]\s*l\b|\b1[,.]5\s*l\b", n):
            return 0.25
        return 0.05

    # Best drinx SKU per drink id
    best_for_drink: dict[str, tuple[float, dict]] = {}
    ambiguous: list[dict] = []
    unmatched_items: list[dict] = []

    for item in catalog:
        if SKIP_NAME.search(item["name"]):
            continue
        scored = best_matches(item, drinks)
        if not scored:
            unmatched_items.append(item)
            continue
        top = scored[0]
        # ambiguity: two drinks within 0.05
        if len(scored) > 1 and scored[0][0] - scored[1][0] < 0.08 and scored[1][0] >= 0.5:
            ambiguous.append(
                {
                    "drinx": item,
                    "candidates": [
                        {"id": s[1]["id"], "name": s[1]["name"], "score": round(s[0], 3)}
                        for s in scored[:4]
                    ],
                }
            )
            continue
        score, drink, _ = top
        if score < 0.5:
            unmatched_items.append(item)
            continue
        adj = score - volume_penalty(item["name"])
        prev = best_for_drink.get(drink["id"])
        if prev is None or adj > prev[0]:
            best_for_drink[drink["id"]] = (adj, item)

    applied: list[dict] = []
    skipped_product: list[dict] = []
    skipped_pack: list[dict] = []

    # Group file writes
    files_to_save: dict[Path, list[dict]] = {}
    for path in {p for p in DRINK_FILES.values()}:
        files_to_save[path] = json.loads(path.read_text(encoding="utf-8"))

    id_to_path: dict[str, Path] = {}
    for path, rows in files_to_save.items():
        for d in rows:
            id_to_path[d["id"]] = path

    for did, (score, item) in sorted(best_for_drink.items(), key=lambda x: -x[1][0]):
        drink = by_id[did]
        action = decide_update(drink, item)
        row = {
            "id": did,
            "name": drink["name"],
            "score": round(score, 3),
            "drinx_name": item["name"],
            "drinx_url": item["url"],
            "drinx_price": item["price_eur"],
            "old_priceUrl": drink.get("priceUrl"),
            "old_shopHR": drink.get("shopHR"),
            "action": action,
        }
        if action == "skip_packaging":
            skipped_pack.append(row)
            continue
        if action == "skip_has_product":
            skipped_product.append(row)
            continue

        # apply_primary
        path = id_to_path[did]
        for d in files_to_save[path]:
            if d["id"] != did:
                continue
            d["priceUrl"] = item["url"]
            d["shopHR"] = "drinx.hr"
            if plausible_drinx_price(item.get("price_eur"), drink):
                d["priceEUR"] = {
                    "min": item["price_eur"],
                    "max": item["price_eur"],
                }
            break
        applied.append(row)

    # Candidates: unmatched Drinx SKUs that look like core 0.7l spirits
    candidates = []
    for item in unmatched_items:
        if SKIP_NAME.search(item["name"]):
            continue
        if not re.search(r"(?i)0[,.]7\s*l|70\s*cl", item["name"]):
            continue
        if item["price_eur"] is None or item["price_eur"] < 25:
            continue
        candidates.append(
            {
                "name": item["name"],
                "price_eur": item["price_eur"],
                "url": item["url"],
                "category": item["category"],
            }
        )
    candidates.sort(key=lambda x: (-(x["price_eur"] or 0), x["name"]))

    report = {
        "catalog_total": len(catalog),
        "matched_drinks": len(best_for_drink),
        "applied": len(applied),
        "skipped_has_product": len(skipped_product),
        "skipped_packaging": len(skipped_pack),
        "ambiguous": len(ambiguous),
        "candidate_new": len(candidates),
        "applied_rows": applied,
        "skipped_has_product_rows": skipped_product[:80],
        "ambiguous_rows": ambiguous[:40],
        "candidate_new_rows": candidates[:80],
        "counts_by_category": {
            c: sum(1 for x in catalog if x["category"] == c) for c in sorted({x["category"] for x in catalog})
        },
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"matched={len(best_for_drink)} apply={len(applied)} "
        f"keep_product={len(skipped_product)} ambiguous={len(ambiguous)} "
        f"candidates={len(candidates)}"
    )
    print(f"Wrote {REPORT}")

    if args.apply and applied:
        for path, rows in files_to_save.items():
            path.write_text(
                json.dumps(rows, ensure_ascii=False, indent=1) + "\n",
                encoding="utf-8",
            )
            print(f"Updated {path.name}")
    elif args.apply:
        print("Nothing to apply")
    else:
        print("Dry-run only; re-run with --apply to write drink JSON")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
