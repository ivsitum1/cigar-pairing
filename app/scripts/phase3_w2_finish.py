#!/usr/bin/env python3
"""Phase 3 W2 finish: remaps for every remaining W2 brand (status != done).

Generic heuristics + light brand-specific rules. Writes taxonomy JSON only;
parent runs apply-taxonomy.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from taxonomy_lib import (
    TAXONOMY_DIR,
    brand_slug,
    is_sampler_line,
    line_ends_with_shape,
    load_json,
    shape_words,
    split_trailing_dimensions,
    write_json,
)
from phase3_w2_status import W1

APP = Path(__file__).resolve().parent.parent
CIGARS_PATH = APP / "src/data/cigars.json"
OUT = Path(__file__).resolve().parent / "output"
SHAPES = shape_words()

# Known truncated / Phase-2 leftovers — flag, still remap lines inside current brand.
TRUNCATED = {"Adv", "Casa", "Dbl", "Csc", "Don Pepin"}  # Don Pepin vs Don Pépin García


def strip_pack(raw: str) -> str:
    return re.sub(r"/\d+\s*$", "", raw).strip()


def dedupe_words(s: str) -> str:
    return re.sub(r"\b(\w+)(?:\s+\1)+\b", r"\1", s, flags=re.I)


def strip_brand_prefix(raw: str, brand: str) -> str:
    for prefix in (brand, brand.replace(".", ""), brand.split()[0] if brand else ""):
        if not prefix or len(prefix) < 3:
            continue
        if raw.lower().startswith(prefix.lower() + " "):
            return raw[len(prefix) :].strip()
        # Torano / Toraño style
        if raw.lower().startswith(prefix.lower().replace("ñ", "n") + " "):
            return raw[len(prefix) :].strip()
    return raw


def generic_remap(brand: str, raw: str, vitola_name: str | None) -> dict:
    cleaned = dedupe_words(strip_pack(raw)).strip()
    cleaned = strip_brand_prefix(cleaned, brand)

    if is_sampler_line(cleaned, vitola_name or ""):
        return {"line": cleaned or raw, "sampler": True}

    dim = split_trailing_dimensions(cleaned)
    if dim:
        base, _fmt = dim
        entry: dict = {"line": base}
        # keep size as vitola hint only when name looks like a size token
        sh = line_ends_with_shape(cleaned, SHAPES)
        if sh and cleaned.lower().endswith(sh):
            vit = cleaned[len(base) :].strip() or cleaned[-len(sh) :]
            # Prefer trailing shape as vitola when dim strip left a shape-ish remainder
        return entry

    sh = line_ends_with_shape(cleaned, SHAPES)
    if sh and " " in cleaned and cleaned.lower().endswith(sh):
        # Don't split if the whole line IS the shape (core size SKU)
        if cleaned.lower() != sh:
            base = cleaned[: -len(sh)].strip(" -·|/")
            if base and len(base) >= 2:
                entry = {"line": base, "vitola": cleaned[len(base) :].strip() or sh.title()}
                # Title-case shape if it was lowercase match
                vit = cleaned[len(base) :].strip()
                entry["vitola"] = vit if vit else sh
                return entry

    # Year Of The X → Year of the X
    if re.match(r"^Year Of The ", cleaned, re.I) or re.match(r"^Year of ", cleaned):
        norm = re.sub(r"^Year Of The ", "Year of the ", cleaned, flags=re.I)
        norm = re.sub(r"^Year of (?!the )", "Year of the ", norm, flags=re.I)
        return {"line": norm}

    # Limited Edition Foo → keep as named LE unless trailing shape already handled
    return {"line": cleaned or raw}


def brand_specific(brand: str, raw: str, generic: dict) -> dict:
    """Light overrides for noisy W2 brands."""
    g = dict(generic)

    if brand == "Macanudo":
        if raw.startswith("Cafe ") or raw == "Cafe":
            return {"line": "Cafe"}
        if "Inspirado" in raw:
            return {"line": raw.replace("  ", " ")}

    if brand in ("Hoyo de Monterrey", "Trinidad", "H. Upmann", "Punch", "José L. Piedra", "Quai d'Orsay", "San Cristobal"):
        # Habanos: fold obvious single-vitola Classic SKUs when line == vitola name
        if g.get("line") == raw and len(raw.split()) <= 3:
            # keep as-is; Classic fold only when clearly numbered / classic
            if re.match(r"^No\.?\s*\d+", raw) or raw in ("Epicure No.2", "Epicure Special", "Coronas", "Churchills"):
                return {"line": "Clásica", "vitola": raw}

    if brand == "Crowned Heads":
        if raw.startswith("Four Kicks "):
            return {"line": "Four Kicks", "vitola": raw[len("Four Kicks ") :]}
        if raw.startswith("Mil Dias ") or raw.startswith("Mil Días "):
            return {"line": "Mil Días", "vitola": re.sub(r"^Mil D[ií]as\s+", "", raw)}

    if brand == "Foundation":
        if "Tabernacle" in raw:
            return {"line": "Tabernacle"} if raw == "Tabernacle" else {"line": "Tabernacle", "vitola": raw.replace("Tabernacle ", "")}
        if raw.startswith("Charter Oak "):
            return {"line": "Charter Oak", "vitola": raw[len("Charter Oak ") :]}

    if brand == "Nub":
        # Nub sizes are the product — keep as line names
        return {"line": raw}

    if brand == "Don Pépin García" or brand == "Don Pepin Garcia":
        if raw.startswith("Blue "):
            return {"line": "Blue", "vitola": raw[5:]} if len(raw) > 5 else {"line": "Blue"}

    if brand == "La Aroma del Caribe":
        # sibling of La Aroma de Cuba — strip redundant brand echo
        if raw.startswith("La Aroma del Caribe "):
            return {"line": raw[len("La Aroma del Caribe ") :]}
        if raw.startswith("La Aroma Del Caribe "):
            return {"line": raw[len("La Aroma Del Caribe ") :]}

    if brand == "Matilde":
        # already has some seed remaps; preserve structure
        return g

    if brand in TRUNCATED or brand in ("Dbl", "Csc"):
        # still apply generic inside truncated brand
        return g

    return g


def write_brand(brand: str, rows: list) -> dict:
    fname = f"{brand_slug(brand)}.json"
    path = TAXONOMY_DIR / fname
    existing = load_json(path, {}) or {}
    lines: dict[str, dict] = {}
    unr: list[str] = list(existing.get("unresolved") or [])

    for r in rows:
        raw = r.get("line") or ""
        vname = (r.get("vitolas") or [{}])[0].get("name")
        g = generic_remap(brand, raw, vname)
        lines[raw] = brand_specific(brand, raw, g)

    if brand in TRUNCATED or brand in ("Dbl", "Csc", "Don Pepin"):
        msg = f"{brand}: brand name looks truncated/ambiguous — renameBrand later"
        if msg not in unr:
            unr.append(msg)

    if brand in ("Hoyo de Monterrey", "Trinidad", "H. Upmann", "Punch", "José L. Piedra", "Quai d'Orsay"):
        msg = f"{brand}: Habanos Clásica fold is partial — verify against catalog"
        if msg not in unr:
            unr.append(msg)

    doc = {
        "brand": brand,
        "renameBrand": existing.get("renameBrand"),
        "status": "done",
        "reviewedAt": "2026-07-24",
        "sources": list(
            dict.fromkeys(
                (existing.get("sources") or [])
                + [
                    "phase3_w2_finish deterministic remaps",
                    "docs/superpowers/plans/2026-07-23-cigar-taxonomy-brand-line-vitola.md §7.3",
                ]
            )
        ),
        "lines": lines,
        "vitolaRenames": existing.get("vitolaRenames") or {},
        "shapes": existing.get("shapes") or {},
        "keepSeparate": existing.get("keepSeparate") or [],
        "lineNotes": existing.get("lineNotes") or {},
        "unresolved": unr,
    }
    write_json(path, doc)
    return {"file": fname, "remaps": len(lines), "unresolved": len(unr)}


def main() -> None:
    cigars = json.loads(CIGARS_PATH.read_text(encoding="utf-8"))
    by_brand: dict[str, list] = defaultdict(list)
    for c in cigars:
        by_brand[c["brand"]].append(c)

    counts = Counter(c["brand"] for c in cigars)
    remaining = []
    for brand, n in counts.most_common():
        if brand in W1:
            continue
        if not (5 <= n <= 19):
            continue
        path = TAXONOMY_DIR / f"{brand_slug(brand)}.json"
        status = "MISSING"
        if path.exists():
            status = (load_json(path, {}) or {}).get("status") or "unknown"
        if status == "done":
            continue
        remaining.append(brand)

    # Snapshot
    snap = {b: [{"id": r.get("id"), "line": r.get("line"), "vitolas": r.get("vitolas")} for r in by_brand[b]] for b in remaining}
    write_json(OUT / "phase3_w2_finish_snapshot.json", snap)

    report = {}
    for brand in remaining:
        report[brand] = write_brand(brand, by_brand[brand])

    write_json(OUT / "phase3_w2_finish_report.json", report)
    print(json.dumps({"brands": len(report), "records": sum(counts[b] for b in remaining), "report": report}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
