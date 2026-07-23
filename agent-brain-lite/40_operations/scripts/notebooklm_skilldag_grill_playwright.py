#!/usr/bin/env python3
"""Grill SkillDAG NotebookLM via Playwright (notebooklm-py browser profile)."""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
PROFILE = Path.home() / ".notebooklm" / "profiles" / "default" / "browser_profile"
OUT_PATH = WORKSPACE / "outputs" / "notebooklm" / "skilldag_query_batch.json"
NOTEBOOK_URL = "https://notebooklm.google.com/notebook/48a6afa2-97d8-44f4-8a41-c87d2ea0b650"

GRILL_QUESTIONS = [
    "List every source in this notebook. For each source give: exact title, URL if present, source type (YouTube, PDF, web, pasted text), and a one-line topic label.",
    "For each source, extract 5-8 main claims as bullets. After each claim add a short quote and tag FACT, OPINION, DEMO, or BENCHMARK.",
    "How do the sources define SkillDAG (or skill dependency graph)? What is a node, edge, cycle, and valid topological order? Give definitions used in the notebook.",
    "How does SkillDAG differ from a flat skill list, from SkillRAE subunit decomposition, and from MUSE/SkillOpt if mentioned?",
    "What routing rules are described: when must skill A load before skill B; which branches can run in parallel vs serial; how are conflicts resolved?",
    "What evaluation or gate nodes appear in a skill DAG (pass/fail, Swiss Cheese, research gate, human-in-the-loop)? Where must execution stop?",
    "Map SkillDAG concepts to harness layers if possible: environment contract, procedural skill, action realization, trajectory regulation (LifeHarness or equivalent).",
    "Are named pipeline sequences (e.g. grill-me -> write-prd -> prd-to-issues -> ralph-loop) represented as DAGs in the sources? How should they be encoded?",
    "What token or context budget rules apply per DAG branch or per parallel fan-out? List each number with its source.",
    "Where do sources disagree? Which claims lack code, papers, or reproducible benchmarks?",
    "List the top 10 changes an agent-rules workspace should make, ranked P0 (rules/MCP/skills), P1 (scripts), P2 (research only). For each: target artifact, acceptance test, dependencies.",
    "Build a table of papers, GitHub repos, and benchmarks cited: claim, source title, external reference, reproducible Y/N.",
    "What recommendations are specific to Cursor, MCP, or file-based agent harnesses (not generic prompt engineering)?",
    "What wiki or knowledge-graph patterns (wikilinks, orphans, multi-hop, cross-linking) are recommended for skill or pipeline memory?",
]

QUERY_INPUT = "textarea.query-box-input"
SUBMIT_BTN = "button.submit-button"
ANSWER_TEXT = ".to-user-container .message-text-content"


def _count_answers(page) -> int:
    return page.locator(ANSWER_TEXT).count()


def _latest_answer(page) -> str:
    loc = page.locator(ANSWER_TEXT)
    if loc.count() == 0:
        return ""
    return (loc.nth(loc.count() - 1).inner_text() or "").strip()


def _ask(page, question: str, timeout_sec: int = 420) -> dict:
    before = _count_answers(page)
    box = page.locator(QUERY_INPUT).first
    box.wait_for(state="visible", timeout=90_000)
    box.click()
    box.fill(question)
    page.locator(SUBMIT_BTN).first.click()
    deadline = time.time() + timeout_sec
    stable_text = ""
    stable_hits = 0
    while time.time() < deadline:
        page.wait_for_timeout(3000)
        if _count_answers(page) <= before:
            continue
        text = _latest_answer(page)
        if len(text) < 40:
            continue
        low = text.lower()
        if any(
            p in low
            for p in (
                "answer is being",
                "antwort wird",
                "bitte warten",
                "please wait",
                "thinking",
            )
        ):
            stable_hits = 0
            continue
        if text == stable_text:
            stable_hits += 1
            if stable_hits >= 3:
                return {"success": True, "answer": text}
        else:
            stable_text = text
            stable_hits = 1
    text = _latest_answer(page)
    if len(text) > 40:
        return {"success": True, "answer": text, "note": "timeout_partial"}
    return {"success": False, "answer": text, "error": "answer_timeout"}


def _load_existing() -> dict:
    if not OUT_PATH.exists():
        return {}
    return json.loads(OUT_PATH.read_text(encoding="utf-8"))


def _done_indices(existing: dict) -> set[int]:
    done: set[int] = set()
    for item in existing.get("results", []):
        idx = item.get("question_index")
        if idx and item.get("result", {}).get("success"):
            done.add(int(idx))
    return done


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1, help="1-based question index")
    parser.add_argument("--timeout", type=int, default=420)
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright

    existing = _load_existing()
    done = _done_indices(existing)
    results_by_idx: dict[int, dict] = {}
    for item in existing.get("results", []):
        idx = item.get("question_index")
        if idx:
            results_by_idx[int(idx)] = item

    if not PROFILE.exists():
        print(f"Browser profile missing: {PROFILE}", file=sys.stderr)
        print("Run: python -m notebooklm.notebooklm_cli login", file=sys.stderr)
        return 2

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(PROFILE), headless=True, channel="chrome"
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(NOTEBOOK_URL, wait_until="domcontentloaded", timeout=120_000)
        page.wait_for_timeout(6000)
        nb_id = (re.search(r"/notebook/([a-f0-9-]+)", NOTEBOOK_URL, re.I) or [None, None])[1]
        title = page.evaluate(
            """() => {
            const t = document.querySelector('.notebook-title, [class*="notebook-title"], h1');
            return (t?.textContent || document.title || '').trim();
          }"""
        ) or "SkillDAG"

        for i in range(args.start, len(GRILL_QUESTIONS) + 1):
            if i in done:
                print(f"[{i}/14] skip", file=sys.stderr)
                continue
            q = GRILL_QUESTIONS[i - 1]
            print(f"[{i}/14] {q[:70]}...", file=sys.stderr)
            r = _ask(page, q, timeout_sec=args.timeout)
            results_by_idx[i] = {"question_index": i, "question": q, "result": r}
            ordered = [results_by_idx[k] for k in sorted(results_by_idx)]
            ok = sum(1 for x in ordered if x.get("result", {}).get("success"))
            payload = {
                "notebook_id": nb_id,
                "notebook_title": title,
                "notebook_url": NOTEBOOK_URL,
                "exported_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "extraction_status": "complete" if ok == 14 else "partial",
                "extraction_notes": [
                    f"Playwright grill via notebooklm_skilldag_grill_playwright.py; {ok}/14 successful.",
                ],
                "results": ordered,
            }
            OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
            OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"[{i}/14] success={r.get('success')}", file=sys.stderr)
            if not r.get("success"):
                ctx.close()
                return 1
            time.sleep(2)

        ctx.close()

    print(OUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
