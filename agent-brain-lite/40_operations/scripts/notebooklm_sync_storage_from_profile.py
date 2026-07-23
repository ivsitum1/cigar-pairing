#!/usr/bin/env python3
"""Export storage_state.json from notebooklm-py Playwright browser_profile for API/MCP."""
from __future__ import annotations

import argparse
from pathlib import Path

PROFILE = Path.home() / ".notebooklm" / "profiles" / "default" / "browser_profile"
STORAGE = Path.home() / ".notebooklm" / "profiles" / "default" / "storage_state.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, default=PROFILE)
    parser.add_argument("--output", type=Path, default=STORAGE)
    args = parser.parse_args()

    if not args.profile.is_dir():
        print(f"Profile missing: {args.profile}", flush=True)
        return 1

    from playwright.sync_api import sync_playwright

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(args.profile), headless=True, channel="chrome"
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(
            "https://notebooklm.google.com/",
            wait_until="domcontentloaded",
            timeout=120_000,
        )
        page.wait_for_timeout(3000)
        ctx.storage_state(path=str(args.output))
        ctx.close()

    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
