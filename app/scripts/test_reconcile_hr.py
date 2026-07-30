# -*- coding: utf-8 -*-
"""Testovi za reconcile-hr-availability.

Pokretanje (iz app/):
    python scripts/test_reconcile_hr.py

Namjerno bez pytesta — CI za Python korake ovdje vrti gole skripte.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_module():
    spec = importlib.util.spec_from_file_location(
        "reconcile_hr", ROOT / "reconcile-hr-availability.py"
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class FakeSync:
    """Minimalni matcher: normalizacija na mala slova bez viska."""

    @staticmethod
    def norm(s: str) -> str:
        return " ".join((s or "").lower().split())


M = load_module()
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
        "markets": ["EU", "WW"],
        "availabilityHR": [],
        "vitolas": [],
    }
    base.update(kw)
    return base


def run(cigars, present, walk_in=frozenset()):
    """reconcile() s podmetnutim walk_in skupom."""
    original = M.walk_in_shops
    M.walk_in_shops = lambda: set(walk_in)
    try:
        return M.reconcile(cigars, present, FakeSync)
    finally:
        M.walk_in_shops = original


print("otkrivanje nove ponude")
# Cigara bez ijedne HR oznake koju trgovina sada drzi -> mora dobiti HR.
c = cig(id="cig-perla", brand="Perla", line="de Calvano")
removed, added = run([c], {("perla", "de calvano"): {"Havana Shop"}})
check("nova ponuda dobiva availabilityHR", c["availabilityHR"], ["Havana Shop"])
check("nova ponuda dobiva markets.HR", "HR" in c["markets"], True)
check("prijavljena je kao dodana", [a["id"] for a in added], ["cig-perla"])

# Bez poklapanja u snapshotu ne smije se nista izmisliti.
c = cig(id="cig-nema", brand="Nema", line="Ovoga")
removed, added = run([c], {})
check("bez poklapanja ostaje bez HR", (c["availabilityHR"], "HR" in c["markets"]), ([], False))
check("i nije prijavljena kao dodana", added, [])

print("\nuklanjanje zastarjele ponude")
c = cig(id="cig-stara", availabilityHR=["Havana Shop"], markets=["HR", "EU", "WW"])
removed, added = run([c], {})
check("nestala iz ponude gubi HR", (c["availabilityHR"], c["markets"]), ([], ["EU", "WW"]))
check("prijavljena je kao maknuta", [r["id"] for r in removed], ["cig-stara"])

print("\nfizicki ducani prezivljavaju")
# Trgovina bez web kataloga ne moze se potvrditi online — ne smije se brisati.
c = cig(id="cig-walkin", availabilityHR=["Tobacco Petica (Branimir)"], markets=["HR", "EU", "WW"])
removed, added = run([c], {}, walk_in={"Tobacco Petica (Branimir)"})
check("walk-in ostaje", c["availabilityHR"], ["Tobacco Petica (Branimir)"])
check("HR ostaje u markets", "HR" in c["markets"], True)
check("nije prijavljena kao maknuta", removed, [])

# Walk-in se zadrzava i kad online trgovina istovremeno ima istu liniju.
c = cig(
    id="cig-oba",
    brand="Don Tomas",
    line="Bundle",
    availabilityHR=["Tobacco Petica (Branimir)"],
    markets=["HR", "EU", "WW"],
)
removed, added = run(
    [c],
    {("don tomas", "bundle"): {"Havana Shop"}},
    walk_in={"Tobacco Petica (Branimir)"},
)
check(
    "walk-in i online stoje zajedno",
    c["availabilityHR"],
    ["Havana Shop", "Tobacco Petica (Branimir)"],
)

# Online trgovina koja nestane iz snapshota se mice, walk-in ostaje.
c = cig(
    id="cig-mix",
    availabilityHR=["Havana Shop", "Tobacco Petica (Branimir)"],
    markets=["HR", "EU", "WW"],
)
removed, added = run([c], {}, walk_in={"Tobacco Petica (Branimir)"})
check("online otpada, walk-in ostaje", c["availabilityHR"], ["Tobacco Petica (Branimir)"])

print("\nzastita od neuspjelog dohvata")
check("prag je definiran", 0 < M.MIN_FETCH_RATIO < 1, True)


class ShortFetch:
    """Trgovina koja odgovori, ali s desetinom kataloga."""

    @staticmethod
    def fetch_havana_catalog():
        return [{"name": f"p{i}"} for i in range(40)]

    @staticmethod
    def fetch_humidor_catalog():
        return [{"name": f"h{i}"} for i in range(300)]


import json
import tempfile

with tempfile.TemporaryDirectory() as tmp:
    snap = Path(tmp) / "snap.json"
    snap.write_text(
        json.dumps({
            "fetched_at": "2026-07-24T00:00:00Z",
            "havana": [{"name": f"p{i}"} for i in range(400)],
            "humidor": [{"name": f"h{i}"} for i in range(312)],
        }),
        encoding="utf-8",
    )
    prev_snapshot, prev_out = M.SNAPSHOT, M.OUT
    M.SNAPSHOT, M.OUT = snap, Path(tmp)
    try:
        M.fetch_snapshot(ShortFetch)
    except SystemExit as e:
        check("kratak dohvat prekida posao", "havana" in str(e), True)
        check("snapshot nije prepisan", json.loads(snap.read_text("utf-8"))["fetched_at"],
              "2026-07-24T00:00:00Z")
    else:
        FAILURES.append("kratak dohvat NIJE prekinuo posao — katalog bi bio pometen")
    finally:
        M.SNAPSHOT, M.OUT = prev_snapshot, prev_out

print("\nwalk-in trgovine iz shops.ts")
detected = M.walk_in_shops()
check("Tobacco Petica je prepoznata", "Tobacco Petica (Branimir)" in detected, True)
check("online trgovine nisu walk-in", "The Humidor" in detected, False)

if FAILURES:
    print(f"\nPALO: {len(FAILURES)}")
    for f in FAILURES:
        print(f"  ✗ {f}")
    sys.exit(1)
print("\nsve prolazi")
