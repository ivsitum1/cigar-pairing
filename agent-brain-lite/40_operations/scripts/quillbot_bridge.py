#!/usr/bin/env python3
"""QuillBot AI Detector bridge for Cursor (Playwright + paid session).

No official QuillBot API — uses browser session in ~/.quillbot/profiles/.
Advisory QA only (HUM-3): not an acceptance gate for manuscripts.

Usage:
  python quillbot_bridge.py login          # one-time: sign in in headed browser
  python quillbot_bridge.py check-auth
  python quillbot_bridge.py detect --file manuscript.md [--json]
  python quillbot_bridge.py detect --text "paste here" [--json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[2]
_OPS = WORKSPACE / "40_operations" / "python"
if str(_OPS) not in sys.path:
    sys.path.insert(0, str(_OPS))

from common.quillbot_paths import (  # noqa: E402
    DETECTOR_URL,
    MIN_WORDS,
    PROFILE_DIR,
    SETTINGS_URL,
    STORAGE_STATE,
)

_STEALTH_ARGS = [
    "--disable-blink-features=AutomationControlled",
]

_STEALTH_INIT = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
"""


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))


def _read_input_text(*, text: str | None, file_path: Path | None) -> str:
    if text:
        return text.strip()
    if file_path and file_path.is_file():
        return file_path.read_text(encoding="utf-8", errors="replace").strip()
    raise ValueError("Provide --text or --file")


def _launch_browser(playwright: Any, *, headed: bool):
    return playwright.chromium.launch(
        headless=not headed,
        channel="chrome",
        ignore_default_args=["--enable-automation"],
        args=_STEALTH_ARGS,
    )


def _launch_context(playwright: Any, *, headed: bool):
    """Prefer storage_state from Chrome import/CDP; else isolated persistent profile."""
    PROFILE_DIR.parent.mkdir(parents=True, exist_ok=True)

    if STORAGE_STATE.is_file():
        browser = _launch_browser(playwright, headed=headed)
        ctx = browser.new_context(
            storage_state=str(STORAGE_STATE),
            viewport={"width": 1366, "height": 900},
        )
        ctx.add_init_script(_STEALTH_INIT)
        ctx._qb_browser = browser  # type: ignore[attr-defined]
        return ctx

    kwargs: dict[str, Any] = {
        "user_data_dir": str(PROFILE_DIR),
        "headless": not headed,
        "channel": "chrome",
        "ignore_default_args": ["--enable-automation"],
        "args": _STEALTH_ARGS,
        "viewport": {"width": 1366, "height": 900},
    }
    ctx = playwright.chromium.launch_persistent_context(**kwargs)
    for page in ctx.pages:
        page.add_init_script(_STEALTH_INIT)
    return ctx


def _close_context(ctx) -> None:
    browser = getattr(ctx, "_qb_browser", None)
    ctx.close()
    if browser:
        browser.close()


def _session_from_cookies(cookies: list[dict[str, Any]]) -> bool:
    qb = [c for c in cookies if "quillbot" in (c.get("domain") or "").lower()]
    by_name = {c.get("name"): c.get("value") for c in qb}
    auth = str(by_name.get("authenticated", "")).lower()
    if auth == "true":
        return True
    if str(by_name.get("premium", "")).lower() == "true":
        return True
    if auth == "false":
        return False
    return bool(by_name.get("connect.sid"))


def _is_logged_in(page, ctx=None) -> bool:
    if ctx is not None:
        if _session_from_cookies(ctx.cookies()):
            return True
        # stale anon cookies — verify on page
    page.goto(SETTINGS_URL, wait_until="domcontentloaded", timeout=120_000)
    page.wait_for_timeout(2500)
    url = (page.url or "").lower()
    body = (page.inner_text("body") or "").lower()
    if any(x in url for x in ("/login", "/sign-in", "/signup", "auth.")):
        return False
    if "log out" in body or "logout" in body or "sign out" in body:
        return True
    if re.search(r"@[\w.-]+\.\w+", body) and "settings" in url:
        return True
    if "log in" in body and "sign up" in body:
        return False
    return False


def cmd_login(headed: bool = True) -> int:
    from playwright.sync_api import sync_playwright

    print(f"Profile dir: {PROFILE_DIR}", flush=True)
    print(
        "If login fails here, use instead:\n"
        "  python quillbot_bridge.py import-chrome   (close Chrome first)\n"
        "  python quillbot_bridge.py sync-cdp       (Chrome with --remote-debugging-port=9222)",
        flush=True,
    )
    print("Sign in to QuillBot in the browser window, then press Enter here.", flush=True)
    with sync_playwright() as p:
        ctx = _launch_context(p, headed=headed)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(DETECTOR_URL, wait_until="domcontentloaded", timeout=120_000)
        input("Press Enter after login completes...")
        STORAGE_STATE.parent.mkdir(parents=True, exist_ok=True)
        try:
            ctx.storage_state(path=str(STORAGE_STATE))
        except Exception as exc:
            print(f"Could not save session (browser closed?): {exc}", file=sys.stderr)
            _close_context(ctx)
            return 1
        ok = _is_logged_in(page, ctx)
        _close_context(ctx)
    if ok:
        print("Login OK; storage saved.", flush=True)
        return 0
    print("Login may have failed — try import-chrome or sync-cdp.", file=sys.stderr)
    return 1


def cmd_import_chrome() -> int:
    from playwright.sync_api import sync_playwright

    from common.quillbot_chrome_import import (  # noqa: E402
        chrome_looks_running,
        default_chrome_user_data,
        load_chrome_cookies_for_playwright,
    )

    if chrome_looks_running():
        print(
            "Close all Chrome windows first (cookie DB is locked), then retry.",
            file=sys.stderr,
        )
        return 1

    print(f"Reading cookies from: {default_chrome_user_data()}", flush=True)
    try:
        cookies = load_chrome_cookies_for_playwright()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        print("Run: pip install browser_cookie3", file=sys.stderr)
        return 1

    if not cookies:
        print("No quillbot.com cookies found in Chrome. Log in at quillbot.com in Chrome first.", file=sys.stderr)
        return 1

    print(f"Found {len(cookies)} cookie(s). Verifying session...", flush=True)
    with sync_playwright() as p:
        browser = _launch_browser(p, headed=False)
        ctx = browser.new_context(viewport={"width": 1366, "height": 900})
        ctx.add_cookies(cookies)
        page = ctx.new_page()
        ok = _is_logged_in(page, ctx)
        if not ok:
            browser.close()
            print("Cookies imported but session not valid. Re-login in Chrome.", file=sys.stderr)
            return 1
        page.goto(DETECTOR_URL, wait_until="domcontentloaded", timeout=120_000)
        STORAGE_STATE.parent.mkdir(parents=True, exist_ok=True)
        ctx.storage_state(path=str(STORAGE_STATE))
        browser.close()

    print(f"Imported Chrome session -> {STORAGE_STATE}", flush=True)
    return 0


def cmd_sync_cdp(port: int) -> int:
    from playwright.sync_api import sync_playwright

    from common.quillbot_chrome_import import (  # noqa: E402
        default_chrome_executable,
        is_debug_port_open,
    )

    if not is_debug_port_open(port):
        chrome = default_chrome_executable()
        print(
            f"Port {port} is not open (Chrome debug not running).\n"
            "Windows ignores --remote-debugging-port if Chrome was already open.\n"
            "Run:\n"
            f"  python 40_operations/scripts/quillbot_bridge.py start-chrome-debug --port {port}\n"
            "Then sign in to QuillBot in that window and run sync-cdp again.",
            file=sys.stderr,
        )
        print(f'Or manually: & "{chrome}" --remote-debugging-port={port}', file=sys.stderr)
        return 1

    endpoint = f"http://127.0.0.1:{port}"
    print(f"Connecting to Chrome CDP at {endpoint} ...", flush=True)
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(endpoint)
            if not browser.contexts:
                print("No browser context on CDP endpoint.", file=sys.stderr)
                return 1
            ctx = browser.contexts[0]
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            ok = _is_logged_in(page, ctx)
            if not ok:
                auth_hint = ""
                if ctx is not None:
                    qb = {
                        c.get("name"): c.get("value")
                        for c in ctx.cookies()
                        if "quillbot" in (c.get("domain") or "").lower()
                    }
                    if qb.get("authenticated") == "false":
                        auth_hint = " (cookie authenticated=false - sign in again)"
                print(
                    "Not logged in on this Chrome. Open quillbot.com in that Chrome and sign in."
                    + auth_hint,
                    file=sys.stderr,
                )
                return 1
            STORAGE_STATE.parent.mkdir(parents=True, exist_ok=True)
            ctx.storage_state(path=str(STORAGE_STATE))
            print(f"Synced session -> {STORAGE_STATE}", flush=True)
    except Exception as exc:
        chrome = default_chrome_executable()
        print(f"CDP connect failed: {exc}", file=sys.stderr)
        print(
            "Start Chrome with remote debugging (close Chrome first):\n"
            f'  & "{chrome}" --remote-debugging-port={port}',
            file=sys.stderr,
        )
        return 1
    return 0


def cmd_check_auth() -> int:
    from playwright.sync_api import sync_playwright

    if not STORAGE_STATE.is_file() and not PROFILE_DIR.is_dir():
        print(
            "No session. Run: import-chrome | sync-cdp | login",
            file=sys.stderr,
        )
        return 1
    with sync_playwright() as p:
        ctx = _launch_context(p, headed=False)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        ok = _is_logged_in(page, ctx)
        _close_context(ctx)
    if ok:
        print("QuillBot session appears valid.")
        return 0
    print("Session expired. Run: import-chrome or sync-cdp", file=sys.stderr)
    return 1


def _fill_detector(page, text: str) -> None:
    page.goto(DETECTOR_URL, wait_until="domcontentloaded", timeout=120_000)
    page.wait_for_timeout(4000)
    editor = page.locator("#aidr-input-editor")
    if editor.count() == 0:
        editor = page.locator("textarea:not(.g-recaptcha-response)")
    if editor.count() == 0:
        editor = page.locator("[contenteditable=true]").first
    editor.first.wait_for(state="visible", timeout=60_000)
    editor.first.click()
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    page.keyboard.insert_text(text)
    page.wait_for_timeout(1500)
    btn = page.locator('[data-testid="aidr-primary-cta"]')
    if btn.count() == 0 or btn.first.is_disabled():
        btn = page.get_by_role("button", name=re.compile(r"^detect\s*ai$", re.I))
    btn.first.wait_for(state="visible", timeout=30_000)
    page.wait_for_function(
        """() => {
          const b = document.querySelector('[data-testid="aidr-primary-cta"]')
            || [...document.querySelectorAll('button')].find(
              (x) => /^detect\\s*ai$/i.test((x.innerText || '').trim())
            );
          return b && !b.disabled;
        }""",
        timeout=60_000,
    )
    btn.first.click()


def _extract_detector_scores(body: str) -> tuple[int | None, int | None]:
    """Parse QuillBot three-bucket UI: AI-generated / Human+AI-refined / Human-written."""
    buckets: dict[str, int] = {}
    for match in re.finditer(
        r"(\d{1,3})\s*%\s*(?:\n\s*)*(AI-generated|Human-written\s*&\s*AI-refined|Human-written)",
        body,
        re.I,
    ):
        label = match.group(2).lower().replace(" ", "")
        buckets[label] = int(match.group(1))

    ai_gen = buckets.get("ai-generated")
    human_refined = buckets.get("human-written&ai-refined")
    human = buckets.get("human-written")

    if ai_gen is not None:
        return ai_gen, (human if human is not None else max(0, 100 - ai_gen))

    # Fallback: first two numeric percentages after Detect AI (ignore --%)
    tail = body.split("Detect AI", 1)[-1] if "Detect AI" in body else body
    nums = [int(x) for x in re.findall(r"(?<![\-])(\d{1,3})\s*%", tail)]
    if nums:
        ai_pct = nums[0]
        return ai_pct, max(0, 100 - ai_pct)
    return None, None


def _parse_results(page) -> dict[str, Any]:
    deadline = time.time() + 120
    last_blob = ""
    while time.time() < deadline:
        page.wait_for_timeout(2000)
        blob = page.evaluate(
            """() => {
            const root = document.body?.innerText || '';
            const highlights = [];
            for (const el of document.querySelectorAll('[class*="highlight"], [data-testid*="highlight"], mark')) {
              const t = (el.textContent || '').trim();
              if (t.length > 10) highlights.push(t.slice(0, 500));
            }
            return { body: root.slice(0, 12000), highlights };
          }"""
        )
        body = blob.get("body", "")
        last_blob = body
        if "--%" in body and "AI-generated" in body:
            continue
        ai_pct, human_pct = _extract_detector_scores(body)
        if ai_pct is not None:
            return {
                "ai_score_percent": ai_pct,
                "human_score_percent": human_pct,
                "flagged_spans": blob.get("highlights", [])[:20],
                "raw_summary": body[:4000],
                "parse_note": "heuristic_from_page_text",
            }
    return {
        "ai_score_percent": None,
        "human_score_percent": None,
        "flagged_spans": [],
        "raw_summary": last_blob[:4000],
        "parse_note": "timeout_or_layout_change",
    }


def cmd_detect(
    *,
    text: str | None,
    file_path: Path | None,
    as_json: bool,
    out_path: Path | None,
    headed: bool,
) -> int:
    from playwright.sync_api import sync_playwright

    if not STORAGE_STATE.is_file() and not PROFILE_DIR.is_dir():
        print("No session. Run: import-chrome | sync-cdp | login", file=sys.stderr)
        return 1

    content = _read_input_text(text=text, file_path=file_path)
    wc = _word_count(content)
    if wc < MIN_WORDS:
        print(
            f"Text has {wc} words; QuillBot recommends ≥{MIN_WORDS}.",
            file=sys.stderr,
        )
        return 1

    with sync_playwright() as p:
        ctx = _launch_context(p, headed=headed)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        if not _is_logged_in(page, ctx):
            _close_context(ctx)
            print("Not logged in. Run: import-chrome or sync-cdp", file=sys.stderr)
            return 1
        _fill_detector(page, content)
        parsed = _parse_results(page)
        _close_context(ctx)

    payload: dict[str, Any] = {
        "tool": "quillbot_ai_detector",
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "source_file": str(file_path).replace("\\", "/") if file_path else None,
        "word_count": wc,
        "text_hash": hashlib.sha256(content.encode("utf-8")).hexdigest()[:16],
        "detector_url": DETECTOR_URL,
        "disclaimer": "Advisory QA only — not manuscript acceptance gate (HUM-3).",
        **parsed,
    }

    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        ai = payload.get("ai_score_percent")
        hum = payload.get("human_score_percent")
        print(f"Words: {wc} | AI: {ai}% | Human: {hum}% | note: {payload.get('parse_note')}")
        if out_path:
            print(f"Wrote {out_path}")
    return 0 if payload.get("ai_score_percent") is not None else 2


def cmd_start_chrome_debug(port: int, *, no_kill: bool) -> int:
    from common.quillbot_chrome_import import (  # noqa: E402
        chrome_looks_running,
        is_debug_port_open,
        start_chrome_with_cdp,
    )

    if is_debug_port_open(port):
        print(f"Debug port {port} already open. Open QuillBot, then: sync-cdp", flush=True)
        return 0

    if chrome_looks_running() and not no_kill:
        print("Closing existing Chrome (required for debug port on Windows)...", flush=True)

    try:
        start_chrome_with_cdp(port, kill_existing=not no_kill)
    except (FileNotFoundError, TimeoutError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(
        f"Chrome ready on port {port} with your profile.\n"
        "1) Confirm you are logged in at quillbot.com\n"
        f"2) python 40_operations/scripts/quillbot_bridge.py sync-cdp --port {port}",
        flush=True,
    )
    return 0


def cmd_bootstrap(port: int) -> int:
    if cmd_start_chrome_debug(port, no_kill=False) != 0:
        return 1
    print("Waiting 5s for QuillBot tab...", flush=True)
    time.sleep(5)
    return cmd_sync_cdp(port)


def main() -> int:
    parser = argparse.ArgumentParser(description="QuillBot AI Detector bridge")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("login", help="Headed login in isolated profile (often blocked — prefer import-chrome)")
    sub.add_parser("import-chrome", help="Copy session from your Chrome (close Chrome first)")
    sync = sub.add_parser("sync-cdp", help="Sync from running Chrome with remote debugging")
    sync.add_argument("--port", type=int, default=9222)
    dbg = sub.add_parser(
        "start-chrome-debug",
        help="Kill Chrome and restart with --remote-debugging-port (Windows fix)",
    )
    dbg.add_argument("--port", type=int, default=9222)
    dbg.add_argument(
        "--no-kill",
        action="store_true",
        help="Do not taskkill chrome.exe (only if port already in use elsewhere)",
    )
    boot = sub.add_parser("bootstrap", help="start-chrome-debug + sync-cdp")
    boot.add_argument("--port", type=int, default=9222)
    sub.add_parser("check-auth", help="Verify QuillBot session")

    det = sub.add_parser("detect", help="Run AI detector on text")
    det.add_argument("--text", default="")
    det.add_argument("--file", type=Path, default=None)
    det.add_argument("--out", type=Path, default=None, help="JSON output path")
    det.add_argument("--json", action="store_true")
    det.add_argument("--headed", action="store_true", help="Show browser (debug)")

    args = parser.parse_args()

    if args.cmd == "login":
        return cmd_login(headed=True)
    if args.cmd == "import-chrome":
        return cmd_import_chrome()
    if args.cmd == "sync-cdp":
        return cmd_sync_cdp(args.port)
    if args.cmd == "start-chrome-debug":
        return cmd_start_chrome_debug(args.port, no_kill=args.no_kill)
    if args.cmd == "bootstrap":
        return cmd_bootstrap(args.port)
    if args.cmd == "check-auth":
        return cmd_check_auth()
    if args.cmd == "detect":
        out = args.out
        if out is None and args.file:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
            slug = args.file.stem[:40]
            out = WORKSPACE / ".agent" / "task" / f"quillbot_scan_{stamp}_{slug}.json"
        return cmd_detect(
            text=args.text or None,
            file_path=args.file,
            as_json=args.json,
            out_path=out,
            headed=args.headed,
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
