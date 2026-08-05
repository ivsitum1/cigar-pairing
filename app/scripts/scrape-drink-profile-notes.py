#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scrape tasting notes for W2 worklist bottles from priceUrl / producer pages.

Rate-limited; never invents notes; skips if network fails or page gives nothing.
Saves raw HTML extracts to scripts/output/drink_notes_raw.json.

Usage:
  python scripts/scrape-drink-profile-notes.py
  python scripts/scrape-drink-profile-notes.py --limit 20
  python scripts/scrape-drink-profile-notes.py --resume   # skip already-scraped ids
"""
from __future__ import annotations

import argparse
import html
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# Fix Windows console encoding for non-ASCII output
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
WORKLIST = OUT / "drink_profile_worklist.json"
RAW_OUT = OUT / "drink_notes_raw.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "hr-HR,hr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

PAUSE_S = 1.8  # polite rate limit


def fetch_html(url: str, timeout: int = 15) -> str | None:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
            charset = "utf-8"
            ct = r.headers.get_content_charset()
            if ct:
                charset = ct
            return data.decode(charset, errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, TimeoutError) as e:
        print(f"  SKIP ({type(e).__name__}): {url}")
        return None


def extract_text_from_html(html_str: str) -> str:
    """Strip tags, collapse whitespace, decode entities."""
    clean = re.sub(r"<[^>]+>", " ", html_str)
    clean = html.unescape(clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def extract_allez_description(page: str) -> str | None:
    """Extract product description from allez.hr Shopify page."""
    # Multiple selector patterns for Shopify themes
    patterns = [
        # Shopify product description meta
        r'<div[^>]*class="[^"]*product[^"]*description[^"]*"[^>]*>(.*?)</div>',
        r'<div[^>]*class="[^"]*rte[^"]*"[^>]*>(.*?)</div>',
        # Section with product details
        r'<div[^>]*class="[^"]*product-description[^"]*"[^>]*>(.*?)</div>',
        # Any paragraph after product title
        r'<meta[^>]+name="description"[^>]+content="([^"]+)"',
        r'<meta[^>]+property="og:description"[^>]+content="([^"]+)"',
    ]
    for pat in patterns:
        m = re.search(pat, page, re.DOTALL | re.IGNORECASE)
        if m:
            text = extract_text_from_html(m.group(1))
            if len(text) > 20:
                return text[:800]

    # Fallback: meta description
    m = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]{20,500})"', page, re.I)
    if m:
        return html.unescape(m.group(1))

    return None


def extract_taste_section(text: str) -> str | None:
    """Find taste/flavor sentence in extracted text."""
    # Look for tasting note keywords
    taste_kw = re.compile(
        r"(taste|aroma|nose|palate|tasting note|flavor|flavour|degustacij|okus"
        r"|voce|aroma|berry|vanilla|caramel|spice|oak|citrus"
        r"|juniper|botanical|floral|pepper|herbal|smoke|peaty)",
        re.I,
    )
    sentences = re.split(r"(?<=[.!?])\s+", text)
    good = [s for s in sentences if taste_kw.search(s) and len(s) > 15]
    if good:
        return " ".join(good[:5])[:600]
    # If no specific sentence, return first ~400 chars of text
    if len(text) > 20:
        return text[:500]
    return None


def scrape_worklist(
    worklist_path: Path,
    out_path: Path,
    limit: int | None = None,
    resume: bool = False,
) -> dict:
    data = json.loads(worklist_path.read_text(encoding="utf-8"))
    entries = data["worklist"]

    # Load existing results if resuming
    existing: dict[str, dict] = {}
    if resume and out_path.exists():
        existing = json.loads(out_path.read_text(encoding="utf-8"))

    results: dict[str, dict] = dict(existing)
    processed = 0

    for entry in entries:
        bid = entry["id"]
        if bid in results and resume:
            continue

        url = entry.get("priceUrl")
        if not url:
            results[bid] = {"id": bid, "url": None, "status": "no_url", "text": None}
            continue

        if limit is not None and processed >= limit:
            break

        print(f"  [{entry['category']}] {bid[:50]}...")
        page = fetch_html(url)
        time.sleep(PAUSE_S)

        if page is None:
            results[bid] = {"id": bid, "url": url, "status": "fetch_fail", "text": None}
        else:
            desc = extract_allez_description(page)
            if desc:
                taste = extract_taste_section(desc)
            else:
                taste = None

            results[bid] = {
                "id": bid,
                "url": url,
                "status": "ok" if taste else "no_content",
                "text": taste,
                "raw_desc": desc,
            }
            if taste:
                print(f"    -> {taste[:80]}")
            else:
                print(f"    -> (no taste text found)")

        processed += 1

        # Save progressively every 20 entries
        if processed % 20 == 0:
            out_path.parent.mkdir(exist_ok=True)
            out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"  [checkpoint] {processed} processed, {len(results)} total saved")

    # Save
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved {len(results)} entries -> {out_path}")

    ok = sum(1 for v in results.values() if v.get("status") == "ok")
    fail = sum(1 for v in results.values() if v.get("status") == "fetch_fail")
    no_url = sum(1 for v in results.values() if v.get("status") == "no_url")
    print(f"  ok={ok}  fail={fail}  no_url={no_url}  no_content={len(results)-ok-fail-no_url}")
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="Max bottles to scrape")
    ap.add_argument("--resume", action="store_true", help="Skip already-scraped ids")
    args = ap.parse_args()

    if not WORKLIST.exists():
        print(f"ERROR: {WORKLIST} not found. Run build-drink-profile-worklist.py first.")
        return 1

    print(f"Scraping drink profile notes (limit={args.limit}, resume={args.resume})")
    scrape_worklist(WORKLIST, RAW_OUT, limit=args.limit, resume=args.resume)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
