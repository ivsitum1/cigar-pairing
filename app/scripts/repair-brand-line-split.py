#!/usr/bin/env python3
"""Popravlja krivo razrezan brend/linija u cigars.json.

Splitter je kod marki od vise rijeci rezao ime na prvoj rijeci, pa je rep marke
ostao u liniji — a kod marki tipa "Casa" jedna je marka pokrila sedam kuca:

    "Flor de las Antillas" | "de las Antillas"      -> linija = ime marke
    "Black Works Studio"   | "Studio Killer Bee"    -> linija "Killer Bee"
    "Casa"                 | "Cuevas Reserva Maduro"-> marka "Casa Cuevas"
    "Rough"                | "Rider Sweets Maduro"  -> marka "Rough Rider"

Dvije operacije:

1. REP MARKE VAN IZ LINIJE. Ako linija pocinje repom imena marke, rep se skida;
   ako od linije ne ostane nista, linija postaje ime marke (katalog to pisanje
   koristi za maticnu liniju marke: "Punch | Punch").
2. KRNJA MARKA. Rucni popis (BRAND_FIX) vraca kucu u marku. Rucni je jer se iz
   podataka ne moze znati je li "Regalia" krnja marka ili prava — potvrda su
   slugovi u linkovima zapisa (casa-cuevas-..., rough-rider-...).

brands.json se drzi u koraku: nova marka dobiva unos, marka bez cigara ga gubi
(test 'brands.json i cigars.json — 1:1 pokrivenost brendova').

Usage:
  python3 scripts/repair-brand-line-split.py --dry-run
  python3 scripts/repair-brand-line-split.py
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

APP = Path(__file__).resolve().parent.parent
DATA = APP / "src" / "data"
CIGARS = DATA / "cigars.json"
BRANDS = DATA / "brands.json"
ALIASES = DATA / "cigarIdAliases.json"

# marka -> kuce koje su ostale u liniji. Redoslijed nije vazan; duljи se
# poklapa prvi (["de Torres"] prije ["de"]).
BRAND_FIX: dict[str, list[str]] = {
    "Casa": ["Carrillo", "Cuevas", "Culinaria", "de Alegría", "de García",
             "De Garcia", "de Nicaragua", "de Torres"],
    "Rough": ["Rider"],
    "El Rico": ["Habano"],
    "Total": ["Flame"],
    "German": ["Engineered"],
    "Rancho": ["Luna"],
    "Alejandro": ["Lopez"],
    "Regalia": ["Fina"],
    "Segovias": ["De Esteli"],
}

# Ujednacenje pisanja kad ista kuca u katalogu stoji dvojako.
BRAND_CANON = {"Casa De Garcia": "Casa de García"}

# Nove marke: unos u brands.json. Blurb je namjerno kratak i cinjenicni —
# opisuje ono sto stoji u podacima, bez izmisljene povijesti kuce.
NEW_BRANDS: dict[str, dict] = {
    "Casa Carrillo": {"country": "Dominikanska Republika", "founded": "—", "blurb": {
        "hr": "Casa Carrillo — dominikanska kuća; u katalogu linije Ascend i TAA Exclusive.",
        "en": "Casa Carrillo — a Dominican house; the catalog carries the Ascend and TAA Exclusive lines."}},
    "Casa Cuevas": {"country": "Dominikanska Republika", "founded": "2016", "blurb": {
        "hr": "Casa Cuevas — obitelj Cuevas, Tamboril (Dominikanska Republika); Habano, Maduro i Reserva linije.",
        "en": "Casa Cuevas — the Cuevas family in Tamboril, Dominican Republic; Habano, Maduro and Reserva lines."}},
    "Casa Culinaria": {"country": "Nikaragva", "founded": "2007", "blurb": {
        "hr": "Casa Culinaria — Paul Bugge (Villingen-Schwenningen) privatna marka od 2007.; Connecticut/Jalapa/Estelí linije (Nikaragva).",
        "en": "Casa Culinaria — Paul Bugge (Villingen-Schwenningen) house brand from 2007; Connecticut/Jalapa/Estelí lines (Nicaragua)."}},
    "Casa de Alegría": {"country": "Nikaragva", "founded": "—", "blurb": {
        "hr": "Casa de Alegría — nikaragvanska marka; u katalogu Criollo, Rico i Suave.",
        "en": "Casa de Alegría — a Nicaraguan brand; Criollo, Rico and Suave in the catalog."}},
    "Casa de García": {"country": "Dominikanska Republika", "founded": "—", "blurb": {
        "hr": "Casa de García — dominikanska marka; Centenario, Connecticut i Maduro linije.",
        "en": "Casa de García — a Dominican brand; Centenario, Connecticut and Maduro lines."}},
    "Casa de Nicaragua": {"country": "Nikaragva", "founded": "—", "blurb": {
        "hr": "Casa de Nicaragua — nikaragvanska marka iz njemačke distribucije.",
        "en": "Casa de Nicaragua — a Nicaraguan brand from German distribution."}},
    "Casa de Torres": {"country": "Nikaragva", "founded": "—", "blurb": {
        "hr": "Casa de Torres — nikaragvanska marka; Bold, Edición Especial i Maduro Selection.",
        "en": "Casa de Torres — a Nicaraguan brand; Bold, Edición Especial and Maduro Selection."}},
    "Rough Rider": {"country": "Nikaragva", "founded": "—", "blurb": {
        "hr": "Rough Rider — pristupačna marka (Chapter One, Sweets, Senoritas).",
        "en": "Rough Rider — an accessible brand (Chapter One, Sweets, Senoritas)."}},
    "El Rico Habano": {"country": "Nikaragva", "founded": "—", "blurb": {
        "hr": "El Rico Habano — El Credito / Ernesto Perez-Carrillo naslijeđe; Maduro i Suprema.",
        "en": "El Rico Habano — from the El Credito / Ernesto Perez-Carrillo lineage; Maduro and Suprema."}},
    "Total Flame": {"country": "Dominikanska Republika", "founded": "—", "blurb": {
        "hr": "Total Flame — marka za istočnoeuropsko tržište; dominikanske linije Persia i Wild One.",
        "en": "Total Flame — a brand for the Eastern European market; the Dominican Persia and Wild One lines."}},
    "German Engineered": {"country": "Njemačka", "founded": "—", "blurb": {
        "hr": "German Engineered — njemačka marka; Rauchvergnügen i Raumzeit linije.",
        "en": "German Engineered — a German brand; the Rauchvergnügen and Raumzeit lines."}},
    "Rancho Luna": {"country": "Kuba", "founded": "—", "blurb": {
        "hr": "Rancho Luna — marka s Blue i Red linijom.",
        "en": "Rancho Luna — a brand with Blue and Red lines."}},
    "Alejandro Lopez": {"country": "Dominikanska Republika", "founded": "—", "blurb": {
        "hr": "Alejandro Lopez — dominikanske i nikaragvanske linije pod istim imenom.",
        "en": "Alejandro Lopez — Dominican and Nicaraguan lines under one name."}},
    "Regalia Fina": {"country": "Brazil", "founded": "—", "blurb": {
        "hr": "Regalia Fina — brazilska marka; linije Sao Carlos, Sao Jose i Sao Paulo.",
        "en": "Regalia Fina — a Brazilian brand; the Sao Carlos, Sao Jose and Sao Paulo lines."}},
    "Segovias De Esteli": {"country": "Nikaragva", "founded": "—", "blurb": {
        "hr": "Segovias De Esteli — nikaragvanska marka; Maduro i Oscuro.",
        "en": "Segovias De Esteli — a Nicaraguan brand; Maduro and Oscuro."}},
}

# Davidoff: Neptune stub "Winston" (i "Winston LE 2025") je isti proizvod kao
# kurirani "Winston Churchill", samo s izmisljenim dimenzijama (sve 47 x 178mm).
# Prenosi se samo USA link na vitolu istog imena; izmisljene vitole se ne uvoze.
STUB_MERGE = {
    "cig-davidoff-winston-toro": "cig-davidoff-winston-churchill",
    "cig-davidoff-winston-le-2025": "cig-davidoff-winston-churchill",
}


def slug(text: str) -> str:
    t = unicodedata.normalize("NFKD", text)
    t = "".join(ch for ch in t if not unicodedata.combining(ch)).lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def strip_brand_tail(brand: str, line: str) -> str | None:
    """Linija pocinje repom imena marke -> vrati liniju bez repa (ili "" za maticnu)."""
    if slug(line) == slug(brand):
        return None                      # "Punch | Punch" je ispravno pisanje
    bslug = slug(brand)
    words = line.split()
    best = 0
    for k in range(1, len(words) + 1):
        head = slug(" ".join(words[:k]))
        if head and (bslug == head or bslug.endswith("-" + head)):
            best = k
    if not best:
        return None
    rest = " ".join(words[best:])
    if rest and (len(rest) < 2 or not rest[0].isalnum()):
        return None                      # "Gran Habano | Habano #3" -> ne krni u "#3"
    return rest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in cigars}
    log: list[str] = []

    # 1) krnja marka -> kuca iz linije ide u marku
    for c in cigars:
        for house in sorted(BRAND_FIX.get(c["brand"], []), key=len, reverse=True):
            hs = slug(house)
            words = c["line"].split()
            for k in range(len(words), 0, -1):
                if slug(" ".join(words[:k])) == hs:
                    old = f"{c['brand']} | {c['line']}"
                    brand = f"{c['brand']} {house}"
                    c["brand"] = BRAND_CANON.get(brand, brand)
                    c["line"] = " ".join(words[k:]) or c["brand"]
                    log.append(f"- marka: `{old}` -> **{c['brand']} | {c['line']}**")
                    break
            else:
                continue
            break

    # 2) rep marke van iz linije
    for c in cigars:
        rest = strip_brand_tail(c["brand"], c["line"])
        if rest is None:
            continue
        old = c["line"]
        c["line"] = rest or c["brand"]
        log.append(f"- linija: {c['brand']} `{old}` -> **{c['line']}**")

    # 3) Davidoff stubovi u kuriranu liniju
    drop: set[str] = set()
    for stub_id, target_id in STUB_MERGE.items():
        stub, target = by_id.get(stub_id), by_id.get(target_id)
        if not stub or not target:
            continue
        moved = 0
        for sv in stub["vitolas"]:
            for tv in target["vitolas"]:
                if slug(tv["name"]).endswith(slug(sv["name"])) and sv.get("regionLinks"):
                    tv.setdefault("regionLinks", {}).update(
                        {k: v for k, v in sv["regionLinks"].items() if k not in tv.get("regionLinks", {})})
                    moved += 1
                    break
        target["sourceUrls"] = sorted(set(target.get("sourceUrls") or [])
                                      | set(stub.get("sourceUrls") or []))
        target["markets"] = [m for m in ("HR", "EU", "USA", "WW")
                             if m in set(target["markets"]) | set(stub["markets"])]
        if "USA" not in target.get("regionLinks", {}) and (stub.get("regionLinks") or {}).get("USA"):
            target.setdefault("regionLinks", {})["USA"] = stub["regionLinks"]["USA"]
        drop.add(stub_id)
        log.append(f"- stub: `{stub['brand']} {stub['line']}` -> **{target['line']}** "
                   f"({moved} linka na vitolu)")

    # 4) skidanje repa je otkrilo zapise koji su ista linija iz dva izvora
    #    (Karen Berger "Berger Cameroon" + "Cameroon") — spoji ih
    seen: dict[tuple[str, str], dict] = {}
    for c in cigars:
        if c["id"] in drop:
            continue
        key = (c["brand"], c["line"])
        first = seen.get(key)
        if first is None:
            seen[key] = c
            continue
        rank = lambda x: (bool((x.get("regionLinks") or {}).get("HR")),
                          x["wrapper"] != "—", len(x["vitolas"]), -len(x["id"]))
        keep, gone = (first, c) if rank(first) >= rank(c) else (c, first)
        seen[key] = keep
        vit = list(keep["vitolas"])
        have = {(v["name"], v.get("format")) for v in vit}
        vit += [v for v in gone["vitolas"] if (v["name"], v.get("format")) not in have]
        vit.sort(key=lambda v: (v.get("ring") or 999, v.get("lengthMM") or 9999, v["name"]))
        keep["vitolas"] = vit
        for region, link in (gone.get("regionLinks") or {}).items():
            keep.setdefault("regionLinks", {}).setdefault(region, link)
        keep["markets"] = [m for m in ("HR", "EU", "USA", "WW")
                           if m in set(keep["markets"]) | set(gone["markets"])]
        keep["availabilityHR"] = sorted(set(keep["availabilityHR"]) | set(gone["availabilityHR"]))
        if keep["wrapper"] == "—" and gone["wrapper"] != "—":
            keep["wrapper"] = gone["wrapper"]
        src = set(keep.get("sourceUrls") or []) | set(gone.get("sourceUrls") or [])
        if src:
            keep["sourceUrls"] = sorted(src)
        drop.add(gone["id"])
        STUB_MERGE[gone["id"]] = keep["id"]
        log.append(f"- spojeno: `{gone['id']}` -> **{keep['brand']} {keep['line']}** "
                   f"({len(vit)} vitola)")

    kept = [c for c in cigars if c["id"] not in drop]

    # 5) brands.json u korak s markama
    brands = json.loads(BRANDS.read_text(encoding="utf-8"))
    live = {c["brand"] for c in kept}
    for name in sorted(live - set(brands)):
        brands[name] = NEW_BRANDS.get(name) or {
            "country": next(c["country"] for c in kept if c["brand"] == name),
            "founded": "—",
            "blurb": {"hr": f"{name} — marka u katalogu.", "en": f"{name} — a brand in the catalog."},
        }
        log.append(f"- brands.json: + **{name}**")
    for name in sorted(set(brands) - live):
        del brands[name]
        log.append(f"- brands.json: - {name}")

    dupes = {}
    for c in kept:
        dupes.setdefault((c["brand"], c["line"]), []).append(c["id"])
    clashes = {k: v for k, v in dupes.items() if len(v) > 1}

    print(f"{len(log)} izmjena; {len(kept)} cigara, {len(brands)} marki")
    for line in log:
        print("  ", line)
    if clashes:
        print("PAZI — (marka, linija) se ponavlja:")
        for k, v in clashes.items():
            print("   ", k, v)
        return 1
    if args.dry_run:
        return 0

    CIGARS.write_text(json.dumps(kept, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    BRANDS.write_text(json.dumps(brands, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    doc = json.loads(ALIASES.read_text(encoding="utf-8"))
    al = doc["aliases"]
    al.update(STUB_MERGE)
    live_ids = {c["id"] for c in kept}          # razrijesi lance do zivog zapisa
    for src in list(al):
        dst, hops = al[src], 0
        while dst not in live_ids and dst in al and hops < 10:
            dst, hops = al[dst], hops + 1
        al[src] = dst
    ALIASES.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
