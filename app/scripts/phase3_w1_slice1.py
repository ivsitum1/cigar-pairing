#!/usr/bin/env python3
"""Phase 3 W1 slice-1: deterministic remaps for Phase-2 tails + La Galera/Oliva/RoMa.

Only writes taxonomy JSON. Parent runs apply-taxonomy.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from taxonomy_lib import TAXONOMY_DIR, brand_slug, load_json, write_json

SNAP = Path(__file__).resolve().parent / "output" / "phase3_w1_snapshot.json"

# Live brand → taxonomy file (Phase-2 rename sources keep old slug)
FILE_FOR = {
    "La Galera": "la-galera.json",
    "Oliva": "oliva.json",
    "RoMa Craft Tobac": "roma.json",
    "Black Label Trading Company": "black-label.json",
    "Laura Chavin": "laura.json",
    "Cavalier Genève": "cavalier.json",
    "Gran Habano": "gh.json",
}

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
}


def as_shape(name: str | None) -> str | None:
    if not name:
        return None
    return name if name.casefold() in SHAPES else None


def load_base(path: Path, brand: str, rename: str | None) -> dict:
    existing = load_json(path, {}) or {}
    return {
        "brand": existing.get("brand") or brand,
        "renameBrand": existing.get("renameBrand") if rename is None else rename,
        "status": "done",
        "reviewedAt": "2026-07-23",
        "sources": list(
            dict.fromkeys(
                (existing.get("sources") or [])
                + [
                    "phase3_w1_slice1 deterministic remaps",
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


def strip_prefix_lines(rows: list, prefix: str) -> dict[str, dict]:
    out = {}
    for r in rows:
        raw = r.get("line") or ""
        if raw.startswith(prefix):
            rest = raw[len(prefix) :].strip()
            if rest:
                out[raw] = {"line": rest}
    return out


def roma_lines(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unresolved: list[str] = []
    for r in rows:
        raw = r.get("line") or ""
        shape = (r.get("vitolas") or [{}])[0].get("name")
        # CroMagnon Aquitaine <vitola>
        m = re.match(r"^CroMagnon Aquitaine (.+)$", raw)
        if m:
            lines[raw] = {
                "line": "CroMagnon Aquitaine",
                "vitola": m.group(1),
                **({"shape": shape} if shape else {}),
            }
            continue
        m = re.match(r"^CroMagnon (.+)$", raw)
        if m:
            lines[raw] = {
                "line": "CroMagnon",
                "vitola": m.group(1),
                **({"shape": shape} if shape else {}),
            }
            continue
        for fam in ("Intemperance BA XXI", "Intemperance EC XVIII", "Intemperance VO 1920", "Intemperance WR 1794"):
            if raw.startswith(fam + " "):
                vit = raw[len(fam) + 1 :]
                lines[raw] = {
                    "line": fam,
                    "vitola": vit,
                    **({"shape": shape} if shape else {}),
                }
                break
        else:
            if raw.startswith("Neanderthal "):
                # HS 5 3 etc. are maker vitola codes — keep as vitola of Neanderthal
                vit = raw[len("Neanderthal ") :]
                lines[raw] = {
                    "line": "Neanderthal",
                    "vitola": vit,
                    **({"shape": shape} if shape else {}),
                }
            elif raw == "Limited Edition Quinquagenario":
                lines[raw] = {"line": "Quinquagenario", "vitola": shape or "Robusto"}
            elif raw.startswith("Weaselitos "):
                lines[raw] = {"line": "Weaselitos", "vitola": raw[len("Weaselitos ") :]}
            elif raw in ("WunderLust", "WunderLust Limited Edition"):
                lines[raw] = {"line": raw}
            else:
                unresolved.append(f"RoMa Craft: no split for {raw!r}")
    return lines, unresolved


def la_galera_lines(rows: list) -> tuple[dict, list, list]:
    lines: dict[str, dict] = {}
    unresolved: list[str] = []
    keep: list[list[str]] = [
        ["Flor de Connecticut", "Flor de Corojo"],  # not Galera — ignore
        ["Imperial Jade", "Imperial Jade Reserva"],
        ["1936", "1936 Box Pressed"],
        ["Anemoi", "Anemoi Eurus"],  # may collapse Eurus into Anemoi — see below
    ]
    for r in rows:
        raw = r.get("line") or ""
        shape = (r.get("vitolas") or [{}])[0].get("name")
        # Samplers / gift
        if "Sampler" in raw or raw == "Rojo Gift Pack":
            lines[raw] = {"line": raw, "sampler": True}
            continue
        # 1936 <vitola>
        m = re.match(r"^1936 (.+)$", raw)
        if m and raw != "1936 Box Pressed":
            vit = m.group(1)
            if vit == "Box Pressed":
                lines[raw] = {"line": "1936 Box Pressed"}
            else:
                lines[raw] = {
                    "line": "1936",
                    "vitola": vit.replace("Pilon", "Pilón"),
                    **({"shape": shape} if shape else {}),
                }
            continue
        if raw == "1936 Box Pressed":
            lines[raw] = {"line": "1936 Box Pressed"}
            continue
        # Anemoi named winds
        m = re.match(r"^Anemoi (.+)$", raw)
        if m:
            vit = m.group(1)
            if vit == "Anemoi":
                lines[raw] = {"line": "Anemoi"}
            else:
                lines[raw] = {
                    "line": "Anemoi",
                    "vitola": vit,
                    **({"shape": shape} if shape else {}),
                }
            continue
        if raw == "Anemoi":
            lines[raw] = {"line": "Anemoi"}
            continue
        # Wrapper lines with trailing vitola
        for wrap in ("Corojo", "Habano", "Maduro", "Connecticut"):
            if raw == wrap:
                lines[raw] = {"line": wrap}
                break
            if raw.startswith(wrap + " "):
                rest = raw[len(wrap) + 1 :].strip(" –")
                # Habano Bonchero No.4 – etc.
                vit = rest
                shape_guess = None
                # strip leading shape word if present
                for sh in ("Robusto", "Half", "Lancero"):
                    if vit.startswith(sh + " "):
                        shape_guess = "Petit Corona" if sh == "Half" else sh
                        vit = vit[len(sh) + 1 :]
                        break
                    if vit == sh:
                        shape_guess = "Petit Corona" if sh == "Half" else sh
                        vit = "Half Corona" if sh == "Half" else sh
                        break
                if wrap == "Corojo" and vit == "Half":
                    vit = "Half Corona"
                    shape_guess = "Petit Corona"
                if wrap == "Habano" and vit in ("Lancero", "Habano Lancero"):
                    vit = "Lancero"
                    shape_guess = "Lancero"
                entry = {"line": wrap, "vitola": vit}
                sh = as_shape(shape_guess) or as_shape(shape)
                if sh:
                    entry["shape"] = sh
                lines[raw] = entry
                break
        else:
            # Imperial Jade
            if raw == "Imperial Jade":
                lines[raw] = {"line": "Imperial Jade"}
            elif raw.startswith("Imperial Jade "):
                vit = raw[len("Imperial Jade ") :]
                lines[raw] = {
                    "line": "Imperial Jade",
                    "vitola": vit.replace("Piramide", "Pirámide"),
                    **({"shape": shape} if shape else {}),
                }
            elif raw.startswith("La Instructora "):
                lines[raw] = {
                    "line": "La Instructora",
                    "vitola": raw[len("La Instructora ") :].replace("Perfeccion", "Perfección"),
                }
            elif raw.startswith("85th Anniversary"):
                lines[raw] = {"line": "85th Anniversary"}
            elif raw.startswith("Limited Edition") or raw.startswith("Fresh Pack"):
                lines[raw] = {"line": raw}
            else:
                unresolved.append(f"La Galera: no split for {raw!r}")
    # drop bogus keepSeparate for Flor de (Oliva)
    keep = [["1936", "1936 Box Pressed"], ["Imperial Jade", "Imperial Jade Reserva"]]
    return lines, unresolved, keep


def oliva_lines(rows: list) -> tuple[dict, list, list]:
    lines: dict[str, dict] = {}
    unresolved: list[str] = []
    keep = [["Flor de Connecticut", "Flor de Corojo"], ["Flor de Gold", "Flor de Maduro"], ["Flor de Original", "Flor de"]]
    for r in rows:
        raw = r.get("line") or ""
        if "Sampler" in raw:
            lines[raw] = {"line": raw, "sampler": True}
            continue
        # NUB leftovers under Oliva — should be Nub brand; leave unresolved
        if raw.startswith("NUB "):
            unresolved.append(f"Oliva: {raw!r} looks like Nub brand leakage — left unchanged")
            continue
        # Monticello already a line; Double Toro is vitola already in list
        if raw == "Monticello":
            lines[raw] = {"line": "Monticello"}
            continue
        if raw.startswith("Flor de ") or raw == "Flor de":
            lines[raw] = {"line": raw}
            continue
        if raw in (
            "Serie G",
            "Serie O",
            "Serie V",
            "Serie V / Melanio",
            "Connecticut Reserve",
            "Master Blends 3",
            "Gilberto Reserva",
            "Gilberto Reserva Blanc",
            "Mareva",
            "Edicion Ano 2024",
            "Extra Edicion Ano 2025",
            "Year of Snake 2025",
        ):
            lines[raw] = {"line": raw}
        else:
            unresolved.append(f"Oliva: review {raw!r}")
    return lines, unresolved, keep


def gran_habano_lines(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unresolved: list[str] = []
    for r in rows:
        raw = r.get("line") or ""
        if raw.startswith("G.H. "):
            rest = raw[len("G.H. ") :]
            mapping = {
                "Black Dahlia": "Black Dahlia",
                "Blue in Green": "Blue in Green",
                "Connecticut No. 1": "Connecticut #1",
                "Corojo No. 5": "Corojo #5",
                "Corojo No. 5 Maduro": "Corojo Maduro #5",
                "Criollo No. 3": "Criollo #3",
                "Gran Reserva No. 5": "Gran Reserva #5",
                "House Connecticut": "House Connecticut",
                "House Corojo": "House Corojo",
                "La Conquista": "La Conquista",
            }
            lines[raw] = {"line": mapping.get(rest, rest)}
        else:
            lines[raw] = {"line": raw}
    unresolved.append(
        "Gran Habano: merged G.H. Connecticut No. 1 with existing Connecticut #1 after apply — confirm vitola union"
    )
    return lines, unresolved


def main() -> None:
    snap = json.loads(SNAP.read_text(encoding="utf-8"))
    report = {}

    # La Galera
    path = TAXONOMY_DIR / "la-galera.json"
    base = load_base(path, "La Galera", None)
    lines, unr, keep = la_galera_lines(snap["La Galera"])
    base["lines"] = lines
    base["unresolved"] = unr
    base["keepSeparate"] = keep
    base["sources"].insert(0, "https://lagaleracigars.com/")
    write_json(path, base)
    report["La Galera"] = {"file": path.name, "remaps": len(lines), "unresolved": len(unr)}

    # Oliva
    path = TAXONOMY_DIR / "oliva.json"
    base = load_base(path, "Oliva", None)
    lines, unr, keep = oliva_lines(snap["Oliva"])
    base["lines"] = lines
    base["unresolved"] = unr
    base["keepSeparate"] = keep
    base["sources"].insert(0, "https://olivacigar.com/")
    write_json(path, base)
    report["Oliva"] = {"file": path.name, "remaps": len(lines), "unresolved": len(unr)}

    # RoMa Craft
    path = TAXONOMY_DIR / "roma.json"
    base = load_base(path, "Roma", "RoMa Craft Tobac")
    lines, unr = roma_lines(snap["RoMa Craft Tobac"])
    base["lines"] = lines
    base["unresolved"] = unr
    base["sources"].insert(0, "https://halfwheel.com/roma-craft-tobac-updating-cromagnon-line-in-2024/428403/")
    write_json(path, base)
    report["RoMa Craft Tobac"] = {"file": path.name, "remaps": len(lines), "unresolved": len(unr)}

    # Black Label
    path = TAXONOMY_DIR / "black-label.json"
    base = load_base(path, "Black Label", "Black Label Trading Company")
    lines = strip_prefix_lines(snap["Black Label Trading Company"], "Trading Company ")
    base["lines"] = lines
    base["keepSeparate"] = [["Santa Muerte", "Santa Muerte Barrio Santo"]]
    base["unresolved"] = ["Phase 3 slice-1: prefix strip only; vitola proprietary names unchanged"]
    write_json(path, base)
    report["Black Label Trading Company"] = {"file": path.name, "remaps": len(lines)}

    # Laura Chavin
    path = TAXONOMY_DIR / "laura.json"
    base = load_base(path, "Laura", "Laura Chavin")
    lines = strip_prefix_lines(snap["Laura Chavin"], "Chavin ")
    base["lines"] = lines
    base["unresolved"] = ["Phase 3 slice-1: Chavin prefix strip; Classic Nos. stay as line names"]
    write_json(path, base)
    report["Laura Chavin"] = {"file": path.name, "remaps": len(lines)}

    # Cavalier
    path = TAXONOMY_DIR / "cavalier.json"
    base = load_base(path, "Cavalier", "Cavalier Genève")
    lines = strip_prefix_lines(snap["Cavalier Genève"], "Genève ")
    # Limited Edition 2024 Double → Limited Edition 2024 + vitola? leave as line for now
    base["lines"] = lines
    base["unresolved"] = ["Phase 3 slice-1: Genève prefix strip only"]
    write_json(path, base)
    report["Cavalier Genève"] = {"file": path.name, "remaps": len(lines)}

    # Gran Habano
    path = TAXONOMY_DIR / "gh.json"
    base = load_base(path, "Gh", "Gran Habano")
    lines, unr = gran_habano_lines(snap["Gran Habano"])
    base["lines"] = lines
    base["unresolved"] = unr
    base["sources"].insert(0, "https://ghcigars.com/")
    write_json(path, base)
    report["Gran Habano"] = {"file": path.name, "remaps": len(lines), "unresolved": len(unr)}

    out = Path(__file__).resolve().parent / "output" / "phase3_w1_slice1_report.json"
    write_json(out, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
