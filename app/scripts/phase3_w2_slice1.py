#!/usr/bin/env python3
"""Phase 3 W2 slice-1: top 15 mid-size brands (5–19 lines)."""
from __future__ import annotations

import json
import re
from pathlib import Path

from taxonomy_lib import TAXONOMY_DIR, load_json, write_json

SNAP = Path(__file__).resolve().parent / "output" / "phase3_w2_slice1_snapshot.json"


def base(path: Path, brand: str) -> dict:
    existing = load_json(path, {}) or {}
    return {
        "brand": brand,
        "renameBrand": existing.get("renameBrand"),
        "status": "done",
        "reviewedAt": "2026-07-24",
        "sources": list(
            dict.fromkeys(
                (existing.get("sources") or [])
                + [
                    "phase3_w2_slice1 deterministic remaps",
                    "docs/superpowers/plans/2026-07-23-cigar-taxonomy-brand-line-vitola.md §7.3",
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


def write_brand(brand: str, fname: str, lines: dict, unresolved=None, keep=None, sources=None):
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


def romeo(rows: list) -> tuple[dict, list]:
    lines, unr = {}, []
    oro = {"Dianas", "Hidalgos", "Nobles"}
    for r in rows:
        raw = r.get("line") or ""
        if raw.startswith("Cedros De Luxe") or raw.startswith("Cedros de Luxe"):
            m = re.search(r"No\.?\s*\d+", raw)
            lines[raw] = {"line": "Cedros de Luxe", "vitola": m.group(0) if m else raw}
            continue
        if raw in ("Churchills", "Churchill Non Tubos", "Short"):
            vit = "Churchill" if raw != "Short" else "Short Churchill"
            if raw == "Churchills":
                lines[raw] = {"line": "Churchills"}
            else:
                lines[raw] = {"line": "Churchills", "vitola": vit}
            continue
        if raw in ("Classic", "Clásica", "Clasica"):
            lines[raw] = {"line": "Clásica"}
            continue
        if re.match(r"^No\.\s*\d+\s+Tubos$", raw):
            lines[raw] = {"line": "Clásica", "vitola": raw}
            continue
        if raw in oro:
            lines[raw] = {"line": "Línea de Oro", "vitola": raw}
            continue
        if raw.startswith("Línea de Oro") or raw.startswith("Linea de Oro"):
            lines[raw] = {"line": "Línea de Oro"}
            continue
        if raw == "Exhibicion No.4":
            lines[raw] = {"line": "Exhibición", "vitola": "No.4"}
            continue
        lines[raw] = {"line": raw}
    return lines, unr


def ajf(rows: list) -> tuple[dict, list]:
    lines, unr = {}, []
    for r in rows:
        raw = r.get("line") or ""
        if "20th Anniversary" in raw:
            wrap = "Maduro" if "Maduro" in " ".join(
                v.get("name") or "" for v in (r.get("vitolas") or [])
            ) or "Maduro" in raw else None
            if raw.startswith("AJF") and any(
                (v.get("name") or "").startswith("Maduro") for v in (r.get("vitolas") or [])
            ):
                lines[raw] = {"line": "20th Anniversary Maduro"}
            elif raw.startswith("A.J.") or raw.startswith("AJF"):
                lines[raw] = {"line": "20th Anniversary"}
            else:
                lines[raw] = {"line": "20th Anniversary"}
            continue
        if "Sampler" in raw:
            lines[raw] = {"line": raw, "sampler": True}
            continue
        if raw.startswith("Días de Gloria") or raw.startswith("Dias de Gloria"):
            lines[raw] = {"line": "Días de Gloria"}
            continue
        if raw.startswith("K by Karen"):
            lines[raw] = {"line": "K by Karen Berger"}
            continue
        lines[raw] = {"line": raw}
    unr.append("AJ Fernandez: New World / San Lotano vitola names still embed wrappers")
    return lines, unr


def asylum(rows: list) -> tuple[dict, list]:
    lines, unr = {}, []
    for r in rows:
        raw = r.get("line") or ""
        if raw == "867 Midnight Oil Midnight Oil":
            lines[raw] = {"line": "867 Midnight Oil"}
            continue
        if raw == "867 Zero Zero":
            lines[raw] = {"line": "867 Zero"}
            continue
        if raw.startswith("Flavoured "):
            vit = raw[len("Flavoured ") :]
            lines[raw] = {"line": "Flavoured", "vitola": vit}
            continue
        if raw == "Straight Jacket Double":
            lines[raw] = {"line": "Straight Jacket", "vitola": "Double"}
            continue
        if raw.startswith("Year 10"):
            lines[raw] = {"line": "Year 10", "vitola": "11/18"}
            continue
        # Size-as-line singles → Asylum core
        if raw in ("Robusto", "Gordo", "Gran Toro", "Short"):
            lines[raw] = {"line": "Asylum", "vitola": raw if raw != "Short" else "Short Corona"}
            continue
        lines[raw] = {"line": raw}
    return lines, unr


def cohiba(rows: list) -> tuple[dict, list]:
    lines, unr = {}, []
    for r in rows:
        raw = r.get("line") or ""
        if raw.startswith("Línea Clásica") or raw.startswith("Linea Clasica") or raw.startswith("Línea Clasica"):
            lines[raw] = {"line": "Línea Clásica"}
            continue
        if raw == "Robusto":
            lines[raw] = {"line": "Línea Clásica", "vitola": "Robusto"}
            continue
        for name in ("Coronas Especiales", "Esplendidos", "Exquisitos", "Ideales", "Maravillas", "Panetelas"):
            if raw == name:
                lines[raw] = {"line": "Línea Clásica", "vitola": name}
                break
        else:
            if raw.startswith("Maduro Genios") or raw.startswith("Maduro Secretos"):
                vit = "Genios" if "Genios" in raw else "Secretos"
                lines[raw] = {"line": "Maduro 5", "vitola": vit}
            elif raw == "Medio Siglo Tubos":
                lines[raw] = {"line": "Medio Siglo"}
            elif raw == "Piramides Extra":
                lines[raw] = {"line": "Pirámides Extra"}
            else:
                lines[raw] = {"line": raw}
    unr.append("Cohiba: Habanos Línea Clásica fold — verify against catalog")
    return lines, unr


def rojas(rows: list) -> tuple[dict, list]:
    lines, unr = {}, []
    for r in rows:
        raw = r.get("line") or ""
        if raw.startswith("Breakfast Tacos "):
            rest = raw[len("Breakfast Tacos ") :].replace(" Petit", "")
            lines[raw] = {"line": f"Breakfast Tacos {rest}", "vitola": "Petit"}
            continue
        if raw.startswith("Custom Blends "):
            rest = raw[len("Custom Blends ") :]
            lines[raw] = {"line": f"Custom Blends {rest}"}
            continue
        if raw.startswith("Gallo Pinto "):
            lines[raw] = {"line": raw}
            continue
        if raw.startswith("Street Tacos "):
            rest = raw[len("Street Tacos ") :]
            rest = re.sub(r"^Street\s+", "", rest)
            rest = re.sub(r"\s+Short$", "", rest)
            entry = {"line": f"Street Tacos {rest}"}
            if "Short" in raw:
                entry["vitola"] = "Short"
            lines[raw] = entry
            continue
        lines[raw] = {"line": raw}
    return lines, unr


def adv(rows: list) -> tuple[dict, list]:
    lines, unr = {}, []
    for r in rows:
        raw = r.get("line") or ""
        if raw.startswith("Conqueror "):
            vit = raw[len("Conqueror ") :]
            vit = re.sub(r"\s*-\s*Plus$", " Plus", vit)
            vit = re.sub(r"\s*-\s*Limited Edition$", "", vit)
            lines[raw] = {"line": "Conqueror", "vitola": vit.strip()}
            continue
        if raw.startswith("Navigator "):
            vit = raw[len("Navigator ") :]
            lines[raw] = {"line": "Navigator", "vitola": vit}
            continue
        if raw.startswith("Royal Return "):
            vit = raw[len("Royal Return ") :]
            lines[raw] = {"line": "Royal Return", "vitola": vit}
            continue
        if raw == "Piece of Heart Short":
            lines[raw] = {"line": "Piece of Heart", "vitola": "Short"}
            continue
        lines[raw] = {"line": raw}
    unr.append("Adv: brand name looks truncated (Phase-2 leftover) — renameBrand later")
    return lines, unr


def partagas(rows: list) -> tuple[dict, list]:
    lines, unr = {}, []
    maestra = {"Maestro", "Origen", "Rito"}
    for r in rows:
        raw = r.get("line") or ""
        if raw in maestra:
            lines[raw] = {"line": "Línea Maestra", "vitola": raw}
            continue
        if raw.startswith("Línea Maestra") or raw.startswith("Linea Maestra"):
            lines[raw] = {"line": "Línea Maestra"}
            continue
        if raw == "Serie E No.2":
            lines[raw] = {"line": "Serie E", "vitola": "No.2"}
            continue
        if raw in ("Classic", "Short", "Shorts / Serie E"):
            if raw == "Classic":
                lines[raw] = {"line": "Clásica"}
            elif raw == "Short":
                lines[raw] = {"line": "Clásica", "vitola": "Short"}
            else:
                lines[raw] = {"line": "Clásica"}
            continue
        if raw in ("Lusitanias", "Presidente", "Capitolio", "Legado", "Mille Fleurs"):
            lines[raw] = {"line": raw}
            continue
        lines[raw] = {"line": raw}
    unr.append("Partagás: Habanos Clásica / Serie fold — verify")
    return lines, unr


def woermann(rows: list) -> tuple[dict, list]:
    lines, unr = {}, []
    for r in rows:
        raw = r.get("line") or ""
        if raw.startswith("Seaman "):
            # Seaman Lord Nelson Brasil No. 80 → Lord Nelson Brasil
            rest = raw[len("Seaman ") :]
            rest = re.sub(r"\s+No\.\s*\d+\s*$", "", rest)
            lines[raw] = {"line": f"Seaman {rest}"}
            continue
        if raw.startswith("Natur Classic "):
            rest = raw[len("Natur Classic ") :]
            m = re.match(r"No\.\s*(\d+)\s+(.+)$", rest)
            if m:
                lines[raw] = {"line": f"Natur Classic {m.group(2)}", "vitola": f"No. {m.group(1)}"}
            else:
                lines[raw] = {"line": "Natur Classic"}
            continue
        lines[raw] = {"line": raw}
    return lines, unr


def casa(rows: list) -> tuple[dict, list]:
    lines, unr = {}, []
    for r in rows:
        raw = r.get("line") or ""
        if raw.startswith("de Torres "):
            rest = raw[len("de Torres ") :]
            if rest.startswith("Edicion Famoso") or rest.startswith("Edición Famoso"):
                lines[raw] = {"line": "de Torres Edición Famoso", "vitola": rest.split(" ", 2)[-1] if False else rest}
                # cleaner: keep Famoso roman as vitola
                m = re.match(r"Edici[oó]n Famoso\s+(\S+)(?:\s+(.+))?$", rest)
                if m:
                    num, tail = m.group(1), m.group(2)
                    vit = f"{num} {tail}".strip() if tail else num
                    lines[raw] = {"line": "de Torres Edición Famoso", "vitola": vit}
                else:
                    lines[raw] = {"line": f"de Torres {rest}"}
            elif rest in ("Bold", "Maduro Selection", "Edicion Especial", "Edición Especial"):
                lines[raw] = {"line": f"de Torres {rest.replace('Edicion', 'Edición')}"}
            else:
                lines[raw] = {"line": f"de Torres {rest}"}
            continue
        if raw == "de Torres":
            lines[raw] = {"line": "de Torres"}
            continue
        if raw.startswith("de Alegria "):
            wrap = raw[len("de Alegria ") :]
            lines[raw] = {"line": f"de Alegría {wrap}"}
            continue
        if raw.startswith("Culinaria "):
            lines[raw] = {"line": raw}
            continue
        if raw.startswith("de Garcia "):
            lines[raw] = {"line": raw.replace("de Garcia", "de García")}
            continue
        lines[raw] = {"line": raw}
    unr.append("Casa: brand truncated (mixed Casa Cuevas/Torres/…) — Phase-2 leftover")
    return lines, unr


def tabacalera(rows: list) -> tuple[dict, list]:
    lines, unr = {}, []
    for r in rows:
        raw = r.get("line") or ""
        if raw.startswith("1881 Perique"):
            rest = raw[len("1881 ") :]
            lines[raw] = {"line": f"1881 {rest}"}
            continue
        if raw.startswith("del Oriente "):
            rest = raw[len("del Oriente ") :]
            if rest.startswith("Amazonas Masterblend"):
                m = re.search(r"No\.\s*\d+", rest)
                lines[raw] = {
                    "line": "del Oriente Amazonas Masterblend",
                    "vitola": m.group(0) if m else rest,
                }
            elif rest.startswith("Pipa "):
                lines[raw] = {"line": "del Oriente Pipa", "vitola": rest[len("Pipa ") :]}
            else:
                lines[raw] = {"line": f"del Oriente {rest}"}
            continue
        if raw.startswith("Don Juan Urquijo "):
            vit = raw[len("Don Juan Urquijo ") :]
            lines[raw] = {"line": "Don Juan Urquijo", "vitola": vit}
            continue
        lines[raw] = {"line": raw}
    return lines, unr


def vegafina(rows: list) -> tuple[dict, list]:
    lines, unr = {}, []
    for r in rows:
        raw = r.get("line") or ""
        if raw.startswith("1998 "):
            rest = raw[len("1998 ") :]
            if rest.startswith("VF "):
                lines[raw] = {"line": "1998", "vitola": rest[len("VF ") :]}
            else:
                lines[raw] = {"line": "1998", "vitola": rest}
            continue
        if "Dosmilcatorce" in raw or "Gran Reserva" in raw and raw.startswith("Nicaragua"):
            lines[raw] = {"line": "Nicaragua Gran Reserva"}
            continue
        if raw in ("Vega Fina", "Vega Fina Nicaragua"):
            lines[raw] = {"line": "Nicaragua" if "Nicaragua" in raw else "Classic"}
            continue
        if raw == "Classic / Fortaleza 2":
            lines[raw] = {"line": "Fortaleza 2"}
            continue
        if raw.startswith("Serie 2"):
            if raw == "Serie 2 Coupage":
                lines[raw] = {"line": "Serie 2", "vitola": "Coupage"}
            else:
                lines[raw] = {"line": "Serie 2"}
            continue
        if raw.startswith("Year Of ") or raw.startswith("Year of "):
            lines[raw] = {"line": raw.replace("Year Of ", "Year of the ").replace("Year of ", "Year of the ")}
            # fix double the
            lines[raw]["line"] = re.sub(r"Year of the the ", "Year of the ", lines[raw]["line"])
            continue
        lines[raw] = {"line": raw}
    return lines, unr


def el_viejo(rows: list) -> tuple[dict, list]:
    lines, unr = {}, []
    for r in rows:
        raw = r.get("line") or ""
        if raw.startswith("Continente "):
            rest = raw[len("Continente ") :]
            if rest.startswith("Gaudi "):
                color = rest[len("Gaudi ") :]
                lines[raw] = {"line": "Gaudí", "vitola": color}
            elif rest.startswith("Mediumfiller "):
                vit = rest[len("Mediumfiller ") :]
                lines[raw] = {"line": "Mediumfiller", "vitola": vit}
            elif rest.startswith("Edicion Aniversario") or rest.startswith("Edición Aniversario"):
                lines[raw] = {"line": "Edición Aniversario"}
            else:
                lines[raw] = {"line": rest}
            continue
        lines[raw] = {"line": raw}
    return lines, unr


def helvada(rows: list) -> tuple[dict, list]:
    lines, unr = {}, []
    for r in rows:
        raw = r.get("line") or ""
        if raw.startswith("Dark Line "):
            rest = raw[len("Dark Line ") :]
            # Brain / Hearth Heart / Skull Skull → dedupe
            rest = re.sub(r"\b(\w+)\s+\1\b", r"\1", rest)
            rest = rest.replace("Hearth Heart", "Heart")
            lines[raw] = {"line": "Dark Line", "vitola": rest}
            continue
        if raw.startswith("Medio Filler "):
            rest = raw[len("Medio Filler ") :]
            if rest.startswith("1973 "):
                wrap = rest[len("1973 ") :]
                lines[raw] = {"line": f"Medio Filler 1973 {wrap}"}
            else:
                lines[raw] = {"line": "Medio Filler", "vitola": rest}
            continue
        if re.fullmatch(r"\d{2}", raw):
            lines[raw] = {"line": "Helvada", "vitola": raw}
            continue
        lines[raw] = {"line": raw}
    return lines, unr


def torano(rows: list) -> tuple[dict, list]:
    lines, unr = {}, []
    for r in rows:
        raw = r.get("line") or ""
        cleaned = re.sub(r"^Torano\s+", "", raw)
        cleaned = re.sub(r"^Toraño\s+", "", cleaned)
        if cleaned.startswith("Exodus 1959"):
            rest = cleaned[len("Exodus 1959") :].strip()
            if not rest:
                lines[raw] = {"line": "Exodus 1959"}
            elif rest.startswith("50 Years"):
                lines[raw] = {"line": "Exodus 1959 50 Years"}
            elif rest in ("Gold", "Silver"):
                lines[raw] = {"line": f"Exodus 1959 {rest}"}
            else:
                lines[raw] = {"line": f"Exodus 1959 {rest}"}
            continue
        if cleaned.startswith("Exodus Gold"):
            lines[raw] = {"line": "Exodus Gold"}
            continue
        if cleaned.startswith("Vault "):
            code = cleaned[len("Vault ") :]
            lines[raw] = {"line": "Vault", "vitola": code}
            continue
        if cleaned.startswith("Salutem"):
            rest = cleaned[len("Salutem") :].strip()
            if rest:
                lines[raw] = {"line": "Salutem", "vitola": rest}
            else:
                lines[raw] = {"line": "Salutem"}
            continue
        lines[raw] = {"line": cleaned or raw}
    unr.append("Toraño: Exodus 1959 Gold vs Exodus Gold kept as distinct lines")
    return lines, unr


def lfd(rows: list) -> tuple[dict, list]:
    lines, unr = {}, []
    for r in rows:
        raw = r.get("line") or ""
        if raw in ("Limited Edition La Nox", "La Nox"):
            lines[raw] = {"line": "La Nox"}
            continue
        if raw.startswith("Limited Edition "):
            lines[raw] = {"line": raw[len("Limited Edition ") :]}
            continue
        if raw.startswith("Reserva Especial "):
            vit = raw[len("Reserva Especial ") :]
            lines[raw] = {"line": "Reserva Especial", "vitola": vit}
            continue
        if raw.startswith("Suave "):
            vit = raw[len("Suave ") :]
            lines[raw] = {"line": "Suave", "vitola": vit}
            continue
        if raw.startswith("Double Claro"):
            m = re.search(r"No\.\s*\d+", raw)
            lines[raw] = {"line": "Double Claro", "vitola": m.group(0) if m else "No. 50"}
            continue
        lines[raw] = {"line": raw}
    return lines, unr


def main() -> None:
    snap = json.loads(SNAP.read_text(encoding="utf-8"))
    report = {}

    specs = [
        ("Romeo y Julieta", "romeo-y-julieta.json", romeo, ["https://www.habanos.com/"]),
        ("AJ Fernandez", "aj-fernandez.json", ajf, ["https://ajfernandez.com/"]),
        ("Asylum", "asylum.json", asylum, ["https://asylumcigars.com/"]),
        ("Cohiba", "cohiba.json", cohiba, ["https://www.habanos.com/"]),
        ("Rojas", "rojas.json", rojas, []),
        ("Adv", "adv.json", adv, []),
        ("Partagás", "partagas.json", partagas, ["https://www.habanos.com/"]),
        ("Woermann", "woermann.json", woermann, []),
        ("Casa", "casa.json", casa, []),
        ("Tabacalera", "tabacalera.json", tabacalera, []),
        ("VegaFina", "vegafina.json", vegafina, []),
        ("El Viejo Continente", "el-viejo-continente.json", el_viejo, []),
        ("Helvada", "helvada.json", helvada, []),
        ("Toraño", "torano.json", torano, []),
        ("La Flor Dominicana", "la-flor-dominicana.json", lfd, ["https://laflordominicana.com/"]),
    ]

    for brand, fname, fn, sources in specs:
        result = fn(snap[brand])
        if len(result) == 3:
            lines, unr, keep = result
            report[brand] = write_brand(brand, fname, lines, unr, keep=keep, sources=sources or None)
        else:
            lines, unr = result
            report[brand] = write_brand(brand, fname, lines, unr, sources=sources or None)

    out = Path(__file__).resolve().parent / "output" / "phase3_w2_slice1_report.json"
    write_json(out, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
