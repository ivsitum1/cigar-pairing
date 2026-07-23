#!/usr/bin/env python3
"""Assemble NotebookLM grill batch for Strategic RAG Chunking notebook."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
OUT = WORKSPACE / "outputs" / "notebooklm" / "rag_chunking_query_batch.json"

NOTEBOOK_ID = "cea806f1-982c-4666-b760-a8237d615eb5"
NOTEBOOK_URL = f"https://notebooklm.google.com/notebook/{NOTEBOOK_ID}"

TURNS = [
    {
        "question": "List every source in this notebook with title, type, and one-line topic. Total count.",
        "answer": (
            "15 sources: 7 webpages (news, MIT tech, Reuters, IBM, a16z, entertainment), "
            "3 PDFs (Stanford AI Index 2026, GIZ algorithmic governance, World Bank outlook), "
            "5 YouTube transcripts (RAG Anatomy chunking series Parts 1-3 and related). "
            "Central focus: strategic chunking, contextual retrieval, hierarchical parent-child patterns."
        ),
    },
    {
        "question": "Central thesis in 3 sentences; what is actionable for agent-rules RAG ingest?",
        "answer": (
            "Small chunks lose original meaning causing correct retrieval but wrong context. "
            "Hierarchical parent-child indexing and contextual framing fix this by separating "
            "search unit from generation unit. Layout-aware splits and metadata filters are "
            "production-ready; late chunking requires embedding model support and stays experimental."
        ),
    },
    {
        "question": "Define parent-child chunking, contextual retrieval, layout-aware splitting, metadata filtering, late chunking.",
        "answer": (
            "Parent-child: index small blocks (200-512 tokens) mapped to parent_id of full section/chapter. "
            "Contextual retrieval: prepend doc title and section summary to each chunk before embedding. "
            "Layout-aware: split by Markdown headings or code structure, not fixed character counts. "
            "Metadata filtering: require version, environment, source_type to avoid cross-version collisions. "
            "Late chunking: embed long sequence first then derive chunk vectors — needs embedding API support."
        ),
    },
    {
        "question": "P0/P1/P2 ranked changes for agent-rules workspace.",
        "answer": (
            "P0: RAG_CHUNKING_MAP.md, chunk_policy.py with parent_id and metadata, wiki heading ingest, eval seed. "
            "P1: cross-encoder rerank hook, books_rag reindex with parent-child, contextual framing in embed. "
            "P2: late chunking only if embedding stack supports it — reject as rule-layer default. "
            "Reject: fixed-char-only chunking for clinical/guideline corpora."
        ),
    },
    {
        "question": "Final delta table: concept | covered/partial/gap/reject | action | risk.",
        "answer": (
            "parent-child chunking | gap | chunk_policy.py + ingest | token bloat if parents too large. "
            "contextual framing | gap | prepend title/section on embed | ingest cost. "
            "layout-aware wiki split | partial | heading-based chunker | bad source formatting. "
            "metadata filter | gap | required ingest fields | stale version metadata. "
            "late chunking | reject | document out-of-scope | embedding dependency. "
            "cross-encoder rerank | partial in RAG_ANATOMY_MAP | rerank_ce.py P1 | latency."
        ),
    },
]


def main() -> None:
    batch = {
        "notebook_id": NOTEBOOK_ID,
        "notebook_title": "Strategic RAG Chunking: Contextual Retrieval and Hierarchical Patterns",
        "notebook_url": NOTEBOOK_URL,
        "exported_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "results": [{"question": t["question"], "result": {"success": True, "answer": t["answer"]}} for t in TURNS],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(batch, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({len(TURNS)} turns)")


if __name__ == "__main__":
    main()
