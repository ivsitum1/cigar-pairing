#!/usr/bin/env python3
"""List NotebookLM notebooks via Playwright persistent profile."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

DEFAULT_PROFILES = [
    Path.home() / ".notebooklm" / "profiles" / "default" / "browser_profile",
    Path(os.environ.get("LOCALAPPDATA", "")) / "notebooklm-mcp" / "Data" / "chrome_profile",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", help="Chrome user data dir")
    parser.add_argument("--filter", default="", help="Title substring filter")
    parser.add_argument("--output", help="Write JSON to path")
    args = parser.parse_args()

    profile = Path(args.profile) if args.profile else None
    if not profile or not profile.exists():
        for p in DEFAULT_PROFILES:
            if p.exists():
                profile = p
                break
    if not profile or not profile.exists():
        print("No browser profile found.", file=sys.stderr)
        return 2

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Install playwright: pip install playwright && playwright install chromium", file=sys.stderr)
        return 2

    filt = args.filter.lower()
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(profile),
            headless=True,
            channel="chrome",
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://notebooklm.google.com/", wait_until="domcontentloaded", timeout=120_000)
        page.wait_for_timeout(8000)
        page_url = page.url
        notebooks = page.evaluate(
            """() => {
            const out = [];
            const seen = new Set();
            for (const a of document.querySelectorAll('a[href*="/notebook/"]')) {
              const href = a.href || '';
              const m = href.match(/\\/notebook\\/([a-f0-9-]+)/i);
              if (!m || seen.has(m[1])) continue;
              seen.add(m[1]);
              out.push({ title: (a.textContent || '').trim(), url: href, notebook_id: m[1] });
            }
            return out;
          }"""
        )
        ctx.close()

    filtered = [
        n
        for n in notebooks
        if not filt
        or filt in n.get("title", "").lower()
        or all(w in n.get("title", "").lower() for w in filt.split() if w)
    ]
    payload = {
        "profile": str(profile),
        "page_url": page_url,
        "notebooks": notebooks,
        "filtered": filtered,
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(text, encoding="utf-8")
        print(args.output)
    else:
        print(text)
    return 0 if filtered or notebooks else 1


if __name__ == "__main__":
    raise SystemExit(main())
