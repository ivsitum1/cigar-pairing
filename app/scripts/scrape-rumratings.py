# -*- coding: utf-8 -*-
"""Scrape community ratings from rumratings.com.

Output: app/scripts/output/rumratings_raw.json
Cache:  app/scripts/output/rumratings_cache/*.html (git-ignored, re-parsable)

  python scripts/scrape-rumratings.py                    # crawl listings, follow pagination
  python scripts/scrape-rumratings.py --max-pages 5      # short probe first
  python scripts/scrape-rumratings.py --targets rums     # only bottles already in rums.json
  python scripts/scrape-rumratings.py --parse-only       # rebuild JSON from cache, no network

The crawl is discovery-driven: it starts from `--start`, collects every
/brands/<id>-<slug> link it sees and follows rel=next / ?page=N. robots.txt
is obeyed; a disallowed URL is skipped, not fetched.

Pages the parser cannot read are written to output/rumratings_misses.json
with their cache path, so a selector fix costs a re-parse and no requests.
"""
from __future__ import annotations

import argparse
import json
import urllib.parse
from pathlib import Path

from rumratings_shared import (
    BASE,
    CACHE_DIR,
    OUT_DIR,
    Fetcher,
    best_match,
    detail_links,
    next_page_url,
    parse_detail,
)

RAW = OUT_DIR / "rumratings_raw.json"
MISSES = OUT_DIR / "rumratings_misses.json"
RUMS = Path(__file__).resolve().parent.parent / "src" / "data" / "rums.json"

DEFAULT_START = f"{BASE}/?sort=rating"


def crawl_listings(fetcher: Fetcher, start: str, max_pages: int) -> list[str]:
    """Detail URLs, in listing order, following pagination."""
    urls: dict[str, None] = {}
    page_url: str | None = start
    seen_pages: set[str] = set()
    for page_no in range(1, max_pages + 1):
        if not page_url or page_url in seen_pages:
            break
        seen_pages.add(page_url)
        html = fetcher.get(page_url)
        if html is None:
            break
        found = detail_links(html)
        for url in found:
            urls.setdefault(url, None)
        print(f"  listing {page_no}: {len(found)} links ({len(urls)} total) — {page_url}")
        if not found:
            break
        page_url = next_page_url(html, page_url)
    return list(urls)


def target_urls_from_catalog(fetcher: Fetcher, max_pages: int) -> list[str]:
    """Detail URLs whose name matches something already in rums.json."""
    catalog = json.loads(RUMS.read_text("utf-8"))
    urls = crawl_listings(fetcher, DEFAULT_START, max_pages)
    keep: list[str] = []
    for url in urls:
        slug = urllib.parse.urlparse(url).path.rsplit("-", 0)[0]
        name = slug.split("/")[-1].split("-", 1)[-1].replace("-", " ")
        hit, _ = best_match(name, catalog, floor=0.6)
        if hit:
            keep.append(url)
    return keep


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default=DEFAULT_START, help="listing URL to crawl from")
    ap.add_argument("--max-pages", type=int, default=40, help="listing pages to follow")
    ap.add_argument("--limit", type=int, default=0, help="stop after N detail pages (0 = all)")
    ap.add_argument("--delay", type=float, default=1.5, help="seconds between requests")
    ap.add_argument("--targets", choices=["all", "rums"], default="all",
                    help="'rums' fetches only bottles that look like ours")
    ap.add_argument("--parse-only", action="store_true", help="use cached HTML only, no network")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fetcher = Fetcher(delay=args.delay, offline=args.parse_only)

    if args.parse_only:
        detail_pages = sorted(CACHE_DIR.glob("brands-*.html"))
        print(f"parse-only: {len(detail_pages)} cached detail pages")
        pages = [(p.read_text("utf-8", "replace"), _url_from_cache(p)) for p in detail_pages]
    else:
        print(f"crawling listings from {args.start}")
        urls = (
            target_urls_from_catalog(fetcher, args.max_pages)
            if args.targets == "rums"
            else crawl_listings(fetcher, args.start, args.max_pages)
        )
        if args.limit:
            urls = urls[: args.limit]
        print(f"{len(urls)} detail pages to fetch")
        pages = []
        for i, url in enumerate(urls, 1):
            html = fetcher.get(url)
            if html is None:
                continue
            pages.append((html, url))
            if i % 25 == 0:
                print(f"  {i}/{len(urls)} fetched")

    records: list[dict] = []
    misses: list[dict] = []
    for html, url in pages:
        rec = parse_detail(html, url)
        if rec:
            records.append(rec)
        else:
            misses.append({"url": url, "cache": str(fetcher.cache_path(url))})

    records.sort(key=lambda r: (-(r["rating"] or 0), -(r["votes"] or 0)))
    RAW.write_text(json.dumps(records, ensure_ascii=False, indent=1) + "\n", "utf-8")
    MISSES.write_text(json.dumps(misses, ensure_ascii=False, indent=1) + "\n", "utf-8")

    with_reviews = sum(1 for r in records if r["reviews"])
    print(f"\nwrote {len(records)} rums → {RAW.relative_to(RAW.parent.parent.parent)}")
    print(f"  {with_reviews} with review text, {len(misses)} pages unparsed → {MISSES.name}")
    print(f"  fetch stats: {fetcher.stats}")
    if misses:
        print("  inspect a miss, fix the selector in rumratings_shared.py, re-run --parse-only")


def _url_from_cache(path: Path) -> str:
    """Cache names are <path-slug>.<hash>.html — recover the source path."""
    slug = path.name.rsplit(".", 2)[0]
    return f"{BASE}/{slug.replace('brands-', 'brands/', 1)}"


if __name__ == "__main__":
    main()
