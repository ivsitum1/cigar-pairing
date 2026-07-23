#!/usr/bin/env python3
"""Aggregate AI news RSS feeds for Machine weekly digest (brain repo)."""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DEFAULT_CONFIG = REPO_ROOT / "30_system" / "config" / "ai_news_feeds.json"
TASK_DIR = REPO_ROOT / ".agent" / "task"


@dataclass
class NewsItem:
    feed: str
    title: str
    link: str
    published: str
    summary: str
    score: float = 0.0
    keyword_hits: list[str] = field(default_factory=list)


def load_config(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def iso_week_label(when: date | None = None) -> str:
    when = when or date.today()
    iso = when.isocalendar()
    return f"{iso.year:04d}-W{iso.week:02d}"


def fetch_feed(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "agent-rules-machine-feed/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _text(elem: ET.Element | None) -> str:
    if elem is None:
        return ""
    return "".join(elem.itertext()).strip()


def parse_rss(xml_text: str, feed_name: str, max_items: int) -> list[NewsItem]:
    root = ET.fromstring(xml_text)
    items: list[NewsItem] = []
    for item in root.findall(".//item")[:max_items]:
        title = _text(item.find("title"))
        link = _text(item.find("link"))
        pub = _text(item.find("pubDate"))
        desc = _text(item.find("description"))
        items.append(NewsItem(feed=feed_name, title=title, link=link, published=pub, summary=desc[:500]))
    if items:
        return items
    # Atom fallback
    ns = {"a": "http://www.w3.org/2005/Atom"}
    for entry in root.findall(".//a:entry", ns)[:max_items]:
        title = _text(entry.find("a:title", ns))
        link_el = entry.find("a:link", ns)
        link = link_el.get("href", "") if link_el is not None else ""
        pub = _text(entry.find("a:updated", ns)) or _text(entry.find("a:published", ns))
        desc = _text(entry.find("a:summary", ns))
        items.append(NewsItem(feed=feed_name, title=title, link=link, published=pub, summary=desc[:500]))
    return items


def parse_published(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc)
    except (TypeError, ValueError):
        pass
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def score_item(item: NewsItem, cfg: dict[str, Any]) -> tuple[float, list[str]]:
    keywords = [k.lower() for k in cfg.get("rank_keywords", [])]
    text = f"{item.title} {item.summary}".lower()
    hits = [kw for kw in keywords if kw in text]
    return float(len(hits) * 2), hits


def run_feeds(config_path: Path, dry_run: bool, week_label: str | None) -> dict[str, Any]:
    cfg = load_config(config_path)
    label = week_label or iso_week_label()
    if dry_run:
        return {"week": label, "dry_run": True, "feeds": [f["name"] for f in cfg.get("feeds", [])], "items": []}

    lookback = int(cfg.get("lookback_days", 7))
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback)
    max_per = int(cfg.get("max_items_per_feed", 25))
    collected: list[NewsItem] = []

    for feed in cfg.get("feeds", []):
        name = feed.get("name", "feed")
        url = feed.get("url", "")
        if not url:
            continue
        try:
            xml_text = fetch_feed(url)
            items = parse_rss(xml_text, name, max_per)
        except Exception as exc:  # noqa: BLE001
            print(f"WARN: feed failed {name}: {exc}", file=sys.stderr)
            continue
        for item in items:
            pub_dt = parse_published(item.published)
            if pub_dt is not None and pub_dt < cutoff:
                continue
            sc, hits = score_item(item, cfg)
            item.score = sc
            item.keyword_hits = hits
            collected.append(item)

    collected.sort(key=lambda x: x.score, reverse=True)
    digest_n = int(cfg.get("digest_top_n", 30))
    collected = collected[:digest_n]

    return {
        "week": label,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "config_path": str(config_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "item_count": len(collected),
        "items": [asdict(i) for i in collected],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="AI news RSS aggregator for Machine digest")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--week", help="ISO week label YYYY-WW")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    if not args.config.is_file():
        print(f"ERROR: config not found: {args.config}", file=sys.stderr)
        return 1

    payload = run_feeds(args.config.resolve(), args.dry_run, args.week)
    if args.dry_run:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if not args.no_write:
        TASK_DIR.mkdir(parents=True, exist_ok=True)
        out = TASK_DIR / f"ai_news_{payload['week']}.json"
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {out.relative_to(REPO_ROOT)}")

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
