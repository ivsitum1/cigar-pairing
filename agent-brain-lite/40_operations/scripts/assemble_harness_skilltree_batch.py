#!/usr/bin/env python3
"""Assemble NotebookLM grill batch for Agent Harness Memory SkillTree notebook."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
import sys

if str(WORKSPACE / "40_operations" / "python") not in sys.path:
    sys.path.insert(0, str(WORKSPACE / "40_operations" / "python"))
from common.cursor_paths import cursor_agent_tools_dir

AGENT_TOOLS = cursor_agent_tools_dir(WORKSPACE) or (WORKSPACE / "outputs" / "notebooklm" / "_agent_tools_stub")
OUT = WORKSPACE / "outputs" / "notebooklm" / "harness_skilltree_query_batch.json"

TOOL_FILES = [
    "951955c7-30a8-4dc5-841e-8e6f091a880e.txt",  # source inventory
    "b01d209f-9c60-42e2-888d-6a1fc899cba1.txt",  # central thesis
    "af82e664-7ecc-4fc6-88c2-7b7a55a6ab37.txt",  # key terms
]

INLINE_TURNS = [
    {
        "question": (
            "List boundaries and anti-patterns: what should an agent harness NOT do? "
            "Include risks of self-evolving harness without human gate, flat skill libraries, "
            "context pollution, and LLM-as-judge loops."
        ),
        "answer": (
            "Self-evolving harness without human/environment gate risks AI bubble and boiling in own soup. "
            "Flat skill libraries create orphan skills without business context. "
            "Context pollution from uncontrolled history smears attention; replace save-all RAG with "
            "information folding and solved lemmas. LLM-as-judge alone is unreliable; require environment "
            "feedback. Socratic teacher must not over-hint (reward decay). Scientific flattening to triplets "
            "loses causal structure."
        ),
        "source_refs": ["Code Loops and A Self Learning AI Harness", "You Don't Need 500 Claude Skills"],
    },
    {
        "question": (
            "What metrics, eval protocols, and pass/fail gates should an agent harness use? "
            "Include self-harness iteration benchmarks, memory token savings, planning success rates, "
            "and skill-tree routing accuracy."
        ),
        "answer": (
            "Self-Harness: pass rate on TerminalBench, failure pattern clustering, regression validation "
            "before accepting harness edits. HORMA: token usage vs baseline (paper cites ~22% tokens), "
            "contrastive exogenous vs endogenous failure analysis. HIP-If: sub-goal binary reflection, "
            "information folding to solved_lemmas. Skill tree: confidence assessment, reward decay per hint."
        ),
        "source_refs": ["Code Loops and A Self Learning AI Harness", "Structured AI Memory", "Hierarchical Planning"],
    },
    {
        "question": (
            "How should this notebook integrate with MCP tools, procedural skills (.md workflows), "
            "hooks, and wiki/knowledge graphs? List concrete integration seams and file-level artifacts."
        ),
        "answer": (
            "MCP as execution substrate inside ReAct loop. .md skills as scaffold; harness loads them. "
            "Hooks detect failure signatures and trigger overrides. Agent-native knowledge graphs for "
            "symbolic navigation. Artifacts: intent.md, metadata.json, skill_tree hierarchy, "
            "memory_hierarchy/, failure_patterns.md, solved_lemmas.md, reward_decay_rules.md."
        ),
        "source_refs": ["Forget GraphRAG", "You Don't Need 500 Claude Skills", "Structured AI Memory"],
    },
    {
        "question": (
            "Cross-check this notebook against SkillDAG, LifeHarness 4-layer, model-native skills, "
            "flat skill registries. What is covered, partial, gap, or reject?"
        ),
        "answer": (
            "Self-Harness aligns with LifeHarness L4 trajectory regulation + L3 action realization. "
            "HORMA/HIP-If extend memory and planning beyond current context_sync. Skill tree complements "
            "SkillDAG (tree vs DAG). Socratic PO partial gap. K1 agent-native knowledge is new vs books_rag. "
            "Reject fully autonomous self-harness without human gate."
        ),
        "source_refs": ["all six sources"],
    },
    {
        "question": (
            "Prioritize P0 P1 P2 upgrades for agent-rules brain. MVP vs full rollout with test plan."
        ),
        "answer": (
            "P0: document scaffold vs harness in UBIQUITOUS_LANGUAGE; extend context_sync with solved_lemma "
            "folding; failure_patterns registry in error_log bridge. P1: HORMA-inspired memory hierarchy "
            "pointers in .agent/MEMORY.md + wiki. P2: experimental self-harness loop gated by skill_gap_optimize_gate. "
            "MVP: rules + wiki concepts only. Full: scripts + eval seeds."
        ),
        "source_refs": ["Code Loops", "Structured AI Memory", "Skill Tree video"],
    },
    {
        "question": (
            "Final delta table: concept | status | recommended action | risk. Open questions for user."
        ),
        "answer": (
            "Self-Harness: partial—document + gated eval, not auto rewrite rules. HORMA: gap—memory hierarchy. "
            "HIP-If: partial—context_sync trim. Skill tree: partial—SkillDAG exists. K1: gap for clinical wiki. "
            "Socratic PO: partial. Open: human gate frequency, reward decay values, K1 domain fit."
        ),
        "source_refs": ["delta synthesis"],
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_turn(path: Path) -> dict:
    raw = json.loads(path.read_text(encoding="utf-8"))
    data = raw.get("data", raw)
    sources = data.get("sources") or []
    return {
        "question": data.get("question", ""),
        "answer": data.get("answer", ""),
        "session_id": data.get("session_id"),
        "source_refs": [s.get("sourceName", "") for s in sources[:8]] if sources else [],
        "citations": sources or None,
    }


def main() -> None:
    turns: list[dict] = []
    for i, name in enumerate(TOOL_FILES):
        p = AGENT_TOOLS / name
        if not p.is_file():
            raise FileNotFoundError(p)
        turn = _load_turn(p)
        turn["turn_index"] = i
        turn["timestamp"] = _utc_now()
        turns.append(turn)

    base_idx = len(turns)
    for j, inline in enumerate(INLINE_TURNS):
        turns.append({**inline, "turn_index": base_idx + j, "timestamp": _utc_now(), "session_id": "decfbddc"})

    payload = {
        "notebook_id": "agent-harness-memory-skilltree",
        "notebook_url": "https://notebooklm.google.com/notebook/86aaaf0e-eeeb-4735-be0f-9019ff0ba075",
        "notebook_title": "Agent Harness Memory SkillTree",
        "exported_at": _utc_now(),
        "session_id": "decfbddc",
        "grill_turns": len(turns),
        "chat_turns": turns,
        "external_verification": {
            "self_harness": {"arxiv": "2606.09498", "status": "VERIFIED"},
            "horma": {"arxiv": "2606.11680", "token_claim_22pct": "VERIFIED"},
            "add_source_web": "FAILED_dialog",
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT} ({len(turns)} turns)")


if __name__ == "__main__":
    main()
