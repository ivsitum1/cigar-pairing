#!/usr/bin/env python3
"""Source expansion recommendations for NotebookLM batch 2026-06."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
OUT_DIR = WORKSPACE / "outputs" / "notebooklm"
CFG = WORKSPACE / "30_system/docs/reference/notebooklm_batch_2026-06_questions.json"

EXPAND_PROMPT = (
    "List every source currently in this notebook (title, URL, type). "
    "For each YouTube source, find the primary paper, official GitHub repo, "
    "and 2-3 independent references. Propose 3-8 additional sources to add "
    "(arxiv, official docs, README). Do not invent URLs — only cite URLs present "
    "in sources or clearly named official sites."
)


def _run_cli(args: list[str], timeout: int = 300, retries: int = 3) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-m", "notebooklm.notebooklm_cli", *args]
    last: subprocess.CompletedProcess[str] | None = None
    for attempt in range(retries):
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=WORKSPACE,
                encoding="utf-8",
                errors="replace",
            )
            last = result
            err = (result.stderr or "") + (result.stdout or "")
            if result.returncode == 0:
                return result
            if "TransportServerError" in err or result.returncode == 2:
                time.sleep(15 * (attempt + 1))
                continue
            return result
        except subprocess.TimeoutExpired:
            if attempt == retries - 1:
                raise
            time.sleep(15 * (attempt + 1))
    assert last is not None
    return last


def _ask_notebook(nb_id: str, question: str) -> dict:
    _run_cli(["use", nb_id])
    result = _run_cli(["ask", "--json", "--yes", "--timeout", "180", "--new", question], timeout=240)
    if result.returncode != 0:
        return {"success": False, "answer": result.stderr or result.stdout, "error": f"cli_exit_{result.returncode}"}
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"success": False, "answer": result.stdout, "error": "non_json"}
    return {
        "success": bool(data.get("answer")),
        "answer": data.get("answer", ""),
        "conversation_id": data.get("conversation_id"),
        "references": data.get("references"),
    }

RECOMMENDED = {
    "okf-knowledge": [
        {"type": "research", "query": "Google Open Knowledge Format OKF schema"},
        {"type": "web", "hint": "Crabbox GitHub sandbox agents"},
        {"type": "paper", "query": "Lost in the Middle long context RAG"},
        {"type": "research", "query": "Open Sinker Agent data cleaning LLM"},
    ],
    "last-mile-glm": [
        {"type": "web", "hint": "GLM-5 Zhipu documentation"},
        {"type": "paper", "query": "JEPA LeCun world models"},
        {"type": "research", "query": "open weight LLM integration enterprise"},
    ],
    "humanize-predictability": [
        {"type": "research", "query": "perplexity burstiness AI text detection"},
        {"type": "paper", "query": "statistical detection machine generated text"},
    ],
    "loop-of-loops": [
        {"type": "paper", "query": "Stanford STORM multi-agent research"},
        {"type": "web", "hint": "STORM GitHub stanford"},
        {"type": "research", "query": "Ralph Wiggum agent loop engineering"},
    ],
}


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slugs(all_flag: bool, slug: str | None) -> list[str]:
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    keys = list(cfg.get("notebooks", {}).keys())
    if all_flag:
        return keys
    if slug:
        return [slug]
    return keys


def _try_cli_add_research(nb_id: str, query: str) -> dict:
    _run_cli(["use", nb_id])
    result = _run_cli(["source", "add-research", query, "--json"], timeout=120)
    return {
        "query": query,
        "returncode": result.returncode,
        "stdout": (result.stdout or "")[:2000],
        "stderr": (result.stderr or "")[:500],
    }


def expand_slug(slug: str, execute: bool, ask: bool) -> Path:
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    nb_id = cfg["notebooks"][slug]["id"]
    batch = OUT_DIR / f"{slug}_query_batch.json"
    grill_answer = ""
    if batch.is_file():
        data = json.loads(batch.read_text(encoding="utf-8"))
        for r in data.get("results") or []:
            if r and "source" in (r.get("question") or "").lower():
                grill_answer = ((r.get("result") or {}).get("answer") or "")[:8000]
                break
    payload = {
        "slug": slug,
        "notebook_id": nb_id,
        "exported_at": _utc(),
        "expand_prompt": EXPAND_PROMPT,
        "recommended_searches": RECOMMENDED.get(slug, []),
        "grill_source_inventory_excerpt": grill_answer,
        "cli_add_research_results": [],
        "notebooklm_expand_ask": None,
    }
    if ask:
        try:
            payload["notebooklm_expand_ask"] = _ask_notebook(nb_id, EXPAND_PROMPT)
        except subprocess.TimeoutExpired as exc:
            payload["notebooklm_expand_ask"] = {"success": False, "error": "timeout", "answer": str(exc)}
    if execute:
        for item in RECOMMENDED.get(slug, []):
            q = item.get("query") or item.get("hint", "")
            if q:
                payload["cli_add_research_results"].append(_try_cli_add_research(nb_id, q))
    out = OUT_DIR / f"{slug}_source_expansion.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--execute", action="store_true", help="Run notebooklm source add-research (best effort)")
    parser.add_argument("--ask", action="store_true", help="Ask NotebookLM expand prompt using full notebook context")
    args = parser.parse_args()
    for slug in _slugs(args.all, args.slug):
        expand_slug(slug, args.execute, args.ask)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
