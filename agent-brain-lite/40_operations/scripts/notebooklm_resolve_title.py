#!/usr/bin/env python3
"""Resolve notebook titles by visiting notebook URLs (Playwright)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROFILE = Path.home() / ".notebooklm" / "profiles" / "default" / "browser_profile"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--meta", required=True, help="JSON from notebooklm_browser_list.py")
    parser.add_argument("--needle", default="rag anatomy", help="Title must contain all words")
    parser.add_argument("--max", type=int, default=60, help="Max notebooks to scan")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    data = json.loads(Path(args.meta).read_text(encoding="utf-8"))
    needles = [w.lower() for w in args.needle.split() if w]
    notebooks = data.get("notebooks", [])[: args.max]

    from playwright.sync_api import sync_playwright

    resolved = []
    match = None
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(str(PROFILE), headless=True, channel="chrome")
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        for nb in notebooks:
            url = nb["url"]
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=90_000)
                page.wait_for_timeout(2500)
                info = page.evaluate(
                    """() => ({
                    title: (document.querySelector('h1')?.textContent || document.title || '').trim(),
                    sourceCount: document.querySelectorAll('[data-source], .source-card, source-panel-item').length
                  })"""
                )
            except Exception as exc:  # noqa: BLE001
                info = {"title": "", "error": str(exc), "sourceCount": 0}
            row = {**nb, **info}
            resolved.append(row)
            title_lc = (info.get("title") or "").lower()
            if needles and all(n in title_lc for n in needles):
                match = row
                break
        ctx.close()

    out = {
        "needle": args.needle,
        "match": match,
        "scanned": len(resolved),
        "resolved": resolved,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.output)
    if match:
        print(f"MATCH: {match['title']} -> {match['url']}", file=sys.stderr)
        return 0
    print("No title match found", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
