#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export raw cigar shop catalogs (HR/EU/USA) into app/scripts/output/.

This is intentionally a "raw" export: it does NOT modify app/src/data/cigars.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure local imports work when running from repo root.
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from shop_scrape.http import HttpClient, HttpConfig  # noqa: E402
from shop_scrape.shops import SCRAPERS  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export raw cigar shop catalogs")
    parser.add_argument(
        "--shop",
        default="all",
        choices=["all", *sorted(SCRAPERS.keys())],
        help="Which shop to scrape",
    )
    parser.add_argument("--limit", type=int, default=None, help="Max items to export per shop")
    parser.add_argument("--out-dir", default=str(SCRIPTS_DIR / "output"), help="Output directory")
    parser.add_argument("--cache-ttl-s", type=int, default=24 * 60 * 60, help="Cache TTL seconds")
    parser.add_argument("--no-cache", action="store_true", help="Disable cache")
    parser.add_argument("--per-host-delay-s", type=float, default=0.6, help="Delay between requests per host")
    parser.add_argument("--timeout-s", type=int, default=45, help="HTTP timeout seconds")
    parser.add_argument("--max-retries", type=int, default=3, help="Retries for 429/5xx")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cache_dir = SCRIPTS_DIR / ".cache" / "cigar_shop_http"
    # Browser-like UA: Humidor Cloudflare is less aggressive than with bot-style UAs.
    ua = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )
    client = HttpClient(
        HttpConfig(
            user_agent=ua,
            cache_dir=cache_dir,
            cache_ttl_s=int(args.cache_ttl_s),
            per_host_delay_s=float(args.per_host_delay_s),
            timeout_s=int(args.timeout_s),
            max_retries=int(args.max_retries),
            cache_enabled=not bool(args.no_cache),
        )
    )

    shop_ids = sorted(SCRAPERS.keys()) if args.shop == "all" else [args.shop]
    for shop_id in shop_ids:
        scrape_fn = SCRAPERS[shop_id]
        print(f"Scraping {shop_id} …", flush=True)
        out_path = out_dir / f"cigar_shop_{shop_id}_raw.json"
        scrape_kwargs: dict = {"limit": args.limit}
        # Long scrapes write incremental checkpoints to the same path.
        if shop_id in ("cigarworld_eu", "holts_us"):
            scrape_kwargs["checkpoint_path"] = str(out_path)
        data = scrape_fn(client, **scrape_kwargs)
        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  wrote {out_path} ({len(data.get('items') or [])} items)", flush=True)


if __name__ == "__main__":
    main()

