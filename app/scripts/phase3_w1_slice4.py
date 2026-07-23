#!/usr/bin/env python3
"""Phase 3 W1 slice-4: Casdagli, Caldwell, CAO, Joya, Montecristo, Plasencia,
Camacho, Leonel.

Only writes taxonomy JSON. Parent runs apply-taxonomy.
Creates missing montecristo.json / plasencia.json.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from taxonomy_lib import TAXONOMY_DIR, load_json, write_json

SNAP = Path(__file__).resolve().parent / "output" / "phase3_w1_slice4_snapshot.json"

SHAPES = {
    "robusto",
    "toro",
    "churchill",
    "corona",
    "half corona",
    "petit corona",
    "lancero",
    "belicoso",
    "torpedo",
    "perfecto",
    "gordo",
    "piramide",
    "pirámide",
    "figurado",
    "gran toro",
    "short robusto",
    "double robusto",
    "double corona",
    "lonsdale",
    "panetela",
}


def as_shape(name: str | None) -> str | None:
    if not name:
        return None
    return name if name.casefold() in SHAPES else None


def base(path: Path, brand: str) -> dict:
    existing = load_json(path, {}) or {}
    return {
        "brand": brand,
        "renameBrand": existing.get("renameBrand"),
        "status": "done",
        "reviewedAt": "2026-07-23",
        "sources": list(
            dict.fromkeys(
                (existing.get("sources") or [])
                + [
                    "phase3_w1_slice4 deterministic remaps",
                    "docs/superpowers/plans/2026-07-23-cigar-taxonomy-brand-line-vitola.md §7.1",
                ]
            )
        ),
        "lines": {},
        "vitolaRenames": {},
        "shapes": {},
        "keepSeparate": existing.get("keepSeparate") or [],
        "lineNotes": existing.get("lineNotes") or {},
        "unresolved": [],
    }


def write_brand(
    brand: str,
    fname: str,
    lines: dict,
    unresolved: list | None = None,
    keep=None,
    sources=None,
):
    path = TAXONOMY_DIR / fname
    b = base(path, brand)
    b["lines"] = lines
    b["unresolved"] = unresolved or []
    if keep is not None:
        b["keepSeparate"] = keep
    if sources:
        b["sources"] = list(dict.fromkeys(sources + b["sources"]))
    write_json(path, b)
    return {"file": fname, "remaps": len(lines), "unresolved": len(b["unresolved"])}


def casdagli(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""

        m = re.match(r"^Basilica C (No\.\s*\d+)(?:\s+(MADURO))?$", raw, re.I)
        if m:
            vit = m.group(1).replace("No.", "No. ").replace("No.  ", "No. ")
            if m.group(2):
                lines[raw] = {"line": "Basilica C Maduro", "vitola": vit}
            else:
                lines[raw] = {"line": "Basilica C", "vitola": vit}
            continue

        if raw.startswith("Brothers of Sabre "):
            vit = raw[len("Brothers of Sabre ") :]
            lines[raw] = {"line": "Brothers of Sabre", "vitola": vit}
            continue

        if raw.startswith("Cypher 3311 "):
            vit = raw[len("Cypher 3311 ") :]
            # Boniface Gordo → Boniface
            vit = re.sub(r"\s+Gordo$", "", vit)
            lines[raw] = {"line": "Cypher 3311", "vitola": vit}
            continue

        if raw.startswith("Traditional ") and raw != "Traditional":
            vit = raw[len("Traditional ") :]
            lines[raw] = {"line": "Traditional", "vitola": vit}
            continue

        if raw.startswith("Villa Exquisito "):
            vit = raw[len("Villa Exquisito ") :]
            lines[raw] = {"line": "Villa Exquisito", "vitola": vit}
            continue

        if raw.startswith("Club "):
            # Club Especial / Club Gran GOLD / Club Mareva …
            lines[raw] = {"line": raw}  # keep Club sub-lines distinct (different blends)
            continue

        if raw.startswith("D`Boiss") or raw.startswith("D'Boiss"):
            m = re.match(r"^D[`']Boiss\s+(.+)$", raw)
            lines[raw] = {"line": "D'Boiss", "vitola": m.group(1) if m else raw}
            continue

        if raw == "Daughters of Wind Pony Express":
            lines[raw] = {"line": "Daughters of Wind", "vitola": "Pony Express"}
            continue

        if raw == "Cabinet Selection Rosetta":
            lines[raw] = {"line": "Cabinet Selection", "vitola": "Rosetta"}
            continue

        lines[raw] = {"line": raw}
    return lines, unr


def caldwell(rows: list) -> tuple[dict, list, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""

        if raw.startswith("Eastern Standard "):
            rest = raw[len("Eastern Standard ") :]
            if rest.startswith("Midnight Express "):
                vit = rest[len("Midnight Express ") :]
                lines[raw] = {"line": "Eastern Standard Midnight Express", "vitola": vit}
            else:
                lines[raw] = {"line": "Eastern Standard", "vitola": rest}
            continue

        if raw.startswith("King is Dead "):
            vit = raw[len("King is Dead ") :]
            lines[raw] = {"line": "The King Is Dead", "vitola": vit}
            continue

        if raw.startswith("Long Live King ") or raw.startswith("Long live King "):
            rest = re.sub(r"^Long [Ll]ive King\s+", "", raw)
            rest = re.sub(r"\s+MAD MOFO\s+", " ", rest)
            rest = re.sub(r"^Mad Mofo\s+", "Mad Mofo ", rest)
            lines[raw] = {"line": "Long Live The King", "vitola": rest.strip()}
            continue

        if raw.startswith("Long live Queen ") or raw.startswith("Long Live Queen "):
            rest = re.sub(r"^Long [Ll]ive Queen\s+", "", raw)
            rest = re.sub(r"^Maduro\s+", "", rest)
            rest = rest.replace("Queens's", "Queen's")
            line = "Long Live The Queen Maduro" if "Maduro" in raw else "Long Live The Queen"
            lines[raw] = {"line": line, "vitola": rest.strip()}
            continue

        if raw.startswith("Blind Man's Bluff"):
            # keep wrapper variants as separate lines (seed pattern)
            lines[raw] = {"line": raw}
            continue

        if raw == "Reserva Sevillana":
            lines[raw] = {"line": "Reserva Sevillana"}
            continue

        lines[raw] = {"line": raw}

    keep = [
        ["Blind Man's Bluff", "Blind Man's Bluff Connecticut"],
        ["Blind Man's Bluff", "Blind Man's Bluff Maduro"],
        ["Long Live The Queen", "Long Live The Queen Maduro"],
    ]
    unr.append("Caldwell: Blind Man's Bluff wrapper variants kept separate")
    return lines, unr, keep


def cao(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""

        if raw == "America Monument":
            lines[raw] = {"line": "America", "vitola": "Monument"}
            continue
        if raw == "Colombia Magdalena":
            lines[raw] = {"line": "Colombia", "vitola": "Magdalena"}
            continue
        if raw == "ba Diamante":
            lines[raw] = {"line": "Bahia Diamante"}
            continue
        if raw == "medio tiempo":
            lines[raw] = {"line": "Medio Tiempo"}
            continue

        if raw.startswith("Limited Edition Arcana "):
            vit = raw[len("Limited Edition Arcana ") :]
            lines[raw] = {"line": "Arcana", "vitola": vit}
            continue

        if raw.startswith("Bones "):
            vit = raw[len("Bones ") :]
            lines[raw] = {"line": "Bones", "vitola": vit}
            continue

        lines[raw] = {"line": raw}
    return lines, unr


def joya(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""

        if raw.startswith("Antano Dark Corojo "):
            vit = raw[len("Antano Dark Corojo ") :]
            lines[raw] = {"line": "Antaño Dark Corojo", "vitola": vit}
            continue

        # Normalize Antaño spelling when already a line name
        if raw.startswith("Antaño") or raw.startswith("Antano"):
            norm = raw.replace("Antano", "Antaño")
            lines[raw] = {"line": norm}
            continue

        if raw == "Cinco de Cinco Gordo":
            lines[raw] = {"line": "Cinco de Cinco", "vitola": "Gordo", "shape": "Gordo"}
            continue

        if raw.startswith("Rosalones Reserva "):
            vit = raw[len("Rosalones Reserva ") :]
            lines[raw] = {"line": "Rosalones Reserva", "vitola": vit}
            continue

        if raw.startswith("Joya de la Romana "):
            vit = raw[len("Joya de la Romana ") :]
            lines[raw] = {"line": "Joya de la Romana", "vitola": vit}
            continue

        if raw.startswith("Cuatro Cinco "):
            # Cuatro Cinco Doble / Reserva Especial — keep as Cuatro Cinco family
            if raw == "Cuatro Cinco Doble":
                lines[raw] = {"line": "Cuatro Cinco", "vitola": "Doble"}
            else:
                lines[raw] = {"line": raw}
            continue

        # Clásico spelling
        if "Clasico" in raw or "Clásico" in raw:
            lines[raw] = {"line": raw.replace("Clasico", "Clásico")}
            continue

        if "Decadas" in raw or "Décadas" in raw:
            lines[raw] = {"line": raw.replace("Decadas", "Décadas")}
            continue

        if "Autenticos" in raw or "Auténticos" in raw:
            lines[raw] = {"line": raw.replace("Autenticos", "Auténticos")}
            continue

        lines[raw] = {"line": raw}
    return lines, unr


def montecristo(rows: list) -> tuple[dict, list]:
    """Habanos: fold single-vitola Classic SKUs into Classic Line / Edmundo / Open / 1935."""
    lines: dict[str, dict] = {}
    unr: list[str] = []
    classic_vitolas = {
        "No. 2",
        "No.3",
        "No.4",
        "No.5",
        "Petit No.2",
        "Especial No.2",
        "Joyitas",
        "Junior",
        "Nacional",
        "Dumas",  # also on 1935 — prefer Classic only if not overlapping; see below
        "Maltes",
        "Media",
        "Leyenda",
    }
    edmundo = {"Edmundo", "Petit Edmundo", "Wide Edmundo", "Double Edmundo"}
    linea_1935 = {"Dumas", "Maltes"}  # when standalone, fold into Línea 1935 if that exists

    has_1935 = any((r.get("line") or "").startswith("Línea 1935") or (r.get("line") or "").startswith("Linea 1935") for r in rows)

    for r in rows:
        raw = r.get("line") or ""

        if raw in ("Classic Line",):
            lines[raw] = {"line": "Classic"}
            continue

        if raw.startswith("Línea 1935") or raw.startswith("Linea 1935") or raw.startswith("LÃ­nea 1935"):
            lines[raw] = {"line": "Línea 1935"}
            continue

        if raw in edmundo:
            if raw == "Edmundo":
                lines[raw] = {"line": "Edmundo"}
            else:
                lines[raw] = {"line": "Edmundo", "vitola": raw}
            continue

        if raw in linea_1935 and has_1935:
            lines[raw] = {"line": "Línea 1935", "vitola": raw}
            continue

        if raw in classic_vitolas or re.match(r"^No\.?\s*\d+$", raw):
            vit = raw
            if raw.startswith("No.") and " " not in raw[3:].strip()[:1]:
                vit = raw.replace("No.", "No. ").replace("No.  ", "No. ")
            lines[raw] = {"line": "Classic", "vitola": vit}
            continue

        if raw == "Master Tubos":
            lines[raw] = {"line": "Open", "vitola": "Master Tubos"}
            continue

        if raw == "Limited Editions":
            lines[raw] = {"line": "Limited Edition"}
            continue

        if raw == "Open":
            lines[raw] = {"line": "Open"}
            continue

        lines[raw] = {"line": raw}

    unr.append("Montecristo: Habanos Classic/Edmundo/Open/1935 fold — verify against catalog")
    return lines, unr


def plasencia(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""

        if raw.startswith("Alma Del Fuego ") or raw.startswith("Alma del Fuego "):
            vit = re.sub(r"^Alma [Dd]el Fuego\s+", "", raw)
            lines[raw] = {"line": "Alma del Fuego", "vitola": vit}
            continue

        m = re.match(r"^Cosecha (\d+)\s+(.+)$", raw)
        if m:
            year, vit = m.group(1), m.group(2)
            # Strip trailing size suffix like San Luis-Toro
            vit_clean = re.sub(r"-(Toro|Robusto|Gordo)$", "", vit)
            lines[raw] = {"line": f"Cosecha {year}", "vitola": vit_clean}
            continue

        if raw.startswith("Year Of The ") or raw.startswith("Year of the "):
            animal = re.sub(r"^Year [Oo]f [Tt]he\s+", "", raw)
            lines[raw] = {"line": f"Year of the {animal}"}
            continue

        if "Edicion Especial" in raw or "Edición Especial" in raw:
            rest = re.sub(r"^Edici[oó]n Especial\s+", "", raw)
            lines[raw] = {"line": "Edición Especial", "vitola": rest or raw}
            continue

        if raw == "Alma Del Campo" or raw == "Alma del Campo":
            lines[raw] = {"line": "Alma del Campo"}
            continue
        if raw == "Alma Del Cielo" or raw == "Alma del Cielo":
            lines[raw] = {"line": "Alma del Cielo"}
            continue

        lines[raw] = {"line": raw}
    return lines, unr


def camacho(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""

        if raw == "Criollo Criollo":
            lines[raw] = {"line": "Criollo"}
            continue

        if "Check Six" in raw:
            lines[raw] = {"line": "Check Six"}
            continue

        if raw.startswith("Liberty Series"):
            lines[raw] = {"line": "Liberty Series"}
            continue

        if raw.startswith("BG Meyer"):
            lines[raw] = {"line": "BG Meyer"}
            continue

        if raw.startswith("Ditka "):
            vit = raw[len("Ditka ") :]
            lines[raw] = {"line": "Ditka", "vitola": vit}
            continue

        if raw == "Scorpion Sun Grown":
            lines[raw] = {"line": "Scorpion"}
            continue

        lines[raw] = {"line": raw}
    return lines, unr


def leonel(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""

        m = re.match(r"^P-Series\s+(\d+)$", raw)
        if m:
            lines[raw] = {"line": "P-Series", "vitola": m.group(1)}
            continue

        if raw == "Signature Signature Connecticut":
            lines[raw] = {"line": "Signature Connecticut"}
            continue
        if raw == "Signature Signature Maduro":
            lines[raw] = {"line": "Signature Maduro"}
            continue

        if raw.startswith("Limited Edition "):
            lines[raw] = {"line": raw}
            continue

        lines[raw] = {"line": raw}
    return lines, unr


def main() -> None:
    snap = json.loads(SNAP.read_text(encoding="utf-8"))
    report = {}

    lines, unr = casdagli(snap["Casdagli"])
    report["Casdagli"] = write_brand(
        "Casdagli", "casdagli.json", lines, unr, sources=["https://casdagli.com/"]
    )

    lines, unr, keep = caldwell(snap["Caldwell"])
    report["Caldwell"] = write_brand(
        "Caldwell",
        "caldwell.json",
        lines,
        unr,
        keep=keep,
        sources=["https://caldwellcigarco.com/"],
    )

    lines, unr = cao(snap["CAO"])
    report["CAO"] = write_brand("CAO", "cao.json", lines, unr, sources=["https://caocigars.com/"])

    lines, unr = joya(snap["Joya de Nicaragua"])
    report["Joya de Nicaragua"] = write_brand(
        "Joya de Nicaragua",
        "joya-de-nicaragua.json",
        lines,
        unr,
        sources=["https://joyacigars.com/"],
    )

    lines, unr = montecristo(snap["Montecristo"])
    report["Montecristo"] = write_brand(
        "Montecristo",
        "montecristo.json",
        lines,
        unr,
        sources=["https://www.habanos.com/"],
    )

    lines, unr = plasencia(snap["Plasencia"])
    report["Plasencia"] = write_brand(
        "Plasencia",
        "plasencia.json",
        lines,
        unr,
        sources=["https://plasenciacigars.com/"],
    )

    lines, unr = camacho(snap["Camacho"])
    report["Camacho"] = write_brand(
        "Camacho", "camacho.json", lines, unr, sources=["https://camachocigars.com/"]
    )

    lines, unr = leonel(snap["Leonel"])
    report["Leonel"] = write_brand(
        "Leonel", "leonel.json", lines, unr, sources=["https://leonelcigars.com/"]
    )

    out = Path(__file__).resolve().parent / "output" / "phase3_w1_slice4_report.json"
    write_json(out, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
