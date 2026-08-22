# -*- coding: utf-8 -*-
"""Scrape community ratings from rumratings.com.

Output: app/scripts/output/rumratings_raw.json
Cache:  app/scripts/output/rumratings_cache/*.html (git-ignored, re-parsable)

  python scripts/scrape-rumratings.py --targets rums --limit 8   # probe
  python scripts/scrape-rumratings.py --targets rums             # our catalogue
  python scripts/scrape-rumratings.py --parse-only               # rebuild JSON from cache

Discovery defaults to the sitemap published in robots.txt (S3). The HTML
listing at /?sort=rating is a JS shell with a handful of featured bottles,
so it is a fallback, not the main crawl. robots.txt crawl-delay (30s as of
2026-08-21) is the floor between requests; --delay cannot go below it.

Pages the parser cannot read are written to output/rumratings_misses.json
with their cache path. A miss is reported, never stored as a zero.
"""
from __future__ import annotations

import argparse
import gzip
import json
import urllib.request
from pathlib import Path

from rumratings_shared import (
    BASE,
    CACHE_DIR,
    OUT_DIR,
    SITEMAP_URL,
    USER_AGENT,
    Fetcher,
    cache_url_from_path,
    catalog_target_urls,
    detail_links,
    next_page_url,
    parse_detail,
    sitemap_rum_urls,
)

RAW = OUT_DIR / "rumratings_raw.json"
MISSES = OUT_DIR / "rumratings_misses.json"
SITEMAP_CACHE = CACHE_DIR / "sitemap.xml"
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


def load_sitemap(offline: bool) -> list[str]:
    """Bottle URLs from the gzip sitemap. Cached as XML; S3 is not rumratings.com."""
    if SITEMAP_CACHE.exists():
        xml = SITEMAP_CACHE.read_text("utf-8", "replace")
        urls = sitemap_rum_urls(xml)
        print(f"sitemap cache: {len(urls)} bottle URLs")
        return urls
    if offline:
        print("parse-only: no sitemap cache")
        return []
    print(f"fetching sitemap {SITEMAP_URL}")
    req = urllib.request.Request(SITEMAP_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()
    try:
        xml = gzip.decompress(raw).decode("utf-8", "replace")
    except OSError:
        xml = raw.decode("utf-8", "replace")
    SITEMAP_CACHE.parent.mkdir(parents=True, exist_ok=True)
    SITEMAP_CACHE.write_text(xml, "utf-8")
    urls = sitemap_rum_urls(xml)
    print(f"sitemap: {len(urls)} bottle URLs")
    return urls


def target_urls_from_catalog(detail_urls: list[str]) -> list[str]:
    catalog = json.loads(RUMS.read_text("utf-8"))
    keep = catalog_target_urls(detail_urls, catalog, floor=0.7)
    print(f"catalogue match: {len(keep)}/{len(catalog)} bottles above floor 0.70")
    return keep


def cached_detail_pages() -> list[Path]:
    pages = []
    for path in sorted(CACHE_DIR.glob("*.html")):
        name = path.name
        if name.startswith("rum-") or name.startswith("brands-"):
            pages.append(path)
    return pages


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default=DEFAULT_START, help="listing URL (discover=listing)")
    ap.add_argument("--max-pages", type=int, default=40, help="listing pages to follow")
    ap.add_argument("--limit", type=int, default=0, help="stop after N detail pages (0 = all)")
    ap.add_argument("--delay", type=float, default=1.5,
                    help="seconds between requests; raised to robots.txt crawl-delay")
    ap.add_argument("--targets", choices=["all", "rums"], default="all",
                    help="'rums' fetches only bottles that look like ours")
    ap.add_argument("--discover", choices=["sitemap", "listing"], default="sitemap",
                    help="sitemap is the live catalogue; listing is a JS shell")
    ap.add_argument("--url-file", default="",
                    help="JSON list of {url} or plain URL lines — fetch these detail pages")
    ap.add_argument("--merge", action="store_true",
                    help="merge fetched records into existing rumratings_raw.json (by url)")
    ap.add_argument("--parse-only", action="store_true", help="use cached HTML only, no network")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fetcher = Fetcher(delay=args.delay, offline=args.parse_only)

    if args.parse_only:
        detail_pages = cached_detail_pages()
        print(f"parse-only: {len(detail_pages)} cached detail pages")
        pages = [(p.read_text("utf-8", "replace"), cache_url_from_path(p.name)) for p in detail_pages]
    elif args.url_file:
        path = Path(args.url_file)
        text = path.read_text("utf-8")
        if path.suffix.lower() == ".json":
            data = json.loads(text)
            urls = [row["url"] if isinstance(row, dict) else row for row in data]
        else:
            urls = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.startswith("#")]
        if args.limit:
            urls = urls[: args.limit]
        print(f"url-file: {len(urls)} detail pages from {path.name}")
        pages = []
        for i, url in enumerate(urls, 1):
            html = fetcher.get(url)
            if html is None:
                continue
            pages.append((html, url))
            if i % 10 == 0 or i == len(urls):
                print(f"  {i}/{len(urls)} fetched")
    else:
        if args.discover == "sitemap":
            urls = load_sitemap(offline=False)
        else:
            print(f"crawling listings from {args.start}")
            urls = crawl_listings(fetcher, args.start, args.max_pages)
        if args.targets == "rums":
            urls = target_urls_from_catalog(urls)
        elif args.discover == "sitemap" and not args.limit:
            print("refusing to fetch the whole sitemap without --limit or --targets rums")
            print(f"  {len(urls)} bottles; crawl-delay makes that a multi-day job")
            return
        if args.limit:
            urls = urls[: args.limit]
        print(f"{len(urls)} detail pages to fetch")
        pages = []
        for i, url in enumerate(urls, 1):
            html = fetcher.get(url)
            if html is None:
                continue
            pages.append((html, url))
            if i % 10 == 0 or i == len(urls):
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
    if args.merge and RAW.exists():
        by_url = {r["url"]: r for r in json.loads(RAW.read_text("utf-8"))}
        for rec in records:
            by_url[rec["url"]] = rec
        records = sorted(by_url.values(), key=lambda r: (-(r["rating"] or 0), -(r["votes"] or 0)))
        print(f"merged → {len(records)} total records")
    RAW.write_text(json.dumps(records, ensure_ascii=False, indent=1) + "\n", "utf-8")
    if args.merge and MISSES.exists():
        old_miss = {m["url"]: m for m in json.loads(MISSES.read_text("utf-8"))}
        for m in misses:
            old_miss[m["url"]] = m
        # Drop misses that we successfully parsed this run.
        ok = {r["url"] for r in records}
        misses = [m for u, m in old_miss.items() if u not in ok]
    MISSES.write_text(json.dumps(misses, ensure_ascii=False, indent=1) + "\n", "utf-8")

    with_reviews = sum(1 for r in records if r["reviews"])
    rel = RAW.relative_to(RAW.parent.parent.parent)
    print(f"\nwrote {len(records)} rums -> {rel}")
    print(f"  {with_reviews} with review text, {len(misses)} pages unparsed -> {MISSES.name}")
    print(f"  fetch stats: {fetcher.stats}")
    if misses:
        print("  inspect a miss, fix the selector in rumratings_shared.py, re-run --parse-only")


if __name__ == "__main__":
    main()
