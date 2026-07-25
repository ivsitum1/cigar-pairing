# -*- coding: utf-8 -*-
"""One-shot: decode HTML entities in line/vitola, strip dangling & brand tails,
translate 3 hr==en notes, refresh taxonomy baselines.

Run from app/: python scripts/_line_display_cleanup.py
Idempotent.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP = ROOT.parent
DATA = APP / "src" / "data"
TAX_DIR = ROOT / "data" / "taxonomy"
OUT = ROOT / "output"
CIGARS = DATA / "cigars.json"
FINDINGS = OUT / "corpus_audit_findings.md"

DIM_IN_LINE = re.compile(r"\d+\s*[x×]\s*\d+|\d+\s*(?:mm|\")", re.I)

NOTE_HR = {
    "cig-bolivar-regional-special": (
        "Kuba, Habano pokrov — pune snage, punog tijela. Okusi: cedrovina, začini, koža."
    ),
    "cig-padron-1964-anniversary-series": (
        "Nikaragva, Maduro pokrov — pune snage, punog tijela. Okusi: kakao, kava, karamela."
    ),
    "cig-padron-damaso": (
        "Nikaragva, Connecticut pokrov — srednje snage, laganog tijela. "
        "Okusi: kremasto, cedrovina, orašasti tonovi."
    ),
}


def decode_entities(s: str) -> str:
    if not s or "&" not in s:
        return s
    prev = None
    cur = s
    while prev != cur:
        prev = cur
        cur = html.unescape(cur)
    return re.sub(r" {2,}", " ", cur).strip()


def strip_dangling_amp(brand: str, line: str) -> str:
    """Remove leading & and duplicated brand-tail after '&' brands."""
    line = decode_entities(line or "")
    brand = decode_entities(brand or "")
    line = re.sub(r"^\s*&\s*", "", line).strip()
    m = re.search(r"&\s*(.+)$", brand)
    if m:
        tail = m.group(1).strip()
        if tail and line.lower().startswith(tail.lower()):
            rest = line[len(tail) :].strip(" -/–—")
            if rest:
                line = rest
    return line


def fix_integrity_line(line: str, vitola: str | None) -> str:
    """After decode, strip dim patterns that fail integrity.test.ts."""
    if not DIM_IN_LINE.search(line):
        return line
    # Mexico "01" — inch-quote false positive; drop ASCII quotes around digits
    cleaned = re.sub(r'"(\d+)"', r"\1", line)
    cleaned = DIM_IN_LINE.sub(" ", cleaned)
    cleaned = re.sub(r" {2,}", " ", cleaned).strip(" -–—·,/")
    if not cleaned:
        return (vitola or "").strip()
    return cleaned


def fix_amp_spacing(line: str) -> str:
    """Heaven& Hell → Heaven & Hell (missing space before &). Leave S&R alone."""
    return re.sub(r"(\S)&(\s)", r"\1 &\2", line)


def clean_line(brand: str, line: str, vitola: str | None) -> str:
    before = line
    line = decode_entities(line or "")
    if re.match(r"^\s*&", line) or "&amp;" in (before or ""):
        line = strip_dangling_amp(brand, before)
    line = fix_amp_spacing(line)
    line = fix_integrity_line(line, vitola)
    return line


def transform_cigars(cigars: list) -> list[tuple[str, str, str]]:
    """Returns list of (id, before, after) for changed lines."""
    changes: list[tuple[str, str, str]] = []
    for c in cigars:
        brand = c.get("brand") or ""
        old_line = c.get("line") or ""
        vitola = c.get("vitola")
        new_line = clean_line(brand, old_line, vitola)
        if new_line != old_line:
            changes.append((c["id"], old_line, new_line))
            c["line"] = new_line
        if vitola:
            nv = decode_entities(vitola)
            if nv != vitola:
                c["vitola"] = nv
        for v in c.get("vitolas") or []:
            if isinstance(v, dict) and v.get("name"):
                nn = decode_entities(v["name"])
                if nn != v["name"]:
                    v["name"] = nn
        cid = c.get("id")
        if cid in NOTE_HR:
            notes = c.setdefault("notes", {})
            notes["hr"] = NOTE_HR[cid]
    return changes


def remap_taxonomy_lines(lines: dict, brand: str, line_fallback: dict[str, str]) -> dict:
    """line_fallback: old_key → preferred new line (from cigars.json)."""
    out: dict = {}
    for key, meta in lines.items():
        fb = line_fallback.get(key) or line_fallback.get(decode_entities(key))
        new_key = clean_line(brand, key, fb)
        if not new_key and fb:
            new_key = fb
        if isinstance(meta, dict):
            meta = dict(meta)
            if "line" in meta and isinstance(meta["line"], str):
                ml = clean_line(brand, meta["line"], fb)
                meta["line"] = ml or fb or meta["line"]
            if isinstance(meta.get("line"), str) and meta["line"]:
                new_key = meta["line"]
        if not new_key:
            new_key = fb or decode_entities(key)
        out[new_key] = meta
    return out


def update_taxonomy(old_to_new_by_brand: dict[str, dict[str, str]]) -> list[str]:
    touched: list[str] = []
    for path in sorted(TAX_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        brand = data.get("brand") or ""
        lines = data.get("lines")
        if not isinstance(lines, dict) or not lines:
            continue
        blob = json.dumps(lines, ensure_ascii=False)
        needs = (
            "&amp;" in blob
            or "&quot;" in blob
            or "&#" in blob
            or any(re.match(r"^\s*&", k) for k in lines)
            or any(re.search(r"\S&\S", k) for k in lines)
        )
        if not needs:
            continue
        brand_map = old_to_new_by_brand.get(brand) or {}
        fb: dict[str, str] = {}
        # Only touch keys that are entity/dangling artifacts — never rewrite
        # intentional alias keys (#2 → My Father Original, Classic No. 1, …).
        def needs_key(k: str) -> bool:
            return bool(
                "&amp;" in k
                or "&quot;" in k
                or "&#" in k
                or re.match(r"^\s*&", k)
                or re.search(r"\S&\s", k)  # Heaven& Hell
            )

        dirty = {k: v for k, v in lines.items() if needs_key(k)}
        if not dirty:
            continue
        for key in dirty:
            if key in brand_map:
                fb[key] = brand_map[key]
            else:
                dec = decode_entities(key)
                if dec in brand_map:
                    fb[key] = brand_map[dec]
                else:
                    cleaned = clean_line(brand, key, None)
                    fb[key] = cleaned or brand_map.get(dec) or cleaned
        new_lines = dict(lines)
        for key, meta in dirty.items():
            remapped = remap_taxonomy_lines({key: meta}, brand, fb)
            del new_lines[key]
            new_lines.update(remapped)
        if new_lines != lines:
            data["lines"] = new_lines
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            touched.append(path.name)
    return touched


def update_vitola_dedup() -> int:
    path = ROOT / "data" / "vitola_dedup_decisions.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    n = 0

    def fix_obj(o):
        nonlocal n
        if isinstance(o, dict):
            brand = o.get("brand") or ""
            if "line" in o and isinstance(o["line"], str):
                nl = clean_line(brand, o["line"], o.get("vitola"))
                if nl != o["line"]:
                    o["line"] = nl
                    n += 1
            for v in o.values():
                fix_obj(v)
        elif isinstance(o, list):
            for v in o:
                fix_obj(v)

    fix_obj(data)
    if n:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return n


def update_line_map() -> int:
    path = ROOT / "data" / "line_map.json"
    if not path.exists():
        return 0
    data = json.loads(path.read_text(encoding="utf-8"))
    m = data.get("map") or data
    if not isinstance(m, dict):
        return 0
    n = 0
    new_map: dict = {}
    for k, v in m.items():
        nk = decode_entities(k)
        nv = decode_entities(v) if isinstance(v, str) else v
        if nk != k or nv != v:
            n += 1
        new_map[nk] = nv
    if n:
        if "map" in data:
            data["map"] = new_map
        else:
            data = new_map
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return n


def append_findings(changes: list[tuple[str, str, str]], tax_files: list[str]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    lines = [
        "",
        "## Line display cleanup (`fix/cigar-line-display-cleanup`)",
        "",
        "### Auto-fixed",
        "",
        f"- Decoded HTML entities + stripped dangling `&` brand tails: **{len(changes)}** line changes.",
        f"- Taxonomy baselines refreshed: {', '.join(tax_files) if tax_files else '(none)'}.",
        "- Integrity: El Vinyet dim-only line → vitola fallback; Mexico `\"01\"` quotes stripped (inch false positive).",
        "- Same-class: `Heaven& Hell` → `Heaven & Hell` (Oscar Valladares).",
        "- Notes HR translated (market_note style): Bolívar Regional & Special, Padrón 1964, Padrón Damaso.",
        "",
        "### Line before → after",
        "",
    ]
    for cid, before, after in changes:
        lines.append(f"- `{cid}`: `{before}` → `{after}`")
    lines += [
        "",
        "### Review (not invented in this PR)",
        "",
        "- Brand rename candidates (truncated brand left `& Surname` residue): "
        "`Carlos` + line `Maria Amorio` (likely *Carlos & Maria*); "
        "`Hernandez` + line `Ruiz` (likely *Hernandez & Ruiz*). "
        "Leading `&` removed; brand merge deferred.",
        "- Partageno `& Corona …` → `Corona …` (product family; brand stays `Partageno`).",
        "",
    ]
    try:
        existing = FINDINGS.read_text(encoding="utf-8") if FINDINGS.exists() else "# Corpus audit findings\n"
    except UnicodeDecodeError:
        existing = FINDINGS.read_text(encoding="latin-1") if FINDINGS.exists() else "# Corpus audit findings\n"
        # Rewrite clean UTF-8 header + our section only for this branch note
        existing = "# Corpus audit findings\n\n(Previous findings file had a non-UTF-8 byte; section below is authoritative for this PR.)\n"
    FINDINGS.write_text(existing.rstrip() + "\n" + "\n".join(lines), encoding="utf-8")


def main() -> None:
    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    # Capture brand → old_line → new_line before write
    old_to_new_by_brand: dict[str, dict[str, str]] = {}
    changes = transform_cigars(cigars)
    for c in cigars:
        # Re-derive: changes list has id/before/after
        pass
    for cid, before, after in changes:
        brand = next(c["brand"] for c in cigars if c["id"] == cid)
        old_to_new_by_brand.setdefault(brand, {})[before] = after
        old_to_new_by_brand[brand][decode_entities(before)] = after
    CIGARS.write_text(
        json.dumps(cigars, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    tax_files = update_taxonomy(old_to_new_by_brand)
    vd_n = update_vitola_dedup()
    lm_n = update_line_map()
    append_findings(changes, tax_files)
    print(f"line changes: {len(changes)}")
    print(f"taxonomy files: {tax_files}")
    print(f"vitola_dedup: {vd_n}, line_map: {lm_n}")
    for cid, b, a in changes:
        print(f"  {cid}: {b!r} -> {a!r}")


if __name__ == "__main__":
    main()
