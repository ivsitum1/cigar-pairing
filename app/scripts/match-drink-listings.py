# -*- coding: utf-8 -*-
"""Match drink_shop_listings_raw.json onto drink JSON; create missing bottles.

Updates priceUrl / priceEUR / shopHR when token overlap is strong enough.
Unmatched listings with a clear category become new catalogue rows
(profileEstimated). Ambiguous near-matches and unclear categories go to
scripts/output/catalog_ask_queue.json for human review.

  python scripts/match-drink-listings.py
  python scripts/match-drink-listings.py --dry-run
  python scripts/match-drink-listings.py --no-create
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from catalog_ask_queue import ask_item, save_ask_queue

DATA = HERE.parent / "src" / "data"
RAW = HERE / "output" / "drink_shop_listings_raw.json"
REPORT = HERE / "output" / "drink_listing_match_report.json"
REGISTRY = DATA / "drinkIdRegistry.json"

FILES = [
    "rums.json",
    "whiskies.json",
    "brandies.json",
    "gins.json",
    "tequilas.json",
    "wines.json",
    "digestifs.json",
]

# listing category -> (file, category id, id prefix)
CATEGORY_TARGET: dict[str, tuple[str, str, str]] = {
    "rum": ("rums.json", "rum", "rum"),
    "whisky": ("whiskies.json", "whisky", "wh"),
    "whiskey": ("whiskies.json", "whisky", "wh"),
    "gin": ("gins.json", "gin", "gin"),
    "brandy": ("brandies.json", "brandy", "br"),
    "cognac": ("brandies.json", "brandy", "br"),
    "tequila": ("tequilas.json", "tequila", "tq"),
    "mezcal": ("tequilas.json", "tequila", "tq"),
    "digestif": ("digestifs.json", "digestif", "dg"),
    "liqueur": ("digestifs.json", "digestif", "dg"),
    "wine": ("wines.json", "wine", "wine"),
}

# shelves that are too mixed to auto-mint
SKIP_CREATE_CATEGORIES = {"all", "spirits", "unknown", ""}

# Only these shops mint new bottles; others only update prices / fill ask queue
CREATE_SHOPS = {"allez", "ecuga", "tipsy", "cugaklik"}

# Auto-mint these categories from CREATE_SHOPS. Others stay in the ask queue.
AUTO_CREATE_CATEGORIES = {"rum", "gin", "whisky", "tequila"}

STOP = {
    "the", "of", "and", "yo", "vol", "old", "years", "year", "single", "malt",
    "scotch", "whisky", "whiskey", "giftbox", "gift", "box", "poklon", "kutiji",
    "u", "in", "gb", "limited", "edition", "batch", "bottle", "l", "cl", "ml",
    "rum", "rhum", "ron", "gin", "cognac", "armagnac", "brandy", "tequila",
    "liker", "liqueur", "sa", "with", "de", "la", "le", "les", "du",
}

PACK = {
    "gran", "reserva", "familiar", "cask", "finish", "anos", "solera",
    "gift", "box", "giftbox", "grand", "royal", "select", "selection",
    "seleccion", "maestros", "original", "pure", "estate", "port",
    "sherry", "oloroso", "madeira", "chateau", "domaine",
    # shop-title noise (not a different expression)
    "spirit", "drink", "superior", "special", "medal", "anniversary",
    "christmas", "danish", "navy", "frigate", "founders", "collection",
    "batch", "release", "unpeated", "peated", "years", "year", "old",
    "vol", "alcohol", "alc", "proof", "strength", "caskstrength",
    "finest", "fine", "premium", "handcrafted", "blend", "blended",
    "vieux", "blanc", "extra", "hors", "age", "anejo", "reserva",
    # region words shops glue onto the title
    "jamaica", "jamaican", "barbados", "martinique", "cuba", "cuban",
    "nicaragua", "trinidad", "tobago", "lucia", "saint", "st",
    "guadeloupe", "haiti", "guyana", "demerara", "panama", "venezuela",
    "dominican", "dominicana", "puerto", "rico", "fiji", "mauritius",
    "reunion", "agricole", "rhum", "ron", "island", "caribbean",
    "scotch", "irish", "bourbon", "tennessee", "japanese", "american",
}

VOLUME_NUMS = {"70", "75", "50", "05", "07"}

NOISE_NAME_RE = re.compile(
    r"(?:advent|kalendar|calendar|minibar|probni\s+set|tasting\s+set|"
    r"sa\s+\d+\s+čaš|with\s+\d+\s+glass)",
    re.I,
)

DEFAULT_SERVING = {
    "rum": {"neat": 3, "water": 2, "rocks": 2, "highball": 1, "cola": 0, "best": "Čisto"},
    "whisky": {"neat": 3, "water": 3, "rocks": 1, "highball": 0, "cola": 0, "best": "Čisto / kap vode"},
    "gin": {"neat": 2, "tonic": 3, "martini": 2, "highball": 2, "best": "Tonic"},
    "brandy": {"neat": 3, "water": 1, "rocks": 1, "highball": 0, "cola": 0, "best": "Čisto"},
    "tequila": {"neat": 3, "water": 1, "rocks": 1, "highball": 1, "cola": 0, "best": "Čisto"},
    "digestif": {"neat": 2, "water": 0, "rocks": 2, "highball": 0, "cola": 0, "best": "Čisto / rocks"},
    "wine": {"neat": 3, "water": 0, "rocks": 0, "highball": 0, "cola": 0, "best": "Čaša"},
}

DEFAULT_STYLE = {
    "rum": ("other", "Nepoznato", 3, 2, ["hrast"]),
    "whisky": ("world", "World", 3, 2, ["hrast"]),
    "gin": ("contemporary", "Nepoznato", 2, 1, ["borovica"]),
    "brandy": ("cognac", "Nepoznato", 3, 2, ["suho-voce"]),
    "tequila": ("blanco", "Meksiko", 2, 1, ["agava"]),
    "digestif": ("liqueur", "Nepoznato", 2, 4, ["slatko"]),
    "wine": ("red", "Nepoznato", 3, 2, ["voce"]),
}


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
        # null / missing — leave surgical path; caller should use full rewrite for creates
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
        # keep ages 5–9; drop other single-digit noise (No. 2 shop crumbs etc. stay via years)
        if t.isdigit() and len(t) == 1 and t not in {"5", "6", "7", "8", "9"}:
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


def clean_display_name(name: str) -> str:
    s = name or ""
    # Collapse dotted abbreviations before tokenization (X.O. → XO)
    s = re.sub(r"\bV\.?\s*S\.?\s*O\.?\s*P\.?\b", "VSOP", s, flags=re.I)
    s = re.sub(r"\bX\.?\s*O\.?\b", "XO", s, flags=re.I)
    s = re.sub(r"\bV\.?\s*S\.?\b", "VS", s, flags=re.I)
    s = re.sub(r"\bN[º°]\s*", "No ", s, flags=re.I)
    s = re.sub(r"\bNo\.\s*", "No ", s, flags=re.I)
    s = re.sub(r"\s*\d{1,2}(?:[.,]\d)?\s*%\s*vol\.?", "", s, flags=re.I)
    s = re.sub(r"\s*\d{1,2}(?:[.,]\d+)?\s*%", "", s)
    s = re.sub(r"\s*\d+(?:[.,]\d+)?\s*(?:cl|ml|l)\b", "", s, flags=re.I)
    s = re.sub(r"\s*u\s+(?:drvenoj\s+)?poklon\s+kutij\w*", "", s, flags=re.I)
    s = re.sub(r"\s*\bgift\s*box\b", "", s, flags=re.I)
    s = re.sub(r"\s*\([^)]*blend[^)]*\)", " ", s, flags=re.I)
    s = re.sub(r"\s{2,}", " ", s).strip(" -–,")
    return s


def meaningful_years(name: str) -> set[str]:
    """Ages (5–99) and vintage years. Strip ABV / volume first."""
    s = strip_volume(norm(clean_display_name(name)))
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
    """Reject when either name has a different expression word (Rye, Grain, Umami…).

    Shop packaging tokens belong in PACK/STOP so they do not count as extras.
    """
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


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text


def mint_drink_id(prefix: str, name: str, used: set[str]) -> str:
    base = f"{prefix}-{slugify(clean_display_name(name))}"[:80].strip("-")
    if not base or base == prefix:
        base = f"{prefix}-shop-{len(used)}"
    cand = base
    n = 2
    while cand in used:
        cand = f"{base}-{n}"
        n += 1
    return cand


def seed_notes(category: str, name: str) -> dict[str, str]:
    hr = (
        f"Automatski unos iz HR webshopa ({category}): {name}. "
        "Profil je procijenjen — treba PDP enrichment i ručni pregled."
    )
    en = (
        f"Auto-added from an HR webshop ({category}): {name}. "
        "Profile is estimated — needs PDP enrichment and human review."
    )
    return {"hr": hr, "en": en}


def build_stub(
    *,
    drink_id: str,
    category: str,
    name: str,
    price: float | None,
    url: str,
    shop_label: str,
) -> dict:
    style, region, body, sweet, tags = DEFAULT_STYLE.get(
        category, ("other", "Nepoznato", 3, 2, ["hrast"])
    )
    serving = deepcopy(DEFAULT_SERVING.get(category, DEFAULT_SERVING["rum"]))
    row: dict = {
        "id": drink_id,
        "category": category,
        "name": clean_display_name(name) or name,
        "style": style,
        "region": region,
        "body": body,
        "sweetness": sweet,
        "flavorTags": list(tags),
        "additiveStatus": "unknown",
        "qualityScore": 6.0,
        "priceEUR": {"min": price, "max": price} if price is not None else None,
        "priceApprox": False,
        "shopHR": shop_label,
        "status": None,
        "pairable": category not in ("digestif",),
        "serving": serving,
        "cigarHint": None,
        "priceUrl": url,
        "notes": seed_notes(category, name),
        "profileEstimated": True,
    }
    if category == "gin":
        row["botanicalProfile"] = "botanical"
    return row


def resolve_category(it: dict) -> str | None:
    cat = (it.get("category") or "").strip().lower()
    if cat in CATEGORY_TARGET:
        return cat
    # name heuristics for mixed shelves
    name = (it.get("name") or "").lower()
    if re.search(r"\b(rhum|ron|rum)\b", name):
        return "rum"
    if re.search(r"\b(whisky|whiskey|bourbon|scotch)\b", name):
        return "whisky"
    if re.search(r"\bgin\b", name):
        return "gin"
    if re.search(r"\b(cognac|armagnac|brandy|calvados)\b", name):
        return "brandy"
    if re.search(r"\b(tequila|mezcal)\b", name):
        return "tequila"
    return None


def should_skip_listing(name: str, url: str) -> bool:
    if not name or not url:
        return True
    if "__trashed" in url.lower():
        return True
    if NOISE_NAME_RE.search(name):
        return True
    return False


def register_ids(new_ids: list[str]) -> None:
    if not new_ids:
        return
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    ids = list(reg.get("ids") or [])
    have = set(ids)
    for i in new_ids:
        if i not in have:
            ids.append(i)
            have.add(i)
    ids.sort()
    REGISTRY.write_text(
        json.dumps({"_comment": reg.get("_comment", ""), "ids": ids}, ensure_ascii=False, indent=1)
        + "\n",
        encoding="utf-8",
    )


def append_creates(creates: list[dict]) -> None:
    by_file: dict[str, list] = {}
    for c in creates:
        drink = dict(c["drink"])
        drink.pop("_pendingCreate", None)
        by_file.setdefault(c["file"], []).append(drink)
    for fname, rows in by_file.items():
        path = DATA / fname
        data = json.loads(path.read_text(encoding="utf-8"))
        data.extend(rows)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  created {len(rows)} in {fname}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--min-score", type=float, default=0.88)
    ap.add_argument(
        "--ask-score",
        type=float,
        default=0.55,
        help="Near-miss band lower bound → ask queue (below this = new or skip)",
    )
    ap.add_argument(
        "--shops",
        default="",
        help="Comma list of shop ids to match (empty = all). Example: allez,ecuga",
    )
    ap.add_argument(
        "--no-create",
        action="store_true",
        help="Do not mint new drink IDs; unmatched go to ask queue instead",
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

    indexed = [
        (fname, d, tokens(d.get("name") or ""), meaningful_years(d.get("name") or ""))
        for fname, d in drinks
    ]
    used_ids = {d["id"] for _, d in drinks}
    used_urls = {
        (d.get("priceUrl") or "").rstrip("/").lower()
        for _, d in drinks
        if d.get("priceUrl")
    }

    updates: list[dict] = []
    creates: list[dict] = []
    asks: list[dict] = []
    used_drink_ids: set[str] = set()
    create_urls: set[str] = set()
    create_slugs: set[str] = set()
    # existing cleaned-name slugs — avoid reminting renames
    for _, d in drinks:
        create_slugs.add(slugify(clean_display_name(d.get("name") or "")))

    for it in items:
        name = it.get("name") or ""
        url = (it.get("url") or "").rstrip("/")
        price = it.get("price_eur")
        shop_label = it.get("shopLabel") or it.get("shop") or ""
        shop = (it.get("shop") or "").lower()
        if should_skip_listing(name, url):
            continue
        url_key = url.lower()
        if url_key in used_urls or url_key in create_urls:
            continue

        it_toks = tokens(clean_display_name(name))
        it_years = meaningful_years(clean_display_name(name))
        if len(it_toks) < 2:
            asks.append(
                ask_item(
                    kind="drink-vague",
                    question="Naziv je prekratak/nejasan za automatski unos. Kako ga zovemo u app-u?",
                    name=name,
                    shop=shop_label,
                    url=url,
                    extra={"price_eur": price, "listingCategory": it.get("category")},
                )
            )
            continue

        best = None
        best_sc = 0.0
        near: list[tuple[float, str, dict]] = []
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
            if sc >= args.ask_score:
                near.append((sc, fname, d))

        if best and best_sc >= args.min_score:
            fname, d = best
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
            changed = False
            old_url = d.get("priceUrl") or ""
            if is_weak_price_url(old_url):
                d["priceUrl"] = url
                changed = True
            elif shop in ("tipsy", "cugaklik", "miva", "roto", "allez", "ecuga") and best_sc >= 0.9:
                if url != old_url:
                    d["priceUrl"] = url
                    changed = True
            elif shop == "humidor":
                pass
            elif "allez.hr" in old_url or "ecuga.com" in old_url:
                pass

            if price is not None and d.get("priceUrl") == url:
                pe = d.get("priceEUR")
                if not isinstance(pe, dict) or pe.get("min") != price or pe.get("max") != price:
                    d["priceEUR"] = {"min": price, "max": price}
                    d["priceApprox"] = False
                    changed = True
            if shop_label and d.get("priceUrl") == url and d.get("shopHR") != shop_label:
                d["shopHR"] = shop_label
                changed = True

            if changed:
                used_drink_ids.add(d["id"])
                used_urls.add(url_key)
                if d.get("_pendingCreate"):
                    # mutate in-memory stub only; append_creates writes it later
                    continue
                updates.append(
                    {
                        "id": d["id"],
                        "file": fname,
                        "score": round(best_sc, 3),
                        "listing": name,
                        "url": url,
                        "before": before,
                        "after": {
                            "priceUrl": d.get("priceUrl"),
                            "priceEUR": d.get("priceEUR"),
                            "shopHR": d.get("shopHR"),
                        },
                    }
                )
            continue

        # Near-miss → ask
        if best and best_sc >= args.ask_score:
            near_sorted = sorted(near, key=lambda x: -x[0])[:5]
            asks.append(
                ask_item(
                    kind="drink-ambiguous",
                    question=(
                        f"Je li shop stavka ista boca kao neki od kandidata "
                        f"(najbolji score {best_sc:.2f}), ili nova boca?"
                    ),
                    name=name,
                    shop=shop_label,
                    url=url,
                    candidates=[
                        {
                            "id": d["id"],
                            "name": d.get("name"),
                            "file": fname,
                            "score": round(sc, 3),
                        }
                        for sc, fname, d in near_sorted
                    ],
                    extra={"price_eur": price, "listingCategory": it.get("category")},
                )
            )
            continue

        # No match → create or ask
        cat = resolve_category(it)
        listing_cat = (it.get("category") or "").strip().lower()
        if listing_cat in SKIP_CREATE_CATEGORIES:
            # Mixed shelves: only ask when name also lacks a category cue
            if cat is None:
                asks.append(
                    ask_item(
                        kind="drink-category",
                        question="U koju kategoriju ide ova boca (rum/whisky/gin/…)?",
                        name=name,
                        shop=shop_label,
                        url=url,
                        extra={"price_eur": price, "listingCategory": listing_cat},
                    )
                )
            # else: name says rum/whisky/… but shelf was "all" — still require
            # a dedicated shelf hit; ask instead of minting from "all"
            elif shop in CREATE_SHOPS:
                asks.append(
                    ask_item(
                        kind="drink-new",
                        question=(
                            f"Nema matcha; polica je {listing_cat!r} ali ime sugerira {cat}. "
                            "Dodati kao novu bocu?"
                        ),
                        name=name,
                        shop=shop_label,
                        url=url,
                        extra={
                            "price_eur": price,
                            "listingCategory": listing_cat,
                            "suggestedCategory": cat,
                        },
                    )
                )
            continue

        if cat is None or cat not in CATEGORY_TARGET:
            asks.append(
                ask_item(
                    kind="drink-category",
                    question="Ne znam kategoriju. Rum, whisky, gin, brandy, tequila, digestif ili wine?",
                    name=name,
                    shop=shop_label,
                    url=url,
                    extra={"price_eur": price, "listingCategory": listing_cat},
                )
            )
            continue

        if shop not in CREATE_SHOPS or args.no_create:
            asks.append(
                ask_item(
                    kind="drink-new",
                    question="Nema matcha u katalogu. Dodati kao novu bocu?",
                    name=name,
                    shop=shop_label,
                    url=url,
                    extra={
                        "price_eur": price,
                        "listingCategory": listing_cat,
                        "suggestedCategory": cat,
                    },
                )
            )
            continue

        fname, category, prefix = CATEGORY_TARGET[cat]
        if category not in AUTO_CREATE_CATEGORIES:
            asks.append(
                ask_item(
                    kind="drink-new",
                    question=(
                        f"Nova {category} boca (auto-create je samo za "
                        f"{', '.join(sorted(AUTO_CREATE_CATEGORIES))}). Dodati?"
                    ),
                    name=name,
                    shop=shop_label,
                    url=url,
                    extra={
                        "price_eur": price,
                        "listingCategory": listing_cat,
                        "suggestedCategory": category,
                    },
                )
            )
            continue

        name_slug = slugify(clean_display_name(name))
        if not name_slug or name_slug in create_slugs:
            continue

        drink_id = mint_drink_id(prefix, name, used_ids)
        used_ids.add(drink_id)
        create_slugs.add(name_slug)
        stub = build_stub(
            drink_id=drink_id,
            category=category,
            name=name,
            price=price if isinstance(price, (int, float)) else None,
            url=url,
            shop_label=shop_label,
        )
        creates.append({"file": fname, "drink": stub, "listing": name, "url": url})
        create_urls.add(url_key)
        stub["_pendingCreate"] = True
        indexed.append((fname, stub, tokens(stub["name"]), meaningful_years(stub["name"])))

    # Updates must only touch IDs already on disk
    report = {
        "updates": updates,
        "creates": [
            {"id": c["drink"]["id"], "file": c["file"], "listing": c["listing"], "url": c["url"]}
            for c in creates
        ],
        "asks": len(asks),
        "countUpdates": len(updates),
        "countCreates": len(creates),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ask_path = None
    if asks and not args.dry_run:
        ask_path = save_ask_queue(asks, merge=True)
    elif asks and args.dry_run:
        # still materialise for review, but mark as dry-run snapshot
        ask_path = save_ask_queue(asks, merge=False)
    print(
        f"matched updates={len(updates)} creates={len(creates)} asks={len(asks)} "
        f"report={REPORT}"
        + (f" ask={ask_path}" if ask_path else "")
    )
    if args.dry_run:
        print("dry-run: not writing drink JSON / registry")
        return
    if updates:
        write_updates(updates)
    if creates:
        append_creates(creates)
        register_ids([c["drink"]["id"] for c in creates])


if __name__ == "__main__":
    main()
