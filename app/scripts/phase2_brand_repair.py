#!/usr/bin/env python3
"""Phase 2: write brand-only taxonomy files + update brands.json.

Does not edit cigars.json — run apply-taxonomy.py afterwards.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from taxonomy_lib import BRANDS_PATH, CIGARS_PATH, TAXONOMY_DIR, brand_slug, write_json

# Verified renames (maker / trade sources). See Phase 2 notes in PR.
RENAMES: list[dict] = [
    {
        "brand": "Roma",
        "renameBrand": "RoMa Craft Tobac",
        "sources": [
            "https://halfwheel.com/roma-craft-tobac-updating-cromagnon-line-in-2024/428403/",
            "brands.json (Roma blurb already names RoMa Craft Tobac)",
        ],
    },
    {
        "brand": "Black Label",
        "renameBrand": "Black Label Trading Company",
        "sources": [
            "https://halfwheel.com/black-label-trading-co-s-founder-launches-black-works-studio/98956/",
            "https://ovejanegracigars.com/",
        ],
    },
    {
        "brand": "Laura",
        "renameBrand": "Laura Chavin",
        "sources": ["brands.json Laura blurb", "product ids cig-laura-chavin-*"],
    },
    {
        "brand": "Cavalier",
        "renameBrand": "Cavalier Genève",
        "sources": ["product ids cig-cavalier-geneve-*", "maker / trade press"],
    },
    {
        "brand": "Marca",
        "renameBrand": "Marca Fina",
        "sources": ["product ids cig-marca-fina-*"],
    },
    {
        "brand": "Gh",
        "renameBrand": "Gran Habano",
        "sources": [
            "https://cigar-coop.com/2018/03/cigar-review-gran-habano-s-t-k-black-dahlia-by-george-rico-robusto.html",
            "ghcigars.com / brands.json Gh blurb",
        ],
    },
    {
        "brand": "Black Works",
        "renameBrand": "Black Works Studio",
        "sources": [
            "https://halfwheel.com/black-label-trading-co-s-founder-launches-black-works-studio/98956/"
        ],
    },
    {
        "brand": "El Viejo",
        "renameBrand": "El Viejo Continente",
        "sources": ["product ids cig-el-viejo-continente-*"],
    },
    {
        "brand": "Maria",
        "renameBrand": "Maria Mancini",
        "sources": ["product ids cig-maria-mancini-*"],
    },
    {
        "brand": "Karen",
        "renameBrand": "Karen Berger",
        "sources": ["https://karenbergercigars.com/our-cigars-2/"],
    },
    {
        "brand": "Valentino",
        "renameBrand": "Valentino Siesto",
        "sources": ["https://www.valentinosiestocigars.com/"],
    },
    {
        "brand": "Hr",
        "renameBrand": "HR Cigars",
        "sources": [
            "https://halfwheel.com/hirochi-robainas-hr-cigars-brand-returns-with-new-hr-black-line/443388/"
        ],
    },
    {
        "brand": "Leon",
        "renameBrand": "León Jimenes",
        "sources": ["brands.json Leon blurb", "La Aurora / product ids cig-leon-jimenes-*"],
    },
    {
        "brand": "Leaf",
        "renameBrand": "Leaf by Oscar",
        "sources": ["https://www.neptunecigar.com/cigar/leaf-by-oscar"],
    },
    {
        "brand": "Jose",
        "renameBrand": "José L. Piedra",
        "sources": [
            "https://www.habanos.com/en/the-habanos-brands-academia/jose-l-piedra-brand/"
        ],
    },
    {
        "brand": "Man O. War",
        "renameBrand": "Man O' War",
        "sources": ["https://www.cigarsinternational.com/p/man-o-war-cigars/1411636/"],
    },
    {
        "brand": "Brun",
        "renameBrand": "Brun del Ré",
        "sources": ["product ids cig-brun-del-re-*"],
    },
    {
        "brand": "Domaine",
        "renameBrand": "Domaine de Lavalette",
        "sources": ["product ids cig-domaine-de-lavalette-*"],
    },
    {
        "brand": "Gilbert",
        "renameBrand": "Gilbert de Montsalvat",
        "sources": ["product ids cig-gilbert-de-montsalvat-*"],
    },
    {
        "brand": "Henk",
        "renameBrand": "Henk Maori",
        "sources": ["https://www.henk-suitcase.com/the-straightshooter/"],
    },
    {
        "brand": "Esteban",
        "renameBrand": "Esteban Carreras",
        "sources": ["product ids cig-esteban-carreras-*"],
    },
    {
        "brand": "Herr",
        "renameBrand": "Herr Lehmann",
        "sources": ["product ids cig-herr-lehmann-*"],
    },
    {
        "brand": "Manuel",
        "renameBrand": "Manuel Alonso",
        "sources": ["product ids cig-manuel-alonso-*"],
    },
    {
        "brand": "Adrian",
        "renameBrand": "Adrian Magnus",
        "sources": ["product ids cig-adrian-magnus-*"],
    },
    {
        "brand": "Vegas",
        "renameBrand": "Vegas de Santiago",
        "sources": ["product ids cig-vegas-de-santiago-*"],
    },
    {
        "brand": "La Rosa",
        "renameBrand": "La Rosa de Sandiego",
        "sources": ["product ids cig-la-rosa-de-sandiego-*"],
    },
    {
        "brand": "Platinum",
        "renameBrand": "Platinum Nova",
        "sources": [
            "https://premiumcigars.org/platinum-nova-cigars-aiming-for-the-pinnacle-of-the-cigar-lifestyle/"
        ],
    },
    {
        "brand": "Privada",
        "renameBrand": "Privada Cigar Club",
        "sources": ["https://privadacigarclub.com/"],
    },
    {
        "brand": "West",
        "renameBrand": "West Tampa Tobacco Co.",
        "sources": ["https://www.westtampatobacco.com/"],
    },
    {
        "brand": "Dona",
        "renameBrand": "Dona Flor",
        "sources": [
            "https://halfwheel.com/press-release-dona-flor-cigars-ready-unveil-brazilian-black-treasure-u-s-market/27564/"
        ],
    },
    {
        "brand": "Les",
        "renameBrand": "Les Privatiers",
        "sources": ["product ids cig-les-privatiers-*"],
    },
    {
        "brand": "Hiram",
        "renameBrand": "Hiram & Solomon",
        "sources": ["https://www.hiramandsolomoncigars.com/"],
    },
    {
        "brand": "T.",
        "renameBrand": "T. Sonthi",
        "sources": ["product ids cig-t-sonthi-*"],
    },
    {
        "brand": "Victor",
        "renameBrand": "Victor Calvo",
        "sources": ["product ids cig-victor-calvo-*"],
    },
    {
        "brand": "Baron",
        "renameBrand": "Baron Ullmann",
        "sources": ["product ids cig-baron-ullmann-*"],
    },
    {
        "brand": "Buena",
        "renameBrand": "Buena Vista",
        "sources": ["product ids cig-buena-vista-*"],
    },
    {
        "brand": "God",
        "renameBrand": "God of Fire",
        "sources": ["https://www.godoffire.com/"],
    },
    {
        "brand": "Flores",
        "renameBrand": "Flores y Rodriguez",
        "sources": ["product ids cig-flores-y-rodriguez-*"],
    },
    {
        "brand": "San Pedro",
        "renameBrand": "San Pedro de Macoris",
        "sources": ["product ids cig-san-pedro-de-macoris-*"],
    },
    {
        "brand": "Smoking",
        "renameBrand": "Smoking Jacket",
        "sources": ["product ids cig-smoking-jacket-by-hendrik-kelner-jr-*"],
    },
    {
        "brand": "Quai",
        "renameBrand": "Quai d'Orsay",
        "sources": ["https://www.habanos.com/en/the-habanos-brands-academia/"],
    },
    {
        "brand": "Ferio",
        "renameBrand": "Ferio Tego",
        "sources": ["https://www.feriotego.com/"],
    },
    {
        "brand": "Indian",
        "renameBrand": "Indian Motorcycle",
        "sources": ["product ids cig-indian-motorcycle-*"],
    },
    {
        "brand": "Cornelius",
        "renameBrand": "Cornelius & Anthony",
        "sources": ["product ids cig-cornelius-amp-anthony-*"],
    },
    {
        "brand": "Bock",
        "renameBrand": "Bock y Ca.",
        "sources": ["product ids cig-bock-y-ca*"],
    },
    {
        "brand": "Castillo",
        "renameBrand": "Castillo de Reyes",
        "sources": ["product ids cig-castillo-de-reyes-*"],
    },
    {
        "brand": "Rodrigo",
        "renameBrand": "Rodrigo de Jerez",
        "sources": ["product ids cig-rodrigo-de-jerez-*"],
    },
    {
        "brand": "Mata",
        "renameBrand": "Mata Hari",
        "sources": ["product ids cig-mata-hari-*"],
    },
    {
        "brand": "Leite",
        "renameBrand": "Leite & Alves",
        "sources": ["product ids cig-leite-amp-alves-*"],
    },
    {
        "brand": "Ra",
        "renameBrand": "R.A. Villamil",
        "sources": ["product ids cig-ra-r-a-villamil-*"],
    },
    {
        "brand": "Aj",
        "renameBrand": "AJ Fernandez",
        "sources": ["product ids cig-aj-a-j-fernandez-*", "existing AJ Fernandez key"],
    },
    {
        "brand": "Alonso",
        "renameBrand": "Alonso Menendez",
        "sources": ["product ids cig-alonso-menendez"],
    },
    {
        "brand": "Daniel",
        "renameBrand": "Daniel Marshall",
        "sources": ["product ids cig-daniel-marshall-*"],
    },
    {
        "brand": "Cuervo",
        "renameBrand": "Cuervo y Sobrinos",
        "sources": ["product ids cig-cuervo-y-sobrinos-*"],
    },
    {
        "brand": "Rafael",
        "renameBrand": "Rafael Gonzalez",
        "sources": ["https://www.habanos.com/en/the-habanos-brands-academia/"],
    },
    {
        "brand": "Rey",
        "renameBrand": "El Rey del Mundo",
        "sources": [
            "https://www.habanos.com/en/the-habanos-brands-academia/el-rey-del-mundo-brand/"
        ],
    },
]

# Line remaps that belong with brand repair (class I character loss).
ROMA_LINES: dict[str, dict] = {}


def build_roma_lines(cigars: list) -> dict[str, dict]:
    """Floor remaps: fix CroMagnon spelling and strip redundant Craft prefix.
    Full line↔vitola splits stay for Phase 3.
    """
    out: dict[str, dict] = {}
    for c in cigars:
        if c.get("brand") != "Roma":
            continue
        raw = c.get("line") or ""
        if raw.startswith("Craft C gnon"):
            rest = raw[len("Craft C gnon") :].strip()
            new_line = f"CroMagnon {rest}".strip() if rest else "CroMagnon"
            out[raw] = {"line": new_line}
        elif raw.startswith("Craft "):
            rest = raw[len("Craft ") :].strip()
            if rest:
                out[raw] = {"line": rest}
    return out


def main() -> None:
    cigars = json.loads(CIGARS_PATH.read_text(encoding="utf-8"))
    brands = json.loads(BRANDS_PATH.read_text(encoding="utf-8"))
    live = {c.get("brand") for c in cigars}

    roma_lines = build_roma_lines(cigars)

    written = []
    skipped = []
    for spec in RENAMES:
        brand = spec["brand"]
        new_name = spec["renameBrand"]
        path = TAXONOMY_DIR / f"{brand_slug(brand)}.json"

        # Always maintain brands.json mapping even after apply removed the old key
        old = brands.get(brand) or brands.get(new_name)
        if new_name not in brands:
            if old:
                brands[new_name] = copy.deepcopy(old)
            else:
                brands[new_name] = {
                    "country": "—",
                    "founded": "—",
                    "blurb": {
                        "hr": f"{new_name} — marka iz kataloga trgovina (HR/EU/USA).",
                        "en": f"{new_name} — a brand listed in retail shop catalogues (HR/EU/USA).",
                    },
                }
        elif brand in brands:
            cur = brands[new_name]
            old_entry = brands[brand]
            old_hr = (old_entry.get("blurb") or {}).get("hr") or ""
            new_hr = (cur.get("blurb") or {}).get("hr") or ""
            if len(old_hr) > len(new_hr) and "kataloga trgovina" not in old_hr:
                brands[new_name] = copy.deepcopy(old_entry)

        if brand != new_name and brand in brands:
            del brands[brand]

        if brand not in live and not path.exists():
            skipped.append({"brand": brand, "reason": "not in cigars.json and no taxonomy file"})
            continue

        existing = {}
        if path.exists():
            existing = json.loads(path.read_text(encoding="utf-8"))
        payload = {
            "brand": brand,
            "renameBrand": new_name,
            "status": "brand-only",
            "reviewedAt": "2026-07-23",
            "sources": spec["sources"],
            "lines": {},
            "vitolaRenames": {},
            "shapes": {},
            "keepSeparate": [],
            "lineNotes": {},
            "unresolved": [],
        }
        if brand == "Roma":
            payload["lines"] = roma_lines or existing.get("lines") or {}
            payload["lineNotes"] = {
                "_phase2": "Craft C gnon → CroMagnon (ingest character loss); brand → RoMa Craft Tobac"
            }
        elif existing.get("unresolved"):
            payload["unresolved"] = existing["unresolved"]
        else:
            payload["unresolved"] = [
                "Phase 2 brand rename only; prior seed line maps cleared for Phase 3 rewrite"
            ]

        write_json(path, payload)
        written.append({"file": path.name, "from": brand, "to": new_name})

    # Sort brands.json keys for stable diffs
    brands_sorted = {k: brands[k] for k in sorted(brands.keys(), key=lambda s: s.casefold())}
    write_json(BRANDS_PATH, brands_sorted)

    report = {
        "written": written,
        "skipped": skipped,
        "roma_line_remaps": len(roma_lines),
        "brands_json_keys": len(brands_sorted),
        "unverified_left_out": [
            "Casa (mixed makers under one key)",
            "Toraño (brand key already correct; line Torano* → Phase 3)",
            "Fine Catch (Marlin is vitola, not brand)",
            "Aging Room / Condega / Room101 / many single-row false positives from audit heuristic",
        ],
    }
    out = Path(__file__).resolve().parent / "output" / "phase2_brand_repair_report.json"
    write_json(out, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
