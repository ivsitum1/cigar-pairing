#!/usr/bin/env python3
"""Kuriraj vitole gdje ime linije / Neptune URL kaže oblik, a zapis ima krivu vitolu.

CONTINUATION OF Claude Code (session_01KgdmTUcoUbMQDoEHHWgisB) — prekinuto na
kuriranju ~72 zapisa. Ovdje:

1. Posjedovna false-positive u title_case_line (Serie S ≠ Serie's) rješava
   taxonomy_lib — ovaj skripta je za rename vitole iz dokaza.
2. Dokaz = Neptune product URL + <title> (npr. `… Robusto Gordo 5" * 54`).
   Dimenzije iz naslova smiju preuzeti vitolu samo kad obore zatečenu
   (shape_fits_dims). Davidoff Winston* s Churchill mjerom ostaje taksonomiji
   kad URL kaže Winston Churchill + oblik — to je invert linija/vitola.

Usage (iz app/):
  python scripts/curate-line-tail-vitolas.py --worklist   # samo popis
  python scripts/curate-line-tail-vitolas.py --apply      # scrape + taxonomy patch
  python scripts/curate-line-tail-vitolas.py --apply --limit 5
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from taxonomy_lib import (  # noqa: E402
    APP,
    CIGARS_PATH,
    TAXONOMY_DIR,
    load_json,
    parse_format,
    shape_canon_index,
    shape_fits_dims,
    write_json,
)

OUT_WORKLIST = APP / "scripts/output/line_tail_vitola_worklist.json"
OUT_RAW = APP / "scripts/output/line_tail_vitola_raw.json"
OUT_DECISIONS = APP / "scripts/data/line_tail_vitola_decisions.json"

TITLE_DIM_RE = re.compile(
    r"""(?ix)
    ^(?P<head>.+?)\s+
    (?P<len>\d+(?:\s+\d+\s*/\s*\d+|\s*[¼½¾])?)\s*[\"″]?\s*[*x×]\s*
    (?P<ring>\d+)\s*$
    """
)

# Oblik na kraju linije koji je dovoljno pouzdan da se uopće razmatra.
CLEAR = {
    "robusto",
    "toro",
    "corona",
    "churchill",
    "lancero",
    "torpedo",
    "belicoso",
    "gordo",
    "perfecto",
    "salomon",
    "figurado",
    "lonsdale",
    "panetela",
    "petit panetela",
    "pyramid",
    "presidente",
    "double corona",
    "petit corona",
    "robusto gordo",
    "toro gordo",
    "petit robusto",
    "short robusto",
}


def neptune_url(c: dict) -> str | None:
    rl = c.get("regionLinks") or {}
    for key in ("USA", "usa", "EU", "eu"):
        u = (rl.get(key) or {}).get("url")
        if u and "neptunecigar.com" in u:
            return u
    for u in (c.get("priceUrl"), c.get("shopHR")):
        if u and "neptunecigar.com" in str(u):
            return str(u)
    return None


def line_tail_shape(line: str) -> str | None:
    words = (line or "").strip().split()
    if not words:
        return None
    for n in (2, 1):
        if len(words) >= n:
            tail = " ".join(words[-n:]).lower()
            if tail in CLEAR:
                return " ".join(words[-n:])
    return None


def suspects(cigars: list[dict]) -> list[dict]:
    index = shape_canon_index()
    out: list[dict] = []
    for c in cigars:
        vits = c.get("vitolas") or []
        if len(vits) != 1:
            continue
        cand = line_tail_shape(c.get("line") or "")
        if not cand:
            continue
        vn = vits[0].get("name") or ""
        if cand.lower() == vn.lower():
            continue
        if cand.lower() in vn.lower() or vn.lower() in cand.lower():
            continue
        canon = index.get(cand.lower())
        out.append(
            {
                "id": c["id"],
                "brand": c.get("brand"),
                "line": c.get("line"),
                "shape_in_line": cand,
                "shape_canon": canon,
                "vitola": vn,
                "format": vits[0].get("format"),
                "url": neptune_url(c),
            }
        )
    return out


def fetch_title(url: str, timeout: float = 20.0) -> str | None:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "cigar-pairing-curate/1.0 (+local taxonomy)"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        html = resp.read(80_000).decode("utf-8", errors="replace")
    m = re.search(r"<title>([^<]+)</title>", html, re.I)
    return m.group(1).strip() if m else None


def parse_title(title: str) -> dict | None:
    """'Blackbird Superb Robusto Gordo 5\" * 54' → head, format, shape tokens."""
    t = re.sub(r"\s+", " ", (title or "").strip())
    t = re.sub(r"\s*[|\-–].*$", "", t)  # drop site suffix if any
    t = re.sub(r",\s*Pack of \d+\s*$", "", t, flags=re.I)
    # glued fraction: 5"1/2 → 5 1/2"
    t = re.sub(r'(\d)"(\d+\s*/\s*\d+)', r'\1 \2"', t)
    m = TITLE_DIM_RE.match(t)
    if not m:
        return None
    head = m.group("head").strip()
    length = m.group("len").replace(" ", "")
    ring = m.group("ring")
    fmt = f'{length}" x {ring}'
    ring_i, len_mm = parse_format(fmt)
    if ring_i is None:
        try:
            # 5 1/2 style already in group
            len_raw = m.group("len").strip()
            if "/" in len_raw:
                parts = re.match(r"(\d+)\s+(\d+)\s*/\s*(\d+)", len_raw)
                if parts:
                    inches = int(parts.group(1)) + int(parts.group(2)) / int(parts.group(3))
                else:
                    a, b = len_raw.split("/", 1)
                    inches = float(a) / float(b)
            else:
                inches = float(len_raw.replace(",", "."))
            ring_i = int(ring)
            len_mm = int(round(inches * 25.4))
            fmt = f"{ring_i} x {len_mm}mm"
        except ValueError:
            return None
    else:
        fmt = f"{ring_i} x {len_mm}mm"
    return {"head": head, "format": fmt, "ring": ring_i, "length_mm": len_mm}


def decide(row: dict, scraped: dict | None) -> dict | None:
    """Vrati taxonomy-ish odluku ili None (ostavi / dvojbeno)."""
    index = shape_canon_index()
    brand = row["brand"]
    line = row["line"]
    cur = row["vitola"]
    cand = row["shape_canon"] or index.get(row["shape_in_line"].lower())
    cur_ring, cur_len = parse_format(row.get("format"))

    # Davidoff Winston*: URL često kaže winston-churchill-<shape>.
    url = (row.get("url") or "").lower()
    if "davidoff" in (brand or "").lower() and "winston" in (line or "").lower():
        if "winston-churchill" in url:
            # linija = Winston Churchill, vitola = oblik s KRAJA URL slugа / title
            slug = url.rstrip("/").split("/")[-1]
            shape_from_url = None
            for sh in sorted(CLEAR, key=len, reverse=True):
                token = sh.replace(" ", "-")
                if slug.endswith("-" + token) or slug == token:
                    shape_from_url = index.get(sh) or sh.title()
                    break
            if scraped:
                head = scraped.get("head") or ""
                for sh in sorted(CLEAR, key=len, reverse=True):
                    if head.lower().endswith(sh):
                        shape_from_url = index.get(sh) or sh.title()
                        line_fix = head[: -len(sh)].strip()
                        if line_fix.lower().startswith("davidoff "):
                            line_fix = line_fix[9:].strip()
                        # collapse "Winston Churchill Churchill"
                        line_fix = re.sub(
                            r"\b(Winston Churchill)(?:\s+Churchill)+\b",
                            r"\1",
                            line_fix,
                            flags=re.I,
                        )
                        return {
                            "id": row["id"],
                            "action": "fix_line_and_vitola",
                            "line": line_fix or "Winston Churchill",
                            "vitola": shape_from_url,
                            "format": scraped["format"],
                            "reason": "neptune title/url: Winston Churchill + shape",
                        }
            if shape_from_url:
                return {
                    "id": row["id"],
                    "action": "fix_line_and_vitola",
                    "line": "Winston Churchill",
                    "vitola": shape_from_url,
                    "format": None,
                    "reason": "neptune url slug winston-churchill-<shape>",
                }
        return {
            "id": row["id"],
            "action": "skip",
            "reason": "davidoff winston ambiguous without churchill slug",
        }

    if not scraped:
        return {"id": row["id"], "action": "skip", "reason": "no scrape"}

    head = scraped["head"]
    new_fmt = scraped["format"]
    new_ring, new_len = scraped["ring"], scraped["length_mm"]

    # oblik iz naslova (najdulji CLEAR na kraju head)
    title_shape = None
    low = head.lower()
    for sh in sorted(CLEAR, key=len, reverse=True):
        if low == sh or low.endswith(" " + sh):
            title_shape = index.get(sh) or sh.title()
            break
    if not title_shape:
        return {"id": row["id"], "action": "skip", "reason": "no shape in title"}

    fits_new = shape_fits_dims(title_shape, new_ring, new_len)
    fits_old = shape_fits_dims(cur, new_ring, new_len)

    # preuzmi vitolu samo kad nove dimenzije potvrde title oblik i obore staru
    if fits_new is True and fits_old is not True:
        return {
            "id": row["id"],
            "action": "rename_vitola",
            "vitola": title_shape,
            "format": new_fmt,
            "reason": f"title dims fit {title_shape}, not {cur}",
        }
    if fits_new is True and title_shape.lower() != cur.lower():
        # dims fit both or old unknown — still rename if title is clear and
        # old name disagrees (Robusto vs Robusto Gordo)
        return {
            "id": row["id"],
            "action": "rename_vitola",
            "vitola": title_shape,
            "format": new_fmt,
            "reason": f"title names {title_shape}; dims fit",
        }
    if fits_new is False:
        return {
            "id": row["id"],
            "action": "skip",
            "reason": f"title dims do not fit parsed shape {title_shape}",
        }
    # fits_new is None — lexicon miss; still apply name+format from shop title
    if title_shape.lower() != cur.lower():
        return {
            "id": row["id"],
            "action": "rename_vitola",
            "vitola": title_shape,
            "format": new_fmt,
            "reason": "shop title shape+size (lexicon unknown)",
        }
    return {"id": row["id"], "action": "skip", "reason": "already aligned"}


def apply_decisions(cigars: list[dict], decisions: list[dict]) -> int:
    by_id = {c["id"]: c for c in cigars}
    n = 0
    for d in decisions:
        if d.get("action") in (None, "skip"):
            continue
        c = by_id.get(d["id"])
        if not c or not c.get("vitolas"):
            continue
        v = c["vitolas"][0]
        if d["action"] == "rename_vitola":
            v["name"] = d["vitola"]
            if d.get("format"):
                v["format"] = d["format"]
                v.pop("formatEstimated", None)
            n += 1
        elif d["action"] == "fix_line_and_vitola":
            if d.get("line"):
                c["line"] = d["line"]
            v["name"] = d["vitola"]
            if d.get("format"):
                v["format"] = d["format"]
                v.pop("formatEstimated", None)
            n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worklist", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--sleep", type=float, default=1.6)
    args = ap.parse_args()

    cigars = load_json(CIGARS_PATH, [])
    rows = suspects(cigars)
    write_json(OUT_WORKLIST, {"count": len(rows), "items": rows})
    print(f"worklist: {len(rows)} -> {OUT_WORKLIST}")

    if args.worklist and not args.apply:
        return 0

    if not args.apply:
        print("Dodaj --apply za scrape+upis, ili --worklist za samo popis.", file=sys.stderr)
        return 0

    todo = [r for r in rows if r.get("url")]
    if args.limit:
        todo = todo[: args.limit]

    raw: list[dict] = []
    decisions: list[dict] = []
    for i, row in enumerate(todo):
        title = None
        scraped = None
        err = None
        try:
            title = fetch_title(row["url"])
            if title:
                scraped = parse_title(title)
        except Exception as e:  # noqa: BLE001 — log and continue
            err = str(e)
        entry = {**row, "title": title, "scraped": scraped, "error": err}
        raw.append(entry)
        decisions.append(decide(row, scraped) or {"id": row["id"], "action": "skip", "reason": "no decision"})
        print(f"[{i+1}/{len(todo)}] {row['id']}: {(decisions[-1] or {}).get('action')} {(decisions[-1] or {}).get('reason')}")
        time.sleep(args.sleep)

    # rows without URL → skip
    have = {d["id"] for d in decisions}
    for row in rows:
        if row["id"] not in have:
            decisions.append({"id": row["id"], "action": "skip", "reason": "no neptune url"})

    write_json(OUT_RAW, raw)
    write_json(OUT_DECISIONS, decisions)
    changed = apply_decisions(cigars, decisions)
    write_json(CIGARS_PATH, cigars)
    applied = sum(1 for d in decisions if d.get("action") not in (None, "skip"))
    print(f"applied {changed} catalog edits ({applied} decisions); raw -> {OUT_RAW}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
