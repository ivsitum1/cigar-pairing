#!/usr/bin/env python3
"""Phase B/C: build new market cigars from the unified shop catalog.

Deterministic + idempotent (playbook §0): every run drops previously generated
entries (catalogSource=="market") from cigars.json, regenerates them from the
pinned unified catalog, merges, sorts, writes. Same input + same args => byte
identical cigars.json regardless of who runs it (Claude or Cursor).

See docs/superpowers/plans/2026-07-21-phase-b-c-execution-playbook.md
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

from shop_common import (
    REGIONS, SHOP_LABEL, best_offer, is_cuban, slug, sort_key, to_eur,
)
import importlib.util


def _load_enrich():
    """Reuse profile-cigars.py enrich() heuristic (strength/body/wrapper/flavorTags)."""
    spec = importlib.util.spec_from_file_location("profile_cigars", HERE / "profile-cigars.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.enrich

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
DATADIR = HERE / "data"
CIGARS = DATA / "cigars.json"
BRANDS = DATA / "brands.json"
UNIFIED = HERE / "output" / "cigar_unified_catalog.json"
HOLD = HERE / "output" / "phase_hold.json"

INPUT_SHA256 = "2a2c080ffb23efa4e7088cf466bc49bad689884ddc3477119add42e74e13d44c"

# Kubanske (Habanos) marke: kurirane su u appu s tvrdim invarijantama
# (country=Kuba, kubanski wrapper). Strane trgovine uglavnom drže ne-kubanske
# imenjake ("(NW)") ili grey-market — zato ih ovaj pipeline NE dira.
HABANOS = {
    "Cohiba", "Montecristo", "Partagás", "Romeo y Julieta", "Hoyo de Monterrey",
    "H. Upmann", "Bolívar", "Punch", "Trinidad", "Ramón Allones", "Quintero",
    "Cuaba", "San Cristóbal de la Habana", "Vegas Robaina", "Juan López",
    "Fonseca", "Quai d'Orsay", "José L. Piedra", "Vegueros",
}

COUNTRY_HR = {
    "nicaragua": "Nikaragva", "dominican republic": "Dominikanska Republika",
    "honduras": "Honduras", "cuba": "Kuba", "mexico": "Meksiko", "usa": "SAD",
    "united states": "SAD", "brazil": "Brazil", "ecuador": "Ekvador",
    "costa rica": "Kostarika", "panama": "Panama", "peru": "Peru",
    "colombia": "Kolumbija", "switzerland": "Švicarska", "belgium": "Belgija",
    "dominikanska republika": "Dominikanska Republika", "kuba": "Kuba",
}

DIM_RE = re.compile(r"\b\d+(?:[.,]\d+)?\s*[x×]\s*\d+(?:[.,]\d+)?\b|\b\d+(?:[.,]\d+)?\s*(?:mm|cm|\")\b|\b#\d+\b", re.I)


def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def write_json(p, obj):
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def length_mm(det):
    if det.get("lengthIn"):
        return round(det["lengthIn"] * 25.4)
    if det.get("lengthCm"):
        return round(det["lengthCm"] * 10)
    return None


def load_vitola_lexicon():
    lex = load_json(DATADIR / "vitola_lexicon.json")["vitolas"]
    # (canonical, synonym) sorted by synonym length desc for longest-match
    syns = []
    for canon, info in lex.items():
        for s in info["syn"]:
            syns.append((s.lower(), canon))
    syns.sort(key=lambda x: -len(x[0]))
    return syns


def match_vitola(text, syns):
    t = f" {re.sub(r'[^a-z0-9]+', ' ', (text or '').lower())} "
    for s, canon in syns:
        if f" {s} " in t:
            return canon
    return None


def _clean(s):
    s = re.sub(r"\([^)]*\)|\[[^\]]*\]", " ", s)      # sadržaj u zagradama
    s = re.sub(r"[()\[\]{}]", " ", s)                # zaostali fragmenti zagrada
    # pakiranje/šum kao zasebne riječi
    s = re.sub(r"\b(tube|tubes|tubos|bundle|pack|count|tin|sampler|gift|box|assortment)\b", " ", s, flags=re.I)
    s = re.sub(r"\bgran\s*$", " ", s, flags=re.I)    # dangling "Gran" (od "Gran Toro/Belicoso")
    s = re.sub(r"\bby\b\s*$", " ", s, flags=re.I)    # dangling "by" (maker već maknut)
    s = re.sub(r"\s{2,}", " ", s)
    return s.strip(" -–—·,/")


def canon_line(brand, name, vitola, syns, line_map):
    base = name or ""
    raw = base.strip()
    # makni brend gdje god se pojavi kao cjelina (i vodeći i u kolaboracijama)
    base = re.sub(re.escape(brand), " ", base, flags=re.I)
    # remove dimension tokens
    base = DIM_RE.sub(" ", base)
    # remove the matched vitola synonyms (samo za prepoznatu vitolu)
    for s, canon in syns:
        if canon == vitola:
            base = re.sub(rf"\b{re.escape(s)}\b", " ", base, flags=re.I)
    # remove modifiers noise
    base = re.sub(r"\b(box[- ]?pressed|tubos?|single|cigar|the)\b", " ", base, flags=re.I)
    line = _clean(base)
    # override map wins
    ov = line_map.get(f"{brand}::{raw}") or line_map.get(f"{brand}::{line}")
    if ov:
        return ov
    return line or vitola  # jednolinijski brend: linija = vitola fallback


def region_links(offers, cuban):
    by = {}
    for o in offers:
        by.setdefault(o.get("region"), []).append(o)
    links = {}
    for region in REGIONS:
        if region == "USA" and cuban:
            continue
        offs = by.get(region)
        if not offs:
            continue
        o = best_offer(offs)
        if not o or not o.get("url"):
            continue
        price, approx = to_eur(o.get("amount"), o.get("currency"))
        e = {"shop": SHOP_LABEL.get(o.get("sourceShopId"), o.get("sourceShopId")), "url": o["url"]}
        if price is not None:
            e["priceEUR"] = price
            if approx:
                e["priceApprox"] = True
        links[region] = e
    return links


def build():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["b", "c", "all"], default="b")
    ap.add_argument("--brands", default="", help="comma list; empty = all eligible for phase")
    ap.add_argument("--check-input-sha", action="store_true")
    ap.add_argument("--list-brands", action="store_true")
    args = ap.parse_args()

    if args.check_input_sha:
        got = hashlib.sha256(UNIFIED.read_bytes()).hexdigest()
        if got != INPUT_SHA256:
            raise SystemExit(f"INPUT SHA MISMATCH: {got} != {INPUT_SHA256} — STOP")

    unified = load_json(UNIFIED)["cigars"]
    all_cigars = load_json(CIGARS)
    base = [c for c in all_cigars if c.get("catalogSource") != "market"]  # idempotent
    known_brands = set(load_json(BRANDS).keys())
    syns = load_vitola_lexicon()
    line_map = load_json(DATADIR / "line_map.json")["map"]
    brand_dict = {}
    bd = DATADIR / "brand_dictionary.json"
    if bd.exists():
        brand_dict = {k: v for k, v in load_json(bd).items() if not k.startswith("_")}
    enrich = _load_enrich()

    # Kurirane linije se NE diraju: market unos ne smije dijeliti (brend, linija)
    # s postojećom kuriranom linijom (te "dodatne vitole" su zaseban korak §10).
    exist_brand_line = set()
    for c in base:
        exist_brand_line.add((c["brand"].lower(), c["line"].lower()))

    # pool for the phase
    pool = []
    for r in unified:
        if r.get("inCatalog"):
            continue
        b = r.get("brand")
        if args.phase in ("b", "all") and b and b in known_brands:
            pool.append((b, r))
        elif args.phase in ("c", "all") and not b:
            # phase C: resolve brand via dictionary (from any offer url slug)
            pass  # C se radi tek kad postoji brand_dictionary (Cursor)

    if args.list_brands:
        import collections
        cnt = collections.Counter(b for b, _ in pool)
        for b, n in cnt.most_common():
            print(f"{n:4d}  {b}")
        return

    wanted = {x.strip() for x in args.brands.split(",") if x.strip()}
    if wanted:
        pool = [(b, r) for (b, r) in pool if b in wanted]

    # Grupiranje po (brend, linija) -> jedna cigara s više vitola.
    lines = {}   # (brand, line) -> aggregate
    hold = []
    stats = {"seen": len(pool), "admitted_records": 0, "lines": 0, "held": 0, "by_reason": {}}

    def rej(reason, r):
        stats["by_reason"][reason] = stats["by_reason"].get(reason, 0) + 1
        hold.append({"reason": reason, "name": r.get("name"), "brand": r.get("brand")})

    for b, r in pool:
        if b in HABANOS:
            rej("habanos_brand_skip", r); continue
        det = r.get("details") or {}
        cuban = is_cuban(r.get("country") or det.get("origin"))
        vit = match_vitola(r.get("vitola") or r.get("name") or "", syns) or match_vitola(det.get("size") or "", syns)
        if not vit:
            rej("no_vitola", r); continue
        ring = det.get("ringGauge")
        lmm = length_mm(det)
        if not ring or not lmm:
            rej("no_format", r); continue
        offers = [o for o in (r.get("offers") or [])]
        if not any(o.get("amount") is not None for o in offers):
            rej("no_price", r); continue
        cen = (r.get("country") or det.get("origin") or "").strip()
        country = COUNTRY_HR.get(cen.lower())
        if not country:
            rej("unknown_country", r); continue
        line = canon_line(b, r.get("name"), vit, syns, line_map)
        if (b.lower(), line.lower()) in exist_brand_line:
            rej("existing_line", r); continue
        stats["admitted_records"] += 1
        agg = lines.get((b, line))
        if agg is None:
            agg = {"brand": b, "line": line, "country": country, "cuban": cuban,
                   "wrappers": {}, "boxpressed": False, "offers": [], "urls": set(),
                   "vitolas": {}}
            lines[(b, line)] = agg
        agg["boxpressed"] = agg["boxpressed"] or bool(det.get("boxPressed"))
        w = det.get("wrapper")
        if w:
            agg["wrappers"][w] = agg["wrappers"].get(w, 0) + 1
        agg["offers"].extend(offers)
        for o in offers:
            if o.get("url"):
                agg["urls"].add(o["url"])
        vkey = (vit, int(ring), int(lmm))
        agg["vitolas"].setdefault(vkey, {"name": vit, "ring": int(ring), "lmm": int(lmm), "offers": []})
        agg["vitolas"][vkey]["offers"].extend(offers)

    # materijalizacija: jedna cigara po (brend, linija)
    used_ids = {c["id"] for c in base}
    new_entries = []
    for (b, line), agg in lines.items():
        cuban = agg["cuban"]
        cid = "cig-" + slug(f"{b} {line}")
        base_id, n = cid, 2
        while cid in used_ids:
            cid = f"{base_id}-{n}"; n += 1
        used_ids.add(cid)
        wrapper = max(agg["wrappers"].items(), key=lambda kv: (kv[1], kv[0]))[0] if agg["wrappers"] else "—"
        # vitole sortirane po ring pa dužini
        vsorted = sorted(agg["vitolas"].values(), key=lambda v: (v["ring"], v["lmm"], v["name"]))
        cigar_links = region_links(agg["offers"], cuban)
        vitolas = []
        for v in vsorted:
            vlinks = region_links(v["offers"], cuban)
            hr = vlinks.get("HR")
            fmt = f"{v['ring']} x {v['lmm']}mm"
            vitolas.append({"name": v["name"], "format": fmt,
                            "smokeTimeMin": max(20, min(120, round(v["lmm"] / 2.6))),
                            "priceEUR": hr.get("priceEUR") if hr else None,
                            "url": hr["url"] if hr else None})
        default_v = vsorted[0]
        markets = set(cigar_links.keys()) | {"WW"}
        if cuban:
            markets.discard("USA")
        markets = [m for m in ["HR", "EU", "USA", "WW"] if m in markets]
        hr_link = cigar_links.get("HR")
        shops = ", ".join(sorted({l["shop"] for l in cigar_links.values()}))
        bp = ", box-pressed" if agg["boxpressed"] else ""
        rec = {
            "id": cid, "brand": b, "line": line, "vitola": default_v["name"],
            "format": f"{default_v['ring']} x {default_v['lmm']}mm", "country": agg["country"],
            "wrapper": wrapper, "strength": 3, "body": 3, "flavorTags": [],
            "profileEstimated": True, "catalogSource": "market",
            "smokeTimeMin": max(20, min(120, round(default_v["lmm"] / 2.6))),
            "priceEUR": hr_link.get("priceEUR") if hr_link else None,
            "priceApprox": bool(hr_link and hr_link.get("priceApprox")),
            "availabilityHR": [hr_link["shop"]] if hr_link else [],
            "notes": {"hr": f"Iz kataloga {shops} — {b} {line}{bp}.",
                       "en": f"From the {shops} catalogue — {b} {line}{bp}."},
            "markets": markets, "vitolas": vitolas, "regionLinks": cigar_links,
            "sourceUrls": sorted(agg["urls"]),
        }
        enrich(rec)  # strength/body/wrapper/flavorTags heuristika
        new_entries.append(rec)

    stats["lines"] = len(new_entries)
    stats["held"] = len(hold)
    merged = base + new_entries
    merged.sort(key=sort_key)
    write_json(CIGARS, merged)
    write_json(HOLD, {"stats": stats, "hold": hold})
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print(f"total cigars now: {len(merged)} (base {len(base)} + new {len(new_entries)})")


if __name__ == "__main__":
    build()
