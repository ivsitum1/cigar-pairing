#!/usr/bin/env python3
"""Grill NotebookLM via Playwright (notebooklm-py browser profile)."""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
PROFILE = Path.home() / ".notebooklm" / "profiles" / "default" / "browser_profile"
OUT_DIR = WORKSPACE / "outputs" / "notebooklm"

GRILL_QUESTIONS = [
    "List every source in this notebook. For each YouTube source give: exact title, URL if present, and a one-line topic label.",
    "For each YouTube video, extract 5-8 main claims as bullets. After each claim add a short quote from the transcript and tag FACT, OPINION, DEMO, or BENCHMARK.",
    "Across all sources, describe the full RAG pipeline stages mentioned: ingest, chunking, embedding, indexing, retrieval, reranking, fusion, and citation grounding. Separate operational steps from marketing language.",
    "What hybrid retrieval patterns are discussed (sparse+dense, graph RAG, multi-hop)? For each, what problem does it solve and what are the stated limitations?",
    "What token or context cost claims appear about RAG? List each number with the video/source it came from.",
    "How do sources define runtime harness vs the language model core? Map to environment contract, procedural skill, action realization, trajectory regulation if possible.",
    "What tool-contract or MCP failure modes and deterministic prescreen fixes are recommended?",
    "What is said about skills as operators (SkillRAE), self-evolving skills (SkillOpt), and edit budgets?",
    "What multi-agent debate, HITL, or deep-research calibration workflows are described?",
    "Where do sources disagree? What claims lack code, paper, or reproducible benchmarks?",
    "List the top 10 changes an agent-rules workspace should make, ranked P0 (rules/MCP/skills), P1 (scripts), P2 (research only). For each: target artifact, acceptance test, dependencies.",
    "Build a table of papers, GitHub repos, benchmarks cited: claim, source video title, external ref, reproducible Y/N.",
    "Summarize harness-specific recommendations that differ from generic prompt engineering.",
    "What wiki or knowledge-graph RAG patterns (wikilinks, orphans, multi-hop) are recommended for long-running agent memory?",
]

QUERY_INPUT = "textarea.query-box-input"
SUBMIT_BTN = "button.submit-button"
ANSWER_TEXT = ".to-user-container .message-text-content"


def _find_notebook_url(page, needle: str) -> str | None:
    page.goto("https://notebooklm.google.com/", wait_until="domcontentloaded", timeout=120_000)
    page.wait_for_timeout(5000)
    words = [w.lower() for w in needle.split() if w]
    cards = page.evaluate(
        """() => {
        const out = [];
        const seen = new Set();
        for (const a of document.querySelectorAll('a[href*="/notebook/"]')) {
          const href = a.href;
          const m = href.match(/\\/notebook\\/([a-f0-9-]+)/i);
          if (!m || seen.has(m[1])) continue;
          seen.add(m[1]);
          const card = a.closest('mat-card') || a.parentElement?.parentElement;
          const blob = ((card?.innerText || '') + ' ' + (a.textContent || '')).trim();
          const lines = blob.split('\\n').map(s => s.trim()).filter(Boolean);
          out.push({ title: lines[0] || '', blob: blob.toLowerCase(), href });
        }
        return out;
      }"""
    )
    for c in cards:
        blob = c.get("blob", "")
        if words and all(w in blob for w in words):
            return c["href"]
    if len(words) >= 2:
        for c in cards:
            blob = c.get("blob", "")
            if "rag" in blob and "anatomy" in blob:
                return c["href"]
    return None


def _count_answers(page) -> int:
    return page.locator(ANSWER_TEXT).count()


def _latest_answer(page) -> str:
    loc = page.locator(ANSWER_TEXT)
    if loc.count() == 0:
        return ""
    return (loc.nth(loc.count() - 1).inner_text() or "").strip()


def _ask(page, question: str, timeout_sec: int = 300) -> dict:
    before = _count_answers(page)
    box = page.locator(QUERY_INPUT).first
    box.wait_for(state="visible", timeout=60_000)
    box.click()
    box.fill(question)
    page.locator(SUBMIT_BTN).first.click()
    deadline = time.time() + timeout_sec
    stable_text = ""
    stable_hits = 0
    while time.time() < deadline:
        page.wait_for_timeout(2500)
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


def _load_questions(path: Path | None) -> list[str]:
    if path is None or not path.is_file():
        return GRILL_QUESTIONS
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [str(q) for q in data]
    if isinstance(data, dict) and "questions" in data:
        return [str(q) for q in data["questions"]]
    raise ValueError(f"Unsupported questions file format: {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--needle", default="RAG Anatomy")
    parser.add_argument("--notebook-url", help="Skip discovery")
    parser.add_argument("--output", default=str(OUT_DIR / "rag_anatomy_query_batch.json"))
    parser.add_argument("--start", type=int, default=0, help="Question index to start at")
    parser.add_argument(
        "--questions-file",
        help="JSON list of grill questions (overrides default RAG set)",
    )
    parser.add_argument(
        "--visible",
        action="store_true",
        help="Show browser window (for Google login)",
    )
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright

    q_path = Path(args.questions_file) if args.questions_file else None
    if q_path and not q_path.is_file():
        q_path = WORKSPACE / args.questions_file
    grill_questions = _load_questions(q_path)

    out = Path(args.output)
    existing: dict = {}
    if out.exists():
        existing = json.loads(out.read_text(encoding="utf-8"))

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(PROFILE), headless=not args.visible, channel="chrome"
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        url = args.notebook_url or existing.get("notebook_url") or _find_notebook_url(page, args.needle)
        if not url:
            print(f"No notebook matching: {args.needle}", file=sys.stderr)
            ctx.close()
            return 1

        page.goto(url, wait_until="domcontentloaded", timeout=120_000)
        page.wait_for_timeout(5000)
        box = page.locator(QUERY_INPUT).first
        if args.visible and box.count() == 0:
            print("If sign-in page appears, complete Google login in the browser window.", file=sys.stderr)
            for _ in range(6):
                page.wait_for_timeout(5000)
                if page.locator(QUERY_INPUT).count() > 0:
                    break
        nb_id = (re.search(r"/notebook/([a-f0-9-]+)", url, re.I) or [None, None])[1]
        title = page.evaluate(
            """() => {
            const t = document.querySelector('.notebook-title, [class*="notebook-title"], h1');
            return (t?.textContent || document.title || '').trim();
          }"""
        )

        results = list(existing.get("results") or [])
        if len(results) < len(grill_questions):
            results.extend([None] * (len(grill_questions) - len(results)))

        for i in range(args.start, len(grill_questions)):
            prior = results[i] if i < len(results) else None
            if prior and (prior.get("result") or {}).get("success"):
                continue
            q = grill_questions[i]
            print(f"[{i+1}/{len(grill_questions)}] {q[:70]}...", file=sys.stderr)
            r = _ask(page, q)
            results[i] = {"question": q, "result": r}
            payload = {
                "notebook_title": title,
                "notebook_url": url,
                "notebook_id": nb_id,
                "exported_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "results": results,
            }
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            time.sleep(2)

        ctx.close()

    meta = {
        "notebook_id": nb_id,
        "title": title,
        "url": url,
        "needle": args.needle,
        "grill_questions": len(grill_questions),
    }
    meta_path = out.with_name(out.stem.replace("_query_batch", "_notebook_meta") + ".json")
    if "_query_batch" not in out.stem:
        meta_path = OUT_DIR / "rag_anatomy_notebook_meta.json"
    meta_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
