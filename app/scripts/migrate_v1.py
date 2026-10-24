#!/usr/bin/env python3
"""Migrate current catalog JSON into app/src/data/v1/{products,vitolas,shops,offers}.json.

Idempotent: same inputs → byte-identical sorted JSON. Does not touch the UI or
alias files. Run from app/:  python scripts/migrate_v1.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src" / "data"
OUT = DATA / "v1"

MIGRATION_DATE = date.today().isoformat()
REGIONS = ("HR", "EU", "USA")

# Cigar shops (mirrors shops.ts) — functions omitted; only registry fields.
CIGAR_SHOPS: list[dict[str, Any]] = [
    {
        "id": "humidor",
        "name": "The Humidor",
        "region": "HR",
        "city": "Zagreb",
        "type": "online",
        "source": "scraper",
        "adapter": "humidor",
        "home": "https://humidor.hr/hr/",
        "productHost": "humidor.hr",
    },
    {
        "id": "havana-hr",
        "name": "Havana Cigar Shop",
        "region": "HR",
        "city": None,
        "type": "online",
        "source": "scraper",
        "adapter": "havana",
        "home": "https://havana-cigar-shop.com/",
        "productHost": "havana-cigar-shop.com",
    },
    {
        "id": "tobacco-petica-branimir",
        "name": "Tobacco Petica (Branimir)",
        "region": "HR",
        "city": "Zagreb",
        "type": "walkIn",
        "source": "manual",
        "adapter": "tobacco-petica",
        "home": "https://www.branimir.hr/minglanje/trgovine/tobacco-petica",
        "productHost": None,
    },
    {
        "id": "aficionado-zg",
        "name": "Aficionado",
        "region": "HR",
        "city": "Zagreb",
        "type": "walkIn",
        "source": "manual",
        "adapter": "aficionado",
        "home": "https://www.aficionado.hr/",
        "productHost": None,
    },
    {
        "id": "cigarworld",
        "name": "CigarWorld",
        "region": "EU",
        "city": None,
        "type": "online",
        "source": "scraper",
        "adapter": "cigarworld",
        "home": "https://www.cigarworld.de/en",
        "productHost": "cigarworld.de",
    },
    {
        "id": "cgars-uk",
        "name": "C.Gars Ltd",
        "region": "EU",
        "city": None,
        "type": "online",
        "source": "scraper",
        "adapter": "cgars",
        "home": "https://www.cgarsltd.co.uk/",
        "productHost": "cgarsltd.co.uk",
    },
    {
        "id": "la-couronne-ch",
        "name": "La Couronne",
        "region": "EU",
        "city": None,
        "type": "online",
        "source": "scraper",
        "adapter": "la-couronne",
        "home": "https://cigarpassion.ch/en/",
        "productHost": "cigarpassion.ch",
    },
    {
        "id": "holts",
        "name": "Holt's",
        "region": "USA",
        "city": "Philadelphia",
        "type": "online",
        "source": "scraper",
        "adapter": "holts",
        "home": "https://www.holts.com/",
        "productHost": None,
    },
    {
        "id": "cigarsdaily",
        "name": "Cigars Daily",
        "region": "USA",
        "city": None,
        "type": "online",
        "source": "scraper",
        "adapter": "cigarsdaily",
        "home": "https://cigarsdaily.com/",
        "productHost": "cigarsdaily.com",
    },
    {
        "id": "famous-smoke",
        "name": "Famous Smoke",
        "region": "USA",
        "city": None,
        "type": "online",
        "source": "scraper",
        "adapter": "famous-smoke",
        "home": "https://www.famous-smoke.com/",
        "productHost": "famous-smoke.com",
    },
    {
        "id": "neptune",
        "name": "Neptune Cigar",
        "region": "USA",
        "city": None,
        "type": "online",
        "source": "scraper",
        "adapter": "neptune",
        "home": "https://www.neptunecigar.com/",
        "productHost": "neptunecigar.com",
    },
]

# Drink shops (mirrors drinkShops.ts) — exclude REF (wine-searcher).
DRINK_SHOPS: list[dict[str, Any]] = [
    {
        "id": "humidor",
        "name": "The Humidor",
        "region": "HR",
        "city": "Zagreb",
        "type": "online",
        "source": "scraper",
        "adapter": "humidor",
        "home": "https://humidor.hr/hr/",
        "productHost": "humidor.hr",
    },
    {
        "id": "allez",
        "name": "allez.hr",
        "region": "HR",
        "city": None,
        "type": "online",
        "source": "scraper",
        "adapter": "allez",
        "home": "https://allez.hr/",
        "productHost": "allez.hr",
    },
    {
        "id": "ecuga",
        "name": "ecuga.com",
        "region": "HR",
        "city": None,
        "type": "online",
        "source": "scraper",
        "adapter": "ecuga",
        "home": "https://ecuga.com/",
        "productHost": "ecuga.com",
    },
    {
        "id": "drinx",
        "name": "drinx.hr",
        "region": "HR",
        "city": None,
        "type": "online",
        "source": "scraper",
        "adapter": "drinx",
        "home": "https://www.drinx.hr/",
        "productHost": "drinx.hr",
    },
    {
        "id": "tipsy",
        "name": "Tipsy",
        "region": "HR",
        "city": None,
        "type": "online",
        "source": "scraper",
        "adapter": "tipsy",
        "home": "https://tipsy.hr/",
        "productHost": "tipsy.hr",
    },
    {
        "id": "cugaklik",
        "name": "Cugaklik",
        "region": "HR",
        "city": None,
        "type": "online",
        "source": "scraper",
        "adapter": "cugaklik",
        "home": "https://www.cugaklik.hr/",
        "productHost": "cugaklik.hr",
    },
    {
        "id": "roto",
        "name": "Roto",
        "region": "HR",
        "city": None,
        "type": "online",
        "source": "scraper",
        "adapter": "roto",
        "home": "https://webshop.rotodinamic.hr/",
        "productHost": "webshop.rotodinamic.hr",
    },
    {
        "id": "vrutak",
        "name": "Vrutak",
        "region": "HR",
        "city": "Zagreb",
        "type": "both",
        "source": "scraper",
        "adapter": "vrutak",
        "home": "https://www.vrutak.hr/",
        "productHost": None,
    },
    {
        "id": "vivat",
        "name": "Vivat fina vina",
        "region": "HR",
        "city": None,
        "type": "online",
        "source": "scraper",
        "adapter": "vivat",
        "home": "https://www.vivat-finavina.hr/",
        "productHost": "vivat-finavina.hr",
    },
    {
        "id": "whisky-exchange",
        "name": "The Whisky Exchange",
        "region": "EU",
        "city": "London",
        "type": "online",
        "source": "scraper",
        "adapter": "whisky-exchange",
        "home": "https://www.thewhiskyexchange.com/",
        "productHost": "thewhiskyexchange.com",
    },
    {
        "id": "total-wine",
        "name": "Total Wine & More",
        "region": "USA",
        "city": None,
        "type": "online",
        "source": "scraper",
        "adapter": "total-wine",
        "home": "https://www.totalwine.com/",
        "productHost": "totalwine.com",
    },
]

DRINK_FILES = {
    "rum": "rums.json",
    "whisky": "whiskies.json",
    "brandy": "brandies.json",
    "wine": "wines.json",
    "coffee": "coffees.json",
    "tequila": "tequilas.json",
    "gin": "gins.json",
    "digestif": "digestifs.json",
}


def slug(label: str) -> str:
    s = unicodedata.normalize("NFKD", label)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[''`]", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_sorted(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")


def build_shops() -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for s in CIGAR_SHOPS + DRINK_SHOPS:
        existing = by_id.get(s["id"])
        if existing is None:
            by_id[s["id"]] = dict(s)
            continue
        # Union: prefer walkIn/both if either side is walkIn; keep productHost if any.
        if s.get("type") == "walkIn" or existing.get("type") == "walkIn":
            if existing.get("type") == "online" and s.get("type") == "walkIn":
                existing["type"] = "both"
            elif s.get("type") == "online" and existing.get("type") == "walkIn":
                existing["type"] = "both"
        if not existing.get("productHost") and s.get("productHost"):
            existing["productHost"] = s["productHost"]
        if not existing.get("city") and s.get("city"):
            existing["city"] = s["city"]
    shops = list(by_id.values())
    shops.sort(key=lambda x: (x["region"], x["id"]))
    return shops


def shop_by_name(shops: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {s["name"]: s for s in shops}


def shop_by_host(shops: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for s in shops:
        host = s.get("productHost")
        if host:
            out[host.lower()] = s
    # Holt's has no productHost but URLs use holts.com
    for s in shops:
        if s["id"] == "holts":
            out["holts.com"] = s
    return out


def host_of(url: str | None) -> str:
    if not url:
        return ""
    try:
        return urlparse(url).hostname.lower() or ""
    except Exception:
        return ""


def resolve_shop_for_url(
    url: str | None,
    shop_name: str | None,
    by_name: dict[str, dict[str, Any]],
    by_host: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    if shop_name and shop_name in by_name:
        return by_name[shop_name]
    h = host_of(url)
    if not h:
        return None
    for host, shop in by_host.items():
        if host in h:
            return shop
    return None


def resolve_drink_shop(
    drink: dict[str, Any],
    by_id: dict[str, dict[str, Any]],
    by_host: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    url = drink.get("priceUrl")
    h = host_of(url)
    if h:
        for host, shop in by_host.items():
            if host in h:
                return shop
    shop_hr = (drink.get("shopHR") or "").strip().lower()
    # Map common shopHR strings to ids
    aliases = {
        "allez.hr": "allez",
        "ecuga.com": "ecuga",
        "humidor.hr": "humidor",
        "drinx.hr": "drinx",
        "tipsy.hr": "tipsy",
        "cugaklik.hr": "cugaklik",
        "roto.hr": "roto",
        "vrutak.hr": "vrutak",
        "vivat": "vivat",
        "vivat fina vina": "vivat",
    }
    sid = aliases.get(shop_hr)
    if sid and sid in by_id:
        return by_id[sid]
    for s in by_id.values():
        if s["name"].lower() == shop_hr or (s.get("productHost") or "").lower() == shop_hr:
            return s
    return None


def offer_id(
    shop_id: str,
    product_id: str,
    vitola_id: str | None,
    url: str | None,
) -> str:
    key = "|".join(
        [
            shop_id,
            product_id,
            vitola_id or "",
            url or "",
        ]
    )
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]
    return f"off-{digest}"


def make_offer(
    *,
    shop: dict[str, Any],
    product_id: str,
    vitola_id: str | None,
    url: str | None,
    price_eur: float | None,
    fetched_at: str | None,
    in_stock: bool | None,
    source: str,
    match_confidence: float = 1.0,
) -> dict[str, Any]:
    is_walkin = shop.get("type") == "walkIn"
    # Walk-in offers must not carry a product URL (acceptance).
    if is_walkin:
        url = None
    fa = fetched_at if fetched_at else None
    valid_until = fa if fa else MIGRATION_DATE
    return {
        "id": offer_id(shop["id"], product_id, vitola_id, url),
        "shopId": shop["id"],
        "productId": product_id,
        "vitolaId": vitola_id,
        "url": url,
        "priceEUR": price_eur,
        "currency": "EUR",
        "packSize": None,
        "inStock": in_stock,
        "fetchedAt": fa,
        "validUntil": valid_until,
        "matchConfidence": match_confidence,
        "checkedStatus": None,
        "source": source,
    }


def dedupe_key(o: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        o["shopId"],
        o["productId"],
        o.get("vitolaId") or "",
        o.get("url") or "",
    )


def profile_source_from(obj: dict[str, Any]) -> str:
    if obj.get("profileEstimated"):
        return "estimated"
    if obj.get("strengthFromTasting") or obj.get("strengthFromShop"):
        return "measured"
    return "curated"


def notes_hr(obj: dict[str, Any]) -> str:
    notes = obj.get("notes") or {}
    if isinstance(notes, dict):
        hr = (notes.get("hr") or "").strip()
        if hr:
            return hr
    return "(nema opisa)"


def notes_en(obj: dict[str, Any]) -> str | None:
    notes = obj.get("notes") or {}
    if isinstance(notes, dict):
        en = (notes.get("en") or "").strip()
        return en or None
    return None


def migrate_cigars(
    cigars: list[dict[str, Any]],
    shops: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    by_name = shop_by_name(shops)
    by_host = shop_by_host(shops)
    products: list[dict[str, Any]] = []
    vitolas_out: list[dict[str, Any]] = []
    offers_map: dict[tuple[str, str, str, str], dict[str, Any]] = {}

    def add_offer(o: dict[str, Any]) -> None:
        k = dedupe_key(o)
        prev = offers_map.get(k)
        if prev is None:
            offers_map[k] = o
            return
        # Prefer richer price / fetchedAt
        if prev.get("priceEUR") is None and o.get("priceEUR") is not None:
            prev["priceEUR"] = o["priceEUR"]
        if prev.get("fetchedAt") is None and o.get("fetchedAt") is not None:
            prev["fetchedAt"] = o["fetchedAt"]
            prev["validUntil"] = o["validUntil"]
        if prev.get("inStock") is None and o.get("inStock") is not None:
            prev["inStock"] = o["inStock"]

    for c in cigars:
        pid = c["id"]
        products.append(
            {
                "id": pid,
                "kind": "cigar",
                "brand": c.get("brand") or "",
                "line": c.get("line") or "",
                "country": c.get("country") or None,
                "strength": c.get("strength"),
                "body": c.get("body"),
                "sweetness": None,
                "flavorTags": list(c.get("flavorTags") or []),
                "profileSource": profile_source_from(c),
                "description": {
                    "hr": notes_hr(c),
                    "en": notes_en(c),
                    "reviewedAt": None,
                },
            }
        )

        for v in c.get("vitolas") or []:
            vname = v.get("name") or ""
            vid = f"{pid}@{slug(vname)}" if vname else pid
            vitolas_out.append(
                {
                    "id": vid,
                    "productId": pid,
                    "name": vname,
                    "ring": v.get("ring"),
                    "lengthMM": v.get("lengthMM"),
                    "shape": v.get("shape"),
                    "smokeTimeMin": v.get("smokeTimeMin"),
                }
            )
            # vitola HR url / price
            if v.get("url") or v.get("priceEUR") is not None:
                shop = resolve_shop_for_url(
                    v.get("url"), None, by_name, by_host
                ) or by_name.get("The Humidor")
                if shop:
                    add_offer(
                        make_offer(
                            shop=shop,
                            product_id=pid,
                            vitola_id=vid,
                            url=v.get("url"),
                            price_eur=v.get("priceEUR"),
                            fetched_at=v.get("fetchedAt"),
                            in_stock=v.get("inStock"),
                            source="migrate:vitola",
                        )
                    )
            for region, link in (v.get("regionLinks") or {}).items():
                if region not in REGIONS or not isinstance(link, dict):
                    continue
                shop = resolve_shop_for_url(
                    link.get("url"), link.get("shop"), by_name, by_host
                )
                if not shop:
                    continue
                add_offer(
                    make_offer(
                        shop=shop,
                        product_id=pid,
                        vitola_id=vid,
                        url=link.get("url"),
                        price_eur=link.get("priceEUR"),
                        fetched_at=link.get("fetchedAt"),
                        in_stock=link.get("inStock"),
                        source=f"migrate:vitola.regionLinks.{region}",
                    )
                )

        # line-level priceUrl / priceEUR
        if c.get("priceUrl") or c.get("priceEUR") is not None:
            shop = resolve_shop_for_url(
                c.get("priceUrl"), None, by_name, by_host
            )
            if shop:
                add_offer(
                    make_offer(
                        shop=shop,
                        product_id=pid,
                        vitola_id=None,
                        url=c.get("priceUrl"),
                        price_eur=c.get("priceEUR"),
                        fetched_at=None,
                        in_stock=c.get("inStock"),
                        source="migrate:line.price",
                    )
                )

        for region, link in (c.get("regionLinks") or {}).items():
            if region not in REGIONS or not isinstance(link, dict):
                continue
            shop = resolve_shop_for_url(
                link.get("url"), link.get("shop"), by_name, by_host
            )
            if not shop:
                continue
            add_offer(
                make_offer(
                    shop=shop,
                    product_id=pid,
                    vitola_id=None,
                    url=link.get("url"),
                    price_eur=link.get("priceEUR"),
                    fetched_at=link.get("fetchedAt"),
                    in_stock=link.get("inStock"),
                    source=f"migrate:line.regionLinks.{region}",
                )
            )

        # availabilityHR without a product URL → offer with no url (shelf / walk-in style).
        for name in c.get("availabilityHR") or []:
            shop = by_name.get(name)
            if not shop:
                continue
            has_url_offer = any(
                o["shopId"] == shop["id"]
                and o["productId"] == pid
                and o.get("url")
                for o in offers_map.values()
            )
            if has_url_offer:
                continue
            add_offer(
                make_offer(
                    shop=shop,
                    product_id=pid,
                    vitola_id=None,
                    url=None,
                    price_eur=None,
                    fetched_at=None,
                    in_stock=None,
                    source="migrate:availabilityHR",
                    match_confidence=0.8,
                )
            )

    products.sort(key=lambda p: p["id"])
    vitolas_out.sort(key=lambda v: v["id"])
    offers = sorted(offers_map.values(), key=lambda o: o["id"])
    return products, vitolas_out, offers


def migrate_drinks(
    drinks: list[tuple[str, dict[str, Any]]],
    shops: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_id = {s["id"]: s for s in shops}
    by_host = shop_by_host(shops)
    products: list[dict[str, Any]] = []
    offers_map: dict[tuple[str, str, str, str], dict[str, Any]] = {}

    def add_offer(o: dict[str, Any]) -> None:
        k = dedupe_key(o)
        if k not in offers_map:
            offers_map[k] = o

    for kind, d in drinks:
        pid = d["id"]
        brand = ""
        line = d.get("name") or ""
        # Prefer explicit brand from name heuristics later; keep name as line.
        products.append(
            {
                "id": pid,
                "kind": kind,
                "brand": brand or (d.get("style") or ""),
                "line": line,
                "country": d.get("country") or d.get("region") or None,
                "strength": None,
                "body": d.get("body"),
                "sweetness": d.get("sweetness"),
                "flavorTags": list(d.get("flavorTags") or []),
                "profileSource": "estimated" if d.get("profileEstimated") else "curated",
                "description": {
                    "hr": notes_hr(d),
                    "en": notes_en(d),
                    "reviewedAt": None,
                },
            }
        )
        price = d.get("priceEUR")
        price_num = None
        if isinstance(price, dict) and price.get("min") is not None:
            price_num = price["min"]
        elif isinstance(price, (int, float)):
            price_num = float(price)

        shop = resolve_drink_shop(d, by_id, by_host)
        if shop and (d.get("priceUrl") or price_num is not None):
            add_offer(
                make_offer(
                    shop=shop,
                    product_id=pid,
                    vitola_id=None,
                    url=d.get("priceUrl"),
                    price_eur=price_num,
                    fetched_at=None,
                    in_stock=d.get("inStock"),
                    source="migrate:drink",
                )
            )

    products.sort(key=lambda p: p["id"])
    offers = sorted(offers_map.values(), key=lambda o: o["id"])
    return products, offers


def run() -> dict[str, int]:
    shops = build_shops()
    cigars_raw = load_json(DATA / "cigars.json")
    if not isinstance(cigars_raw, list):
        raise SystemExit("cigars.json must be a list")

    # Dedupe cigars by id (same as index.ts richness heuristic — keep first after sort by id)
    best: dict[str, dict[str, Any]] = {}
    for c in cigars_raw:
        cid = c.get("id")
        if not cid:
            continue
        prev = best.get(cid)
        richness = len(c.get("vitolas") or []) * 10 + len(c.get("flavorTags") or [])
        if prev is None:
            best[cid] = c
        else:
            prev_r = len(prev.get("vitolas") or []) * 10 + len(prev.get("flavorTags") or [])
            if richness > prev_r:
                best[cid] = c
    cigars = list(best.values())

    c_products, vitolas, c_offers = migrate_cigars(cigars, shops)

    drink_pairs: list[tuple[str, dict[str, Any]]] = []
    for kind, fname in DRINK_FILES.items():
        rows = load_json(DATA / fname)
        if not isinstance(rows, list):
            raise SystemExit(f"{fname} must be a list")
        for d in rows:
            drink_pairs.append((kind, d))

    d_products, d_offers = migrate_drinks(drink_pairs, shops)

    products = sorted(c_products + d_products, key=lambda p: p["id"])
    # Merge offers with dedupe
    offers_map: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for o in c_offers + d_offers:
        k = dedupe_key(o)
        if k not in offers_map:
            offers_map[k] = o
    offers = sorted(offers_map.values(), key=lambda o: o["id"])

    dump_sorted(OUT / "shops.json", shops)
    dump_sorted(OUT / "products.json", products)
    dump_sorted(OUT / "vitolas.json", vitolas)
    dump_sorted(OUT / "offers.json", offers)

    expired = sum(1 for o in offers if o.get("fetchedAt") is None)
    return {
        "products": len(products),
        "vitolas": len(vitolas),
        "shops": len(shops),
        "offers": len(offers),
        "expiredOffers": expired,
    }


def main(argv: list[str] | None = None) -> int:
    counts = run()
    print(json.dumps(counts, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
