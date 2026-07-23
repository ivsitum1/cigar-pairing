#!/usr/bin/env python3
"""Grill user notebook 91614142 via Playwright (notebooklm-mcp Chrome profile)."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
OUT_DIR = WORKSPACE / "outputs" / "notebooklm"
QUESTIONS_FILE = OUT_DIR / "user_notebook_91614142_questions.json"
NOTEBOOK_URL = "https://notebooklm.google.com/notebook/91614142-303b-45b8-ad5c-91ee60b66e06"
MCP_PROFILE = (
    Path.home()
    / "AppData"
    / "Local"
    / "notebooklm-mcp"
    / "Data"
    / "chrome_profile"
)
GRILL_SCRIPT = WORKSPACE / "40_operations" / "scripts" / "notebooklm_grill_playwright.py"


def _load_questions(*, discovery_only: bool) -> list[str]:
    data = json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))
    if discovery_only:
        return list(data["discovery"])
    return list(data["discovery"]) + list(data["full_grill"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Grill user notebook 91614142")
    parser.add_argument(
        "--discovery-only",
        action="store_true",
        help="Run only Q1–Q3 discovery questions",
    )
    parser.add_argument("--start", type=int, default=0, help="Question index to resume")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    questions = _load_questions(discovery_only=args.discovery_only)
    q_temp = OUT_DIR / "user_notebook_91614142_questions_temp.json"
    q_temp.write_text(json.dumps(questions, ensure_ascii=False, indent=2), encoding="utf-8")

    out = OUT_DIR / "user_notebook_91614142_query_batch.json"
    meta_out = OUT_DIR / "user_notebook_91614142_notebook_meta.json"

    if not MCP_PROFILE.is_dir():
        meta = {
            "notebook_uuid": "91614142-303b-45b8-ad5c-91ee60b66e06",
            "notebook_url": NOTEBOOK_URL,
            "auth_status": "profile_missing",
            "message": "Run: node scripts/notebooklm-setup-auth.mjs",
        }
        meta_out.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        print(f"MCP profile missing: {MCP_PROFILE}", file=sys.stderr)
        return 2

    if args.dry_run:
        print(f"Would grill {len(questions)} questions -> {out}")
        return 0

    import subprocess

    # Delegate to shared grill script with MCP profile via env override
    env = {**dict(__import__("os").environ), "NOTEBOOKLM_PROFILE": str(MCP_PROFILE)}
    # Patch profile in subprocess by passing notebook URL directly
    cmd = [
        sys.executable,
        str(GRILL_SCRIPT),
        "--notebook-url",
        NOTEBOOK_URL,
        "--output",
        str(out),
        "--questions-file",
        str(q_temp),
        "--start",
        str(args.start),
    ]
    # notebooklm_grill_playwright uses hardcoded PROFILE; run inline if import works
    try:
        from notebooklm_grill_playwright import _ask, _count_answers  # type: ignore
    except ImportError:
        pass

    # Inline grill using MCP profile (grill script uses ~/.notebooklm path)
    from playwright.sync_api import sync_playwright

    import re

    QUERY_INPUT = "textarea.query-box-input"
    SUBMIT_BTN = "button.submit-button"
    ANSWER_TEXT = ".to-user-container .message-text-content"

    def count_answers(page):
        return page.locator(ANSWER_TEXT).count()

    def latest_answer(page):
        loc = page.locator(ANSWER_TEXT)
        if loc.count() == 0:
            return ""
        return (loc.nth(loc.count() - 1).inner_text() or "").strip()

    def ask(page, question: str, timeout_sec: int = 300) -> dict:
        before = count_answers(page)
        box = page.locator(QUERY_INPUT).first
        try:
            box.wait_for(state="visible", timeout=60_000)
        except Exception as exc:
            return {"success": False, "error": f"chat_input_missing: {exc}"}
        box.click()
        box.fill(question)
        page.locator(SUBMIT_BTN).first.click()
        deadline = time.time() + timeout_sec
        stable_text = ""
        stable_hits = 0
        while time.time() < deadline:
            page.wait_for_timeout(2500)
            if count_answers(page) <= before:
                continue
            text = latest_answer(page)
            if len(text) < 40:
                continue
            if text == stable_text:
                stable_hits += 1
                if stable_hits >= 3:
                    return {"success": True, "answer": text}
            else:
                stable_text = text
                stable_hits = 1
        text = latest_answer(page)
        if len(text) > 40:
            return {"success": True, "answer": text, "note": "timeout_partial"}
        return {"success": False, "answer": text, "error": "answer_timeout"}

    existing: dict = {}
    if out.exists():
        existing = json.loads(out.read_text(encoding="utf-8"))

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(MCP_PROFILE), headless=True, channel="chrome"
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(NOTEBOOK_URL, wait_until="domcontentloaded", timeout=120_000)
        page.wait_for_timeout(5000)

        page_url = page.url
        if "accounts.google.com" in page_url:
            meta = {
                "notebook_uuid": "91614142-303b-45b8-ad5c-91ee60b66e06",
                "notebook_url": NOTEBOOK_URL,
                "auth_status": "sign_in_required",
                "redirect_url": page_url,
                "grill_turns_completed": 0,
                "message": "Complete Google sign-in: node scripts/notebooklm-setup-auth.mjs",
            }
            meta_out.write_text(json.dumps(meta, indent=2), encoding="utf-8")
            ctx.close()
            print("Sign-in required. Run notebooklm-setup-auth.mjs", file=sys.stderr)
            return 2

        title = page.evaluate(
            """() => {
            const t = document.querySelector('.notebook-title, [class*="notebook-title"], h1');
            return (t?.textContent || document.title || '').trim();
          }"""
        )
        nb_id = (re.search(r"/notebook/([a-f0-9-]+)", NOTEBOOK_URL, re.I) or [None, None])[1]

        results = list(existing.get("results") or [])
        if len(results) < len(questions):
            results.extend([None] * (len(questions) - len(results)))

        completed = 0
        for i in range(args.start, len(questions)):
            if (
                i < len(results)
                and results[i]
                and results[i].get("result", {}).get("success")
            ):
                completed += 1
                continue
            q = questions[i]
            print(f"[{i+1}/{len(questions)}] {q[:70]}...", file=sys.stderr)
            r = ask(page, q)
            results[i] = {"question": q, "result": r}
            if r.get("success"):
                completed += 1
            payload = {
                "notebook_title": title,
                "notebook_url": NOTEBOOK_URL,
                "notebook_id": nb_id,
                "notebook_uuid": "91614142-303b-45b8-ad5c-91ee60b66e06",
                "exported_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "results": results,
            }
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            if not r.get("success"):
                break
            time.sleep(2)

        ctx.close()

    meta = {
        "notebook_uuid": "91614142-303b-45b8-ad5c-91ee60b66e06",
        "notebook_url": NOTEBOOK_URL,
        "notebook_title": title if "title" in dir() else "",
        "auth_status": "ok" if completed > 0 else "grill_failed",
        "grill_turns_completed": completed,
        "grill_turns_total": len(questions),
        "discovery_only": args.discovery_only,
    }
    meta_out.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(out)
    return 0 if completed > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
