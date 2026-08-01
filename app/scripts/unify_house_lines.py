#!/usr/bin/env python3
"""Unify house-line brands under parent houses with clear line labels.

Crowned Heads / Foundation / Dunbarton T&T children become brand=house;
line names keep (or gain) the marque so Brand › Line reads clearly.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
TAX = HERE / "data" / "taxonomy"
DATA = HERE.parent / "src" / "data"

TODAY = date.today().isoformat()
NOTE = "house-line unify 2026-08-01 (CH / Foundation / Dunbarton — mark as named lines)"

# stem → (child brand key, parent, lines map)
PATCHES: dict[str, tuple[str, str, dict]] = {
    # --- Crowned Heads ---
    "four-kicks": (
        "Four Kicks",
        "Crowned Heads",
        {
            "Kicks": {"line": "Four Kicks"},
            "Four Kicks": {"line": "Four Kicks"},
            "Mule Kick LE 2022": {"line": "Four Kicks Mule Kick LE 2022"},
        },
    ),
    "la-imperiosa": (
        "La Imperiosa",
        "Crowned Heads",
        {"La Imperiosa": {"line": "La Imperiosa"}},
    ),
    "juarez": (
        "Juarez",
        "Crowned Heads",
        {
            "Limited Edition 2025 Bulldozer": {
                "line": "Juarez Limited Edition 2025 Bulldozer"
            },
        },
    ),
    "mil-dias": (
        "Mil Dias",
        "Crowned Heads",
        {
            "Dias": {"line": "Mil Dias"},
            "des deux le 2025 61 8 42": {"line": "Mil Dias Des Deux LE 2025"},
        },
    ),
    "luminosa": (
        "Luminosa",
        "Crowned Heads",
        {"Luminosa": {"line": "Luminosa"}},
    ),
    # --- Foundation ---
    "charter-oak": (
        "Charter Oak",
        "Foundation",
        {
            "Broadleaf": {"line": "Charter Oak", "vitola": "Broadleaf"},
            "Connecticut": {"line": "Charter Oak", "vitola": "Connecticut"},
        },
    ),
    "the-tabernacle": (
        "The Tabernacle",
        "Foundation",
        {
            "Corona": {"line": "Tabernacle", "vitola": "Corona"},
            "CT Broadleaf": {"line": "Tabernacle", "vitola": "CT Broadleaf"},
            "david": {"line": "Tabernacle", "vitola": "David"},
            "Doble": {"line": "Tabernacle", "vitola": "Doble"},
            "goliath": {"line": "Tabernacle", "vitola": "Goliath"},
            "Havana Seed CT 142": {
                "line": "Tabernacle",
                "vitola": "Havana Seed CT 142",
            },
            "Lancero": {"line": "Tabernacle", "vitola": "Lancero"},
            "Robusto": {"line": "Tabernacle", "vitola": "Robusto"},
            "Toro": {"line": "Tabernacle", "vitola": "Toro"},
            "Torpedo": {"line": "Tabernacle", "vitola": "Torpedo"},
        },
    ),
    "olmec": (
        "Olmec",
        "Foundation",
        {
            "Claro": {"line": "Olmec", "vitola": "Claro"},
            "Maduro": {"line": "Olmec", "vitola": "Maduro"},
        },
    ),
    "menelik": (
        "Menelik",
        "Foundation",
        {"Petite": {"line": "Menelik", "vitola": "Petite"}},
    ),
    "el-gueguense": (
        "El Gueguense",
        "Foundation",
        {
            "El Güegüense": {"line": "El Güegüense"},
            "huaco": {"line": "El Güegüense", "vitola": "Huaco"},
        },
    ),
    "wise-man": (
        "Wise Man",
        "Foundation",
        {
            "Corojo": {"line": "Wise Man", "vitola": "Corojo"},
            "Maduro": {"line": "Wise Man", "vitola": "Maduro"},
        },
    ),
    # --- Dunbarton T&T ---
    "sobremesa": (
        "Sobremesa",
        "Dunbarton T&T",
        {
            "Fino": {"line": "Sobremesa Fino"},
            "Largo": {"line": "Sobremesa Largo"},
            "Short": {"line": "Sobremesa Short"},
            "brulee": {"line": "Sobremesa Brûlée"},
            "solita el americano": {"line": "Sobremesa Solita El Americano"},
            "solita elegantes en cedros": {
                "line": "Sobremesa Solita Elegantes en Cedros"
            },
            "solita gran imperiales": {
                "line": "Sobremesa Solita Gran Imperiales"
            },
            "solita red": {"line": "Sobremesa Solita Red"},
            "solita tiempo": {"line": "Sobremesa Solita Tiempo"},
            "tapa negra 6 52": {"line": "Sobremesa Tapa Negra"},
            "tapa negra gorda 55 8 48": {"line": "Sobremesa Tapa Negra Gorda"},
        },
    ),
    "mi-querida": (
        "Mi Querida",
        "Dunbarton T&T",
        {
            "Muy": {"line": "Mi Querida Muy", "vitola": "Grande"},
            "ancho corto": {"line": "Mi Querida Ancho Corto"},
            "ancho largo": {"line": "Mi Querida Ancho Largo"},
            "black papasaka": {"line": "Mi Querida Black Papasaka"},
            "black sakakhan": {"line": "Mi Querida Black Sakakhan"},
            "black unicorn": {"line": "Mi Querida Black Unicorn"},
            "fino largo": {"line": "Mi Querida Fino Largo"},
            "gordita": {"line": "Mi Querida Gordita"},
            "gorila 6 60": {"line": "Mi Querida Gorila"},
            "gran bufalo": {"line": "Mi Querida Gran Búfalo"},
            "triqui traca no 448": {"line": "Mi Querida Triqui Traca No. 448"},
            "triqui traca no 552": {"line": "Mi Querida Triqui Traca No. 552"},
            "triqui traca no 648": {"line": "Mi Querida Triqui Traca No. 648"},
            "triqui traca no 652": {"line": "Mi Querida Triqui Traca No. 652"},
            "triqui traca no 764": {"line": "Mi Querida Triqui Traca No. 764"},
        },
    ),
    "querida": (
        "Querida",
        "Dunbarton T&T",
        {"Tripa Larga": {"line": "Mi Querida Tripa Larga"}},
    ),
}

ORPHANS = [
    "Four Kicks",
    "La Imperiosa",
    "Juarez",
    "Mil Dias",
    "Luminosa",
    "Charter Oak",
    "The Tabernacle",
    "Olmec",
    "Menelik",
    "El Gueguense",
    "Wise Man",
    "Sobremesa",
    "Mi Querida",
    "Querida",
]

HOUSE_BLURBS = {
    "Crowned Heads": {
        "country": "Nikaragva / SAD",
        "founded": "2011",
        "blurb": {
            "hr": "Boutique kuća iz Nashvillea (Jon Huber) koja surađuje s tvornicama My Father i Tabacalera Pichardo. Imenovane linije — Four Kicks, La Imperiosa, Juarez, Mil Días, Luminosa, Le Carême — u katalogu stoje pod Crowned Heads; na kartici ostaje ime linije, ne zasebna marka.",
            "en": "A Nashville boutique house (Jon Huber) working with My Father and Tabacalera Pichardo. Named lines — Four Kicks, La Imperiosa, Juarez, Mil Días, Luminosa, Le Carême — live under Crowned Heads; the line name stays on the card, not as a separate brand.",
        },
    },
    "Foundation": {
        "country": "Nikaragva",
        "founded": "2015",
        "blurb": {
            "hr": "Nicholas Melillo (Foundation Cigar Co.), bivši 'duhanski nos' Drew Estatea. Imenovane linije — Charter Oak, Tabernacle, Olmec, Menelik, El Güegüense, Wise Man — u katalogu stoje pod Foundation; na kartici ostaje ime linije.",
            "en": "Nicholas Melillo (Foundation Cigar Co.), Drew Estate's former 'tobacco nose'. Named lines — Charter Oak, Tabernacle, Olmec, Menelik, El Güegüense, Wise Man — live under Foundation; the line name stays on the card.",
        },
    },
    "Dunbarton T&T": {
        "country": "Nikaragva",
        "founded": "2015",
        "blurb": {
            "hr": "Steve Saka (Dunbarton Tobacco & Trust). Imenovane linije Sobremesa i Mi Querida u katalogu stoje pod Dunbarton T&T; na kartici ostaje ime linije (npr. Sobremesa Fino, Mi Querida Ancho Corto), ne zasebna marka.",
            "en": "Steve Saka (Dunbarton Tobacco & Trust). Named lines Sobremesa and Mi Querida live under Dunbarton T&T; the line name stays on the card (e.g. Sobremesa Fino, Mi Querida Ancho Corto), not as a separate brand.",
        },
    },
}


def patch_file(stem: str, brand: str, rename: str, lines: dict) -> None:
    path = TAX / f"{stem}.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {"brand": brand, "lines": {}}
    data["brand"] = brand
    data["renameBrand"] = rename
    data["status"] = "done"
    data["reviewedAt"] = TODAY
    sources = list(data.get("sources") or [])
    if NOTE not in sources:
        sources.append(NOTE)
    data["sources"] = sources
    merged = dict(data.get("lines") or {})
    merged.update(lines)
    data["lines"] = merged
    for key in ("vitolaRenames", "shapes", "lineNotes"):
        data.setdefault(key, {})
    data.setdefault("keepSeparate", [])
    data.setdefault("unresolved", [])
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"patched {path.name}: {brand!r} -> {rename!r} ({len(lines)} line rules)")


def sync_brands(cigars: list, brands: dict) -> dict:
    used = {c["brand"] for c in cigars}
    for o in ORPHANS:
        if o not in used and o in brands:
            del brands[o]
            print(f"removed brands.json key {o!r}")
    for key, meta in HOUSE_BLURBS.items():
        brands[key] = meta
        print(f"updated house blurb {key!r}")
    for b in used:
        if b not in brands:
            sample = next(c for c in cigars if c["brand"] == b)
            brands[b] = {
                "country": sample.get("country") or "—",
                "founded": "—",
                "blurb": {"hr": f"Marka {b}.", "en": f"Brand {b}."},
            }
            print(f"added missing brand {b!r}")
    return dict(sorted(brands.items(), key=lambda kv: kv[0].casefold()))


def main() -> int:
    for stem, (child, parent, lines) in PATCHES.items():
        patch_file(stem, child, parent, lines)

    print("running apply-taxonomy.py …")
    r = subprocess.run(
        [sys.executable, str(HERE / "apply-taxonomy.py")],
        cwd=str(HERE.parent),
    )
    if r.returncode != 0:
        return r.returncode

    cigars = json.loads((DATA / "cigars.json").read_text(encoding="utf-8"))
    brands = json.loads((DATA / "brands.json").read_text(encoding="utf-8"))
    brands = sync_brands(cigars, brands)
    (DATA / "brands.json").write_text(
        json.dumps(brands, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    still = sorted({c["brand"] for c in cigars if c["brand"] in ORPHANS})
    print(f"cigars={len(cigars)} leftover_child_brands={still}")
    return 0 if not still else 1


if __name__ == "__main__":
    raise SystemExit(main())
