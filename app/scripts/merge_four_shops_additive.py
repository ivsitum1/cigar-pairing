#!/usr/bin/env python3
"""Additive merge of four-shop offers into cigars.json.

Hard rules:
- never delete cigars / vitolas / existing URLs
- never overwrite existing regionLinks[region] URL (unless --refresh-prices for price fields only)
- secondary shop → vitola.url or vitola.regionLinks
- Cuban origin → never USA
- idempotent: re-run skips already-present URLs
- --refresh-prices: update priceEUR/priceApprox on matching shop/URL; do not change URL; no new lines

Offer schema (raw JSON list):
  {
    "sourceShopId": "famous_smoke_us"|"neptune_us"|"cgars_uk"|"la_couronne_ch",
    "brand": str, "line": str, "vitola": str|null,
    "ring": int|null, "lengthMM": int|null,
    "amount": float|null, "currency": "USD"|"EUR"|"GBP"|"CHF",
    "url": str, "country": str|null, "wrapper": str|null,
    "inStock": bool|null
  }
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from shop_common import SHOP_LABEL, SHOP_REGION, is_cuban, slug, sort_key, to_eur

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
CIGARS = DATA / "cigars.json"
BRANDS = DATA / "brands.json"
OUT = HERE / "output"
LEDGER = OUT / "four_shops_ledger.jsonl"
HOLD = OUT / "four_shops_hold.json"

COUNTRY_HR = {
    "nicaragua": "Nikaragva",
    "dominican republic": "Dominikanska Republika",
    "dominicana": "Dominikanska Republika",
    "honduras": "Honduras",
    "cuba": "Kuba",
    "mexico": "Meksiko",
    "usa": "SAD",
    "united states": "SAD",
    "brazil": "Brazil",
    "ecuador": "Ekvador",
    "costa rica": "Kostarika",
    "panama": "Panama",
    "peru": "Peru",
    "indonesia": "Indonezija",
    "cameroon": "Kamerun",
    "switzerland": "Švicarska",
}

COUNTRY_EN = {
    "Nikaragva": "Nicaragua",
    "Dominikanska Republika": "Dominican Republic",
    "Honduras": "Honduras",
    "Kuba": "Cuba",
    "Meksiko": "Mexico",
    "SAD": "USA",
    "Brazil": "Brazil",
    "Ekvador": "Ecuador",
    "Kostarika": "Costa Rica",
    "Panama": "Panama",
    "Peru": "Peru",
    "Indonezija": "Indonesia",
    "Kamerun": "Cameroon",
    "Švicarska": "Switzerland",
}

# Cuban Habanos brands — non-Cuban lines must use \"(NW)\" brand suffix
HABANOS_BRANDS = {
    "Cohiba",
    "Montecristo",
    "Partagás",
    "Romeo y Julieta",
    "Hoyo de Monterrey",
    "H. Upmann",
    "Bolívar",
    "Punch",
    "Trinidad",
    "Ramón Allones",
    "Quintero",
    "Cuaba",
    "San Cristóbal de la Habana",
    "Vegas Robaina",
    "Juan López",
    "Fonseca",
    "Quai d'Orsay",
    "José L. Piedra",
    "Vegueros",
}


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, obj) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def country_hr(raw: str | None) -> str | None:
    if not raw:
        return None
    return COUNTRY_HR.get(raw.strip().lower()) or (
        raw if re.search(r"[čćžšđ]", raw, re.I) else None
    )


def parse_ring_len(text: str) -> tuple[int | None, int | None]:
    """Parse '5" x 50' / '5x50' / '50 x 127mm'."""
    t = text or ""
    m = re.search(
        r'(\d+)\s+(\d+)/(\d+)\s*(?:"|in|″)?\s*[x×*]\s*(\d{2,3})\b',
        t,
        re.I,
    )
    if m:
        inches = int(m.group(1)) + int(m.group(2)) / int(m.group(3))
        return int(m.group(4)), int(round(inches * 25.4))
    m = re.search(
        r'(\d+(?:\.\d+)?)\s*(?:"|in|″)?\s*[x×*]\s*(\d{2,3})\b',
        t,
        re.I,
    )
    if m:
        inches = float(m.group(1).replace(",", "."))
        return int(m.group(2)), int(round(inches * 25.4))
    m = re.search(r"(\d{2,3})\s*[x×]\s*(\d{2,3})\s*mm", t, re.I)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        # ring is usually smaller (40-70), length mm larger
        if a < 80 and b >= 80:
            return a, b
        if b < 80 and a >= 80:
            return b, a
    return None, None


def cigar_urls(c: dict) -> set[str]:
    urls: set[str] = set()
    for link in (c.get("regionLinks") or {}).values():
        if link.get("url"):
            urls.add(link["url"])
    if c.get("priceUrl"):
        urls.add(c["priceUrl"])
    for v in c.get("vitolas") or []:
        if v.get("url"):
            urls.add(v["url"])
        for link in (v.get("regionLinks") or {}).values():
            if link.get("url"):
                urls.add(link["url"])
    return urls


def build_indexes(cigars: list[dict]):
    by_brand: dict[str, list[dict]] = {}
    exact: dict[tuple[str, str], dict] = {}
    for c in cigars:
        bs = slug(c.get("brand", ""))
        ls = slug(c.get("line", ""))
        by_brand.setdefault(bs, []).append(c)
        exact[(bs, ls)] = c
    return by_brand, exact


def find_line(by_brand, exact, brand: str, line: str) -> dict | None:
    bs, ls = slug(brand), slug(line)
    if (bs, ls) in exact:
        return exact[(bs, ls)]
    for c in by_brand.get(bs, []):
        cl = slug(c.get("line", ""))
        if ls and (ls in cl or cl in ls):
            return c
    return None


def find_vitola(c: dict, name: str | None, ring: int | None, length_mm: int | None):
    vitolas = c.get("vitolas") or []
    if name:
        ns = slug(name)
        for v in vitolas:
            if slug(v.get("name") or "") == ns:
                return v
            if slug(v.get("shape") or "") == ns:
                return v
    if ring is not None and length_mm is not None:
        for v in vitolas:
            vr = v.get("ring")
            vl = v.get("lengthMM")
            if vr is None or vl is None:
                # try format "50 x 127mm"
                fr, fl = parse_ring_len(v.get("format") or "")
                vr = vr if vr is not None else fr
                vl = vl if vl is not None else fl
            if vr is None or vl is None:
                continue
            if abs(int(vr) - ring) <= 1 and abs(int(vl) - length_mm) <= 2:
                return v
    return None


def append_ledger(row: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def link_entry(offer: dict) -> dict:
    shop = SHOP_LABEL[offer["sourceShopId"]]
    price, approx = to_eur(offer.get("amount"), offer.get("currency") or "USD")
    e: dict = {"shop": shop, "url": offer["url"]}
    if price is not None:
        e["priceEUR"] = price
        if approx or (offer.get("currency") or "").upper() in ("USD", "GBP", "CHF"):
            # GBP/CHF also approximate vs EUR
            if (offer.get("currency") or "").upper() != "EUR":
                e["priceApprox"] = True
            elif approx:
                e["priceApprox"] = True
    return e


def _host(url: str) -> str:
    return re.sub(r"^www\.", "", re.sub(r"^https?://", "", (url or "").split("/")[0].lower()))


def refresh_prices_on_cigar(c: dict, offer: dict) -> str:
    """Update priceEUR on existing regionLinks / vitola links matching shop or URL host.

    Returns: price_updated | skipped_no_price | skipped_no_match
    """
    region = SHOP_REGION[offer["sourceShopId"]]
    shop = SHOP_LABEL[offer["sourceShopId"]]
    offer_url = offer.get("url") or ""
    offer_host = _host(offer_url)
    price, approx = to_eur(offer.get("amount"), offer.get("currency") or "USD")
    if price is None:
        return "skipped_no_price"

    def patch(entry: dict) -> bool:
        if not isinstance(entry, dict):
            return False
        same_shop = (entry.get("shop") or "") == shop
        same_host = offer_host and _host(entry.get("url") or "") == offer_host
        same_url = offer_url and (entry.get("url") or "") == offer_url
        if not (same_shop or same_host or same_url):
            return False
        changed = entry.get("priceEUR") != price
        entry["priceEUR"] = price
        if approx or (offer.get("currency") or "").upper() != "EUR":
            entry["priceApprox"] = True
        elif "priceApprox" in entry and (offer.get("currency") or "").upper() == "EUR":
            entry.pop("priceApprox", None)
        return changed

    updated = False
    rl = dict(c.get("regionLinks") or {})
    if region in rl and patch(rl[region]):
        c["regionLinks"] = rl
        updated = True
    for v in c.get("vitolas") or []:
        vrl = dict(v.get("regionLinks") or {})
        if region in vrl and patch(vrl[region]):
            v["regionLinks"] = vrl
            updated = True
        # vitola primary url on same host
        if offer_host and _host(v.get("url") or "") == offer_host and v.get("priceEUR") != price:
            v["priceEUR"] = price
            updated = True
    return "price_updated" if updated else "skipped_no_match"


def ensure_market(c: dict, region: str) -> None:
    markets = list(c.get("markets") or [])
    changed = False
    if region not in markets:
        markets.append(region)
        changed = True
    if "WW" not in markets:
        markets.append("WW")
        changed = True
    if changed:
        # stable order
        order = ["HR", "EU", "USA", "WW"]
        c["markets"] = [m for m in order if m in markets] + [
            m for m in markets if m not in order
        ]


def add_link_to_cigar(c: dict, offer: dict, vitola_name: str | None) -> str:
    """Return action: link_added | skipped_dup | skipped_embargo."""
    region = SHOP_REGION[offer["sourceShopId"]]
    url = offer["url"]
    if url in cigar_urls(c):
        return "skipped_dup"
    cuban = is_cuban(c.get("country")) or is_cuban(offer.get("country"))
    if region == "USA" and cuban:
        return "skipped_embargo"

    ensure_market(c, region)
    entry = link_entry(offer)

    # Prefer attaching to matching vitola
    ring = offer.get("ring")
    length_mm = offer.get("lengthMM")
    if (ring is None or length_mm is None) and vitola_name:
        r2, l2 = parse_ring_len(vitola_name)
        ring = ring if ring is not None else r2
        length_mm = length_mm if length_mm is not None else l2
    v = find_vitola(c, vitola_name or offer.get("vitola"), ring, length_mm)

    if v is not None:
        # secondary URL on vitola
        if not v.get("url"):
            v["url"] = url
        else:
            vrl = dict(v.get("regionLinks") or {})
            if region not in vrl:
                vrl[region] = entry
                v["regionLinks"] = vrl
            elif vrl[region].get("url") != url:
                # already has region link — put Famous/secondary on url if host differs
                if url not in (v.get("url") or "") and offer["sourceShopId"] in (
                    "famous_smoke_us",
                    "cgars_uk",
                    "la_couronne_ch",
                    "neptune_us",
                ):
                    # keep existing url; store alt in regionLinks only if absent shop
                    # if same region taken, leave as sourceUrls on cigar
                    src = list(c.get("sourceUrls") or [])
                    if url not in src:
                        src.append(url)
                        c["sourceUrls"] = src
        # fill line-level regionLinks only if absent
        rl = dict(c.get("regionLinks") or {})
        if region not in rl:
            rl[region] = entry
            c["regionLinks"] = rl
        return "link_added"

    # no vitola match — line-level
    rl = dict(c.get("regionLinks") or {})
    if region not in rl:
        rl[region] = entry
        c["regionLinks"] = rl
        return "link_added"
    # region already has primary — append sourceUrls + try first vitola.url empty
    src = list(c.get("sourceUrls") or [])
    if url not in src:
        src.append(url)
        c["sourceUrls"] = src
    vitolas = c.get("vitolas") or []
    if vitolas:
        v0 = vitolas[0]
        host = re.sub(r"^www\.", "", re.sub(r"^https?://", "", url).split("/")[0].lower())
        if not v0.get("url"):
            v0["url"] = url
        elif host not in (v0.get("url") or ""):
            vrl = dict(v0.get("regionLinks") or {})
            if region not in vrl:
                vrl[region] = entry
                v0["regionLinks"] = vrl
    return "link_added"


def create_cigar(offer: dict, brands: dict, brand_country: dict[str, str] | None = None) -> dict | None:
    brand = (offer.get("brand") or "").strip()
    line = (offer.get("line") or "").strip()
    vitola = (offer.get("vitola") or "Robusto").strip()
    if not brand or not line:
        return None
    country = country_hr(offer.get("country")) or (brand_country or {}).get(brand)
    if not country:
        return None
    # Non-Cuban lines under Habanos names → New World brand
    if brand in HABANOS_BRANDS and not is_cuban(country):
        brand = f"{brand} (NW)"
    ring = offer.get("ring")
    length_mm = offer.get("lengthMM")
    if ring is None or length_mm is None:
        r2, l2 = parse_ring_len(f"{vitola} {offer.get('format') or ''}")
        ring = ring if ring is not None else r2
        length_mm = length_mm if length_mm is not None else l2
    # vitola lexicon midpoints for common shapes
    if ring is None or length_mm is None:
        mids = {
            "robusto": (50, 124),
            "toro": (52, 152),
            "churchill": (47, 178),
            "corona": (42, 140),
            "gordo": (60, 152),
            "belicoso": (52, 152),
            "torpedo": (52, 156),
            "lancero": (38, 190),
            "lonsdale": (42, 165),
        }
        mid = mids.get(vitola.lower())
        if mid:
            ring = ring if ring is not None else mid[0]
            length_mm = length_mm if length_mm is not None else mid[1]
    if ring is None or length_mm is None:
        return None
    price, approx = to_eur(offer.get("amount"), offer.get("currency") or "USD")
    region = SHOP_REGION[offer["sourceShopId"]]
    if region == "USA" and is_cuban(country):
        return None
    cid = f"cig-{slug(brand)}-{slug(line)}"
    # avoid colliding with wildly different existing ids — caller checks by_id
    fmt = f"{ring} x {length_mm}mm"
    entry = link_entry(offer)
    wrapper = offer.get("wrapper") or "—"
    country_en = COUNTRY_EN.get(country, country)
    note = {
        "hr": f"{country} — linija iz trgovine {SHOP_LABEL[offer['sourceShopId']]}.",
        "en": f"{country_en} — line from {SHOP_LABEL[offer['sourceShopId']]}.",
    }
    cig = {
        "id": cid,
        "brand": brand,
        "line": line,
        "vitola": vitola,
        "format": fmt,
        "country": country,
        "wrapper": wrapper,
        "strength": 3,
        "body": 3,
        "flavorTags": [],
        "profileEstimated": True,
        "formatEstimated": True,
        "smokeTimeMin": max(30, int(round(length_mm / 127 * 60))),
        "priceEUR": price if region == "HR" else None,
        "priceUrl": None,
        "vitolas": [
            {
                "name": vitola,
                "format": fmt,
                "smokeTimeMin": max(30, int(round(length_mm / 127 * 60))),
                "priceEUR": None,
                "url": offer["url"],
                "shape": vitola
                if vitola.lower()
                in {
                    "robusto",
                    "toro",
                    "churchill",
                    "corona",
                    "gordo",
                    "belicoso",
                    "torpedo",
                    "lancero",
                }
                else None,
                "ring": ring,
                "lengthMM": length_mm,
                "regionLinks": {region: entry},
            }
        ],
        "markets": [region, "WW"] if region != "WW" else ["WW"],
        "regionLinks": {region: entry},
        "catalogSource": "market",
        "availabilityHR": [],
        "notes": note,
        "sourceUrls": [offer["url"]],
    }
    if approx or (price is not None and (offer.get("currency") or "").upper() != "EUR"):
        cig["priceApprox"] = True
    if brand not in brands:
        brands[brand] = {
            "country": country,
            "founded": "—",
            "blurb": {
                "hr": f"Marka iz kataloga trgovina ({SHOP_LABEL[offer['sourceShopId']]}).",
                "en": f"Brand from shop catalogue ({SHOP_LABEL[offer['sourceShopId']]}).",
            },
        }
    return cig


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--offers",
        nargs="+",
        required=True,
        help="One or more raw offer JSON files (list of offers)",
    )
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--admit-new", action="store_true", help="Create new lines for unmatched offers")
    ap.add_argument(
        "--refresh-prices",
        action="store_true",
        help="Update priceEUR on existing regionLinks for matching shop/URL; never change URL or admit new",
    )
    args = ap.parse_args()
    if args.refresh_prices and args.admit_new:
        raise SystemExit("--refresh-prices cannot be combined with --admit-new")

    cigars = load(CIGARS)
    brands = load(BRANDS)
    by_id = {c["id"]: c for c in cigars}
    by_brand, exact = build_indexes(cigars)
    brand_country: dict[str, str] = {}
    for c in cigars:
        if c.get("country"):
            brand_country.setdefault(c["brand"], c["country"])
    held = []
    held_reasons: dict[str, int] = {}
    stats = {
        "offers": 0,
        "link_added": 0,
        "line_created": 0,
        "skipped_dup": 0,
        "skipped_embargo": 0,
        "no_match": 0,
        "held": 0,
        "price_updated": 0,
        "skipped_no_price": 0,
        "skipped_no_match": 0,
    }
    ts = datetime.now(timezone.utc).isoformat()

    offers: list[dict] = []
    for path in args.offers:
        p = Path(path)
        raw = load(p)
        if isinstance(raw, dict) and "offers" in raw:
            offers.extend(raw["offers"])
        elif isinstance(raw, list):
            offers.extend(raw)
        else:
            raise SystemExit(f"Unknown offer format: {p}")

    # Enrich offers missing country from brand majority in catalog
    for o in offers:
        if not o.get("country") and o.get("brand") in brand_country:
            o["country"] = brand_country[o["brand"]]

    print(f"merging {len(offers)} offers into {len(cigars)} cigars...", flush=True)
    for i, offer in enumerate(offers, 1):
        if i % 500 == 0:
            print(
                f"  ... {i}/{len(offers)} link_added={stats['link_added']} new={stats['line_created']}",
                flush=True,
            )
        stats["offers"] += 1
        sid = offer.get("sourceShopId")
        if sid not in SHOP_LABEL:
            held_reasons["bad_shop"] = held_reasons.get("bad_shop", 0) + 1
            stats["held"] += 1
            continue
        if not offer.get("url"):
            held_reasons["no_url"] = held_reasons.get("no_url", 0) + 1
            stats["held"] += 1
            continue
        brand = (offer.get("brand") or "").strip()
        line = (offer.get("line") or "").strip()
        if not brand or not line:
            held_reasons["no_brand_line"] = held_reasons.get("no_brand_line", 0) + 1
            stats["held"] += 1
            continue

        existing = find_line(by_brand, exact, brand, line)
        if existing:
            if args.refresh_prices:
                action = refresh_prices_on_cigar(existing, offer)
                stats[action] = stats.get(action, 0) + 1
                if action == "price_updated":
                    append_ledger(
                        {
                            "ts": ts,
                            "action": "price_updated",
                            "cigarId": existing["id"],
                            "shop": SHOP_LABEL[sid],
                            "url": offer["url"],
                            "brand": brand,
                            "line": line,
                            "amount": offer.get("amount"),
                            "currency": offer.get("currency"),
                        }
                    )
                continue
            action = add_link_to_cigar(existing, offer, offer.get("vitola"))
            stats[action] = stats.get(action, 0) + 1
            if action == "link_added":
                append_ledger(
                    {
                        "ts": ts,
                        "action": "link_added",
                        "cigarId": existing["id"],
                        "shop": SHOP_LABEL[sid],
                        "url": offer["url"],
                        "brand": brand,
                        "line": line,
                    }
                )
            continue

        if args.refresh_prices or not args.admit_new:
            stats["no_match"] += 1
            held_reasons["no_match"] = held_reasons.get("no_match", 0) + 1
            if len(held) < 200:
                held.append({"reason": "no_match", "brand": brand, "line": line, "url": offer["url"]})
            continue

        new_c = create_cigar(offer, brands, brand_country)
        if not new_c:
            held_reasons["quality_gate"] = held_reasons.get("quality_gate", 0) + 1
            stats["held"] += 1
            if len(held) < 200:
                held.append(
                    {
                        "reason": "quality_gate",
                        "brand": brand,
                        "line": line,
                        "url": offer["url"],
                    }
                )
            continue
        if new_c["id"] in by_id:
            action = add_link_to_cigar(by_id[new_c["id"]], offer, offer.get("vitola"))
            stats[action] = stats.get(action, 0) + 1
            if action == "link_added":
                append_ledger(
                    {
                        "ts": ts,
                        "action": "link_added",
                        "cigarId": new_c["id"],
                        "shop": SHOP_LABEL[sid],
                        "url": offer["url"],
                    }
                )
            continue
        cigars.append(new_c)
        by_id[new_c["id"]] = new_c
        bs, ls = slug(new_c["brand"]), slug(new_c["line"])
        by_brand.setdefault(bs, []).append(new_c)
        exact[(bs, ls)] = new_c
        brand_country.setdefault(new_c["brand"], new_c["country"])
        stats["line_created"] += 1
        append_ledger(
            {
                "ts": ts,
                "action": "line_created",
                "cigarId": new_c["id"],
                "shop": SHOP_LABEL[sid],
                "url": offer["url"],
                "brand": brand,
                "line": line,
            }
        )

    cigars.sort(key=sort_key)
    dump(HOLD, {"held_sample": held, "held_reasons": held_reasons, "count": stats["held"] + stats["no_match"]})
    print(json.dumps(stats, indent=2), flush=True)
    print(f"hold_reasons={held_reasons} -> {HOLD}", flush=True)
    if args.dry_run:
        print("dry-run: not writing cigars.json / brands.json", flush=True)
        return
    dump(CIGARS, cigars)
    dump(BRANDS, brands)
    print(f"wrote {CIGARS} ({len(cigars)} cigars)", flush=True)


if __name__ == "__main__":
    main()
