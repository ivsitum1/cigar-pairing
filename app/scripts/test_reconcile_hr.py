# -*- coding: utf-8 -*-
"""Testovi za reconcile-hr-availability.

Pokretanje (iz app/):
    python scripts/test_reconcile_hr.py

Namjerno bez pytesta — CI za Python korake ovdje vrti gole skripte.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import types
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


def run(cigars, present, walk_in=frozenset(), present_vitola=None):
    """reconcile() s podmetnutim walk_in skupom."""
    original = M.walk_in_shops
    M.walk_in_shops = lambda: set(walk_in)
    try:
        return M.reconcile(cigars, present, FakeSync, present_vitola)
    finally:
        M.walk_in_shops = original


print("otkrivanje nove ponude")
# Cigara bez ijedne HR oznake koju trgovina sada drzi -> mora dobiti HR.
c = cig(id="cig-perla", brand="Perla", line="de Calvano")
removed, added = run([c], {("perla", "de calvano"): {"Havana Cigar Shop"}})
check("nova ponuda dobiva availabilityHR", c["availabilityHR"], ["Havana Cigar Shop"])
check("nova ponuda dobiva markets.HR", "HR" in c["markets"], True)
check("prijavljena je kao dodana", [a["id"] for a in added], ["cig-perla"])

# Bez poklapanja u snapshotu ne smije se nista izmisliti.
c = cig(id="cig-nema", brand="Nema", line="Ovoga")
removed, added = run([c], {})
check("bez poklapanja ostaje bez HR", (c["availabilityHR"], "HR" in c["markets"]), ([], False))
check("i nije prijavljena kao dodana", added, [])

print("\npresent_vitola samo za shopove bez imenovane linije")
try:
    import requests  # noqa: F401
    import bs4  # noqa: F401
except ImportError:
    _req = types.ModuleType("requests")
    _req.Session = type("Session", (), {})  # type: ignore[attr-defined]
    sys.modules["requests"] = _req
    _bs4 = types.ModuleType("bs4")
    _bs4.BeautifulSoup = object  # type: ignore[attr-defined]
    sys.modules["bs4"] = _bs4
spec_sync_vit = importlib.util.spec_from_file_location(
    "sync_hr_shops_vit", ROOT / "sync-hr-shops.py"
)
sync_vit = importlib.util.module_from_spec(spec_sync_vit)
assert spec_sync_vit.loader is not None
spec_sync_vit.loader.exec_module(sync_vit)
cigars_stub = json.loads(
    (ROOT.parent / "src" / "data" / "cigars.json").read_text(encoding="utf-8")
)
_, by_vitola_opus = M.build_present(
    sync_vit,
    {"havana": [{"name": "A. Fuente Fuente Fuente OpusX Robusto"}], "humidor": []},
    cigars_stub,
)
check(
    "opusx robusto nije u present_vitola",
    ("arturo fuente", "robusto") in by_vitola_opus,
    False,
)
_, by_vitola_cusano = M.build_present(
    sync_vit,
    {"havana": [{"name": "Bundle Selection by Cusano Robusto"}], "humidor": []},
    cigars_stub,
)
check(
    "cusano robusto jest u present_vitola (shop bez imenovane linije)",
    ("cusano", "robusto") in by_vitola_cusano,
    True,
)

print("\nmarket discovery + brand/vitola fallback")
# catalogSource=market ranije je preskakao discovery — mora dobiti HR.
c = cig(
    id="cig-cain-646",
    brand="Cain Daytona",
    line="646",
    vitola="Corona",
    vitolas=[{"name": "Corona"}],
    catalogSource="market",
    markets=["EU", "USA", "WW"],
)
removed, added = run(
    [c],
    {},  # line "646" nije u snapshotu
    present_vitola={("cain daytona", "corona"): {"Havana Cigar Shop"}},
)
check("market+vitola dobiva Havana", c["availabilityHR"], ["Havana Cigar Shop"])
check("market+vitola dobiva markets.HR", "HR" in c["markets"], True)
check("market+vitola prijavljen kao dodan", [a["id"] for a in added], ["cig-cain-646"])

# Market s walk-in bez HR u markets — mora dobiti HR.
c = cig(
    id="cig-cao",
    brand="CAO",
    line="Bones",
    catalogSource="market",
    availabilityHR=["Tobacco Petica (Branimir)"],
    markets=["EU", "WW"],
)
removed, added = run([c], {}, walk_in={"Tobacco Petica (Branimir)"})
check("market walk-in ostaje", c["availabilityHR"], ["Tobacco Petica (Branimir)"])
check("market walk-in dobiva markets.HR", "HR" in c["markets"], True)

print("\nuklanjanje zastarjele ponude")
c = cig(id="cig-stara", availabilityHR=["Havana Cigar Shop"], markets=["HR", "EU", "WW"])
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
    {("don tomas", "bundle"): {"Havana Cigar Shop"}},
    walk_in={"Tobacco Petica (Branimir)"},
)
check(
    "walk-in i online stoje zajedno",
    c["availabilityHR"],
    ["Havana Cigar Shop", "Tobacco Petica (Branimir)"],
)

# Online trgovina koja nestane iz snapshota se mice, walk-in ostaje.
c = cig(
    id="cig-mix",
    availabilityHR=["Havana Cigar Shop", "Tobacco Petica (Branimir)"],
    markets=["HR", "EU", "WW"],
)
removed, added = run([c], {}, walk_in={"Tobacco Petica (Branimir)"})
check("online otpada, walk-in ostaje", c["availabilityHR"], ["Tobacco Petica (Branimir)"])

print("\nzastita od neuspjelog dohvata")
check("prag je definiran", 0 < M.MIN_FETCH_RATIO < 1, True)
check("prag uklanjanja je definiran", 0 < M.MAX_REMOVAL_RATIO < 1, True)

print("\nsnapshot + povrat cigars.json")
with tempfile.TemporaryDirectory() as tmp:
    cigars_path = Path(tmp) / "cigars.json"
    backup_path = Path(tmp) / "hr_cigars_pre_reconcile.json"
    cigars_path.write_text(
        json.dumps([cig(id="cig-a", markets=["HR", "EU"], availabilityHR=["Havana Cigar Shop"])]),
        encoding="utf-8",
    )
    prev_cigars, prev_backup, prev_out = M.CIGARS, M.CIGARS_BACKUP, M.OUT
    M.CIGARS, M.CIGARS_BACKUP, M.OUT = cigars_path, backup_path, Path(tmp)
    try:
        M.backup_cigars()
        check("sigurnosna kopija postoji", backup_path.exists(), True)
        bad = [cig(id="cig-b", markets=["HR"], availabilityHR=[])]
        try:
            M.validate_reconcile(bad, removed=[], hr_before=1)
        except SystemExit:
            pass
        else:
            FAILURES.append("validate_reconcile nije odbio HR bez izvora")
        restored = M.rollback_cigars()
        check("povrat uspješan", restored, True)
        check(
            "cigars.json vraćen",
            json.loads(cigars_path.read_text("utf-8"))[0]["id"],
            "cig-a",
        )
    finally:
        M.CIGARS, M.CIGARS_BACKUP, M.OUT = prev_cigars, prev_backup, prev_out

print("\nzastita od masovnog uklanjanja")
try:
    M.validate_reconcile([], removed=[{}] * 100, hr_before=100)
except SystemExit as e:
    check("masovno uklanjanje prekida posao", "sumnjivo" in str(e).lower() or "maknuo" in str(e), True)
else:
    FAILURES.append("validate_reconcile nije odbio masovno uklanjanje")


class ShortFetch:
    """Trgovina koja odgovori, ali s desetinom kataloga."""

    @staticmethod
    def fetch_havana_catalog():
        return [{"name": f"p{i}"} for i in range(40)]

    @staticmethod
    def fetch_humidor_catalog():
        return [{"name": f"h{i}"} for i in range(300)]


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

print("\nsync-hr-shops Cusano parser")
# CI Python job does not install scraper deps; stub before loading the module.
try:
    import requests  # noqa: F401
    import bs4  # noqa: F401
except ImportError:
    _req = types.ModuleType("requests")
    _req.Session = type("Session", (), {})  # type: ignore[attr-defined]
    sys.modules["requests"] = _req
    _bs4 = types.ModuleType("bs4")
    _bs4.BeautifulSoup = object  # type: ignore[attr-defined]
    sys.modules["bs4"] = _bs4
spec_sync = importlib.util.spec_from_file_location(
    "sync_hr_shops", ROOT / "sync-hr-shops.py"
)
sync = importlib.util.module_from_spec(spec_sync)
assert spec_sync.loader is not None
spec_sync.loader.exec_module(sync)

check(
    "Petit Panatela nije linija Petit",
    sync.line_name_from_product("Cusano", "Bundle Selection by Cusano Petit Panatela"),
    "Cusano",
)
check(
    "Short Robusto prazan rest pada na brand (LINE_RULES hvata id)",
    sync.line_name_from_product("Cusano", "Bundle Selection by Cusano Short Robusto"),
    "Cusano",
)
check(
    "Petit Panatela vitola",
    sync.vitola_from_product("Bundle Selection by Cusano Petit Panatela", "Cusano"),
    "Petit Panatela",
)
cid = sync.detect_line_id("Cusano", "Bundle Selection by Cusano Robusto")
check("Cusano HR proizvod ide na Bundle Selection", cid, "cig-cusano-bundle-selection")

live_ids = {
    c["id"]
    for c in json.loads((ROOT.parent / "src" / "data" / "cigars.json").read_text(encoding="utf-8"))
}
stale = []
for _brand, _kw, rule_id in sync.LINE_RULES:
    if not rule_id:
        continue
    resolved = sync.resolve_catalog_id(rule_id)
    if resolved not in live_ids:
        stale.append(f"{rule_id} -> {resolved}")
check("LINE_RULES ciljevi su živi id-evi", stale, [])

if FAILURES:
    print(f"\nPALO: {len(FAILURES)}")
    for f in FAILURES:
        print(f"  ✗ {f}")
    sys.exit(1)
print("\nsve prolazi")
