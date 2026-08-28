# -*- coding: utf-8 -*-
"""Match drink_shop_listings_raw.json onto existing drink JSON (no new IDs).

Updates priceUrl / priceEUR / shopHR when token overlap is strong enough.

  python scripts/match-drink-listings.py
  python scripts/match-drink-listings.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
RAW = HERE / "output" / "drink_shop_listings_raw.json"
REPORT = HERE / "output" / "drink_listing_match_report.json"

FILES = [
    "rums.json",
    "whiskies.json",
    "brandies.json",
    "gins.json",
    "tequilas.json",
    "wines.json",
    "digestifs.json",
]

STOP = {
    "the", "of", "and", "yo", "vol", "old", "years", "year", "single", "malt",
    "scotch", "whisky", "whiskey", "giftbox", "gift", "box", "poklon", "kutiji",
    "u", "in", "gb", "limited", "edition", "batch", "bottle", "l", "cl", "ml",
    "rum", "rhum", "ron", "gin", "cognac", "armagnac", "brandy", "tequila",
    "liker", "liqueur", "sa", "with", "de", "la", "le", "les", "du",
}

# Shop titles add packaging / finish words the catalogue name often omits.
PACK = {
    "gran", "reserva", "familiar", "cask", "finish", "anos", "solera",
    "gift", "box", "giftbox", "grand", "royal", "select", "selection",
    "seleccion", "maestros", "original", "pure", "estate", "port",
    "sherry", "oloroso", "madeira", "chateau", "domaine",
}

# 0.70 L / 0.75 L / 1 L — not an age.
VOLUME_NUMS = {"70", "75", "50", "05", "07"}


def is_weak_price_url(url: str | None) -> bool:
    """Empty, Google, or an ecuga *category* page — not a product SKU."""
    if not url:
        return True
    low = url.lower()
    if "google." in low:
        return True
    try:
        path = url.split("://", 1)[-1].split("/", 1)[-1].split("?")[0]
        segs = [s for s in path.split("/") if s]
    except Exception:
        return True
    if "katalog" in segs:
        return len(segs) < 4
    return False


def object_slice(text: str, drink_id: str) -> tuple[int, int]:
    needle = f'"id": "{drink_id}"'
    at = text.find(needle)
    if at < 0:
        raise SystemExit(f"id not found: {drink_id}")
    start = text.rfind("{", 0, at)
    nxt = text.find("\n {", at)
    if nxt < 0:
        nxt = text.find("\n]", at)
    if start < 0 or nxt < 0:
        raise SystemExit(f"cannot slice object: {drink_id}")
    return start, nxt


def patch_block(block: str, after: dict) -> str:
    """Replace priceUrl / shopHR / priceEUR inside one drink object, keep file indent."""
    url = after["priceUrl"]
    shop = after["shopHR"]
    pe = after["priceEUR"]
    if '"priceUrl": null' in block:
        block = block.replace('"priceUrl": null', f'"priceUrl": {json.dumps(url)}', 1)
    else:
        block, n_url = re.subn(
            r'"priceUrl":\s*"[^"]*"',
            f'"priceUrl": {json.dumps(url)}',
            block,
            count=1,
        )
        if n_url != 1:
            raise SystemExit("priceUrl not replaced")
    if '"shopHR": null' in block:
        block = block.replace('"shopHR": null', f'"shopHR": {json.dumps(shop)}', 1)
    else:
        block, n_shop = re.subn(
            r'"shopHR":\s*"[^"]*"',
            f'"shopHR": {json.dumps(shop)}',
            block,
            count=1,
        )
        if n_shop != 1:
            raise SystemExit("shopHR not replaced")
    m = re.search(
        r'(?ms)^(\s*)"priceEUR":\s*\{\s*"min":\s*[^,]+,\s*"max":\s*[^}]+\s*\}',
        block,
    )
    if not m:
        raise SystemExit("priceEUR not found")
    indent = m.group(1)
    inner = indent + "  "
    pe_block = (
        f'{indent}"priceEUR": {{\n{inner}"min": {pe["min"]},\n'
        f'{inner}"max": {pe["max"]}\n{indent}}}'
    )
    block = block[: m.start()] + pe_block + block[m.end() :]
    block = re.sub(r'"priceApprox":\s*true', '"priceApprox": false', block, count=1)
    return block


def write_updates(updates: list[dict]) -> None:
    by_file: dict[str, list] = {}
    for u in updates:
        by_file.setdefault(u["file"], []).append(u)
    for fname, rows in by_file.items():
        path = DATA / fname
        text = path.read_text(encoding="utf-8")
        for u in sorted(rows, key=lambda x: -len(x["id"])):
            start, end = object_slice(text, u["id"])
            text = text[:start] + patch_block(text[start:end], u["after"]) + text[end:]
        path.write_text(text, encoding="utf-8")
        print(f"  wrote {path.name} ({len(rows)} drinks)")


def shop_url_plausible(shop: str | None, url: str | None) -> bool:
    hosts = {
        "tipsy": "tipsy.hr",
        "cugaklik": "cugaklik.hr",
        "miva": "miva.com.hr",
        "roto": "rotodinamic.hr",
        "humidor": "humidor.hr",
        "allez": "allez.hr",
        "ecuga": "ecuga.com",
    }
    h = hosts.get((shop or "").lower())
    return bool(h and h in (url or "").lower())


def propose_update(
    drink: dict,
    listing: dict,
    *,
    score: float,
) -> dict | None:
    """Propose priceUrl/shopHR/priceEUR changes for an existing drink.

    Returns an ``after`` dict if anything would change, else None.
    Respects allez/ecuga lock, humidor gap-fill-only, and weak-URL rules.
    """
    url = listing.get("url") or ""
    price = listing.get("price_eur")
    shop = (listing.get("shop") or "").lower()
    shop_label = listing.get("shopLabel") or listing.get("shop") or ""
    if not url:
        return None
    if drink.get("lineup"):
        return None

    before_url = drink.get("priceUrl") or ""
    new_url = before_url
    changed = False

    # Strong primary shops: never replace with another host.
    if "allez.hr" in before_url or "ecuga.com" in before_url:
        new_url = before_url
    elif is_weak_price_url(before_url):
        new_url = url
        changed = True
    elif shop in ("tipsy", "cugaklik", "miva", "roto") and score >= 0.9:
        if url != before_url:
            new_url = url
            changed = True
    elif shop == "humidor":
        # fill gaps only — already handled by weak URL branch
        pass
    elif shop == "allez" and is_weak_price_url(before_url):
        new_url = url
        changed = True

    # Price/shopHR only when the drink's priceUrl ends up equal to this listing.
    pe = drink.get("priceEUR")
    new_pe = pe if isinstance(pe, dict) else None
    if price is not None and new_url == url:
        if not isinstance(pe, dict) or pe.get("min") != price or pe.get("max") != price:
            new_pe = {"min": price, "max": price}
            changed = True

    new_shop = drink.get("shopHR")
    if shop_label and new_url == url and drink.get("shopHR") != shop_label:
        new_shop = shop_label
        changed = True

    if not changed:
        return None
    if new_pe is None and price is not None and new_url == url:
        new_pe = {"min": price, "max": price}
    if new_pe is None:
        # patch_block requires priceEUR — keep existing or invent from listing
        if isinstance(pe, dict):
            new_pe = pe
        elif price is not None:
            new_pe = {"min": price, "max": price}
        else:
            return None
    return {
        "priceUrl": new_url or url,
        "shopHR": new_shop or shop_label or drink.get("shopHR"),
        "priceEUR": new_pe,
    }


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"(\d)([a-z])", r"\1 \2", s)
    s = re.sub(r"([a-z])(\d)", r"\1 \2", s)
    return re.sub(r"\s+", " ", s.strip())


def strip_volume(s: str) -> str:
    s = re.sub(r"\b0\s*[,.]\s*\d+\s*l\b", " ", s)
    s = re.sub(r"\b\d+[.,]\d+\s*l\b", " ", s)
    s = re.sub(r"\b\d+\s*(?:cl|ml)\b", " ", s)
    s = re.sub(r"\b[01]\s*l\b", " ", s)
    return s


def tokens(name: str) -> set[str]:
    toks = set(re.findall(r"[a-z0-9]+", strip_volume(norm(name))))
    out: set[str] = set()
    for t in toks:
        if t in STOP or t in VOLUME_NUMS:
            continue
        if t.isdigit() and len(t) == 1:
            continue
        out.add(t)
    return out


def score(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    return inter / min(len(a), len(b))


def meaningful_years(name: str) -> set[str]:
    """Ages (5–99) and vintage years. Volumes must already be stripped."""
    s = strip_volume(norm(name))
    ages = set()
    for n in re.findall(r"\b(\d{1,2})\b", s):
        v = int(n)
        if n in VOLUME_NUMS:
            continue
        if 5 <= v <= 99:
            ages.add(n.lstrip("0") or n)
    years = set(re.findall(r"\b((?:17|18|19|20)\d{2})\b", s))
    return ages | years


def listing_extras_ok(listing_toks: set[str], drink_toks: set[str]) -> bool:
    """Reject when either name has a different expression word (Rye, Grain, Umami…)."""
    return _extras_one_way(listing_toks, drink_toks) and _extras_one_way(
        drink_toks, listing_toks
    )


def _extras_one_way(src: set[str], other: set[str]) -> bool:
    extra = src - other
    for t in extra:
        if t.isdigit() or t in PACK:
            continue
        if len(t) >= 3:
            return False
    return True


def years_compatible(listing_years: set[str], drink_years: set[str]) -> bool:
    if not listing_years and not drink_years:
        return True
    return bool(listing_years & drink_years)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--min-score", type=float, default=0.88)
    ap.add_argument(
        "--shops",
        default="",
        help="Comma list of shop ids to match (empty = all). Example: humidor",
    )
    args = ap.parse_args()

    raw = json.loads(RAW.read_text(encoding="utf-8"))
    items = raw["items"] if isinstance(raw, dict) else raw
    wanted = {s.strip().lower() for s in args.shops.split(",") if s.strip()}
    if wanted:
        items = [it for it in items if (it.get("shop") or "").lower() in wanted]

    drinks: list[tuple[str, dict]] = []
    by_file: dict[str, list] = {}
    for fname in FILES:
        path = DATA / fname
        if not path.exists():
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        by_file[fname] = rows
        for d in rows:
            drinks.append((fname, d))

    # index drinks
    indexed = [(fname, d, tokens(d.get("name") or ""), meaningful_years(d.get("name") or "")) for fname, d in drinks]

    updates = []
    used_drink_ids: set[str] = set()

    for it in items:
        name = it.get("name") or ""
        url = it.get("url") or ""
        price = it.get("price_eur")
        shop_label = it.get("shopLabel") or it.get("shop") or ""
        if not url or not name:
            continue
        if "__trashed" in url.lower():
            continue
        it_toks = tokens(name)
        it_years = meaningful_years(name)
        if len(it_toks) < 2:
            continue
        best = None
        best_sc = 0.0
        for fname, d, dt, dy in indexed:
            if d["id"] in used_drink_ids:
                continue
            if not years_compatible(it_years, dy):
                continue
            if not listing_extras_ok(it_toks, dt):
                continue
            sc = score(it_toks, dt)
            if sc > best_sc:
                best_sc = sc
                best = (fname, d)
        if not best or best_sc < args.min_score:
            continue
        fname, d = best
        # skip meta/lineup entries (ECS series containers)
        if d.get("lineup"):
            continue
        shared = tokens(d.get("name") or "") & it_toks
        if len(shared) < 2 and best_sc < 0.95:
            continue

        before = {
            "priceUrl": d.get("priceUrl"),
            "priceEUR": d.get("priceEUR"),
            "shopHR": d.get("shopHR"),
        }
        after = propose_update(
            d,
            {
                "url": url,
                "price_eur": price,
                "shop": it.get("shop"),
                "shopLabel": shop_label,
            },
            score=best_sc,
        )
        if not after:
            continue
        d["priceUrl"] = after["priceUrl"]
        d["priceEUR"] = after["priceEUR"]
        d["shopHR"] = after["shopHR"]
        d["priceApprox"] = False
        used_drink_ids.add(d["id"])
        updates.append(
            {
                "id": d["id"],
                "file": fname,
                "score": round(best_sc, 3),
                "listing": name,
                "url": url,
                "before": before,
                "after": after,
            }
        )

    REPORT.write_text(json.dumps({"updates": updates, "count": len(updates)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"matched updates={len(updates)} report={REPORT}")
    if args.dry_run:
        print("dry-run: not writing drink JSON")
        return
    write_updates(updates)


if __name__ == "__main__":
    main()
