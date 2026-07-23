#!/usr/bin/env python3
"""arXiv scan for self-evolving / harness / agent-skill papers.

Runs standalone or as a sensor in the weekly Machine digest and monthly
arXiv scout task. Compares hits to the canonical registry and flags new IDs.

Usage:
  py -3 40_operations/scripts/arxiv_self_evolving_scan.py
  py -3 40_operations/scripts/arxiv_self_evolving_scan.py --period weekly
  py -3 40_operations/scripts/arxiv_self_evolving_scan.py --period monthly --month 2026-07
  py -3 40_operations/scripts/arxiv_self_evolving_scan.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from calendar import monthrange
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
TASK_DIR = REPO_ROOT / ".agent" / "task"
REGISTRY_PATH = REPO_ROOT / "30_system" / "docs" / "reference" / "self_evolving_arxiv_registry.json"

QUERIES = [
    'ti:"self-evolving"',
    'ti:"self evolving"',
    'abs:"self-evolving agent"',
    'abs:"source-level rewriting"',
    'abs:"Agent Trajectory Data Protocol"',
    'abs:"self-consolidation" AND abs:agent',
    'abs:"Gödel Agent" OR abs:"Godel Agent"',
    'abs:"MetaAgent" AND abs:"meta-learning"',
    'abs:"agentic skills" AND abs:SoK',
    'all:MOSS AND all:"self-evolution"',
    'abs:"SkillCoach" AND abs:agent',
    'abs:"Harness-Aware" AND abs:evolv',
]

NS = {"a": "http://www.w3.org/2005/Atom"}
REQUEST_DELAY_SECONDS = 3.0


def parse_week(week_str: str | None) -> tuple[str, date, date]:
    if week_str:
        year_s, week_s = week_str.split("-W", 1)
        year, week = int(year_s), int(week_s)
    else:
        today = date.today()
        monday = date.fromisocalendar(today.isocalendar().year, today.isocalendar().week, 1) - timedelta(days=7)
        iso = monday.isocalendar()
        year, week = iso.year, iso.week
    start = date.fromisocalendar(year, week, 1)
    end = start + timedelta(days=6)
    return f"{year:04d}-W{week:02d}", start, end


def parse_month(month_str: str | None) -> tuple[str, date, date]:
    if month_str:
        year_s, mon_s = month_str.split("-", 1)
        year, mon = int(year_s), int(mon_s)
    else:
        today = date.today()
        if today.month == 1:
            year, mon = today.year - 1, 12
        else:
            year, mon = today.year, today.month - 1
    last_day = monthrange(year, mon)[1]
    return f"{year:04d}-{mon:02d}", date(year, mon, 1), date(year, mon, last_day)


def fetch(query: str, max_results: int = 10) -> list[dict[str, str]]:
    url = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {
            "search_query": query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
    )
    with urllib.request.urlopen(url, timeout=30) as resp:
        root = ET.fromstring(resp.read())
    out: list[dict[str, str]] = []
    for entry in root.findall("a:entry", NS):
        aid = entry.find("a:id", NS).text.split("/abs/")[-1].split("v")[0]
        published = (entry.find("a:published", NS).text or "")[:10]
        out.append(
            {
                "id": aid,
                "published": published,
                "title": (entry.find("a:title", NS).text or "").strip().replace("\n", " "),
                "url": f"https://arxiv.org/abs/{aid}",
            }
        )
    return out


def fetch_all(*, dry_run: bool) -> list[dict[str, str]]:
    if dry_run:
        return []
    seen: dict[str, dict[str, str]] = {}
    for idx, query in enumerate(QUERIES):
        if idx:
            time.sleep(REQUEST_DELAY_SECONDS)
        for item in fetch(query, 8):
            seen[item["id"]] = item
    return sorted(seen.values(), key=lambda x: x["published"], reverse=True)


def in_window(published: str, start: date, end: date) -> bool:
    try:
        pub = date.fromisoformat(published[:10])
    except ValueError:
        return False
    return start <= pub <= end


def load_registry_ids() -> set[str]:
    if not REGISTRY_PATH.is_file():
        return set()
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return {p.get("arxiv_id", "").split("v")[0] for p in data.get("papers", []) if p.get("arxiv_id")}


def build_payload(
    *,
    period: str,
    label: str,
    start: date,
    end: date,
    hits: list[dict[str, str]],
    registry_ids: set[str],
    dry_run: bool,
) -> dict[str, Any]:
    window_hits = [h for h in hits if in_window(h["published"], start, end)]
    new_hits = [h for h in window_hits if h["id"] not in registry_ids]
    return {
        "period": period,
        "label": label,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dry_run": dry_run,
        "query_count": len(QUERIES),
        "unique_hits_total": len(hits),
        "hits_in_window": window_hits,
        "new_hits": new_hits,
        "registry_path": str(REGISTRY_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "landscape_doc": "30_system/docs/SELF_EVOLVING_AGENTS_LANDSCAPE.md",
        "notebook_bundle": "20_knowledge/wiki/sources/notebooklm/self_evolving_2026_arxiv_bundle.md",
    }


def write_output(payload: dict[str, Any]) -> Path:
    TASK_DIR.mkdir(parents=True, exist_ok=True)
    path = TASK_DIR / f"self_evolving_arxiv_scan_{payload['label']}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Self-evolving agents arXiv sensor")
    parser.add_argument("--period", choices=("adhoc", "weekly", "monthly"), default="adhoc")
    parser.add_argument("--week", help="ISO week YYYY-WW (weekly period)")
    parser.add_argument("--month", help="Month YYYY-MM (monthly period)")
    parser.add_argument("--dry-run", action="store_true", help="Skip API calls; show window only")
    parser.add_argument("--no-write", action="store_true", help="Do not write .agent/task file")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    args = parser.parse_args()

    if args.period == "weekly":
        label, start, end = parse_week(args.week)
    elif args.period == "monthly":
        label, start, end = parse_month(args.month)
    else:
        label, start, end = "adhoc", date(2025, 1, 1), date.today()

    registry_ids = load_registry_ids()
    hits = fetch_all(dry_run=args.dry_run)
    payload = build_payload(
        period=args.period,
        label=label,
        start=start,
        end=end,
        hits=hits,
        registry_ids=registry_ids,
        dry_run=args.dry_run,
    )

    if args.dry_run and not args.json:
        print(f"Period: {args.period} | Window: {label} ({start} .. {end})")
        print(f"Queries: {len(QUERIES)} | Registry papers: {len(registry_ids)}")
        return 0

    if not args.no_write and args.period != "adhoc":
        out = write_output(payload)
        print(f"Wrote {out.relative_to(REPO_ROOT)}")

    if args.json or args.period == "adhoc":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif not args.dry_run:
        print(
            f"In-window: {len(payload['hits_in_window'])} | "
            f"New vs registry: {len(payload['new_hits'])}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
