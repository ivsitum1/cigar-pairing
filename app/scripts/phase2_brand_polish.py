#!/usr/bin/env python3
"""Polish truncated brand keys (Phase 2 leftovers) with verified renameBrand + line remaps.

Only 1:1 verified renames. Casa stays unresolved (mixed Casa Cuevas / de Alegría / de Torres).
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from taxonomy_lib import TAXONOMY_DIR, BRANDS_PATH, brand_slug, load_json, write_json

# current brand key → (canonical name, line remaps or None to keep, sources, country, founded, blurb)
# blurb used only when brands.json lacks the canonical entry
RENAMES: dict[str, dict] = {
    "Adv": {
        "renameBrand": "ADVentura",
        "sources": [
            "https://www.neptunecigar.com/adventura-cigar",
            "https://halfwheel.com/adventura-barbarrojas-invasion-corona/417380/",
        ],
        "country": "Dominikanska Republika",
        "founded": "2016",
        "blurb": {
            "hr": "ADVentura (ADV & McKay) — Marcel Knobel i Henderson Ventura; Dominikanska Republika (Tabacalera William Ventura) od 2016./2017.",
            "en": "ADVentura (ADV & McKay) — Marcel Knobel and Henderson Ventura; Dominican Republic (Tabacalera William Ventura) from 2016/2017.",
        },
    },
    "Csc": {
        "renameBrand": "CSC",
        "sources": [
            "https://cigarseedcompany.eu/en/collections/cigars",
            "https://www.cigarworld.de/en/zigarren/nicaragua/csc-fire-oak-90016477",
        ],
        "country": "Nikaragva",
        "founded": "2023",
        "blurb": {
            "hr": "CSC (Cigar Seed Company) — nikaragvanske linije (Fire Oak, Apache, Doble Capa); EU distribucija iz Pforzheima.",
            "en": "CSC (Cigar Seed Company) — Nicaraguan lines (Fire Oak, Apache, Doble Capa); EU distribution from Pforzheim.",
        },
    },
    "Dbl": {
        "renameBrand": "DBL",
        "sources": [
            "https://www.dblcigars.com/el-final/",
            "https://halfwheel.com/dbl-el-final-debuting-at-pca-2022/410694/",
        ],
        "country": "Dominikanska Republika",
        "founded": "2013",
        "blurb": {
            "hr": "DBL Cigars (Francisco Almonte) — Tabacalera DBL, Tamboril, Dominikanska Republika; El Final i druge linije.",
            "en": "DBL Cigars (Francisco Almonte) — Tabacalera DBL, Tamboril, Dominican Republic; El Final and other lines.",
        },
    },
    "K.": {
        "renameBrand": "Karen Berger",
        "line_remaps": {
            "K by Karen Berger Cameroon": {"line": "Cameroon"},
            "K by Karen Berger Connecticut": {"line": "Connecticut"},
            "K by Karen Berger Habano": {"line": "Habano"},
        },
        "sources": ["https://karenbergercigars.com/our-cigars-2/", "https://humidor.hr/"],
    },
    "Omar": {
        "renameBrand": "Omar Ortez",
        "line_remaps": {
            "Rodriguez Form 50": {"line": "Form 50"},
            "Rodriguez Reserva Escogida": {"line": "Reserva Escogida"},
        },
        "sources": ["https://www.cigarcoop.com/", "existing Omar Ortez taxonomy"],
    },
    "Sons": {
        "renameBrand": "Sons of Anarchy",
        "line_remaps": {
            "of Anarchy Black Crown": {"line": "Black Crown"},
        },
        "sources": ["https://www.cigarsinternational.com/"],
        "country": "Honduras",
        "founded": "2013",
        "blurb": {
            "hr": "Sons of Anarchy — licencirana marka (TV serija); honduranska produkcija, Black Crown linija.",
            "en": "Sons of Anarchy — licensed TV brand; Honduran production, Black Crown line.",
        },
    },
    "Jesus": {
        "renameBrand": "Jesus Fuego",
        "line_remaps": {
            "Fuego Origen Natural Spirit of Caribe": {"line": "Origen Natural Spirit of Caribe"},
        },
        "sources": [
            "https://www.cigarworld.de/en/zigarren/nicaragua/jesus-fuego-origen-natural-90013473",
        ],
        "country": "Nikaragva",
        "founded": "2006",
        "blurb": {
            "hr": "Jesus Fuego / J. Fuego — blender Jesus Fuego; Origen i druge nikaragvanske/honduranske linije.",
            "en": "Jesus Fuego / J. Fuego — blender Jesus Fuego; Origen and other Nicaraguan/Honduran lines.",
        },
    },
    "Jas": {
        "renameBrand": "Jas Sum Kral",
        "line_remaps": {
            "Sum Kral Red Knight": {"line": "Red Knight"},
        },
        "sources": [
            "https://developingpalates.com/reviews/cigar-reviews/team-cigar-review-jas-sum-kral-red-knight-robusto/",
        ],
        "country": "Nikaragva",
        "founded": "2015",
        "blurb": {
            "hr": "Jas Sum Kral — Riste Ristevski; nikaragvanske boutique linije (Red Knight i dr.).",
            "en": "Jas Sum Kral — Riste Ristevski; Nicaraguan boutique lines (Red Knight and others).",
        },
    },
    "Il": {
        "renameBrand": "Il Padrino",
        "line_remaps": {
            "Padrino Luigi": {"line": "Luigi"},
        },
        "sources": ["product catalogue / Costa Rica Il Padrino Luigi"],
        "country": "Kostarika",
        "founded": "2021",
        "blurb": {
            "hr": "Il Padrino — kostarikanska marka; linija Luigi.",
            "en": "Il Padrino — Costa Rican brand; Luigi line.",
        },
    },
    "Rosa": {
        "renameBrand": "Rosa Nicaragua",
        "line_remaps": {
            "Nicaragua Connecticut": {"line": "Connecticut"},
            "Nicaragua Esteli": {"line": "Esteli"},
            "Nicaragua Jalapa": {"line": "Jalapa"},
        },
        "sources": [
            "https://www.cigarworld.de/rosa-nicaragua",
            "https://www.hacico.de/en/rosa-nicaragua",
        ],
        "country": "Nikaragva",
        "founded": "2011",
        "blurb": {
            "hr": "Rosa Nicaragua — Ralf Westerwick / Casa de Alegría (Estelí); medium-filler linije Connecticut, Estelí, Jalapa.",
            "en": "Rosa Nicaragua — Ralf Westerwick / Casa de Alegría (Estelí); medium-filler Connecticut, Estelí, Jalapa lines.",
        },
    },
    "Jfr": {
        "renameBrand": "JFR",
        "sources": ["https://humidor.hr/hr/proizvod/jfr-connecticut-robusto-5%c2%bd-x-50/"],
        "country": "Nikaragva",
        "founded": "—",
        "blurb": {
            "hr": "JFR — Aganorsa Leaf (Nicaragua); Connecticut i druge linije.",
            "en": "JFR — Aganorsa Leaf (Nicaragua); Connecticut and other lines.",
        },
    },
    "G.": {
        "renameBrand": "De Graaff",
        "line_remaps": {
            "De Graaff mediumfiller": {"line": "Mediumfiller"},
        },
        "sources": ["product catalogue — De Graaff mediumfiller"],
        "country": "Kostarika",
        "founded": "1859",
        "blurb": {
            "hr": "De Graaff — povijesna nizozemska/kostarikanska marka; mediumfiller linije.",
            "en": "De Graaff — historic Dutch/Costa Rican brand; mediumfiller lines.",
        },
    },
}


def patch_tax_file(brand: str, spec: dict) -> Path:
    path = TAXONOMY_DIR / f"{brand_slug(brand)}.json"
    data = load_json(path, {}) or {}
    if not data:
        data = {
            "brand": brand,
            "status": "done",
            "reviewedAt": "2026-07-24",
            "sources": [],
            "lines": {},
            "vitolaRenames": {},
            "shapes": {},
            "keepSeparate": [],
            "lineNotes": {},
            "unresolved": [],
        }
    data["brand"] = brand
    data["renameBrand"] = spec["renameBrand"]
    data["status"] = "done"
    data["reviewedAt"] = "2026-07-24"
    srcs = list(data.get("sources") or [])
    for s in spec.get("sources") or []:
        if s not in srcs:
            srcs.append(s)
    if "brand-polish truncated rename" not in srcs:
        srcs.append("brand-polish truncated rename")
    data["sources"] = srcs

    lines = dict(data.get("lines") or {})
    for old, rem in (spec.get("line_remaps") or {}).items():
        lines[old] = rem
    data["lines"] = lines
    write_json(path, data)
    return path


def ensure_brands_json() -> None:
    brands = load_json(BRANDS_PATH, {}) or {}
    for old, spec in RENAMES.items():
        canon = spec["renameBrand"]
        if canon not in brands:
            if old in brands:
                brands[canon] = deepcopy(brands[old])
            else:
                brands[canon] = {
                    "country": spec.get("country") or "—",
                    "founded": spec.get("founded") or "—",
                    "blurb": spec.get("blurb") or {"hr": canon, "en": canon},
                }
        # drop truncated key once canonical exists (integrity: no orphan brands.json)
        if old in brands and old != canon:
            del brands[old]
    write_json(BRANDS_PATH, brands)


def note_casa_unresolved() -> None:
    path = TAXONOMY_DIR / "casa.json"
    data = load_json(path, {}) or {}
    unresolved = list(data.get("unresolved") or [])
    note = (
        "Truncation mixes multiple makers under Casa: Culinaria→Casa Cuevas; "
        "de Alegría→Casa de Alegría; de Torres→Casa de Torres; de García / de Nicaragua — "
        "needs per-line brand split (not a single renameBrand)."
    )
    if note not in unresolved:
        unresolved.append(note)
    data["unresolved"] = unresolved
    data["status"] = data.get("status") or "done"
    write_json(path, data)


def patch_destination_lines(canon: str, line_remaps: dict) -> None:
    """Ensure remaps land on the taxonomy file keyed by the canonical brand, if it exists."""
    path = TAXONOMY_DIR / f"{brand_slug(canon)}.json"
    if not path.exists():
        # try common variants
        for p in TAXONOMY_DIR.glob("*.json"):
            d = load_json(p, {}) or {}
            if d.get("brand") == canon and not d.get("renameBrand"):
                path = p
                break
        else:
            return
    data = load_json(path, {}) or {}
    lines = dict(data.get("lines") or {})
    for old, rem in line_remaps.items():
        lines[old] = rem
        # also index by target line for fail-on-new
        if isinstance(rem, dict) and rem.get("line"):
            lines.setdefault(rem["line"], {"line": rem["line"]})
    data["lines"] = lines
    write_json(path, data)


def main() -> None:
    touched = []
    for brand, spec in RENAMES.items():
        p = patch_tax_file(brand, spec)
        touched.append(p.name)
        remaps = spec.get("line_remaps") or {}
        if remaps:
            patch_destination_lines(spec["renameBrand"], remaps)
    note_casa_unresolved()
    ensure_brands_json()
    print(json.dumps({"patched": touched, "renames": {k: v["renameBrand"] for k, v in RENAMES.items()}}, indent=2))


if __name__ == "__main__":
    import json

    main()
