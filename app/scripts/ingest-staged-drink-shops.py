# -*- coding: utf-8 -*-
"""Ingest Tier D staged shop listings into drink JSON + drinkIdRegistry.

Only categories: rum, whisky, brandy, gin, tequila, digestif.
Stubs start pairable=false, then enrich-shop-ingest-stubs may flip pairable
when name heuristics say the bottle is pairing-worthy.

  python scripts/ingest-staged-drink-shops.py --dry-run
  python scripts/ingest-staged-drink-shops.py --apply
  python scripts/ingest-staged-drink-shops.py --apply --limit 20
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
OUT = HERE / "output"
STAGING = OUT / "shop_ingest_staging.json"
REGISTRY = DATA / "drinkIdRegistry.json"

CATEGORY_FILE = {
    "rum": "rums.json",
    "whisky": "whiskies.json",
    "brandy": "brandies.json",
    "gin": "gins.json",
    "tequila": "tequilas.json",
    "digestif": "digestifs.json",
}

CATEGORY_PREFIX = {
    "rum": "rum",
    "whisky": "whisky",
    "brandy": "brandy",
    "gin": "gin",
    "tequila": "tequila",
    "digestif": "digestif",
}

DEFAULT_PROFILE = {
    "rum": {
        "style": "other",
        "region": "Nepoznato",
        "body": 3,
        "sweetness": 2,
        "flavorTags": ["hrast", "voce"],
        "additiveStatus": "unknown",
        "qualityScore": 6.0,
    },
    "whisky": {
        "style": "other",
        "region": "Nepoznato",
        "body": 3,
        "sweetness": 2,
        "flavorTags": ["hrast", "vanilija"],
        "additiveStatus": "unknown",
        "qualityScore": 6.0,
    },
    "brandy": {
        "style": "other",
        "region": "Nepoznato",
        "body": 3,
        "sweetness": 2,
        "flavorTags": ["suho-voce", "hrast"],
        "additiveStatus": "unknown",
        "qualityScore": 6.0,
    },
    "gin": {
        "style": "london-dry",
        "region": "Nepoznato",
        "body": 2,
        "sweetness": 1,
        "flavorTags": ["borovica", "citrus"],
        "additiveStatus": "unknown",
        "qualityScore": 6.0,
    },
    "tequila": {
        "style": "blanco",
        "region": "Nepoznato",
        "body": 2,
        "sweetness": 1,
        "flavorTags": ["agava", "citrus"],
        "additiveStatus": "unknown",
        "qualityScore": 6.0,
    },
    "digestif": {
        "style": "other",
        "region": "Nepoznato",
        "body": 2,
        "sweetness": 3,
        "flavorTags": ["biljno", "zacini"],
        "additiveStatus": "flavored",
        "qualityScore": 5.5,
    },
}

MINI_RE = re.compile(
    r"(?:0\s*[,.]\s*0[1-5]\s*l|\b50\s*ml\b|\b5\s*cl\b|miniature|sample)",
    re.I,
)


def slugify(name: str) -> str:
    s = unicodedata.normalize("NFKD", name or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:80]


def clean_display_name(name: str) -> str:
    s = name or ""
    s = re.sub(r"\s*u poklon kutiji.*$", "", s, flags=re.I)
    s = re.sub(r"\s*\d+[.,]\d+\s*%\s*Vol\.?\s*[\d,.]+\s*l.*$", "", s, flags=re.I)
    s = re.sub(r"\s*0[,.]7\s*l.*$", "", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip()
    return s or (name or "").strip()


def mint_id(category: str, name: str, existing: set[str]) -> str:
    prefix = CATEGORY_PREFIX[category]
    base = f"{prefix}-{slugify(clean_display_name(name))}"
    if not base.endswith("-") and base != prefix:
        candidate = base
    else:
        candidate = f"{prefix}-shop-{abs(hash(name)) % 10_000_000}"
    if candidate not in existing:
        return candidate
    n = 2
    while f"{candidate}-{n}" in existing:
        n += 1
    return f"{candidate}-{n}"


def stub_notes(name: str, category: str) -> dict:
    return {
        "hr": (
            f"Automatski unos iz HR shopa ({category}). "
            f"Profil i pairable treba potvrditi ručno za {name}."
        ),
        "en": (
            f"Auto-ingested from an HR shop ({category}). "
            f"Confirm profile and pairable manually for {name}."
        ),
    }


def build_stub(item: dict, drink_id: str) -> dict:
    cat = item["suggestedCategory"]
    name = clean_display_name(item.get("name") or "")
    price = item.get("price_eur")
    shop = item.get("shopLabel") or item.get("shop")
    profile = dict(DEFAULT_PROFILE[cat])
    stub = {
        "id": drink_id,
        "category": cat,
        "name": name,
        **profile,
        "priceEUR": {"min": price, "max": price} if price is not None else None,
        "priceApprox": False,
        "shopHR": shop,
        "status": None,
        "pairable": False,
        "serving": {"best": "Čisto"},
        "cigarHint": None,
        "priceUrl": item.get("url"),
        "notes": stub_notes(name, cat),
        "profileEstimated": True,
        "shopIngest": True,
    }
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "enrich_shop_ingest_stubs", HERE / "enrich-shop-ingest-stubs.py"
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.enrich_stub_fields(cat, stub)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="Max new stubs (0 = all)")
    args = ap.parse_args()
    if not args.apply:
        args.dry_run = True

    if not STAGING.exists():
        raise SystemExit(f"missing {STAGING}; run scan-drink-shop-gaps.py first")

    staging = load_json(STAGING)
    items = staging.get("items") or []

    # existing ids across catalog + registry
    existing_ids: set[str] = set()
    url_seen: set[str] = set()
    by_file: dict[str, list] = {}
    for cat, fname in CATEGORY_FILE.items():
        path = DATA / fname
        if not path.exists():
            by_file[fname] = []
            continue
        rows = load_json(path)
        by_file[fname] = rows
        for d in rows:
            existing_ids.add(d["id"])
            u = (d.get("priceUrl") or "").rstrip("/").lower()
            if u:
                url_seen.add(u)

    registry = load_json(REGISTRY)
    reg_ids = list(registry.get("ids") or [])
    existing_ids |= set(reg_ids)

    planned: list[tuple[str, dict]] = []
    skipped = 0
    for item in items:
        cat = item.get("suggestedCategory")
        if cat not in CATEGORY_FILE:
            skipped += 1
            continue
        name = item.get("name") or ""
        if MINI_RE.search(name):
            skipped += 1
            continue
        url = (item.get("url") or "").rstrip("/").lower()
        if url and url in url_seen:
            skipped += 1
            continue
        drink_id = mint_id(cat, name, existing_ids)
        existing_ids.add(drink_id)
        if url:
            url_seen.add(url)
        stub = build_stub(item, drink_id)
        planned.append((CATEGORY_FILE[cat], stub))
        if args.limit and len(planned) >= args.limit:
            break

    print(f"planned={len(planned)} skipped={skipped}")
    for fname, stub in planned[:10]:
        print(f"  + {stub['id']} -> {fname} pairable={stub['pairable']}")
    if len(planned) > 10:
        print(f"  ... +{len(planned) - 10} more")

    if args.dry_run:
        print("dry-run: not writing")
        return

    added_ids: list[str] = []
    for fname, stub in planned:
        by_file.setdefault(fname, []).append(stub)
        added_ids.append(stub["id"])

    for fname, rows in by_file.items():
        path = DATA / fname
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {fname} ({len(rows)} drinks)")

    for did in added_ids:
        if did not in reg_ids:
            reg_ids.append(did)
    reg_ids.sort()
    REGISTRY.write_text(
        json.dumps({"_comment": registry.get("_comment"), "ids": reg_ids}, ensure_ascii=False, indent=1)
        + "\n",
        encoding="utf-8",
    )
    print(f"registry +{len(added_ids)} ids")


if __name__ == "__main__":
    main()
