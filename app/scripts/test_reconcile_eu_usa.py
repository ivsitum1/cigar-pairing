# -*- coding: utf-8 -*-
"""Testovi za reconcile-eu-usa-availability + fetch parsere.

Pokretanje (iz app/):
    python scripts/test_reconcile_eu_usa.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / file)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


M = load("reconcile_eu_usa", "reconcile-eu-usa-availability.py")
F = load("fetch_eu_usa", "fetch-eu-usa-catalogs.py")
FAILURES: list[str] = []


def check(label: str, actual, expected) -> None:
    if actual != expected:
        FAILURES.append(f"{label}\n     dobiveno: {actual!r}\n     ocekivano: {expected!r}")
    else:
        print(f"  ok  {label}")


def cig(**kw) -> dict:
    base = {
        "id": "cig-x",
        "brand": "Brand",
        "line": "Line",
        "country": "Nikaragva",
        "markets": ["WW"],
        "vitolas": [],
    }
    base.update(kw)
    return base


print("fetch URL parseri")
cw = F.parse_cw_product_url(
    "https://www.cigarworld.de/en/zigarren/nicaragua/oliva-serie-v-melanio-robusto-123_45"
)
check("CW name", cw["name"] if cw else None, "Oliva Serie V Melanio Robusto")
check(
    "Holts brand hub",
    (F.parse_holts_brand_url("https://www.holts.com/cigars/all-cigar-brands/brand/oliva") or {}).get(
        "brand"
    ),
    "Oliva",
)
check(
    "Holts listing nije product",
    F.parse_holts_brand_url("https://www.holts.com/cigars/all-cigar-brands.html"),
    None,
)

print("\nEU discovery iz snapshota")
c = cig(id="cig-eu-new", brand="Oliva", line="Serie V Melanio", markets=["WW"])
removed, added = M.reconcile(
    [c],
    {"EU": {("oliva", "serie v melanio")}, "USA": set()},
    set(),
)
check("EU dodan", "EU" in c["markets"], True)
check("prijavljen", [a["id"] for a in added], ["cig-eu-new"])

print("\nUSA brand-level ne otkriva novo")
c = cig(id="cig-usa-brand", brand="Oliva", line="Serie V", markets=["WW"])
removed, added = M.reconcile([c], {"EU": set(), "USA": set()}, {"oliva"})
check("USA nije dodan samo zbog brenda", "USA" in c["markets"], False)

print("\nUSA brand-level zadrzava postojece")
c = cig(id="cig-usa-keep", brand="Oliva", line="Serie V", markets=["USA", "WW"])
removed, added = M.reconcile([c], {"EU": set(), "USA": set()}, {"oliva"})
check("USA ostaje", "USA" in c["markets"], True)
check("nije maknut", [r["id"] for r in removed], [])

print("\nembargo")
c = cig(id="cig-cuba", brand="Cohiba", line="Siglo", country="Kuba", markets=["EU", "USA", "WW"])
removed, added = M.reconcile(
    [c],
    {"EU": {("cohiba", "siglo")}, "USA": {("cohiba", "siglo")}},
    {"cohiba"},
)
check("USA skinut s kubanke", "USA" in c["markets"], False)
check("EU ostaje", "EU" in c["markets"], True)

print("\nCigars Daily nije u primarnom fetchu")
check("nema daily u HOSTS EU", "cigarsdaily.com" in M.HOSTS["EU"], False)
check("daily jos kao legacy USA hard host", "cigarsdaily.com" in M.HOSTS["USA"], True)

if FAILURES:
    print(f"\nPALO: {len(FAILURES)}")
    for f in FAILURES:
        print(f"  ✗ {f}")
    sys.exit(1)
print("\nsve prolazi")
