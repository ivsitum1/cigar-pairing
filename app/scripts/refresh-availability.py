#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ping known product URLs and write inStock / stockFetchedAt.

Does not recrawl catalogues. Does not touch price `fetchedAt`. Failed fetches
leave the previous stock fields in place.

  python scripts/refresh-availability.py --dry-run
  python scripts/refresh-availability.py --limit 20
  python scripts/refresh-availability.py --cigars --hosts humidor.hr,famous-smoke.com
  python scripts/refresh-availability.py --drinks --sleep 2
  python scripts/refresh-availability.py --stale-days 14
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from availability_catalog import (  # noqa: E402
    apply_stock_to_cigar,
    apply_stock_to_drink,
    cigar_link_stock,
    collect_cigar_urls,
    collect_drink_urls,
    drink_stock,
    normalize_url,
    wants_stealth,
)
from shop_fetch import fetch_html, scrapling_available  # noqa: E402
from stock_parse import parse_stock  # noqa: E402

ROOT = HERE.parent
DATA = ROOT / "src" / "data"
CIGARS_JSON = DATA / "cigars.json"
OVERLAY_JSON = HERE / "output" / "stock_overlay.json"
DRINK_FILES = (
    DATA / "rums.json",
    DATA / "whiskies.json",
    DATA / "brandies.json",
    DATA / "gins.json",
    DATA / "tequilas.json",
    DATA / "digestifs.json",
    DATA / "wines.json",
    DATA / "coffees.json",
)

# Slower shops — seconds between consecutive requests to the same host.
HOST_SLEEP = {
    "cigarworld.de": 4.0,
    "www.cigarworld.de": 4.0,
    "neptunecigar.com": 3.0,
    "www.neptunecigar.com": 3.0,
    "famous-smoke.com": 3.0,
    "www.famous-smoke.com": 3.0,
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _round_robin_hosts(jobs: list[tuple[str, str, str]]) -> list[tuple[str, str, str]]:
    """Spread requests across shops so CigarWorld/Neptune are not hit in a row."""
    buckets: dict[str, list] = defaultdict(list)
    order: list[str] = []
    for job in jobs:
        host = (urlparse(job[2]).hostname or "").lower()
        if host not in buckets:
            order.append(host)
        buckets[host].append(job)
    out: list[tuple[str, str, str]] = []
    while len(out) < len(jobs):
        for host in order:
            if buckets[host]:
                out.append(buckets[host].pop(0))
    return out


def _persist(cigars, cigars_dirty: bool, drink_payloads, drinks_dirty: set[Path]) -> None:
    if cigars_dirty:
        _save(CIGARS_JSON, cigars)
        print(f"wrote {CIGARS_JSON}", flush=True)
    for path in sorted(drinks_dirty, key=lambda p: p.name):
        payload = next(records for p, records in drink_payloads if p == path)
        _save(path, payload)
        print(f"wrote {path}", flush=True)


def _host_ok(url: str, hosts: set[str] | None) -> bool:
    if not hosts:
        return True
    host = (urlparse(url).hostname or "").lower().removeprefix("www.")
    return any(host == h or host.endswith(f".{h}") for h in hosts)


def _is_stale(fetched_at: str | None, cutoff: date) -> bool:
    if not fetched_at:
        return True
    try:
        return datetime.strptime(fetched_at, "%Y-%m-%d").date() < cutoff
    except ValueError:
        return True


def _known_stock(
    kind: str,
    rid: str,
    url: str,
    cigars: list,
    drink_payloads: list[tuple[Path, list]],
) -> tuple[bool | None, str | None]:
    if kind == "cigar":
        for c in cigars:
            if c.get("id") != rid:
                continue
            hit = cigar_link_stock(c, url)
            if hit:
                return hit.get("inStock"), hit.get("stockFetchedAt")
    else:
        for _path, records in drink_payloads:
            for d in records:
                if d.get("id") != rid:
                    continue
                hit = drink_stock(d, url)
                if hit:
                    return hit.get("inStock"), hit.get("stockFetchedAt")
    return None, None


def collect_jobs(
    cigars: list,
    drink_payloads: list[tuple[Path, list]],
    *,
    do_cigars: bool,
    do_drinks: bool,
    hosts: set[str] | None,
    stale_days: int | None,
) -> list[tuple[str, str, str]]:
    """(kind, record_id, url) — kind is 'cigar' or 'drink'."""
    cutoff = date.today() - timedelta(days=stale_days) if stale_days else None
    jobs: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    if do_cigars:
        for c in cigars:
            cid = c.get("id") or ""
            for url in collect_cigar_urls(c):
                if not _host_ok(url, hosts):
                    continue
                key = f"cigar|{url.lower()}"
                if key in seen:
                    continue
                if cutoff is not None:
                    _stock, fetched = _known_stock("cigar", cid, url, cigars, drink_payloads)
                    if not _is_stale(fetched, cutoff):
                        continue
                seen.add(key)
                jobs.append(("cigar", cid, url))
    if do_drinks:
        for _path, records in drink_payloads:
            for d in records:
                did = d.get("id") or ""
                for url in collect_drink_urls(d):
                    if not _host_ok(url, hosts):
                        continue
                    key = f"drink|{url.lower()}"
                    if key in seen:
                        continue
                    if cutoff is not None:
                        _stock, fetched = _known_stock("drink", did, url, cigars, drink_payloads)
                        if not _is_stale(fetched, cutoff):
                            continue
                    seen.add(key)
                    jobs.append(("drink", did, url))
    return jobs


def _save_overlay(overlay: dict[str, dict]) -> None:
    OVERLAY_JSON.parent.mkdir(parents=True, exist_ok=True)
    _save(OVERLAY_JSON, dict(sorted(overlay.items())))


def main() -> int:
    p = argparse.ArgumentParser(description="Ping known shop URLs for in-stock status.")
    p.add_argument("--cigars", action="store_true", help="Only cigars.json")
    p.add_argument("--drinks", action="store_true", help="Only drink JSON files")
    p.add_argument("--dry-run", action="store_true", help="List URLs, do not fetch")
    p.add_argument("--limit", type=int, default=0, help="Max URLs (0 = all)")
    p.add_argument("--sleep", type=float, default=2.0, help="Default seconds between requests")
    p.add_argument(
        "--stale-days",
        type=int,
        default=0,
        help="Only ping URLs whose stockFetchedAt is older than N days (0 = all)",
    )
    p.add_argument(
        "--hosts",
        default="",
        help="Comma-separated host filter (e.g. humidor.hr,famous-smoke.com,allez.hr)",
    )
    p.add_argument("--timeout", type=int, default=45)
    args = p.parse_args()

    do_cigars = True
    do_drinks = True
    if args.cigars and not args.drinks:
        do_drinks = False
    if args.drinks and not args.cigars:
        do_cigars = False

    hosts = {h.strip().lower().removeprefix("www.") for h in args.hosts.split(",") if h.strip()}
    cigars = _load(CIGARS_JSON) if do_cigars else []
    drink_payloads: list[tuple[Path, list]] = []
    if do_drinks:
        for path in DRINK_FILES:
            if path.exists():
                payload = _load(path)
                if isinstance(payload, list):
                    drink_payloads.append((path, payload))

    stale_days = args.stale_days or None
    jobs = collect_jobs(
        cigars,
        drink_payloads,
        do_cigars=do_cigars,
        do_drinks=do_drinks,
        hosts=hosts or None,
        stale_days=stale_days,
    )
    jobs = _round_robin_hosts(jobs)
    if args.limit:
        jobs = jobs[: args.limit]

    print(
        f"jobs={len(jobs)} scrapling={'yes' if scrapling_available() else 'no (urllib)'} "
        f"date={date.today().isoformat()} stale_days={stale_days or 'all'}",
        flush=True,
    )
    if args.dry_run:
        for kind, rid, url in jobs:
            flag = " stealth" if wants_stealth(url) else ""
            print(f"  {kind}\t{rid}\t{url}{flag}")
        return 0

    overlay: dict[str, dict] = {}
    if OVERLAY_JSON.is_file():
        try:
            overlay = json.loads(OVERLAY_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            overlay = {}

    fetched_at = date.today().isoformat()
    stats = {"ok_in": 0, "ok_out": 0, "unknown": 0, "fetch_fail": 0, "applied": 0}
    cigars_dirty = False
    drinks_dirty: set[Path] = set()
    last_host = ""

    for i, (kind, rid, url) in enumerate(jobs, 1):
        host = (urlparse(url).hostname or "").lower()
        if i > 1:
            pause = HOST_SLEEP.get(host, args.sleep)
            if host == last_host:
                time.sleep(pause)
            else:
                time.sleep(min(pause, args.sleep))
        last_host = host

        result = fetch_html(url, timeout=args.timeout)
        if not result.html:
            stats["fetch_fail"] += 1
            print(f"[{i}/{len(jobs)}] FAIL {rid} {url} {result.status} {result.error}", flush=True)
        else:
            stock = parse_stock(result.html)
            if stock is True:
                stats["ok_in"] += 1
                label = "IN"
            elif stock is False:
                stats["ok_out"] += 1
                label = "OUT"
            else:
                stats["unknown"] += 1
                label = "UNKNOWN"
            applied = 0
            if stock is not None:
                overlay[normalize_url(url) or url] = {
                    "inStock": stock,
                    "stockFetchedAt": fetched_at,
                }
                if kind == "cigar":
                    for c in cigars:
                        applied += apply_stock_to_cigar(c, url, stock, fetched_at)
                    if applied:
                        cigars_dirty = True
                else:
                    for path, records in drink_payloads:
                        wrote = 0
                        for d in records:
                            wrote += apply_stock_to_drink(d, url, stock, fetched_at)
                        if wrote:
                            drinks_dirty.add(path)
                            applied += wrote
                stats["applied"] += applied
            print(
                f"[{i}/{len(jobs)}] {label} applied={applied} {rid} {url}",
                flush=True,
            )
        if i % 200 == 0:
            _persist(cigars, cigars_dirty, drink_payloads, drinks_dirty)
            _save_overlay(overlay)
        if i < len(jobs) and args.sleep > 0 and host not in HOST_SLEEP:
            pass  # host-aware pause already applied above

    _persist(cigars, cigars_dirty, drink_payloads, drinks_dirty)
    _save_overlay(overlay)

    print("done " + " ".join(f"{k}={v}" for k, v in stats.items()), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
