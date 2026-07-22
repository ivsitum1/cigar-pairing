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

# CigarWorld drži zemlju podrijetla u putanji URL-a — pouzdan izvor kad polje fali.
CW_COUNTRY = {
    "dominikanische-republik": "Dominikanska Republika", "nicaragua": "Nikaragva",
    "honduras": "Honduras", "costa-rica": "Kostarika", "kuba": "Kuba",
    "deutschland": "Njemačka", "brasilien": "Brazil", "spanien": "Španjolska",
    "mexiko": "Meksiko", "indonesien": "Indonezija", "panama": "Panama",
    "philippinen": "Filipini", "peru": "Peru", "kolumbien": "Kolumbija",
    "ecuador": "Ekvador", "italien": "Italija", "usa": "SAD", "mosambik": "Mozambik",
}


def derive_country(record):
    det = record.get("details") or {}
    cen = (record.get("country") or det.get("origin") or "").strip()
    if COUNTRY_HR.get(cen.lower()):
        return COUNTRY_HR[cen.lower()]
    for o in record.get("offers") or []:
        m = re.search(r"cigarworld\.de/en/zigarren/([^/]+)/", o.get("url") or "")
        if m and m.group(1) in CW_COUNTRY:
            return CW_COUNTRY[m.group(1)]
    return None

DIM_RE = re.compile(r"\b\d+(?:[.,]\d+)?\s*[x×]\s*\d+(?:[.,]\d+)?\b|\b\d+(?:[.,]\d+)?\s*(?:mm|cm|\")\b|\b#\d+\b", re.I)


def brand_slug(url: str):
    """Brand-slug kandidat iz product URL-a (za brand_dictionary lookup)."""
    if not url:
        return None
    m = re.search(r"/all-cigar-brands/([^/.]+)\.html", url)   # Holt's (egzaktno)
    if m:
        return m.group(1)
    m = re.search(r"/product/([^/]+)/", url)                    # Cigars Daily
    if m:
        return m.group(1)
    m = re.search(r"/zigarren/[^/]+/([^/?]+)", url)             # CigarWorld
    if m:
        return re.sub(r"-\d{6,}.*$", "", m.group(1))            # makni završni id-blok
    return None


# Sigurnosni gate: odbij "brend" koji zapravo izgleda kao brend+linija
# (obrana i kad rječnik ima zaostatke). Konzervativno — pušta prave marke.
_VIT_WORDS = {
    "robusto", "robustos", "toro", "toros", "corona", "coronas", "churchill",
    "churchills", "torpedo", "belicoso", "gordo", "lancero", "perfecto", "perfectos",
    "figurado", "piramide", "lonsdale", "panetela", "epicure", "presidente", "gigante",
}
_LINE_WORDS = {
    "serie", "series", "reserva", "reserve", "edicion", "edition", "limited",
    "vintage", "signature", "anniversary", "aniversario", "especial", "exclusivo",
    "maduro", "connecticut", "habano", "selection", "master", "collection", "batch",
}


_STRENGTH_HR = {1: "vrlo lagane", 2: "lagane", 3: "srednje", 4: "jače", 5: "pune"}
_STRENGTH_EN = {1: "very mild", 2: "mild", 3: "medium", 4: "medium-full", 5: "full"}
_BODY_HR = {1: "vrlo laganog", 2: "laganog", 3: "srednjeg", 4: "punijeg", 5: "punog"}
_BODY_EN = {1: "very light", 2: "light", 3: "medium", 4: "fuller", 5: "full"}
# nekoliko okusnih tagova -> čitljiv opis
_TAG_HR = {"kremasto": "kremasto", "cedar": "cedrovina", "koza": "koža", "kava": "kava",
           "zacini": "začini", "med": "med", "orasasti": "orašasti tonovi",
           "zemljano": "zemljani tonovi", "cokolada": "čokolada", "papar": "papar",
           "vanilija": "vanilija", "slatko": "slatkoća", "trava-slatka": "slatka trava",
           "duhan": "duhan", "drvenasto": "drvenasto"}


def market_note(rec):
    """Opis linije iz atributa (bez izmišljanja) — snaga/tijelo/wrapper/okusi."""
    country = rec["country"]
    wrapper = rec.get("wrapper")
    wr_hr = f", {wrapper} pokrov" if wrapper and wrapper != "—" else ""
    wr_en = f", {wrapper} wrapper" if wrapper and wrapper != "—" else ""
    tags = [t for t in rec.get("flavorTags") or []][:3]
    tags_hr = ", ".join(_TAG_HR.get(t, t) for t in tags)
    hr = f"{country}{wr_hr} — {_STRENGTH_HR[rec['strength']]} snage, {_BODY_HR[rec['body']]} tijela."
    en = f"{country}{wr_en} — {_STRENGTH_EN[rec['strength']]} in strength, {_BODY_EN[rec['body']]}-bodied."
    if tags_hr:
        hr += f" Okusi: {tags_hr}."
    if tags:
        en += f" Notes: {', '.join(tags)}."
    return {"hr": hr, "en": en}


def brand_ok(b: str) -> bool:
    toks = re.findall(r"[a-z0-9]+", b.lower())
    if any(t in _VIT_WORDS for t in toks):
        return False
    if any(t in _LINE_WORDS for t in toks) and len(toks) > 2:
        return False
    if re.search(r"\b(19|20)\d{2}\b", b):
        return False
    if f" {b.lower()} ".find(" by ") >= 0:
        return False
    return True


def resolve_brand(record, brand_dict, keys_by_len):
    for o in record.get("offers") or []:
        s = brand_slug(o.get("url"))
        if not s:
            continue
        if s in brand_dict:
            return brand_dict[s]
        for k in keys_by_len:                                   # longest-prefix
            if s == k or s.startswith(k + "-"):
                return brand_dict[k]
    return None


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
    syns = []
    mid = {}
    for canon, info in lex.items():
        for s in info["syn"]:
            syns.append((s.lower(), canon))
        lo, hi = info.get("lenMM", [None, None])
        if lo and hi:
            mid[canon] = round((lo + hi) / 2)
    syns.sort(key=lambda x: -len(x[0]))
    return syns, mid


def match_vitola(text, syns):
    t = f" {re.sub(r'[^a-z0-9]+', ' ', (text or '').lower())} "
    for s, canon in syns:
        if f" {s} " in t:
            return canon
    return None


def _clean(s):
    s = re.sub(r"\([^)]*\)|\[[^\]]*\]", " ", s)      # sadržaj u zagradama
    s = re.sub(r"[()\[\]{}]", " ", s)                # zaostali fragmenti zagrada
    s = re.sub(r"\b100\s*%\s*tobacco\b", " ", s, flags=re.I)  # marketinški tag
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
    base = re.sub(r"\b(box[- ]?pressed|tubos?|single|cigars?|the|bp)\b", " ", base, flags=re.I)
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
    syns, vit_mid = load_vitola_lexicon()
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
    keys_by_len = sorted(brand_dict.keys(), key=len, reverse=True)
    pool = []
    for r in unified:
        if r.get("inCatalog"):
            continue
        b = r.get("brand")
        if args.phase in ("b", "all") and b and b in known_brands:
            pool.append((b, r))
        elif args.phase in ("c", "all") and not b:
            # Faza C: razriješi NOVI brend iz rječnika (slug iz product URL-a)
            rb = resolve_brand(r, brand_dict, keys_by_len)
            if rb:
                pool.append((rb, r))

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
        if b not in known_brands and not brand_ok(b):
            rej("malformed_brand", r); continue
        det = r.get("details") or {}
        cuban = is_cuban(r.get("country") or det.get("origin"))
        vit = match_vitola(r.get("vitola") or r.get("name") or "", syns) or match_vitola(det.get("size") or "", syns)
        if not vit:
            rej("no_vitola", r); continue
        ring = det.get("ringGauge")
        lmm = length_mm(det)
        len_est = False
        if ring and not lmm and vit in vit_mid:
            lmm = vit_mid[vit]          # procjena duljine iz vitole (označeno)
            len_est = True
        if not ring or not lmm:
            rej("no_format", r); continue
        offers = [o for o in (r.get("offers") or [])]
        if not any(o.get("amount") is not None for o in offers):
            rej("no_price", r); continue
        country = derive_country(r)     # polje/origin pa CigarWorld URL putanja
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
                   "vitolas": {}, "len_est": False}
            lines[(b, line)] = agg
        agg["len_est"] = agg["len_est"] or len_est
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
            ventry = {"name": v["name"], "format": fmt,
                      "smokeTimeMin": max(20, min(120, round(v["lmm"] / 2.6))),
                      "priceEUR": hr.get("priceEUR") if hr else None,
                      "url": hr["url"] if hr else None}
            if vlinks:  # linkovi te vitole (EU/USA/HR) — za odabir vitole u appu
                ventry["regionLinks"] = vlinks
            vitolas.append(ventry)
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
            "notes": {"hr": "", "en": ""},
            "markets": markets, "vitolas": vitolas, "regionLinks": cigar_links,
        }
        if agg["len_est"]:
            rec["formatEstimated"] = True  # duljina procijenjena iz vitole
        enrich(rec)  # strength/body/wrapper/flavorTags heuristika
        rec["notes"] = market_note(rec)  # opis iz atributa (nakon profila)
        new_entries.append(rec)

    stats["lines"] = len(new_entries)
    stats["held"] = len(hold)
    merged = base + new_entries
    merged.sort(key=sort_key)
    write_json(CIGARS, merged)

    # brands.json = TOČNO brendovi prisutni u cigars.json (1:1, bez orphana,
    # idempotentno): postojeće/kurirane zadrži, nove dodaj iz drafta (zemlja iz
    # cigara). Rebuild svaki run da se stara Faza C stanja ne gomilaju.
    import collections
    draft_path = DATADIR / "new_brands_draft.json"
    draft = {k: v for k, v in load_json(draft_path).items() if not k.startswith("_")} if draft_path.exists() else {}
    brands_now = load_json(BRANDS)
    country_by_brand = collections.defaultdict(collections.Counter)
    for rec in new_entries:
        country_by_brand[rec["brand"]][rec["country"]] += 1
    all_used = {c["brand"] for c in merged}
    final_brands = {}
    added_brands = 0
    for b in sorted(all_used, key=lambda s: s.casefold()):
        if b in brands_now:
            final_brands[b] = brands_now[b]          # kurirani ili već dodani
        else:
            d = draft.get(b, {})
            country = country_by_brand[b].most_common(1)[0][0] if country_by_brand[b] else d.get("country", "—")
            final_brands[b] = {
                "country": country,
                "founded": d.get("founded", "—"),
                "blurb": d.get("blurb", {
                    "hr": f"{b} — marka iz kataloga trgovina (HR/EU/USA).",
                    "en": f"{b} — a brand listed in retail shop catalogues (HR/EU/USA).",
                }),
            }
            added_brands += 1
    Path(BRANDS).write_text(json.dumps(final_brands, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    stats["new_brands_added"] = added_brands

    write_json(HOLD, {"stats": stats, "hold": hold})
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print(f"total cigars now: {len(merged)} (base {len(base)} + new {len(new_entries)}) | brands +{added_brands}")


if __name__ == "__main__":
    build()
