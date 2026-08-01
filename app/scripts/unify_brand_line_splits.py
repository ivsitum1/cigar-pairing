#!/usr/bin/env python3
"""Patch taxonomy for line-as-brand splits, then apply-taxonomy + brands sync."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
TAX = HERE / "data" / "taxonomy"
DATA = HERE.parent / "src" / "data"
ROOT = HERE.parent.parent

TODAY = date.today().isoformat()

# child taxonomy file stem → (renameBrand, lines map)
PATCHES: dict[str, tuple[str, dict]] = {
    "argyle-fumas": (
        "Argyle",
        {
            "Connecticut": {"line": "Fumas Connecticut"},
            "Fumas": {"line": "Fumas"},
        },
    ),
    "bahia-blu": (
        "Bahia",
        {"Blu": {"line": "Blu"}},
    ),
    "cain-black": (
        "Cain",
        {"654": {"line": "Black", "vitola": "654"}},
    ),
    "cain-ct": (
        "Cain",
        {"Connecticut CT 654": {"line": "Connecticut CT", "vitola": "654"}},
    ),
    "cain-daytona": (
        "Cain",
        {
            "550": {"line": "Daytona", "vitola": "550"},
            "646": {"line": "Daytona", "vitola": "646"},
            "654": {"line": "Daytona", "vitola": "654"},
            "Double 660": {"line": "Daytona", "vitola": "Double 660"},
        },
    ),
    "cain-f-1": (
        "Cain",
        {"F 654": {"line": "F", "vitola": "654"}},
    ),
    "don-lino-fumas": (
        "Don Lino",
        {
            "Connecticut": {"line": "Fumas Connecticut"},
            "Fumas": {"line": "Fumas"},
        },
    ),
    "nat-sherman-host": (
        "Nat Sherman",
        {"Hanover": {"line": "Host", "vitola": "Hanover"}},
    ),
    "nat-sherman-metropolitan": (
        "Nat Sherman",
        {
            "Connecticut": {"line": "Metropolitan Connecticut"},
            "Habano": {"line": "Metropolitan Habano"},
            "Maduro": {"line": "Metropolitan Maduro"},
        },
    ),
    "nat-sherman-timeless": (
        "Nat Sherman",
        {
            "2019 limited edition": {"line": "Timeless 2019 Limited Edition"},
            "Prestige": {"line": "Timeless Prestige"},
            "Supreme 652": {"line": "Timeless Supreme 652"},
            "nicaragua 652t": {"line": "Timeless Nicaragua 652T"},
            "nicaragua 749": {"line": "Timeless Nicaragua 749"},
            "sterling": {"line": "Timeless Sterling"},
            "supreme 546": {"line": "Timeless Supreme 546"},
            "supreme 556": {"line": "Timeless Supreme 556"},
        },
    ),
    "timeless": (
        "Nat Sherman",
        {
            "Prestige": {"line": "Timeless Prestige"},
            "Sterling": {"line": "Timeless Sterling"},
        },
    ),
    "lunatic": (
        "JFR",
        {
            "Classic": {"line": "Lunatic Classic"},
            "El Loquito": {"line": "Lunatic El Loquito"},
            "Maduro": {"line": "Lunatic Maduro"},
        },
    ),
}

# Destination-side line cleanup (Cain Neptune stubs + La Aroma EE #5)
DEST_LINE_PATCHES: dict[str, dict] = {
    "cain": {
        "habano 550": {"line": "Habano", "vitola": "550"},
        "Habano 654": {"line": "Habano", "vitola": "654"},
        "maduro 550": {"line": "Maduro", "vitola": "550"},
        "Maduro 654": {"line": "Maduro", "vitola": "654"},
        "maduro 660": {"line": "Maduro", "vitola": "660"},
        "Serie F 550": {"line": "Serie F", "vitola": "550"},
        "Serie F Double 660": {"line": "Serie F", "vitola": "Double 660"},
        "f 654t": {"line": "F", "vitola": "654T"},
        "f 660": {"line": "F", "vitola": "660"},
        "f nub 460": {"line": "F", "vitola": "Nub 460"},
        "nub habano 460": {"line": "Habano", "vitola": "Nub 460"},
        "nub maduro 460": {"line": "Maduro", "vitola": "Nub 460"},
    },
    "la-aroma-de-cuba": {
        "edicion especial no 5": {"line": "Edición Especial #5"},
        "Edición Especial No. 5": {"line": "Edición Especial #5"},
    },
}


def patch_file(
    stem: str,
    *,
    brand: str,
    rename: str | None,
    lines: dict,
    note: str,
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
    if note not in sources:
        sources.append(note)
    data["sources"] = sources
    merged_lines = dict(data.get("lines") or {})
    merged_lines.update(lines)
    data["lines"] = merged_lines
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"patched {path.name} brand={brand!r} renameBrand={data.get('renameBrand')!r} lines={len(merged_lines)}")


def sync_brands(cigars: list, brands: dict) -> dict:
    used = {c["brand"] for c in cigars}
    # drop orphan child brands created by splits
    orphans = [
        "Argyle Fumas",
        "Bahia Blu",
        "Cain Black",
        "Cain Ct",
        "Cain Daytona",
        "Cain F. 1",
        "Don Lino Fumas",
        "Nat Sherman Host",
        "Nat Sherman Metropolitan",
        "Nat Sherman Timeless",
        "Timeless",
        "Lunatic",
    ]
    for o in orphans:
        if o not in used and o in brands:
            del brands[o]
            print(f"removed brands.json key {o!r}")
    for b in used:
        if b not in brands:
            sample = next(c for c in cigars if c["brand"] == b)
            brands[b] = {
                "country": sample.get("country") or "—",
                "founded": "—",
                "blurb": {
                    "hr": f"Marka {b}.",
                    "en": f"Brand {b}.",
                },
            }
            print(f"added missing brand {b!r}")
    return brands


CHILD_BRANDS = {
    "argyle-fumas": "Argyle Fumas",
    "bahia-blu": "Bahia Blu",
    "cain-black": "Cain Black",
    "cain-ct": "Cain Ct",
    "cain-daytona": "Cain Daytona",
    "cain-f-1": "Cain F. 1",
    "don-lino-fumas": "Don Lino Fumas",
    "nat-sherman-host": "Nat Sherman Host",
    "nat-sherman-metropolitan": "Nat Sherman Metropolitan",
    "nat-sherman-timeless": "Nat Sherman Timeless",
    "timeless": "Timeless",
    "lunatic": "Lunatic",
}


def main() -> int:
    note = "brand-line-split unify 2026-08-01 (Argyle/Bahia/Cain/Don Lino/Nat Sherman/Lunatic)"
    for stem, (parent, lines) in PATCHES.items():
        patch_file(
            stem,
            brand=CHILD_BRANDS[stem],
            rename=parent,
            lines=lines,
            note=note,
            set_rename=True,
        )
    patch_file(
        "cain",
        brand="Cain",
        rename=None,
        lines=DEST_LINE_PATCHES["cain"],
        note=note,
        set_rename=False,
    )
    patch_file(
        "la-aroma-de-cuba",
        brand="La Aroma de Cuba",
        rename=None,
        lines=DEST_LINE_PATCHES["la-aroma-de-cuba"],
        note=note,
        set_rename=False,
    )

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

    children = list(CHILD_BRANDS.values())
    still = sorted({c["brand"] for c in cigars if c["brand"] in children})
    print(f"cigars={len(cigars)} leftover_child_brands={still}")
    return 0 if not still else 1


if __name__ == "__main__":
    raise SystemExit(main())
