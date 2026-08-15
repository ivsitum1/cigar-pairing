#!/usr/bin/env python3
"""Scrape description and leaf fields from Neptune Cigar product pages via Playwright.

Input:  scripts/output/neptune_worklist.json  (built by build-neptune-worklist.py)
Output: scripts/output/neptune_raw.json

Per product page the script extracts:
  - description: og:description meta tag (clean product text written by Neptune)
  - strength:    numeric 1-5 derived from description text
  - wrapper:     "Cigar Wrapper" spec row
  - binder:      "Cigar Binder" spec row
  - filler:      "Cigar Filler" spec row
  - origin:      "Origin" spec row (country)

Items already present in the output are skipped unless --force is given.

Usage (run from app/):
  python scripts/scrape-neptune-profiles.py
  python scripts/scrape-neptune-profiles.py --limit 50
  python scripts/scrape-neptune-profiles.py --force    # re-scrape everything
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from taxonomy_lib import OUT_DIR, load_json, write_json  # noqa: E402

WORKLIST = OUT_DIR / "neptune_worklist.json"
OUT = OUT_DIR / "neptune_raw.json"

PAUSE = 1.8  # seconds between requests

# Snaga i tijelo iz opisa — DVIJE OSI, ne jedan broj.
#
# Neptuneov tekst ih uredno razlikuje: "-bodied" govori o tijelu (koliko je dim
# gust i tezak), "strength / strong / potent" o snazi (koliko nikotina nosi).
# Cigara zna biti full-bodied a medium-strength (Asylum Schizo, Avo Signature
# 30 Years) — to je poznat par, ne greska u tekstu. Od 1366 opisa njih 641
# govori SAMO o tijelu, 282 SAMO o snazi, 42 o oboje. Dok se citao jedan broj,
# oba su polja dobivala istu vrijednost, pa je velik dio kataloga imao tijelo =
# snaga bez ijednog izvora koji to tvrdi.
#
# REDOSLIJED JE DIO ZNACENJA: prvi pogodak pobjeduje, pa raspon ("medium to
# full") mora stajati PRIJE svoje krajnje tocke ("full"). Dok je "full-strength"
# stajao prvi, opis "a medium-full strength puro" padao je na 5 umjesto na 4 —
# `.` u uzorku hvata i razmak i crticu, a \b stoji i iza crtice.

# Os tijela: trazi se izricito "-bodied".
BODY_PATTERNS = [
    (r"\bmedium.to.full.bodied\b|\bmedium.full.bodied\b|\bfull.to.medium.bodied\b", 4),
    (r"\bmild.to.medium.bodied\b|\bmedium.to.mild.bodied\b", 2),
    (r"\bvery full.bodied\b", 5),
    (r"\bfull.bodied\b", 5),
    (r"\bmedium.bodied\b", 3),
    (r"\bmild.bodied\b|\blight.bodied\b", 2),
]

# Os snage: trazi se izricito snaga (strength / strong / potent / powerhouse).
STRENGTH_PATTERNS = [
    (r"\bmedium.to.full.(?:strength|strong)\b|\bmedium.full.(?:strength|strong)\b", 4),
    (r"\bmild.to.medium.(?:strength|strong)\b|\bmedium.to.mild.(?:strength|strong)\b", 2),
    # samo rijeci koje nose ljestvicu. "potent", "bold", "powerhouse" su
    # reklamni pridjevi bez mjere — Neptune ih lijepi i na kremaste Connecticute
    # ("a potent yet flavorful smoke" uz light brown wrapper i note vrhnja), pa
    # bi od njih blage cigare ispale najjace u katalogu.
    (r"\bfull.(?:strength|strong)\b|\bvery strong\b", 5),
    (r"\bmedium.(?:strength|strong)\b", 3),
    (r"\bmild.(?:strength|strong)\b", 2),
]

# Bez osi: "a medium to full cigar". Cita se kao ukupan dojam i sluzi samo kad
# nijedna os nije izrecena — merge onda iz njega izvede obje po karakteru
# pokrova, umjesto da ih izjednaci.
OVERALL_PATTERNS = [
    (r"\bmedium.to.full\b|\bmedium.full\b|\bfull.to.medium\b", 4),
    (r"\bmild.to.medium\b|\bmedium.to.mild\b|\bmild.medium\b", 2),
    (r"\bvery full\b", 5),
    (r"\bvery mild\b", 1),
    (r"\bmedium\b", 3),
    (r"\bmild\b", 2),
]

# Dvoblendni proizvodi (dual-ended cigare, kutije s dva blenda) opisu OBA kraja
# u istom tekstu: "mild to medium ... full-bodied". Tu nijedan uzorak nije
# istina o cijeloj kutiji, pa uzimamo sredinu umjesto da odlucuje redoslijed.
MILD_RANGE = re.compile(r"\bmild.to.medium\b|\bmedium.to.mild\b|\bmild.medium\b")
FULL_MARK = re.compile(r"\bfull.bodied\b|\bfull.strength\b|\bvery full\b")


def _first_match(text: str, patterns: list[tuple[str, int]]) -> int | None:
    for pat, val in patterns:
        if re.search(pat, text):
            return val
    return None


def parse_profile_from_text(text: str) -> dict:
    """Opis -> {"strength": int|None, "body": int|None, "overall": int|None}.

    Sve tri smiju biti None: opis koji o jacini ne govori nista ne smije nista
    ni tvrditi. `overall` se puni samo kad nijedna os nije izrecena.
    """
    low = (text or "").lower()
    if not low:
        return {"strength": None, "body": None, "overall": None}
    if MILD_RANGE.search(low) and FULL_MARK.search(low):
        # dva blenda u istoj kutiji — sredina, za obje osi
        return {"strength": 3, "body": 3, "overall": None}
    body = _first_match(low, BODY_PATTERNS)
    strength = _first_match(low, STRENGTH_PATTERNS)
    overall = None
    if body is None and strength is None:
        overall = _first_match(low, OVERALL_PATTERNS)
    return {"strength": strength, "body": body, "overall": overall}


def parse_page(html: str) -> dict:
    result: dict = {}

    # ── og:description ───────────────────────────────────────────────────────
    m = re.search(r'property="og:description"\s+content="([^"]+)"', html, re.I)
    if not m:
        m = re.search(r'content="([^"]+)"\s+property="og:description"', html, re.I)
    if m:
        desc = m.group(1).strip()
        # Fix smart apostrophes / encoding artefacts
        desc = desc.replace("\u2019", "'").replace("\u2018", "'").replace("\ufffd", "'")
        desc = re.sub(r"\s+", " ", desc)
        if len(desc) > 40:
            result["description"] = desc
            prof = parse_profile_from_text(desc)
            for key in ("strength", "body", "overall"):
                if prof[key]:
                    result[key] = prof[key]
            if any(prof.values()):
                result["strength_source"] = "description_text"

    # ── Spec table rows ──────────────────────────────────────────────────────
    # Pattern: <li class="pr_pItem"><div>LABEL</div>...<div class="onHover">VALUE
    spec_items = re.findall(
        r'pr_pItem[^>]*><div>([^<]+)</div><div><div[^>]*class="onHover">([^<]+)',
        html,
    )
    spec = {label.strip(): value.strip() for label, value in spec_items}

    if spec.get("Cigar Wrapper"):
        result["wrapper"] = spec["Cigar Wrapper"]
    if spec.get("Cigar Binder"):
        result["binder"] = spec["Cigar Binder"]
    if spec.get("Cigar Filler"):
        result["filler"] = spec["Cigar Filler"]
    if spec.get("Origin"):
        result["origin"] = spec["Origin"]

    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--limit", type=int, default=0, help="Max URLs to scrape (0 = all)")
    ap.add_argument("--force", action="store_true", help="Re-scrape already-present ids")
    args = ap.parse_args()

    worklist = load_json(WORKLIST, None)
    if worklist is None:
        print(f"Worklist not found: {WORKLIST}. Run build-neptune-worklist.py first.", file=sys.stderr)
        sys.exit(1)

    existing: dict[str, dict] = {}
    if OUT.exists():
        raw_list = load_json(OUT, []) or []
        existing = {item["id"]: item for item in raw_list if isinstance(item, dict)}

    todo = worklist if args.force else [w for w in worklist if w["id"] not in existing]
    if args.limit:
        todo = todo[: args.limit]

    print(f"Worklist: {len(worklist)} items, to scrape: {len(todo)}")
    if not todo:
        print("Nothing to scrape.")
        out_list = sorted(existing.values(), key=lambda x: x.get("id", ""))
        write_json(OUT, out_list)
        return 0

    # Import Playwright here so the script fails gracefully if not installed
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed. Run: pip install playwright && playwright install chromium", file=sys.stderr)
        sys.exit(1)

    scraped = 0
    errors = 0

    SAVE_EVERY = 25  # persist to disk after every N new scrapes

    def _flush():
        out = sorted(existing.values(), key=lambda x: x.get("id", ""))
        write_json(OUT, out)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"}
        )
        for i, item in enumerate(todo):
            cid = item["id"]
            url = item["url"]
            if i > 0:
                time.sleep(PAUSE)
            try:
                page.goto(url, timeout=30000, wait_until="domcontentloaded")
                # Wait for spec table to appear
                try:
                    page.wait_for_selector(".pr_pItem", timeout=8000)
                except Exception:
                    pass
                html = page.content()
                parsed = parse_page(html)
                parsed["id"] = cid
                parsed["url"] = url
                existing[cid] = parsed
                scraped += 1
                fields = [k for k in ("strength", "wrapper", "description") if k in parsed]
                print(f"  [{i+1}/{len(todo)}] {cid}: {fields if fields else '(no data)'}")
            except Exception as exc:  # noqa: BLE001
                print(f"  [{i+1}/{len(todo)}] ERROR {cid}: {exc}", file=sys.stderr)
                errors += 1
                existing[cid] = {"id": cid, "url": url, "error": str(exc)}

            # Incremental save so progress survives interruption
            if (scraped + errors) % SAVE_EVERY == 0:
                _flush()

        browser.close()

    out_list = sorted(existing.values(), key=lambda x: x.get("id", ""))
    write_json(OUT, out_list)
    print(f"\nDone: {scraped} scraped, {errors} errors -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
