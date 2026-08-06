#!/usr/bin/env python3
"""Mjerilo za četiri toka čišćenja podataka — vidi
docs/superpowers/plans/2026-08-05-data-quality-four-workstreams.md

Samo ČITA podatke i ispisuje brojke. Nikad ne piše. Pokreni prije i poslije
svakog koraka da se vidi pomiče li se brojka koju taj korak cilja:

  python3 scripts/data-quality-report.py
  python3 scripts/data-quality-report.py --json    # za dnevnik napretka
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "src" / "data"
DRINK_FILES = ["rums", "whiskies", "brandies", "gins", "wines", "tequilas", "digestifs"]

# URL slugovi u imenima linija su uvijek malim slovima ("xo 61 2 52",
# "serie r no", "pca exclusive").  Pravi nazivi imaju barem jedno veliko slovo,
# ili su isključivo znamenke/simboli (serijski broj, godina, ordinal).
_LOWER_LETTER = re.compile(r"[a-z]")
_UPPER_LETTER = re.compile(r"[A-Z]")
# Ordinali poput "115th", "250th" su oznake obljetnice, ne slug-ovi.
_ORDINAL_ONLY = re.compile(r"^\d+(th|st|nd|rd)$", re.I)

# Rep scrapea u imenu boce: jakost, volumen, pakiranje, HTML entitet.
NAME_TAIL = re.compile(
    r"\d+[.,]?\d*\s*%\s*Vol|u poklon kutij|\d+[.,]?\d*\s*l\b|&#0\d\d;"
    r"|in Giftbox|sa\s+[cčć]a[sš]om|in wooden case",
    re.I,
)


def junk_line(c: dict) -> bool:
    """True kad ime linije izgleda kao neočišćeni URL slug.

    URL slug je tekst samo malim slovima ("xo 61 2 52", "serie r no").
    Sljedeće nije slug i nije označeno:
    - Barem jedno veliko slovo → pravi naziv proizvoda (Title Case):
      "Padrón 1926", "Asylum 13", "20th Anniversary Maduro", "La Aurora 107"
    - Nema slova uopće → serijski broj / godina / oznaka: 858, 1926, #3
    - Čisti ordinal → oznaka obljetnice: "115th", "250th"
    Dimenzijski repovi ("xo 61 2 52") su implicitno pokriveni trećim pravilom:
    sadrže mala slova i nisu ordinali, pa i dalje prolaze ovim filtrom.
    """
    line = c.get("line", "")
    if not line:
        return False
    if _UPPER_LETTER.search(line):
        return False
    if not _LOWER_LETTER.search(line):
        return False
    if _ORDINAL_ONLY.match(line):
        return False
    return True


def cigar_profiles(cigars: list[dict]) -> dict:
    thin = [c for c in cigars if not c.get("flavorTags")]
    buckets = Counter(
        (c["body"], c["strength"], tuple(sorted(c.get("flavorTags") or [])))
        for c in cigars
    )
    top = buckets.most_common(1)[0]
    slug_examples: list[str] = []
    slug_count = 0
    for c in cigars:
        if junk_line(c):
            slug_count += 1
            if len(slug_examples) < 10:
                slug_examples.append(c.get("line", ""))
    return {
        "total": len(cigars),
        "no_flavor_tags": len(thin),
        "no_wrapper": sum(1 for c in cigars if c.get("wrapper") == "—"),
        "slug_line_names": slug_count,
        "slug_line_examples": slug_examples,
        "distinct_profiles": len(buckets),
        "largest_profile_bucket": top[1],
        "largest_profile_share_pct": round(100 * top[1] / len(cigars), 1),
        "profile_estimated": sum(1 for c in cigars if c.get("profileEstimated")),
    }


def drink_profiles() -> dict:
    per_file = {}
    total = 0
    in_big = 0
    for f in DRINK_FILES:
        ds = json.loads((DATA / f"{f}.json").read_text(encoding="utf-8"))
        buckets = Counter(
            (d["body"], d["sweetness"], tuple(sorted(d.get("flavorTags") or [])))
            for d in ds
        )
        big = sum(v for v in buckets.values() if v >= 5)
        per_file[f] = {
            "bottles": len(ds),
            "distinct_profiles": len(buckets),
            "largest_bucket": max(buckets.values()),
            "in_buckets_ge_5": big,
        }
        total += len(ds)
        in_big += big
    return {
        "per_category": per_file,
        "bottles": total,
        "in_buckets_ge_5": in_big,
        "in_buckets_ge_5_pct": round(100 * in_big / total, 1),
    }


def price_freshness(cigars: list[dict]) -> dict:
    stamped = 0
    priced = 0
    for c in cigars:
        for v in c.get("vitolas") or []:
            if v.get("priceEUR") is not None:
                priced += 1
                if v.get("fetchedAt"):
                    stamped += 1
        for rl in (c.get("regionLinks") or {}).values():
            if rl.get("priceEUR") is not None:
                priced += 1
                if rl.get("fetchedAt"):
                    stamped += 1
    return {
        "price_points": priced,
        "with_fetched_at": stamped,
        "with_fetched_at_pct": round(100 * stamped / priced, 1) if priced else 0.0,
    }


def drink_names() -> dict:
    """Sirovi scrape-rep u `name` bez prikaznog imena (nameLoc ili drinkDisplayNames)."""
    display_map: dict[str, str] = {}
    disp_path = DATA / "drinkDisplayNames.json"
    if disp_path.exists():
        display_map = json.loads(disp_path.read_text(encoding="utf-8")).get("names") or {}

    tails = 0
    display = 0
    total = 0
    examples: list[str] = []
    for f in DRINK_FILES:
        for d in json.loads((DATA / f"{f}.json").read_text(encoding="utf-8")):
            total += 1
            has_display = bool(d.get("nameLoc")) or d["id"] in display_map
            if has_display:
                display += 1
            if NAME_TAIL.search(d["name"]) and not has_display:
                tails += 1
                if len(examples) < 5:
                    examples.append(d["name"][:80])
    return {
        "bottles": total,
        "raw_scrape_tails": tails,
        "with_display_name": display,
        "examples": examples,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    cigars = json.loads((DATA / "cigars.json").read_text(encoding="utf-8"))
    report = {
        "w1_cigar_profiles": cigar_profiles(cigars),
        "w2_drink_profiles": drink_profiles(),
        "w3_price_freshness": price_freshness(cigars),
        "w4_drink_names": drink_names(),
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    w1 = report["w1_cigar_profiles"]
    print("W1 — profili cigara")
    print(f"   {w1['total']} cigara, {w1['distinct_profiles']} različitih profila")
    print(f"   bez flavorTags:      {w1['no_flavor_tags']}      cilj: < 300")
    print(f"   wrapper '—':         {w1['no_wrapper']}      cilj: < 300")
    print(f"   ime linije iz sluga: {w1['slug_line_names']}      cilj: < 200")
    print(
        f"   najveći profil:      {w1['largest_profile_bucket']}"
        f" ({w1['largest_profile_share_pct']}%)   cilj: < 15%"
    )

    w2 = report["w2_drink_profiles"]
    print("\nW2 — profili pića")
    for f, v in w2["per_category"].items():
        print(
            f"   {f:10} {v['bottles']:4} boca -> {v['distinct_profiles']:3} profila"
            f" | najveći {v['largest_bucket']:3} | u bucketima >=5: {v['in_buckets_ge_5']}"
        )
    print(
        f"   ukupno u bucketima >=5: {w2['in_buckets_ge_5']}/{w2['bottles']}"
        f" ({w2['in_buckets_ge_5_pct']}%)   cilj: < 15%"
    )

    w3 = report["w3_price_freshness"]
    print("\nW3 — svježina cijena")
    print(
        f"   {w3['price_points']} cijena, s oznakom datuma: {w3['with_fetched_at']}"
        f" ({w3['with_fetched_at_pct']}%)   cilj: 100%"
    )

    w4 = report["w4_drink_names"]
    print("\nW4 — prikazna imena pića")
    print(f"   {w4['bottles']} boca, s prikaznim imenom: {w4['with_display_name']}")
    print(f"   sirovi repovi scrapea:  {w4['raw_scrape_tails']}      cilj: 0")
    for e in w4["examples"]:
        print(f"      {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
