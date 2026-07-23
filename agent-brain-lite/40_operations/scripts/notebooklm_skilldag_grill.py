#!/usr/bin/env python3
"""Run SkillDAG grill batch via notebooklm-py CLI (14 questions)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
OUT_PATH = WORKSPACE / "outputs" / "notebooklm" / "skilldag_query_batch.json"
NOTEBOOK_ID = "48a6afa2-97d8-44f4-8a41-c87d2ea0b650"
NOTEBOOK_URL = f"https://notebooklm.google.com/notebook/{NOTEBOOK_ID}"

GRILL_QUESTIONS = [
    "List every source in this notebook. For each source give: exact title, URL if present, source type (YouTube, PDF, web, pasted text), and a one-line topic label.",
    "For each source, extract 5–8 main claims as bullets. After each claim add a short quote and tag FACT, OPINION, DEMO, or BENCHMARK.",
    "How do the sources define SkillDAG (or skill dependency graph)? What is a node, edge, cycle, and valid topological order? Give definitions used in the notebook.",
    "How does SkillDAG differ from a flat skill list, from SkillRAE subunit decomposition, and from MUSE/SkillOpt if mentioned?",
    "What routing rules are described: when must skill A load before skill B; which branches can run in parallel vs serial; how are conflicts resolved?",
    "What evaluation or gate nodes appear in a skill DAG (pass/fail, Swiss Cheese, research gate, human-in-the-loop)? Where must execution stop?",
    "Map SkillDAG concepts to harness layers if possible: environment contract, procedural skill, action realization, trajectory regulation (LifeHarness or equivalent).",
    "Are named pipeline sequences (e.g. grill-me → write-prd → prd-to-issues → ralph-loop) represented as DAGs in the sources? How should they be encoded?",
    "What token or context budget rules apply per DAG branch or per parallel fan-out? List each number with its source.",
    "Where do sources disagree? Which claims lack code, papers, or reproducible benchmarks?",
    "List the top 10 changes an agent-rules workspace should make, ranked P0 (rules/MCP/skills), P1 (scripts), P2 (research only). For each: target artifact, acceptance test, dependencies.",
    "Build a table of papers, GitHub repos, and benchmarks cited: claim, source title, external reference, reproducible Y/N.",
    "What recommendations are specific to Cursor, MCP, or file-based agent harnesses (not generic prompt engineering)?",
    "What wiki or knowledge-graph patterns (wikilinks, orphans, multi-hop, cross-linking) are recommended for skill or pipeline memory?",
]


def _default_storage() -> Path:
    profile = Path.home() / ".notebooklm" / "profiles" / "default" / "storage_state.json"
    legacy = Path.home() / ".notebooklm" / "storage_state.json"
    return profile if profile.exists() else legacy


def _run_ask(storage: Path, notebook_id: str, question: str, timeout: int) -> dict:
    cmd = [
        sys.executable,
        "-m",
        "notebooklm.notebooklm_cli",
        "--storage",
        str(storage),
        "use",
        notebook_id,
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)

    cmd = [
        sys.executable,
        "-m",
        "notebooklm.notebooklm_cli",
        "--storage",
        str(storage),
        "ask",
        question,
        "-n",
        notebook_id,
        "--json",
        "--timeout",
        str(timeout),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 30, check=False)
    if result.returncode != 0:
        return {
            "success": False,
            "error": result.stderr.strip() or result.stdout.strip() or "ask failed",
            "answer": "",
        }
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        text = result.stdout.strip()
        if text:
            return {"success": True, "answer": text, "note": "non_json_stdout"}
        return {"success": False, "error": "non-JSON empty stdout", "answer": ""}

    answer = payload.get("answer", payload.get("response", payload.get("text", "")))
    if isinstance(answer, dict):
        answer = answer.get("text", str(answer))
    if not answer and isinstance(payload, dict):
        answer = json.dumps(payload, ensure_ascii=False)
    return {
        "success": bool(answer),
        "answer": str(answer),
        "session_id": payload.get("conversation_id", payload.get("session_id")),
        "raw_keys": list(payload.keys()) if isinstance(payload, dict) else None,
    }


def _load_existing() -> dict:
    if not OUT_PATH.exists():
        return {}
    return json.loads(OUT_PATH.read_text(encoding="utf-8"))


def _index_done(existing: dict) -> set[int]:
    done: set[int] = set()
    for item in existing.get("results", []):
        idx = item.get("question_index")
        if idx is None:
            continue
        if item.get("result", {}).get("success"):
            done.add(int(idx))
    return done


def _save(payload: dict) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--storage", default=str(_default_storage()))
    parser.add_argument("--start", type=int, default=1, help="1-based question index")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--sleep", type=int, default=3, help="Seconds between questions")
    args = parser.parse_args()

    storage = Path(args.storage).expanduser()
    existing = _load_existing()
    done = _index_done(existing)
    results_by_idx: dict[int, dict] = {}
    for item in existing.get("results", []):
        idx = item.get("question_index")
        if idx is not None:
            results_by_idx[int(idx)] = item

    for i in range(args.start, len(GRILL_QUESTIONS) + 1):
        if i in done:
            print(f"[{i}/14] skip (already success)", file=sys.stderr)
            continue
        q = GRILL_QUESTIONS[i - 1]
        print(f"[{i}/14] asking: {q[:72]}...", file=sys.stderr)
        r = _run_ask(storage, NOTEBOOK_ID, q, args.timeout)
        results_by_idx[i] = {
            "question_index": i,
            "question": q,
            "result": r,
        }
        ordered = [results_by_idx[k] for k in sorted(results_by_idx)]
        success_count = sum(1 for x in ordered if x.get("result", {}).get("success"))
        payload = {
            "notebook_id": NOTEBOOK_ID,
            "notebook_title": existing.get("notebook_title", "SkillDAG"),
            "notebook_url": NOTEBOOK_URL,
            "exported_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "extraction_status": "complete" if success_count == 14 else "partial",
            "extraction_notes": [
                f"CLI grill via notebooklm_skilldag_grill.py; {success_count}/14 successful.",
            ],
            "results": ordered,
        }
        _save(payload)
        print(f"[{i}/14] success={r.get('success')}", file=sys.stderr)
        if not r.get("success"):
            print(f"ERROR: {r.get('error', 'unknown')}", file=sys.stderr)
            return 1
        time.sleep(args.sleep)

    print(str(OUT_PATH))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
