# -*- coding: utf-8 -*-
"""Crawl HR drink shops, classify listings into tiers A/B/C/D, write reports.

Canonical raw: scripts/output/drink_shop_listings_raw.json
Report:        scripts/output/shop_gaps_report.json
Snapshot:      scripts/output/shop_gaps_snapshot.json
Staging (D):   scripts/output/shop_ingest_staging.json

Does not mutate drink JSON (merge/ingest are separate scripts).

  python scripts/scan-drink-shop-gaps.py
  python scripts/scan-drink-shop-gaps.py --shops allez --category rum
  python scripts/scan-drink-shop-gaps.py --skip-fetch
  powershell -File scripts/schedule-shop-gaps-scan.ps1 -Install
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "src" / "data"
OUT = HERE / "output"
REPORT_JSON = OUT / "shop_gaps_report.json"
SNAPSHOT_JSON = OUT / "shop_gaps_snapshot.json"
RAW_JSON = OUT / "drink_shop_listings_raw.json"
LEGACY_RAW_JSON = OUT / "shop_gaps_listings_raw.json"
STAGING_JSON = OUT / "shop_ingest_staging.json"

DRINK_FILES = (
    "rums.json",
    "whiskies.json",
    "brandies.json",
    "gins.json",
    "tequilas.json",
    "wines.json",
    "digestifs.json",
)

MINI_RE = re.compile(
    r"(?:0\s*[,.]\s*0[1-5]\s*l|\b50\s*ml\b|\b5\s*cl\b|\b0,05\b|miniature|minijatura|sample set|uzork)",
    re.I,
)
SKIP_NAME_RE = re.compile(
    r"(?:advent\s*calendar|kalendar|sa\s+\d+\s+(?:case|čaš|cas)|"
    r"\b\d+\s*x\s*\d+\s*ml\b|gift\s*set\s*\d+|assortment)",
    re.I,
)

ALL_SHOPS = ("allez", "tipsy", "cugaklik", "miva", "roto", "humidor")

SHOP_LABEL = {
    "allez": "allez.hr",
    "tipsy": "tipsy.hr",
    "cugaklik": "cugaklik.hr",
    "miva": "miva.com.hr",
    "roto": "webshop.rotodinamic.hr",
    "humidor": "humidor.hr",
}

ECS_WORDS = re.compile(
    r"\b(?:convocation|equidem|covenant|sovereignty|principia|exceptional\s+cask|"
    r"selection\s+mark|ecs)\b",
    re.I,
)

FILE_BY_CATEGORY = {
    "rum": "rums.json",
    "whisky": "whiskies.json",
    "whiskey": "whiskies.json",
    "brandy": "brandies.json",
    "cognac": "brandies.json",
    "gin": "gins.json",
    "tequila": "tequilas.json",
    "digestif": "digestifs.json",
    "wine": "wines.json",
    "liqueur": None,
}


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def normalize_url(url: str | None) -> str:
    if not url:
        return ""
    raw = url.strip().split("#", 1)[0].split("?", 1)[0].rstrip("/")
    parsed = urlparse(raw)
    host = (parsed.netloc or "").lower().removeprefix("www.")
    path = parsed.path.rstrip("/") or ""
    return f"{parsed.scheme.lower()}://{host}{path}".lower()


def suggested_category(listing: dict) -> str | None:
    cat = (listing.get("category") or "").lower()
    blob = f"{cat} {(listing.get('url') or '')} {(listing.get('name') or '')}".lower()
    if any(k in blob for k in ("whisky", "whiskey", "bourbon", "scotch")):
        return "whisky"
    if "rum" in blob or "rhum" in blob or "ron " in blob:
        return "rum"
    if "gin" in blob:
        return "gin"
    if any(k in blob for k in ("tequila", "mezcal", "mezcal")):
        return "tequila"
    if any(k in blob for k in ("cognac", "armagnac", "calvados", "brandy", "grappa")):
        return "brandy"
    if any(k in blob for k in ("digestif", "amaro", "absinthe", "chartreuse")):
        return "digestif"
    if "wine" in blob or "/vina" in blob:
        return "wine"
    if "liqueur" in blob or "liker" in blob:
        return "liqueur"
    return None


def load_catalog() -> tuple[
    set[str],
    dict[str, tuple[str, dict]],
    list[tuple[str, dict, set[str], set[str]]],
]:
    """Return (known_urls, url->(file,drink), indexed drinks)."""
    known_urls: set[str] = set()
    by_url: dict[str, tuple[str, dict]] = {}
    indexed: list[tuple[str, dict, set[str], set[str]]] = []
    mdl = _load_module("mdl", HERE / "match-drink-listings.py")
    for fname in DRINK_FILES:
        path = DATA / fname
        if not path.exists():
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        for d in rows:
            for key in ("priceUrl",):
                u = normalize_url(d.get(key))
                if u:
                    known_urls.add(u)
                    by_url.setdefault(u, (fname, d))
            for su in d.get("sourceUrls") or []:
                if isinstance(su, str):
                    u = normalize_url(su)
                    known_urls.add(u)
                    by_url.setdefault(u, (fname, d))
            name = d.get("name") or ""
            indexed.append((fname, d, mdl.tokens(name), mdl.meaningful_years(name)))
    return known_urls, by_url, indexed


def best_catalog_matches(
    listing: dict,
    indexed: list[tuple[str, dict, set[str], set[str]]],
    *,
    top_n: int = 3,
) -> list[tuple[dict, float]]:
    mdl = sys.modules["mdl"]
    name = listing.get("name") or ""
    it_toks = mdl.tokens(name)
    it_years = mdl.meaningful_years(name)
    if len(it_toks) < 2:
        return []
    scored: list[tuple[dict, float]] = []
    for fname, d, dt, dy in indexed:
        if d.get("lineup"):
            continue
        if not mdl.years_compatible(it_years, dy):
            continue
        if not mdl.listing_extras_ok(it_toks, dt):
            continue
        sc = mdl.score(it_toks, dt)
        if sc <= 0:
            continue
        scored.append(
            (
                {"file": fname, "id": d.get("id"), "name": d.get("name")},
                sc,
            )
        )
    scored.sort(key=lambda x: -x[1])
    return scored[:top_n]


def should_skip_listing(listing: dict) -> str | None:
    name = listing.get("name") or ""
    if MINI_RE.search(name):
        return "mini/sample"
    if SKIP_NAME_RE.search(name):
        return "packaging/set"
    url = (listing.get("url") or "").lower()
    if "__trashed" in url:
        return "trashed"
    return None


def scrape_shops(wanted: list[str], category: str | None) -> list[dict]:
    items: list[dict] = []
    if "allez" in wanted:
        allez = _load_module("allez_listings", HERE / "allez_listings.py")
        cats = allez.ALLEZ_SPIRIT_LISTS
        if category:
            cats = [(u, l) for u, l in cats if l == category]
            if not cats:
                raise SystemExit(f"unknown allez category: {category}")
        items.extend(allez.scrape_allez(cats))
    sdl_shops = [s for s in wanted if s != "allez"]
    if sdl_shops:
        sdl = _load_module("sdl", HERE / "scrape-drink-shop-listings.py")
        for shop in sdl_shops:
            if shop == "tipsy":
                items.extend(sdl.scrape_tipsy())
            elif shop == "cugaklik":
                items.extend(sdl.scrape_cugaklik())
            elif shop == "miva":
                items.extend(sdl.scrape_miva())
            elif shop == "roto":
                items.extend(sdl.scrape_roto())
            elif shop == "humidor":
                items.extend(sdl.scrape_humidor())
            else:
                raise SystemExit(f"unknown shop: {shop}")
    return items


def diff_new_urls(current: list[dict], previous: dict | None) -> set[str]:
    if not previous:
        return {normalize_url(it.get("url")) for it in current if it.get("url")}
    prev_urls = set(previous.get("urls") or [])
    return {
        normalize_url(it.get("url"))
        for it in current
        if normalize_url(it.get("url")) and normalize_url(it.get("url")) not in prev_urls
    }


def classify_listing(
    listing: dict,
    *,
    known_urls: set[str],
    by_url: dict[str, tuple[str, dict]],
    indexed: list[tuple[str, dict, set[str], set[str]]],
    new_urls: set[str],
    min_score: float,
) -> dict | None:
    """Return classified row or None if skipped."""
    skip = should_skip_listing(listing)
    if skip:
        return None
    url_key = normalize_url(listing.get("url"))
    sug = suggested_category(listing)
    base = {
        **listing,
        "suggestedCategory": sug,
        "newSinceLastRun": url_key in new_urls,
    }

    if url_key and url_key in known_urls:
        fname, drink = by_url.get(url_key, (None, None))
        return {
            **base,
            "tier": "A",
            "bestScore": 1.0,
            "matchId": (drink or {}).get("id"),
            "matchFile": fname,
            "matchName": (drink or {}).get("name"),
        }

    matches = best_catalog_matches(listing, indexed, top_n=3)
    best = matches[0] if matches else None
    best_sc = best[1] if best else 0.0

    if best and best_sc >= min_score:
        return {
            **base,
            "tier": "B",
            "bestScore": round(best_sc, 3),
            "matchId": best[0]["id"],
            "matchFile": best[0]["file"],
            "matchName": best[0]["name"],
            "candidates": [
                {**m[0], "score": round(m[1], 3)} for m in matches
            ],
        }

    if best and best_sc >= 0.5:
        return {
            **base,
            "tier": "C",
            "bestScore": round(best_sc, 3),
            "matchId": best[0]["id"],
            "matchFile": best[0]["file"],
            "matchName": best[0]["name"],
            "candidates": [
                {**m[0], "score": round(m[1], 3)} for m in matches
            ],
        }

    # ECS-style names with a parent lineup → ask, do not stage as D
    if ECS_WORDS.search(listing.get("name") or "") and matches:
        return {
            **base,
            "tier": "C",
            "bestScore": round(best_sc, 3),
            "matchId": best[0]["id"] if best else None,
            "matchFile": best[0]["file"] if best else None,
            "matchName": best[0]["name"] if best else None,
            "candidates": [{**m[0], "score": round(m[1], 3)} for m in matches],
            "ecsHint": True,
        }

    return {
        **base,
        "tier": "D",
        "bestScore": round(best_sc, 3),
        "matchId": None,
        "matchFile": None,
        "matchName": None,
        "candidates": [{**m[0], "score": round(m[1], 3)} for m in matches],
    }


def enqueue_tier_c(rows: list[dict]) -> int:
    from catalog_ask_queue import ask_item, load_ask_queue, save_ask_queue

    existing_keys = {
        (it.get("key") or "")
        for it in (load_ask_queue().get("items") or [])
        if not it.get("answered")
    }
    items = []
    for r in rows:
        shop_id = (r.get("shop") or "").lower()
        label = r.get("shopLabel") or SHOP_LABEL.get(shop_id) or shop_id
        q = (
            "ECS/lineup varijanta — povezi s parent id ili skip."
            if r.get("ecsHint")
            else "Koji katalog id odgovara ovoj boci (ili new / skip)?"
        )
        row = ask_item(
            kind="drink-ambiguous",
            question=q,
            name=r.get("name") or "",
            shop=label,
            url=r.get("url"),
            candidates=r.get("candidates") or [],
            extra={
                "bestScore": r.get("bestScore"),
                "suggestedCategory": r.get("suggestedCategory"),
                "tier": "C",
            },
        )
        if row["key"] not in existing_keys:
            items.append(row)
    if not items:
        return 0
    save_ask_queue(items, merge=True)
    return len(items)


def write_staging(rows: list[dict], stamp: str) -> int:
    prev_urls: set[str] = set()
    if STAGING_JSON.exists():
        prev = json.loads(STAGING_JSON.read_text(encoding="utf-8"))
        for it in prev.get("items") or []:
            u = normalize_url(it.get("url"))
            if u:
                prev_urls.add(u)
    ingestable = {"rum", "whisky", "brandy", "gin", "tequila", "digestif"}
    staged: list[dict] = []
    vague_ask: list[dict] = []
    from catalog_ask_queue import ask_item, save_ask_queue

    for r in rows:
        sug = r.get("suggestedCategory")
        url_key = normalize_url(r.get("url"))
        if sug not in ingestable:
            shop_id = (r.get("shop") or "").lower()
            label = r.get("shopLabel") or SHOP_LABEL.get(shop_id) or shop_id
            kind = "drink-vague" if not sug else "drink-category"
            vague_ask.append(
                ask_item(
                    kind=kind,
                    question="Predloži kategoriju ili skip.",
                    name=r.get("name") or "",
                    shop=label,
                    url=r.get("url"),
                    extra={"suggestedCategory": sug, "tier": "D"},
                )
            )
            continue
        if url_key in prev_urls and not r.get("newSinceLastRun"):
            # keep existing staging entry by rebuilding from current row
            pass
        staged.append(
            {
                "name": r.get("name"),
                "url": r.get("url"),
                "price_eur": r.get("price_eur"),
                "shop": r.get("shop"),
                "shopLabel": r.get("shopLabel") or SHOP_LABEL.get((r.get("shop") or "").lower()),
                "suggestedCategory": sug,
                "fetchedAt": stamp,
                "newSinceLastRun": r.get("newSinceLastRun"),
                "bestScore": r.get("bestScore"),
            }
        )
    # merge by url with previous staging
    by_url: dict[str, dict] = {}
    for it in staged:
        by_url[normalize_url(it.get("url"))] = it
    if STAGING_JSON.exists():
        for it in (json.loads(STAGING_JSON.read_text(encoding="utf-8")).get("items") or []):
            u = normalize_url(it.get("url"))
            if u and u not in by_url:
                by_url[u] = it
    payload = {
        "updatedAt": stamp,
        "count": len(by_url),
        "items": sorted(by_url.values(), key=lambda x: (x.get("suggestedCategory") or "", x.get("name") or "")),
    }
    STAGING_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if vague_ask:
        save_ask_queue(vague_ask, merge=True)
    return len(staged)


def load_raw_listings(skip_fetch: bool, wanted: list[str], category: str | None) -> list[dict]:
    if skip_fetch:
        path = RAW_JSON if RAW_JSON.exists() else LEGACY_RAW_JSON
        if not path.exists():
            raise SystemExit("no raw listings; run without --skip-fetch first")
        raw = json.loads(path.read_text(encoding="utf-8"))
        listings = raw.get("items") if isinstance(raw, dict) else raw
        print(f"loaded {len(listings)} listings from {path.name}", flush=True)
        return listings

    listings = scrape_shops(wanted, category)
    # merge-preserve: keep shops not scraped this run (e.g. ecuga)
    if RAW_JSON.exists():
        prev = json.loads(RAW_JSON.read_text(encoding="utf-8"))
        old_items = prev.get("items") if isinstance(prev, dict) else prev
        keep = [it for it in (old_items or []) if (it.get("shop") or "") not in wanted]
        listings = keep + listings
        notes = list((prev.get("notes") if isinstance(prev, dict) else None) or [])
    else:
        notes = []
    RAW_JSON.write_text(
        json.dumps(
            {
                "fetchedAt": datetime.now(timezone.utc).isoformat(),
                "shops": wanted,
                "category": category,
                "notes": notes,
                "count": len(listings),
                "items": listings,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {RAW_JSON} ({len(listings)} listings)", flush=True)
    return listings


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--shops", default=",".join(ALL_SHOPS))
    ap.add_argument("--category", default="", help="Allez category filter")
    ap.add_argument("--min-score", type=float, default=0.88)
    ap.add_argument("--skip-fetch", action="store_true")
    ap.add_argument("--no-ask", action="store_true", help="Do not write catalog_ask_queue")
    ap.add_argument("--no-staging", action="store_true", help="Do not write shop_ingest_staging")
    args = ap.parse_args()
    wanted = [s.strip().lower() for s in args.shops.split(",") if s.strip()]
    for s in wanted:
        if s not in ALL_SHOPS:
            raise SystemExit(f"unknown shop: {s}")

    OUT.mkdir(parents=True, exist_ok=True)
    prev_snapshot = None
    if SNAPSHOT_JSON.exists():
        prev_snapshot = json.loads(SNAPSHOT_JSON.read_text(encoding="utf-8"))

    listings = load_raw_listings(args.skip_fetch, wanted, args.category or None)
    known_urls, by_url, indexed = load_catalog()
    new_urls = diff_new_urls(listings, prev_snapshot)

    classified: list[dict] = []
    skipped = 0
    for it in listings:
        if should_skip_listing(it):
            skipped += 1
            continue
        row = classify_listing(
            it,
            known_urls=known_urls,
            by_url=by_url,
            indexed=indexed,
            new_urls=new_urls,
            min_score=args.min_score,
        )
        if row is None:
            skipped += 1
            continue
        classified.append(row)

    by_tier: dict[str, int] = {}
    for r in classified:
        t = r.get("tier") or "?"
        by_tier[t] = by_tier.get(t, 0) + 1

    tier_a = [r for r in classified if r.get("tier") == "A"]
    tier_b = [r for r in classified if r.get("tier") == "B"]
    tier_c = [r for r in classified if r.get("tier") == "C"]
    tier_d = [r for r in classified if r.get("tier") == "D"]

    # Gaps for human review = C + D (unmatched); A/B are actionable matches
    gaps = tier_c + tier_d
    gaps.sort(
        key=lambda x: (
            (not x.get("newSinceLastRun")),
            x.get("tier") or "",
            x.get("shop") or "",
            x.get("name") or "",
        )
    )

    by_shop: dict[str, int] = {}
    by_shop_new: dict[str, int] = {}
    for g in gaps:
        shop = g.get("shop") or "?"
        by_shop[shop] = by_shop.get(shop, 0) + 1
        if g.get("newSinceLastRun"):
            by_shop_new[shop] = by_shop_new.get(shop, 0) + 1

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ask_added = 0
    if not args.no_ask:
        ask_added = enqueue_tier_c(tier_c)
    staged_n = 0
    if not args.no_staging:
        staged_n = write_staging(tier_d, stamp)

    report = {
        "generatedAt": stamp,
        "shops": wanted,
        "category": args.category or None,
        "listingsScraped": len(listings),
        "skippedListings": skipped,
        "byTier": by_tier,
        "tierA": len(tier_a),
        "tierB": len(tier_b),
        "tierC": len(tier_c),
        "tierD": len(tier_d),
        "gaps": len(gaps),
        "gapsNewSinceLastRun": sum(1 for g in gaps if g.get("newSinceLastRun")),
        "askQueueAdded": ask_added,
        "stagingWritten": staged_n,
        "byShop": by_shop,
        "byShopNew": by_shop_new,
        "itemsA": tier_a,
        "itemsB": tier_b,
        "items": gaps,
    }
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    SNAPSHOT_JSON.write_text(
        json.dumps(
            {
                "generatedAt": stamp,
                "urls": sorted(
                    {normalize_url(it.get("url")) for it in listings if it.get("url")}
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"\n=== shop gap scan ({stamp}) ===", flush=True)
    print(
        f"listings: {len(listings)} | skipped: {skipped} | "
        f"A={by_tier.get('A', 0)} B={by_tier.get('B', 0)} "
        f"C={by_tier.get('C', 0)} D={by_tier.get('D', 0)}",
        flush=True,
    )
    print(f"ask-queue new~{ask_added} | staging D written={staged_n}", flush=True)
    for shop, n in sorted(by_shop.items()):
        extra = f" ({by_shop_new.get(shop, 0)} new)" if by_shop_new.get(shop) else ""
        print(f"  gaps {shop}: {n}{extra}", flush=True)
    print(f"report: {REPORT_JSON}", flush=True)


if __name__ == "__main__":
    main()
