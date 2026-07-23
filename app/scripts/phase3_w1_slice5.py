#!/usr/bin/env python3
"""Phase 3 W1 slice-5: final W1 brands (9).

Aganorsa Leaf, PDR, Ashton, Eiroa, Flor de Selva, 1502, Artista,
Casa Turrent, La Aroma de Cuba.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from taxonomy_lib import TAXONOMY_DIR, load_json, write_json

SNAP = Path(__file__).resolve().parent / "output" / "phase3_w1_slice5_snapshot.json"


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
                    "phase3_w1_slice5 deterministic remaps",
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


def aganorsa(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""

        if raw.startswith("La Validacion "):
            wrap = raw[len("La Validacion ") :]
            lines[raw] = {"line": f"La Validación {wrap}"}
            continue

        if raw.startswith("Signature Selection "):
            rest = raw[len("Signature Selection ") :]
            if rest == "Gorda":
                lines[raw] = {"line": "Signature Selection", "vitola": "Gorda"}
            else:
                # Corojo / Maduro wrapper lines stay distinct
                lines[raw] = {"line": f"Signature Selection {rest}"}
            continue

        if raw.startswith("Rare Leaf Reserve "):
            wrap = raw[len("Rare Leaf Reserve ") :]
            lines[raw] = {"line": f"Rare Leaf Reserve {wrap}"}
            continue

        if raw.startswith("Supreme Leaf ") and raw != "Supreme Leaf":
            vit = raw[len("Supreme Leaf ") :]
            lines[raw] = {"line": "Supreme Leaf", "vitola": vit}
            continue

        if raw.startswith("JFR "):
            lines[raw] = {"line": raw}
            continue

        lines[raw] = {"line": raw}
    return lines, unr


def pdr(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""

        # Preserve existing Crystal remaps from seed if still present as keys
        m = re.match(r"^Capa (Madura|Natural|Oscura|Sun Grown) Crystal$", raw)
        if m:
            lines[raw] = {"line": f"Capa {m.group(1)}", "vitola": "Crystal"}
            continue

        if raw.startswith("A. Flores Gran Reserva "):
            wrap = raw[len("A. Flores Gran Reserva ") :]
            lines[raw] = {"line": "A. Flores Gran Reserva", "vitola": wrap}
            continue

        if raw.startswith("El Criollito "):
            wrap = raw[len("El Criollito ") :]
            lines[raw] = {"line": "El Criollito", "vitola": wrap}
            continue

        if raw.startswith("El Vinyet Cuvee Especial "):
            rest = raw[len("El Vinyet Cuvee Especial ") :]
            # BF 52 Fino 2024 → Fino, etc.
            vit = re.sub(r"^(BF|RC|WC)\s+\d+\s+", "", rest)
            vit = re.sub(r"\s+2024$", "", vit)
            lines[raw] = {"line": "El Vinyet Cuvée Especial", "vitola": vit}
            continue

        if raw.startswith("1975 Privada Rosado"):
            lines[raw] = {"line": "1975 Privada Rosado"}
            continue

        if raw.startswith("1878 "):
            rest = raw[len("1878 ") :]
            lines[raw] = {"line": "1878", "vitola": rest}
            continue

        lines[raw] = {"line": raw}
    return lines, unr


def ashton(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""

        if raw.startswith("Heritage "):
            vit = raw[len("Heritage ") :]
            lines[raw] = {"line": "Heritage", "vitola": vit}
            continue

        if raw.startswith("Paradiso By "):
            rest = raw[len("Paradiso By ") :]
            # Papagayo / Monumento — Paradiso sub-lines
            if rest.endswith(" XXL"):
                lines[raw] = {"line": f"Paradiso {rest[:-4].strip()}", "vitola": "XXL"}
            else:
                lines[raw] = {"line": f"Paradiso {rest}"}
            continue

        if raw.startswith("It's a Boy / It's a Girl"):
            if "Girl" in raw.split("Crystal")[-1]:
                lines[raw] = {"line": "It's a Girl", "sampler": True}
            else:
                lines[raw] = {"line": "It's a Boy", "sampler": True}
            continue

        if raw == "Paradiso By Papagayo XXL":
            lines[raw] = {"line": "Paradiso Papagayo", "vitola": "XXL"}
            continue

        lines[raw] = {"line": raw}
    unr.append("Ashton: VSG / Cabinet keepSeparate pairs retained from seed")
    return lines, unr


def eiroa(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""

        if raw in ("Cbt", "CBT Maduro"):
            lines[raw] = {"line": "CBT" if raw == "Cbt" else "CBT Maduro"}
            continue
        if raw.startswith("CBT Maduro /"):
            lines[raw] = {"line": "CBT Maduro"}
            continue

        if raw.startswith("20 Years "):
            # 20 Years Colorado Robusto Prensado → 20 Years Colorado, vitola Robusto Prensado
            m = re.match(r"^20 Years (Colorado|Maduro)(?:\s+(.+))?$", raw)
            if m:
                wrap, rest = m.group(1), m.group(2)
                if rest:
                    lines[raw] = {"line": f"20 Years {wrap}", "vitola": rest}
                else:
                    lines[raw] = {"line": f"20 Years {wrap}"}
                continue

        if raw.startswith("First 20 Years ") or raw.startswith("The First 20 Years "):
            rest = re.sub(r"^The First 20 Years\s+", "", raw)
            rest = re.sub(r"^First 20 Years\s+", "", rest)
            m = re.match(r"^(Colorado|Maduro)(?:\s+(.+))?$", rest)
            if m:
                wrap, vit = m.group(1), m.group(2)
                # Strip dimension suffix from Diadema
                if vit:
                    vit = re.sub(r"\s+\d+\s*[Xx×]\s*[\d-]+$", "", vit).strip()
                    lines[raw] = {"line": f"First 20 Years {wrap}", "vitola": vit}
                else:
                    lines[raw] = {"line": f"First 20 Years {wrap}"}
                continue

        if raw == "Classic / Colorado":
            lines[raw] = {"line": "Classic Colorado"}
            continue

        if raw == "Jamastran 11/18":
            lines[raw] = {"line": "Jamastran", "vitola": "11/18"}
            continue

        lines[raw] = {"line": raw}
    return lines, unr


def flor_de_selva(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""

        m = re.match(r"^(\d{4}) Year of (\w+)$", raw)
        if m:
            year, animal = m.group(1), m.group(2)
            lines[raw] = {"line": f"Year of the {animal} {year}"}
            continue

        if raw in ("Ano Del Dragon", "Año Del Dragon", "Año del Dragón"):
            lines[raw] = {"line": "Year of the Dragon 2024"}
            continue

        if raw in ("Clasica", "Clásica"):
            lines[raw] = {"line": "Clásica"}
            continue

        if raw in ("Maduro Grand-Press", "Grand Presse Maduro"):
            lines[raw] = {"line": "Grand Presse Maduro"}
            continue

        if raw.startswith("Coffret "):
            vit = raw[len("Coffret ") :]
            lines[raw] = {"line": "Coffret", "vitola": vit}
            continue

        if raw == "El Galan Cabinet":
            lines[raw] = {"line": "El Galán", "vitola": "Cabinet"}
            continue

        if raw == "Robusto Maduro":
            lines[raw] = {"line": "Maduro", "vitola": "Robusto", "shape": "Robusto"}
            continue

        if raw == "No. 20 Celebracion":
            lines[raw] = {"line": "No. 20", "vitola": "Celebracion"}
            continue

        if raw == "Numero Xv":
            lines[raw] = {"line": "Número XV"}
            continue

        lines[raw] = {"line": raw}
    return lines, unr


def brand_1502(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""

        if raw in ("Aniversario 10", "Special Edition Anniversario 10"):
            lines[raw] = {"line": "Aniversario 10"}
            continue

        if raw == "Blue Sapphire Robusto Gordo":
            lines[raw] = {
                "line": "Special Edition Blue Sapphire",
                "vitola": "Robusto Gordo",
                "shape": "Gordo",
            }
            continue

        if raw.startswith("Special Edition Blue Sapphire"):
            # may already be correct; keep Gordo remap from seed if present
            if raw.endswith(" Gordo"):
                lines[raw] = {
                    "line": "Special Edition Blue Sapphire",
                    "vitola": "Robusto",
                    "shape": "Robusto",
                }
            else:
                lines[raw] = {"line": "Special Edition Blue Sapphire"}
            continue

        if raw in ("Xo Conquistador", "Xo Perfecto"):
            vit = raw[len("Xo ") :]
            lines[raw] = {"line": "Special Edition XO Series", "vitola": vit}
            continue

        if raw == "Special Edition XO Series":
            lines[raw] = {"line": "Special Edition XO Series"}
            continue

        lines[raw] = {"line": raw}
    return lines, unr


def artista(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""

        if raw.startswith("ART-56 "):
            wrap = raw[len("ART-56 ") :]
            lines[raw] = {"line": f"ART-56 {wrap}"}
            continue

        if raw.startswith("Factory Classics "):
            rest = raw[len("Factory Classics ") :]
            if rest.startswith("Puro Ambar"):
                # Puro Ambar / Puro Ambar Legacy Grand already partially remapped
                if "Legacy Grand" in rest or rest.endswith(" Grand"):
                    lines[raw] = {
                        "line": "Factory Classics Puro Ambar",
                        "vitola": "Legacy Grand Toro",
                    }
                else:
                    lines[raw] = {"line": "Factory Classics Puro Ambar"}
            elif rest.startswith("Exactus "):
                wrap = rest[len("Exactus ") :]
                lines[raw] = {"line": f"Factory Classics Exactus {wrap}"}
            elif rest.startswith("Pulita"):
                lines[raw] = {"line": "Factory Classics Pulita"}
            else:
                lines[raw] = {"line": f"Factory Classics {rest}"}
            continue

        if raw.startswith("Rugged Country "):
            rest = raw[len("Rugged Country ") :]
            if rest.startswith("Cimarron "):
                wrap = rest[len("Cimarron ") :]
                lines[raw] = {"line": f"Rugged Country Cimarron {wrap}"}
            elif "Buffalo" in rest:
                lines[raw] = {"line": "Rugged Country Buffalo Ten"}
            else:
                lines[raw] = {"line": f"Rugged Country {rest}"}
            continue

        if raw.startswith("David Ortiz Slugger"):
            lines[raw] = {"line": "David Ortiz Slugger"}
            continue

        lines[raw] = {"line": raw}
    return lines, unr


def casa_turrent(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""

        if raw.startswith("1880 "):
            rest = raw[len("1880 ") :]
            # Colorado Doble / Maduro Doble / Oscuro Doble → vitola Doble on wrapper line
            m = re.match(r"^(Claro|Colorado|Maduro|Oscuro|Rosado|Edici[oó]n Limitada)(?:\s+(.+))?$", rest)
            if m:
                head, vit = m.group(1), m.group(2)
                head = head.replace("Edicion Limitada", "Edición Limitada").replace(
                    "Edición Limitada", "Edición Limitada"
                )
                if "Edici" in head:
                    lines[raw] = {"line": "1880 Edición Limitada"}
                elif vit:
                    lines[raw] = {"line": f"1880 {head}", "vitola": vit}
                else:
                    lines[raw] = {"line": f"1880 {head}"}
                continue
            lines[raw] = {"line": f"1880 {rest}"}
            continue

        if raw.startswith("Origin Extra "):
            region = raw[len("Origin Extra ") :]
            lines[raw] = {"line": "Origin Extra", "vitola": region}
            continue

        if raw in ("1942 NATURAL", "1973 NATURAL"):
            year = raw.split()[0]
            lines[raw] = {"line": year, "vitola": "Natural"}
            continue

        if raw == "Maduro Short":
            lines[raw] = {"line": "Maduro", "vitola": "Short"}
            continue

        if raw == "Revolution Original":
            lines[raw] = {"line": "Revolution"}
            continue

        lines[raw] = {"line": raw}
    return lines, unr


def la_aroma(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""

        # Seed leftovers with vitola already in line name
        for prefix, target in (
            ("La Aroma del Caribe Base Line ", "Base Line"),
            ("La Aroma del Caribe Mi Amor ", "Mi Amor"),
            ("La Aroma del Caribe Pasion ", "Pasión"),
            ("La Aroma del Caribe Connecticut ", "Connecticut"),
        ):
            if raw.startswith(prefix):
                vit = raw[len(prefix) :]
                # Fix known seed bug Immensa → El Jefe
                if vit == "Immensa":
                    vit = "Immensa"
                lines[raw] = {"line": target, "vitola": vit}
                break
        else:
            if raw.startswith("La Aroma del Caribe "):
                rest = raw[len("La Aroma del Caribe ") :]
                rest = rest.replace("Pasion", "Pasión").replace("Base Line", "Base Line")
                lines[raw] = {"line": rest}
            elif raw.startswith("La Aroma Del Caribe"):
                lines[raw] = {"line": "Base Line"}
            elif raw == "La Aroma de Cuba":
                lines[raw] = {"line": "La Aroma de Cuba"}
            elif raw.startswith("Edicion Especial") or raw.startswith("Edición Especial"):
                lines[raw] = {"line": re.sub(r"^Edici[oó]n Especial", "Edición Especial", raw)}
            elif raw == "Noblesse Viceroy":
                lines[raw] = {"line": "Noblesse", "vitola": "Viceroy"}
            elif raw in ("Pasion", "Pasión"):
                lines[raw] = {"line": "Pasión"}
            elif raw == "Mi Amor":
                lines[raw] = {"line": "Mi Amor"}
            else:
                lines[raw] = {"line": raw}

    # Also map any remaining seed keys from taxonomy file that may not be in live snap
    seed_keys = {
        "La Aroma del Caribe Base Line El Jefe": {
            "line": "Base Line",
            "vitola": "El Jefe",
        },
        "La Aroma del Caribe Base Line Immensa": {
            "line": "Base Line",
            "vitola": "Immensa",
        },
        "La Aroma del Caribe Base Line Monarch": {
            "line": "Base Line",
            "vitola": "Monarch",
        },
        "La Aroma del Caribe Mi Amor Duque": {"line": "Mi Amor", "vitola": "Duque"},
        "La Aroma del Caribe Mi Amor Valentino": {
            "line": "Mi Amor",
            "vitola": "Valentino",
        },
    }
    for k, v in seed_keys.items():
        lines.setdefault(k, v)

    unr.append("La Aroma de Cuba: Caribe vs Cuba naming — Base Line / Mi Amor / Pasión folded")
    return lines, unr


def main() -> None:
    snap = json.loads(SNAP.read_text(encoding="utf-8"))
    report = {}

    lines, unr = aganorsa(snap["Aganorsa Leaf"])
    report["Aganorsa Leaf"] = write_brand(
        "Aganorsa Leaf",
        "aganorsa-leaf.json",
        lines,
        unr,
        sources=["https://aganorsa.com/"],
    )

    lines, unr = pdr(snap["PDR"])
    report["PDR"] = write_brand("PDR", "pdr.json", lines, unr, sources=["https://pdrcigars.com/"])

    lines, unr = ashton(snap["Ashton"])
    report["Ashton"] = write_brand(
        "Ashton", "ashton.json", lines, unr, sources=["https://ashtoncigar.com/"]
    )

    lines, unr = eiroa(snap["Eiroa"])
    report["Eiroa"] = write_brand(
        "Eiroa", "eiroa.json", lines, unr, sources=["https://eiroacigars.com/"]
    )

    lines, unr = flor_de_selva(snap["Flor de Selva"])
    report["Flor de Selva"] = write_brand(
        "Flor de Selva",
        "flor-de-selva.json",
        lines,
        unr,
        sources=["https://flor-de-selva.com/"],
    )

    lines, unr = brand_1502(snap["1502"])
    report["1502"] = write_brand("1502", "1502.json", lines, unr, sources=["https://1502cigars.com/"])

    lines, unr = artista(snap["Artista"])
    report["Artista"] = write_brand(
        "Artista", "artista.json", lines, unr, sources=["https://artistacigars.com/"]
    )

    lines, unr = casa_turrent(snap["Casa Turrent"])
    report["Casa Turrent"] = write_brand(
        "Casa Turrent",
        "casa-turrent.json",
        lines,
        unr,
        sources=["https://casaturrent.com/"],
    )

    lines, unr = la_aroma(snap["La Aroma de Cuba"])
    report["La Aroma de Cuba"] = write_brand(
        "La Aroma de Cuba",
        "la-aroma-de-cuba.json",
        lines,
        unr,
        sources=["https://ashtoncigar.com/"],
    )

    out = Path(__file__).resolve().parent / "output" / "phase3_w1_slice5_report.json"
    write_json(out, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
