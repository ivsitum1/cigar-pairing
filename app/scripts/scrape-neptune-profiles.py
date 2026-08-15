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

# Strength parsing from description text.
#
# REDOSLIJED JE DIO ZNACENJA: prvi pogodak pobjeduje, pa raspon ("medium to
# full") mora stajati PRIJE svoje krajnje tocke ("full"). Dok je "full-strength"
# stajao prvi, opis "a medium-full strength puro" padao je na 5 umjesto na 4 —
# `.` u uzorku hvata i razmak i crticu, a \b stoji i iza crtice. To je 209
# cigara u katalogu ocijenilo punu tocku prejakima (i tijelo uz njih, jer
# merge-neptune-profiles.py tijelo prepisuje snagom).
STRENGTH_PATTERNS = [
    # rasponi prvo — inace ih progutaju jednoclani uzorci ispod
    (r"\bmedium.full\b|\bmedium.to.full\b|\bfull.to.medium\b", 4),
    (r"\bmild.to.medium\b|\bmedium.to.mild\b|\bmild.medium\b", 2),
    (r"\bfull.bodied\b", 5),
    (r"\bfull.strength\b", 5),
    (r"\bvery full\b", 5),
    (r"\bmedium.bodied\b|\bmedium.strength\b", 3),
    (r"\bmedium\b", 3),
    (r"\bmild.bodied\b|\bmild.strength\b", 2),
    (r"\bvery mild\b|\blight\b", 1),
]

# Dvoblendni proizvodi (dual-ended cigare, kutije s dva blenda) opisu OBA kraja
# u istom tekstu: "mild to medium ... full-bodied". Tu nijedan uzorak nije
# istina o cijeloj kutiji, pa uzimamo sredinu umjesto da odlucuje redoslijed.
MILD_RANGE = re.compile(r"\bmild.to.medium\b|\bmedium.to.mild\b|\bmild.medium\b")
FULL_MARK = re.compile(r"\bfull.bodied\b|\bfull.strength\b|\bvery full\b")


def _parse_strength_from_text(text: str) -> int | None:
    low = (text or "").lower()
    if MILD_RANGE.search(low) and FULL_MARK.search(low):
        return 3
    for pat, val in STRENGTH_PATTERNS:
        if re.search(pat, low):
            return val
    return None


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
            s = _parse_strength_from_text(desc)
            if s:
                result["strength"] = s
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
