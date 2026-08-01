#!/usr/bin/env python3
"""Unify truncated / parallel brand keys: Don Pepin, Aliados, The Oscar."""
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
NOTE = "orthography/house unify 2026-08-01 (Don Pepin / Aliados / The Oscar)"

PARENT_PEPIN = "Don Pépin García"

# stem → (child brand, parent, lines)
PATCHES: dict[str, tuple[str, str, dict]] = {
    "don-pepin": (
        "Don Pepin",
        PARENT_PEPIN,
        {
            "Clasicos 1950": {"line": "Clásicos 1950"},
            "Clasicos 1979": {"line": "Clásicos 1979"},
            "E.R.H": {"line": "Pepin Garcia E.R.H."},
            "Limited Edition Original 20th Anniversary 2023": {
                "line": "Original 20th Anniversary LE 2023"
            },
            "Original": {"line": "Pepin Garcia Original"},
            "Series JJ Selectos": {
                "line": "Pepin Garcia Serie JJ",
                "vitola": "Selectos",
            },
            "Series JJ Sublimes": {
                "line": "Pepin Garcia Serie JJ",
                "vitola": "Sublimes",
            },
            "VC": {"line": "Pepin Garcia Vegas Cubanas"},
            "vegas cubanas generosos": {
                "line": "Pepin Garcia Vegas Cubanas",
                "vitola": "Generosos",
            },
            "vegas cubanas invictos": {
                "line": "Pepin Garcia Vegas Cubanas",
                "vitola": "Invictos",
            },
            "vintage edition": {"line": "Pepin Garcia Vintage"},
        },
    ),
    "aliados": (
        "Aliados",
        "Cuba Aliados",
        {
            "Cabinet Edition": {"line": "Cabinet Edition"},
            "Original Blend": {"line": "Original Blend"},
        },
    ),
    "the-oscar": (
        "The Oscar",
        "Oscar Valladares",
        {
            "11": {"line": "The Oscar 11"},
            "connecticut": {"line": "The Oscar Connecticut"},
            "habano": {"line": "The Oscar Habano"},
            "maduro": {"line": "The Oscar Maduro"},
        },
    ),
}

# Clean redundant Neptune stubs already under Don Pépin García
DEST_LINE_PATCHES: dict[str, dict] = {
    "don-pepin-garcia": {
        "don pepin garcia black edition 1979": {"line": "Black Edition 1979"},
        "don pepin garcia black edition 2001 toro": {
            "line": "Black Edition 2001",
            "vitola": "Toro",
        },
        "don pepin garcia delicias": {"line": "Delicias"},
        "don pepin garcia exquisitos": {"line": "Exquisitos"},
        "don pepin garcia generosos": {
            "line": "Pepin Garcia Vegas Cubanas",
            "vitola": "Generosos",
        },
        "don pepin garcia imperiales": {"line": "Imperiales"},
        "don pepin garcia invictos": {
            "line": "Pepin Garcia Vegas Cubanas",
            "vitola": "Invictos",
        },
        "don pepin garcia lanceros": {"line": "Lanceros"},
        "don pepin garcia series jj 20th anniversary": {
            "line": "Pepin Garcia Serie JJ 20th Anniversary"
        },
        "don pepin garcia toro": {"line": "Toro", "vitola": "Toro"},
        "by epc": {"line": "by EPC"},  # noop if wrong file — kept out
    },
    "cuba-aliados": {
        "by epc": {"line": "by EPC"},
        "natural": {"line": "Natural"},
    },
}

ORPHANS = ["Don Pepin", "Aliados", "The Oscar"]

HOUSE_BLURBS = {
    PARENT_PEPIN: {
        "country": "Nikaragva",
        "founded": "2003",
        "blurb": {
            "hr": "José „Pepín” García — eponimna marka od 2003. (El Rey de los Habanos, Miami; My Father, Estelí). U katalogu stoji kao Don Pépin García; skraćeni unos „Don Pepin” spojen je ovamo, a ime linije ostaje na kartici (Original, Serie JJ, Vegas Cubanas…).",
            "en": "José “Pepín” García — namesake brand from 2003 (El Rey de los Habanos, Miami; My Father, Estelí). Catalogued as Don Pépin García; the truncated “Don Pepin” key is merged here, with the line name kept on the card (Original, Serie JJ, Vegas Cubanas…).",
        },
    },
    "Cuba Aliados": {
        "country": "Honduras",
        "founded": "1955",
        "blurb": {
            "hr": "Rolando Reyes Sr. — Havana 1955., kasnije Honduras; danas pod Olivom. Imenovane linije (Original Blend, Cabinet Edition, Limitado Zeppelin, Vintage…) stoje pod Cuba Aliados; kraći unos „Aliados” spojen je ovamo.",
            "en": "Rolando Reyes Sr. — Havana 1955, later Honduras; now under Oliva. Named lines (Original Blend, Cabinet Edition, Limitado Zeppelin, Vintage…) live under Cuba Aliados; the short “Aliados” key is merged here.",
        },
    },
    "Oscar Valladares": {
        "country": "Honduras",
        "founded": "2014",
        "blurb": {
            "hr": "Honduraška boutique kuća Oscara Vallade — slatko-začinski i moderni blendovi. Imenovana linija The Oscar (i srodne 2012 / Leaf linije) stoji pod Oscar Valladares; na kartici ostaje ime linije.",
            "en": "Oscar Valladares’ Honduran boutique house — sweet-spicy, modern blends. The Oscar named line (and related 2012 / Leaf lines) lives under Oscar Valladares; the line name stays on the card.",
        },
    },
}


def patch_file(
    stem: str,
    *,
    brand: str,
    rename: str | None,
    lines: dict,
    set_rename: bool,
) -> None:
    path = TAX / f"{stem}.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {"brand": brand, "lines": {}}
    data["brand"] = brand
    if set_rename:
        data["renameBrand"] = rename
    data["status"] = "done"
    data["reviewedAt"] = TODAY
    sources = list(data.get("sources") or [])
    if NOTE not in sources:
        sources.append(NOTE)
    data["sources"] = sources
    merged = dict(data.get("lines") or {})
    # drop bogus key if we accidentally put cuba remap here
    for k, v in lines.items():
        merged[k] = v
    data["lines"] = merged
    if "unresolved" in data and isinstance(data["unresolved"], list):
        data["unresolved"] = [
            u
            for u in data["unresolved"]
            if "truncated" not in str(u).lower() and "renameBrand later" not in str(u)
        ]
    for key in ("vitolaRenames", "shapes", "lineNotes"):
        data.setdefault(key, {})
    data.setdefault("keepSeparate", data.get("keepSeparate") or [])
    data.setdefault("unresolved", data.get("unresolved") or [])
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"patched {path.name}: brand={brand!r} rename={data.get('renameBrand')!r}")


def sync_brands(cigars: list, brands: dict) -> dict:
    used = {c["brand"] for c in cigars}
    for o in ORPHANS:
        if o not in used and o in brands:
            del brands[o]
            print(f"removed brands.json key {o!r}")
    for key, meta in HOUSE_BLURBS.items():
        brands[key] = meta
        print(f"updated blurb {key!r}")
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
        patch_file(stem, brand=child, rename=parent, lines=lines, set_rename=True)

    # destination cleanups (no rename)
    patch_file(
        "don-pepin-garcia",
        brand=PARENT_PEPIN,
        rename=None,
        lines={
            k: v
            for k, v in DEST_LINE_PATCHES["don-pepin-garcia"].items()
            if k != "by epc"
        },
        set_rename=False,
    )
    patch_file(
        "cuba-aliados",
        brand="Cuba Aliados",
        rename=None,
        lines=DEST_LINE_PATCHES["cuba-aliados"],
        set_rename=False,
    )

    print("running apply-taxonomy.py ...")
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
    print(f"cigars={len(cigars)} leftover={still}")
    return 0 if not still else 1


if __name__ == "__main__":
    raise SystemExit(main())
