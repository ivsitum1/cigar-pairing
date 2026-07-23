#!/usr/bin/env python3
"""Merge live harness v2 grill: keep only long live answers; match archive by question."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
LIVE = WORKSPACE / "outputs/notebooklm/harness_v2_query_batch.json"
ARCHIVE = WORKSPACE / "outputs/notebooklm/_archive/pre_refresh_2026-06-30/harness_skilltree_query_batch.json"
INLINE = [
    (
        "List step-by-step operational workflows",
        "Memory (HORMA): trigger on session milestone; stop when summary node written; artifacts: memory_hierarchy/, provenance pointers. "
        "Planning (HIP-If): trigger on sub-goal complete; stop after fold to solved_lemma; artifacts: solved_lemmas.jsonl. "
        "Tool loops: ReAct act-observe; stop on verifier pass or max iterations. Self-correction: failure_patterns_bridge → self_harness_propose with human gate every 3rd iteration.",
    ),
    (
        "List boundaries and anti-patterns",
        "Reject self-evolving harness without human gate (AI bubble). Reject flat skill libraries without business context. "
        "Replace save-all RAG with information folding. Do not use LLM-as-judge alone; require environment feedback.",
    ),
    (
        "integrate with MCP tools",
        "MCP as execution substrate; SKILL_*.md as scaffold; hooks for failure signatures; wiki/graph for symbolic navigation. "
        "Artifacts: intent.md, memory_hierarchy/, failure_patterns, solved_lemmas.jsonl, reward_decay in skill_rerank eval.",
    ),
    (
        "metrics, eval protocols",
        "Self-Harness: TerminalBench pass rate + regression gate. HORMA: token vs baseline (~22%). HIPIF: sub-goal reflection + fold success. "
        "Skill tree: routing accuracy via skill_rerank --dag.",
    ),
    (
        "experimental vs production-ready",
        "Production: scaffold/harness terms, fold-lemma, failure_patterns bridge, NotebookLM gate. "
        "Experimental: full self-harness auto-edit, K1 pipeline, Socratic PO runtime defaults.",
    ),
    (
        "Cross-check this notebook",
        "Self-Harness → LifeHarness L3-L4 partial. HORMA/HIPIF extend context_sync. Skill tree complements SkillDAG. K1 vs books_rag gap. Reject autonomous rule rewrite.",
    ),
    (
        "Prioritize P0 P1 P2",
        "P0: UBIQUITOUS_LANGUAGE, fold-lemma, failure_patterns. P1: memory_hierarchy, cluster intents. P2: gated self_harness_propose, K1 clinical spike.",
    ),
    (
        "List risks",
        "Token budget: tiered context + fold-lemma. Hallucination: NotebookLM gate + research-lookup. Ethics: no detection evasion in MS. "
        "AI bubble: human gate on self-harness. Autonomous rewrite: REJECT for production rules.",
    ),
    (
        "MVP vs full rollout",
        "MVP: wiki concepts + UBIQUITOUS_LANGUAGE + fold-lemma. Full: memory_hierarchy sync, self_harness eval loop, K1 sample eval on 3 clinical PDFs.",
    ),
    (
        "open questions",
        "Human gate frequency (resolved: every 3rd). K1 PHI deployment. Reward decay tuning in verifier eval only.",
    ),
    (
        "Final delta table",
        "Self-Harness: partial, gated eval. HORMA: partial, memory_hierarchy wired. HIPIF: partial, fold-lemma. K1: spike with verified paper. Reject: auto rule rewrite, 500-skill import.",
    ),
]

MIN_LIVE_LEN = 2000


def _arch_map(arch_turns: list[dict]) -> dict[str, str]:
    return {t["question"]: t.get("answer", "") for t in arch_turns if t.get("question")}


def _inline_answer(question: str) -> str | None:
    qlow = question.lower()
    for prefix, ans in INLINE:
        if prefix.lower() in qlow:
            return ans
    return None


def main() -> None:
    live = json.loads(LIVE.read_text(encoding="utf-8"))
    arch = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    arch_by_q = _arch_map(arch["chat_turns"])
    merged = []
    stats = {"live": 0, "archive": 0, "inline": 0, "missing": 0}
    for item in live["results"]:
        q = item["question"]
        r = item.get("result") or {}
        ans = r.get("answer", "")
        if r.get("success") and len(ans) >= MIN_LIVE_LEN:
            merged.append({"question": q, "result": {"success": True, "answer": ans}, "provenance": "live_notebooklm"})
            stats["live"] += 1
        elif q in arch_by_q and len(arch_by_q[q]) > 100:
            merged.append(
                {"question": q, "result": {"success": True, "answer": arch_by_q[q]}, "provenance": "v1_archive_exact"}
            )
            stats["archive"] += 1
        elif (inline := _inline_answer(q)):
            merged.append({"question": q, "result": {"success": True, "answer": inline}, "provenance": "inline_fallback"})
            stats["inline"] += 1
        else:
            merged.append({"question": q, "result": r, "provenance": "missing"})
            stats["missing"] += 1
    out = {
        "notebook_title": "Harness Memory v2",
        "notebook_url": live["notebook_url"],
        "notebook_id": live["notebook_id"],
        "exported_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "merge_stats": stats,
        "results": merged,
    }
    LIVE.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(stats)


if __name__ == "__main__":
    main()
