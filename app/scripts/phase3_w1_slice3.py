#!/usr/bin/env python3
"""Phase 3 W1 slice-3: Arturo Fuente, Alec Bradley, La Aurora, Kristoff,
My Father, Padrón, Padilla, Tatuaje.

Only writes taxonomy JSON. Parent runs apply-taxonomy.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from taxonomy_lib import TAXONOMY_DIR, load_json, write_json

SNAP = Path(__file__).resolve().parent / "output" / "phase3_w1_slice3_snapshot.json"

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
    "double toro",
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
                    "phase3_w1_slice3 deterministic remaps",
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


def strip_pack_suffix(raw: str) -> str:
    # A. Fuente Don Carlos /15 → A. Fuente Don Carlos
    return re.sub(r"/\d+\s*$", "", raw).strip()


def arturo(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""
        cleaned = strip_pack_suffix(raw)

        if cleaned.startswith("A. Fuente Don Carlos"):
            lines[raw] = {"line": "Don Carlos"}
            continue
        if cleaned.startswith("A. Fuente Hemingway "):
            vit = cleaned[len("A. Fuente Hemingway ") :].strip()
            lines[raw] = {"line": "Hemingway", "vitola": vit, "shape": as_shape(vit) or "Perfecto"}
            continue
        if cleaned.startswith("A. Fuente Fuente Fuente OpusX "):
            vit = cleaned[len("A. Fuente Fuente Fuente OpusX ") :].strip()
            lines[raw] = {"line": "Opus X", "vitola": vit}
            continue
        if cleaned.startswith("A. Fuente "):
            rest = cleaned[len("A. Fuente ") :]
            lines[raw] = {"line": rest}
            continue

        m = re.match(r"^Anejo (?:No\.?\s*|#)?(\d+|8-8-8)(?:\s+Maduro)?$", cleaned, re.I)
        if m or cleaned.startswith("Anejo "):
            # Anejo #55 / Anejo No. 46 / Anejo 50 Maduro → Añejo
            vit = cleaned
            for prefix in ("Anejo No. ", "Anejo No ", "Anejo #", "Anejo "):
                if vit.startswith(prefix):
                    vit = vit[len(prefix) :]
                    break
            lines[raw] = {"line": "Añejo", "vitola": vit}
            continue

        if cleaned.startswith("Brevas Royal"):
            lines[raw] = {"line": "Brevas Royales", "vitola": cleaned.replace("Brevas ", "")}
            continue

        if cleaned == "Curly Head Deluxe":
            lines[raw] = {"line": "Curly Head", "vitola": "Deluxe"}
            continue

        if cleaned == "Fuente Fuente Opus X Lost City":
            lines[raw] = {"line": "Opus X Lost City"}
            continue

        if cleaned == "King T Sungrown":
            lines[raw] = {"line": "Chateau Fuente", "vitola": "King T Sungrown"}
            continue

        if cleaned == "Seleccion d'Oro Imperial":
            lines[raw] = {"line": "Seleccion d'Oro", "vitola": "Imperial"}
            continue

        if cleaned == "Piramide":
            lines[raw] = {"line": "Gran Reserva", "vitola": "Piramide", "shape": "Piramide"}
            continue

        if cleaned.startswith("Limited Edition "):
            lines[raw] = {"line": cleaned}
            continue

        lines[raw] = {"line": cleaned or raw}

    unr.append(
        "Arturo Fuente: Opus X / Hemingway vitola names still embed line tokens — polish later"
    )
    return lines, unr


def alec(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""
        shape = (r.get("vitolas") or [{}])[0].get("name")

        m = re.match(r"^Project 40(?: Maduro)? (\d{2}\.\d{2})$", raw)
        if m:
            size = m.group(1)
            base_line = "Project 40 Maduro" if "Maduro" in raw else "Project 40"
            size_to_vit = {
                "05.50": "Robusto",
                "06.52": "Toro",
                "06.60": "Gordo",
            }
            vit = size_to_vit.get(size, size)
            entry = {"line": base_line, "vitola": vit}
            if as_shape(vit):
                entry["shape"] = vit
            lines[raw] = entry
            continue

        m = re.match(r"^MAXX (CURVE|FIXX|NANO)$", raw)
        if m:
            code = m.group(1)
            vit_map = {"CURVE": "Curve", "FIXX": "Fixx", "NANO": "Nano"}
            lines[raw] = {"line": "MAXX", "vitola": vit_map[code]}
            continue

        m = re.match(r"^Mundial (PL\d+)$", raw)
        if m:
            lines[raw] = {"line": "Mundial", "vitola": m.group(1), "shape": "Perfecto"}
            continue

        if raw == "Family Blend T11":
            lines[raw] = {"line": "Family Blend", "vitola": "T11"}
            continue

        if raw == "Dissident Bloc":
            lines[raw] = {"line": "Dissident", "vitola": "Bloc"}
            continue

        if raw == "Texas Lancero":
            lines[raw] = {"line": "Texas", "vitola": "Lancero", "shape": "Lancero"}
            continue

        lines[raw] = {"line": raw}
    unr.append("Alec Bradley: Gatekeeper/Magic Toast vitola names still embed line tokens")
    return lines, unr


def la_aurora(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""
        shape = (r.get("vitolas") or [{}])[0].get("name")

        # Keep 107 Ecuador Maduro USA separate (keepSeparate)
        if raw == "107 Ecuador Maduro USA":
            lines[raw] = {"line": "107 Ecuador Maduro USA"}
            continue

        if raw == "107 Belicoso":
            lines[raw] = {"line": "107", "vitola": "Belicoso", "shape": "Belicoso"}
            continue
        if raw in ("107 Zeppelin", "107 Nicaragua Zepelin"):
            lines[raw] = {"line": "107 Nicaragua", "vitola": "Zeppelin"}
            continue

        if raw == "107 / 107 Nicaragua":
            lines[raw] = {"line": "107 Nicaragua"}
            continue

        if raw == "115 Aniversario Gordo":
            lines[raw] = {"line": "115 Anniversary", "vitola": "Gordo", "shape": "Gordo"}
            continue

        if raw == "107 Ecuador Sumo":
            lines[raw] = {"line": "107 Ecuador", "vitola": "Sumo"}
            continue

        if raw == "1495 Series Sumo":
            lines[raw] = {"line": "1495 Series", "vitola": "Sumo"}
            continue

        if raw == "Principes MADURO":
            lines[raw] = {"line": "Principes Maduro"}
            continue

        if raw.startswith("Limited Editions "):
            lines[raw] = {"line": raw}
            continue

        lines[raw] = {"line": raw}
    unr.append("La Aurora: Preferidos / ADN vitola names still embed line tokens")
    return lines, unr


def kristoff(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""

        if raw.startswith("GC Signature Series"):
            if raw == "GC Signature Series":
                lines[raw] = {"line": "GC Signature Series"}
            else:
                # LE releases stay as named limited lines under GC family
                rest = raw[len("GC Signature Series") :].strip()
                lines[raw] = {"line": f"GC Signature Series {rest}" if rest else "GC Signature Series"}
            continue

        if raw.startswith("It's a Girl / It's a Boy"):
            # Shop mashed boy/girl SKUs into one pseudo-line name.
            if "GIRL" in raw.upper():
                lines[raw] = {"line": "It's a Girl", "sampler": True}
            else:
                lines[raw] = {"line": "It's a Boy", "sampler": True}
            continue

        if raw == "Twentieth Anniversary Veinte":
            lines[raw] = {"line": "Veinte"}
            continue

        if raw == "Edicion Limitada 685 Woodlawn":
            lines[raw] = {"line": "685 Woodlawn"}
            continue

        lines[raw] = {"line": raw}
    return lines, unr


def my_father(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""

        if raw in ("#2", "#4"):
            vit = "No. 2" if raw == "#2" else "No. 4"
            shape = "Belicoso" if raw == "#2" else "Lancero"
            lines[raw] = {"line": "My Father Original", "vitola": vit, "shape": shape}
            continue

        if raw.startswith("Classic No."):
            m = re.match(r"^Classic No\.\s*(\d+)$", raw)
            if m:
                lines[raw] = {"line": "Classic", "vitola": f"No. {m.group(1)}"}
                continue

        if raw.startswith("La Duena"):
            m = re.match(r"^La Duena (.+)$", raw)
            if m:
                lines[raw] = {"line": "La Duena", "vitola": m.group(1)}
            else:
                lines[raw] = {"line": "La Duena"}
            continue

        if raw.startswith("& Tatuaje"):
            lines[raw] = {"line": "La Union Red Especial"}
            unr.append(f"My Father: collab line {raw!r} → La Union Red Especial (verify)")
            continue

        if raw == "Le Bijou Limited Edition 2016":
            lines[raw] = {"line": "Le Bijou 1922", "vitola": "Limited Edition 2016"}
            continue

        lines[raw] = {"line": raw}
    return lines, unr


def padron(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""

        m = re.match(r"^Padron Classic No\.\s*(\d+)\s+(NATURAL|MADURO)$", raw, re.I)
        if m:
            num, wrap = m.group(1), m.group(2).title()
            lines[raw] = {"line": "Classic", "vitola": f"No. {num} {wrap}"}
            continue

        if raw == "Core (2000/3000)":
            lines[raw] = {"line": "Classic"}
            continue

        if raw == "40th Anniversary 40th":
            lines[raw] = {"line": "40th Anniversary"}
            continue
        if raw == "40th Anniversary 40th Maduro":
            lines[raw] = {"line": "40th Anniversary Maduro"}
            continue

        if raw == "60th Anniversary 60th":
            lines[raw] = {"line": "60th Anniversary"}
            continue
        if raw == "60th Anniversary 60th Maduro":
            lines[raw] = {"line": "60th Anniversary Maduro"}
            continue

        if raw == "80 Years 80th":
            lines[raw] = {"line": "80 Years"}
            continue
        if raw == "80 Years 80th Maduro":
            lines[raw] = {"line": "80 Years Maduro"}
            continue

        if raw == "50th Anniversary Natural":
            lines[raw] = {"line": "50th Anniversary", "vitola": "Natural"}
            continue
        if raw == "50th Anniversary Maduro":
            lines[raw] = {"line": "50th Anniversary", "vitola": "Maduro"}
            continue

        if raw == "Padron Black Black PB 97":
            lines[raw] = {"line": "Black"}
            continue
        if raw == "Padron Black Black PB 97 Maduro":
            lines[raw] = {"line": "Black Maduro"}
            continue

        if raw == "1926 Serie":
            lines[raw] = {"line": "1926 Serie"}
            continue

        # Churchill / Panetela / Maduro single-size cores — keep as named lines
        lines[raw] = {"line": raw}

    # Refresh keepSeparate to post-rename names where we renamed both sides
    keep = [
        ["#6000", "#6000 Maduro"],
        ["1964 Anniversary", "1964 Anniversary Series"],
        ["40th Anniversary", "40th Anniversary Maduro"],
        ["60th Anniversary", "60th Anniversary Maduro"],
        ["80 Years", "80 Years Maduro"],
        ["Black", "Black Maduro"],
    ]
    unr.append("Padrón: 1964 Anniversary vs Anniversary Series kept separate per seed")
    return lines, unr, keep


def padilla(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""

        if raw in ("88th Aniversario", "88th Anniversario"):
            lines[raw] = {"line": "88th Aniversario"}
            continue

        if raw == "Finest Hour Oscuro OSCURO":
            lines[raw] = {"line": "Finest Hour Oscuro"}
            continue

        if raw == "Signature 1932":
            lines[raw] = {"line": "1932", "vitola": "Signature"}
            continue

        if raw.startswith("Serie 1968 "):
            rest = raw[len("Serie 1968 ") :]
            lines[raw] = {"line": f"Serie 1968 {rest}"}
            continue

        lines[raw] = {"line": raw}
    return lines, unr


def tatuaje(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""

        m = re.match(r"^HCS(?: Maduro)? #(\d+) (.+)$", raw)
        if m:
            num, name = m.group(1), m.group(2)
            base_line = "HCS Maduro" if "Maduro" in raw else "HCS"
            lines[raw] = {"line": base_line, "vitola": f"#{num} {name}"}
            continue

        if raw.startswith("La Seleccion de Cazador "):
            rest = raw[len("La Seleccion de Cazador ") :]
            # Anniversary sizes → one anniversary line
            if "20th Anniversary" in rest:
                vit = rest.replace("20th Anniversary ", "").strip()
                lines[raw] = {"line": "La Seleccion de Cazador 20th Anniversary", "vitola": vit}
            else:
                lines[raw] = {"line": "La Seleccion de Cazador", "vitola": rest}
            continue

        if raw == "10th Anniversary Capa Especial Belle Encre":
            lines[raw] = {"line": "10th Anniversary Capa Especial", "vitola": "Belle Encre"}
            continue
        if raw == "10th Anniversary Belle Encre":
            lines[raw] = {"line": "10th Anniversary", "vitola": "Belle Encre"}
            continue
        if raw == "Tuxtla Belle Encre":
            lines[raw] = {"line": "Tuxtla", "vitola": "Belle Encre"}
            continue

        if raw == "Mexican Experiment ME II":
            lines[raw] = {"line": "Mexican Experiment II"}
            continue

        if raw == "El Triunfador Original":
            lines[raw] = {"line": "El Triunfador"}
            continue

        lines[raw] = {"line": raw}
    return lines, unr


def main() -> None:
    snap = json.loads(SNAP.read_text(encoding="utf-8"))
    report = {}

    lines, unr = arturo(snap["Arturo Fuente"])
    report["Arturo Fuente"] = write_brand(
        "Arturo Fuente",
        "arturo-fuente.json",
        lines,
        unr,
        sources=["https://www.arturofuente.com/"],
    )

    lines, unr = alec(snap["Alec Bradley"])
    report["Alec Bradley"] = write_brand(
        "Alec Bradley",
        "alec-bradley.json",
        lines,
        unr,
        sources=["https://alecbradley.com/"],
    )

    lines, unr = la_aurora(snap["La Aurora"])
    report["La Aurora"] = write_brand(
        "La Aurora",
        "la-aurora.json",
        lines,
        unr,
        sources=["https://www.laaurora.com.do/"],
    )

    lines, unr = kristoff(snap["Kristoff"])
    report["Kristoff"] = write_brand(
        "Kristoff",
        "kristoff.json",
        lines,
        unr,
        sources=["https://kristoffcigars.com/"],
    )

    lines, unr = my_father(snap["My Father"])
    report["My Father"] = write_brand(
        "My Father",
        "my-father.json",
        lines,
        unr,
        sources=["https://myfathercigars.com/"],
    )

    lines, unr, keep = padron(snap["Padrón"])
    report["Padrón"] = write_brand(
        "Padrón",
        "padron.json",
        lines,
        unr,
        keep=keep,
        sources=["https://www.padron.com/"],
    )

    lines, unr = padilla(snap["Padilla"])
    report["Padilla"] = write_brand(
        "Padilla",
        "padilla.json",
        lines,
        unr,
        sources=["https://padillacigars.com/"],
    )

    lines, unr = tatuaje(snap["Tatuaje"])
    report["Tatuaje"] = write_brand(
        "Tatuaje",
        "tatuaje.json",
        lines,
        unr,
        sources=["https://tatuajecigars.com/"],
    )

    out = Path(__file__).resolve().parent / "output" / "phase3_w1_slice3_report.json"
    write_json(out, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
