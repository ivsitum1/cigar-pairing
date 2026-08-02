#!/usr/bin/env python3
"""Izvodi marku pica iz imena -> src/data/drinkBrands.json.

Pica, za razliku od cigara, nemaju `brand` polje — marka zivi samo unutar
`name`. Ovo je izvodi jednom, u datoteku koja se moze pregledati i rucno
ispraviti, umjesto da se pogadanje ukopa u osam podatkovnih datoteka.

KAVA JE NAMJERNO IZOSTAVLJENA: sva 33 zapisa su nacini pripreme (Ristretto,
Cold brew), podrijetla (Brazil Santos) ili recepti (Irish coffee) — pojam
marke ondje ne postoji.

Rucne ispravke idu u scripts/data/drink_brand_overrides.json i uvijek
nadjacavaju heuristiku; ponovno pokretanje ih ne gazi.

Usage:
  python3 scripts/derive-drink-brands.py
  python3 scripts/derive-drink-brands.py --check   # CI: pada ako bi se mijenjalo
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import unicodedata
from pathlib import Path

APP = Path(__file__).resolve().parent.parent
DATA = APP / "src" / "data"
OUT = DATA / "drinkBrands.json"
OVERRIDES = APP / "scripts" / "data" / "drink_brand_overrides.json"

# Kava nema marke — vidi docstring.
FILES = ["rums", "whiskies", "brandies", "gins", "wines", "tequilas", "digestifs"]

# Rijeci koje same ne mogu biti marka: clanovi, "ron/rhum" (= rum), oznake
# vinarija. Za njih se marka trazi jednu razinu dublje ("Ron Abuelo", ne "Ron").
GENERIC = {
    "the", "ron", "rhum", "rum", "gin", "gran", "don", "el", "la", "le", "les",
    "casa", "chateau", "château", "castello", "domaine", "tenuta", "vina",
    "viña", "san", "santa", "dom", "ile", "isle",
}

# Scrape repovi koji nisu dio imena.
TAIL = re.compile(
    r"\s*(?:\d+[.,]?\d*\s*%\s*Vol\.?.*|u poklon kutij.*|"
    r"\d+[.,]?\d*\s*l\b.*|MAGNUM.*)$",
    re.I,
)


def clean(name: str) -> str:
    n = html.unescape(name or "").replace("&#039;", "'")
    n = TAIL.sub("", n)
    return re.sub(r"\s+", " ", n).strip(" -–—,")


def _norm(w: str) -> str:
    return w.strip("(),.'’\"").lower()


def derive_all(names: dict[str, str]) -> dict[str, str]:
    """Marka = najdulji zajednicki prefiks svih boca koje dijele pocetak imena.

    Podatkovno umjesto rucnog popisa: "Ardbeg Corryvreckan" i "Ardbeg Uigeadail"
    dijele samo "Ardbeg", pa je to marka; "Johnnie Walker Black/Blue Label"
    dijele obje rijeci. Kad ispadne genericna rijec ("Ron"), trazi se dublje.
    """
    values = list(names.values())

    def brand_for(name: str, level: int = 1) -> str:
        words = name.split()
        if not words:
            return name
        key = tuple(_norm(w) for w in words[:level])
        group = [n for n in values if tuple(_norm(w) for w in n.split()[:level]) == key]
        if len(group) < 2:
            take = 2 if _norm(words[0]) in GENERIC and len(words) > 1 else 1
            return " ".join(words[:take])
        split = [g.split() for g in group]
        lcp: list[str] = []
        for i in range(min(len(s) for s in split)):
            w = _norm(split[0][i])
            if all(_norm(s[i]) == w for s in split):
                lcp.append(split[0][i])
            else:
                break
        if not lcp:
            lcp = words[:1]
        if len(lcp) == 1 and _norm(lcp[0]) in GENERIC and len(words) > 1:
            return brand_for(name, level + 1)
        return " ".join(lcp)

    return {i: brand_for(n) for i, n in names.items()}


def slugify(label: str) -> str:
    """Isti slug kao `slugifyLabel` u src/data/index.ts (deep-link adresa marke)."""
    s = unicodedata.normalize("NFKD", label)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"['‘’`]", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def slug_collisions(brands: dict[str, str]) -> list[str]:
    """Dvije marke na istom slugu = jedna je nedohvatljiva deep-linkom.

    Skoro uvijek je uzrok isto ime pisano dvojako ("Gran Patron" / "Gran
    Patron" s naglaskom) — dakle jedna kuca razlomljena na dvije marke. Ispravlja
    se u drink_brand_overrides.json, ne ovdje.
    """
    seen: dict[str, str] = {}
    out: list[str] = []
    for brand in sorted(set(brands.values())):
        slug = slugify(brand)
        if slug in seen:
            out.append(f"{slug}: {seen[slug]!r} / {brand!r}")
        else:
            seen[slug] = brand
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    overrides = {}
    if OVERRIDES.exists():
        overrides = json.loads(OVERRIDES.read_text(encoding="utf-8")).get("brands", {})

    names: dict[str, str] = {}
    for f in FILES:
        for d in json.loads((DATA / f"{f}.json").read_text(encoding="utf-8")):
            names[d["id"]] = clean(d.get("name", ""))
    brands = derive_all(names)
    for cid, brand in overrides.items():
        if cid in brands:
            brands[cid] = brand

    collisions = slug_collisions(brands)
    if collisions:
        print("Dvije marke dijele slug (ispravi u drink_brand_overrides.json):",
              file=sys.stderr)
        for c in collisions:
            print(f"  {c}", file=sys.stderr)
        return 1

    payload = {
        "_comment": (
            "Marka pica izvedena iz imena (pica nemaju `brand` polje). "
            "Generira scripts/derive-drink-brands.py. Rucne ispravke NE upisuj "
            "ovdje nego u scripts/data/drink_brand_overrides.json — one "
            "nadjacavaju heuristiku i prezivljavaju regeneraciju. "
            "Kava je namjerno izostavljena: nema pojam marke."
        ),
        "brands": dict(sorted(brands.items())),
    }
    text = json.dumps(payload, ensure_ascii=False, indent=1) + "\n"

    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print("--check: drinkBrands.json nije u skladu s podacima", file=sys.stderr)
            return 1
        print(f"--check: {len(brands)} marki na mjestu")
        return 0

    OUT.write_text(text, encoding="utf-8")
    uniq = sorted(set(brands.values()))
    print(f"{len(brands)} pica -> {len(uniq)} marki ({len(overrides)} rucnih ispravki)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
