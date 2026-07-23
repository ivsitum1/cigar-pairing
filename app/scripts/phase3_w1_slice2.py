#!/usr/bin/env python3
"""Phase 3 W1 slice-2: Oscar, Rocky, Perdomo, Gurkha, Villiger, EPC, Drew, Davidoff."""
from __future__ import annotations

import json
import re
from pathlib import Path

from taxonomy_lib import TAXONOMY_DIR, load_json, write_json

SNAP = Path(__file__).resolve().parent / "output" / "phase3_w1_slice2_snapshot.json"

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
    "figurado",
    "epicure",
    "grande",
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
                    "phase3_w1_slice2 deterministic remaps",
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


def write_brand(brand: str, fname: str, lines: dict, unresolved: list | None = None, keep=None, sources=None):
    path = TAXONOMY_DIR / fname
    b = base(path, brand)
    b["lines"] = lines
    b["unresolved"] = unresolved or []
    if keep:
        b["keepSeparate"] = keep
    if sources:
        b["sources"] = list(dict.fromkeys(sources + b["sources"]))
    write_json(path, b)
    return {"file": fname, "remaps": len(lines), "unresolved": len(b["unresolved"])}


def oscar(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""
        shape = (r.get("vitolas") or [{}])[0].get("name")
        if raw == "Sampler":
            lines[raw] = {"line": "Sampler", "sampler": True}
            continue
        # Ciseron Edition Toro Color → Ciseron Edition Color
        m = re.match(r"^Ciseron Edition Toro (.+)$", raw)
        if m:
            lines[raw] = {"line": f"Ciseron Edition {m.group(1)}", "vitola": "Toro"}
            continue
        m = re.match(r"^Edition Toro (.+)$", raw)
        if m:
            lines[raw] = {"line": f"Ciseron Edition {m.group(1)}", "vitola": "Toro"}
            continue
        # Wrapper+shape mashed: Connecticut Robusto (Round)
        m = re.match(r"^(Connecticut|Corojo|Maduro) (.+)$", raw)
        if m and "by Oscar" not in raw and not raw.startswith("Oscar "):
            wrap, rest = m.group(1), m.group(2)
            if rest.lower().startswith(("robusto", "short robusto", "toro", "gordo", "lancero")):
                lines[raw] = {"line": wrap, "vitola": rest}
                continue
        # 2012 by Oscar <wrapper>
        m = re.match(r"^2012 by Oscar (.+)$", raw)
        if m:
            lines[raw] = {"line": f"2012 by Oscar {m.group(1)}"}
            continue
        if raw.startswith("Leaf ") or raw.startswith("Plan B ") or raw.startswith("Super Fly ") or raw.startswith(
            "Island Jim "
        ):
            lines[raw] = {"line": raw}
            continue
        if raw in ("Oscar Connecticut", "Oscar Maduro"):
            lines[raw] = {"line": raw}
            continue
        if "Heaven" in raw:
            lines[raw] = {"line": raw.replace("&amp;", "&")}
            continue
        if raw.startswith("Gurkha "):
            unr.append(f"Oscar Valladares: {raw!r} looks like Gurkha leakage — left as-is")
            lines[raw] = {"line": raw}
            continue
        lines[raw] = {"line": raw}
    return lines, unr


def rocky(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""
        # Collapse Limited Editions Conviction → Conviction if duplicate intent
        if raw == "Limited Editions Conviction":
            lines[raw] = {"line": "Conviction"}
            continue
        if raw == "Alr 2nd":
            lines[raw] = {"line": "Aged Limited Rare Second Edition"}
            continue
        if raw.startswith("Renaissance Fumas "):
            lines[raw] = {"line": raw}
            continue
        if raw.startswith("Olde World Reserve "):
            lines[raw] = {"line": raw}
            continue
        if raw.startswith("Hamlet "):
            lines[raw] = {"line": raw}
            continue
        if raw.startswith("Seed To Smoke "):
            lines[raw] = {"line": raw}
            continue
        lines[raw] = {"line": raw}
    unr.append("Rocky Patel: Decade/Edge/A.L.B. vitola names still embed line tokens — Phase 3 polish later")
    return lines, unr


def perdomo(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""
        shape = (r.get("vitolas") or [{}])[0].get("name")
        m = re.match(r"^(Small Batch .+?) Half$", raw)
        if m:
            lines[raw] = {
                "line": m.group(1),
                "vitola": "Half Corona",
                "shape": "Petit Corona",
            }
            continue
        # 30th Anniversary Connecticut Epicure → 30th Anniversary Connecticut + Epicure
        m = re.match(r"^30th Anniversary Connecticut Epicure$", raw)
        if m:
            lines[raw] = {"line": "30th Anniversary Connecticut", "vitola": "Epicure"}
            continue
        if "Freshpack" in raw or "Fresh Pack" in raw:
            lines[raw] = {"line": raw, "sampler": True}
            continue
        lines[raw] = {"line": raw}
    return lines, unr


def gurkha(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""
        m = re.match(r"^Cellar Reserve (\d+ Years) (.+)$", raw)
        if m:
            years, vit = m.group(1), m.group(2)
            # Limitada Hedonism → keep Limitada as line qualifier
            if vit.startswith("Limitada "):
                lines[raw] = {"line": f"Cellar Reserve {years} Limitada", "vitola": vit[len("Limitada ") :]}
            else:
                lines[raw] = {"line": f"Cellar Reserve {years}", "vitola": vit}
            continue
        if raw == "Marquesa Kiste":
            lines[raw] = {"line": "Marquesa", "vitola": "Kiste"}
            continue
        lines[raw] = {"line": raw}
    return lines, unr


def villiger(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""
        if raw == "Villiger 1888":
            lines[raw] = {"line": "1888"}
            continue
        if raw == "Villiger Export":
            lines[raw] = {"line": "Export"}
            continue
        if raw == "San'Doro Maduro":
            lines[raw] = {"line": "San Doro Maduro"}
            continue
        lines[raw] = {"line": raw}
    unr.append("Villiger: 125 DNU / Selecto DNU meaning unverified — left unchanged")
    return lines, unr


def epc(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""
        shape = (r.get("vitolas") or [{}])[0].get("name")
        # Strip redundant EPC prefix
        if raw.startswith("EPC "):
            rest = raw[4:]
            # EPC Encore Celestial → Encore + Celestial
            m = re.match(r"^Encore (.+)$", rest)
            if m:
                vit = m.group(1)
                lines[raw] = {"line": "Encore", "vitola": vit}
                continue
            m = re.match(r"^Allegiance (.+)$", rest)
            if m:
                lines[raw] = {"line": "Allegiance", "vitola": m.group(1)}
                continue
            m = re.match(r"^Essence (Connecticut|Honduras|Maduro|Sumatra)$", rest)
            if m:
                lines[raw] = {"line": f"Essence {m.group(1)}"}
                continue
            m = re.match(r"^INCH Natural (.+)$", rest)
            if m:
                lines[raw] = {"line": "INCH Natural", "vitola": m.group(1)}
                continue
            m = re.match(r"^INCH Nicaragua (.+)$", rest)
            if m:
                lines[raw] = {"line": "INCH Nicaragua", "vitola": m.group(1)}
                continue
            m = re.match(r"^New Wave Connecticut (.+)$", rest)
            if m:
                lines[raw] = {"line": "New Wave Connecticut", "vitola": m.group(1)}
                continue
            if rest in ("Endure", "Pledge", "Aniversario 15", "Short Run 2023", "La Historia Silk"):
                if rest == "La Historia Silk":
                    lines[raw] = {"line": "La Historia", "vitola": "Silk"}
                elif rest == "Aniversario 15":
                    lines[raw] = {"line": "Aniversario 15"}
                else:
                    lines[raw] = {"line": rest}
                continue
            lines[raw] = {"line": rest}
            continue
        if raw == "Inch Maduro":
            lines[raw] = {"line": "INCH Maduro"}
            continue
        if raw == "Inch Natural":
            lines[raw] = {"line": "INCH Natural"}
            continue
        if raw == "Seleccion Oscuro Piramides Royal":
            lines[raw] = {"line": "Seleccion Oscuro", "vitola": "Piramides Royal"}
            continue
        if raw == "Maduro Predilectos":
            lines[raw] = {"line": "Maduro", "vitola": "Predilectos"}
            continue
        lines[raw] = {"line": raw}
    return lines, unr


def drew(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""
        # Strip shipping-restriction noise
        cleaned = re.sub(r"\s*-\s*Shipping restrictions\s*$", "", raw).strip()
        cleaned = re.sub(r"\s+by\s*-\s*$", "", cleaned).strip()
        cleaned = re.sub(r"\s+by\s+$", "", cleaned).strip()
        # Deadwood by Crazy Alice → Deadwood Crazy Alice (line) or Deadwood + vitola
        m = re.match(r"^Deadwood by (.+)$", cleaned)
        if m:
            lines[raw] = {"line": f"Deadwood {m.group(1)}"}
            continue
        m = re.match(r"^Liga Undercrown(?: (.+))?$", cleaned)
        if m:
            rest = m.group(1)
            if not rest:
                lines[raw] = {"line": "Undercrown"}
            elif rest.startswith("10"):
                # Undercrown 10 / 10 by Doble
                if "by Doble" in rest or rest == "10 by Doble":
                    lines[raw] = {"line": "Undercrown 10", "vitola": "Doble"}
                else:
                    lines[raw] = {"line": f"Undercrown {rest}"}
            elif rest.startswith("by "):
                lines[raw] = {"line": "Undercrown", "vitola": rest[3:]}
            else:
                lines[raw] = {"line": f"Undercrown {rest}"}
            continue
        if cleaned.startswith("Factory Smokes "):
            lines[raw] = {"line": cleaned}
            continue
        if cleaned.startswith("Nica Rustica "):
            lines[raw] = {"line": cleaned}
            continue
        if cleaned.startswith("Blackened "):
            # Blackened M81 Maduro to Core M81 → Blackened M81
            if "M81" in cleaned:
                lines[raw] = {"line": "Blackened M81"}
            elif "S84" in cleaned:
                lines[raw] = {"line": "Blackened S84"}
            else:
                lines[raw] = {"line": cleaned}
            continue
        if cleaned != raw and cleaned:
            lines[raw] = {"line": cleaned}
            continue
        lines[raw] = {"line": cleaned or raw}
    unr.append("Drew Estate: Acid/Java/Tabak shipping-restriction SKUs need catalog cleanup")
    return lines, unr


def davidoff(rows: list) -> tuple[dict, list]:
    lines: dict[str, dict] = {}
    unr: list[str] = []
    for r in rows:
        raw = r.get("line") or ""
        if raw.startswith("Millenium"):
            lines[raw] = {"line": "Millennium"}
            continue
        if raw in ("WSC Late Hour /4", "Winston Churchill The Late Hour"):
            lines[raw] = {"line": "Winston Churchill The Late Hour"}
            continue
        if raw.startswith("Year Of The ") or raw.startswith("Year of "):
            # normalize Year Of The Dragon 2024 → Year of the Dragon 2024
            norm = raw.replace("Year Of The ", "Year of the ").replace("Year of ", "Year of ")
            lines[raw] = {"line": norm}
            continue
        if raw.startswith("Chef") or raw.startswith("Chefs"):
            lines[raw] = {"line": raw.replace("Chefs Edition", "Chef's Edition")}
            continue
        lines[raw] = {"line": raw}
    return lines, unr


def main() -> None:
    snap = json.loads(SNAP.read_text(encoding="utf-8"))
    report = {}

    lines, unr = oscar(snap["Oscar Valladares"])
    report["Oscar Valladares"] = write_brand(
        "Oscar Valladares",
        "oscar-valladares.json",
        lines,
        unr,
        sources=["https://oscarvalladarescigars.com/"],
    )
    lines, unr = rocky(snap["Rocky Patel"])
    report["Rocky Patel"] = write_brand(
        "Rocky Patel", "rocky-patel.json", lines, unr, sources=["https://www.rockypatel.com/"]
    )
    lines, unr = perdomo(snap["Perdomo"])
    report["Perdomo"] = write_brand(
        "Perdomo", "perdomo.json", lines, unr, sources=["https://perdomocigars.com/"]
    )
    lines, unr = gurkha(snap["Gurkha"])
    report["Gurkha"] = write_brand(
        "Gurkha", "gurkha.json", lines, unr, sources=["https://gurkhacigars.com/"]
    )
    lines, unr = villiger(snap["Villiger"])
    report["Villiger"] = write_brand(
        "Villiger", "villiger.json", lines, unr, sources=["https://www.villiger.com/"]
    )
    lines, unr = epc(snap["E.P. Carrillo"])
    report["E.P. Carrillo"] = write_brand(
        "E.P. Carrillo", "e-p-carrillo.json", lines, unr, sources=["https://epcarrillo.com/"]
    )
    lines, unr = drew(snap["Drew Estate"])
    report["Drew Estate"] = write_brand(
        "Drew Estate", "drew-estate.json", lines, unr, sources=["https://drewestate.com/"]
    )
    lines, unr = davidoff(snap["Davidoff"])
    report["Davidoff"] = write_brand(
        "Davidoff", "davidoff.json", lines, unr, sources=["https://www.davidoff.com/"]
    )

    out = Path(__file__).resolve().parent / "output" / "phase3_w1_slice2_report.json"
    write_json(out, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
