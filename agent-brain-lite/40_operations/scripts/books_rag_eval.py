#!/usr/bin/env python3
"""Evaluate books RAG: dense-only vs rerank vs summary gateway on fixed queries."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE))

from books_rag.config import load_config
from books_rag.retrieval import BooksRetriever

DEFAULT_QUERIES = WORKSPACE / "books_rag" / "eval_queries.json"


def _run_variant(
    retriever: BooksRetriever,
    query: str,
    domain: str | None,
    *,
    variant: str,
) -> dict[str, Any]:
    try:
        if variant == "dense":
            result = retriever.search(
                query,
                k=5,
                domain=domain,
                use_rerank=False,
                use_hybrid=False,
            )
        elif variant == "rerank":
            result = retriever.search(
                query,
                k=5,
                domain=domain,
                use_rerank=True,
                use_hybrid=True,
            )
        elif variant == "summary":
            result = retriever.search_answer(query, k=5, domain=domain)
        else:
            raise ValueError(f"Unknown variant: {variant}")
    except Exception as exc:  # noqa: BLE001 — eval should continue on Chroma lock/errors
        return {
            "variant": variant,
            "ready": False,
            "error": str(exc),
        }

    items = result.get("items") or []
    top = items[0] if items else {}
    return {
        "variant": variant,
        "ready": result.get("ready", False),
        "top_score": top.get("score"),
        "top_chunk_id": top.get("chunk_id"),
        "top_title": (top.get("metadata") or {}).get("title"),
        "n_items": len(items),
        "answer_len": len(str(result.get("answer", ""))),
        "summary_source": result.get("summary_source"),
    }


def evaluate(
    queries_path: Path,
    *,
    variants: list[str],
    limit: int | None = None,
) -> dict[str, Any]:
    cfg = load_config()
    retriever = BooksRetriever(cfg)
    if not retriever.is_ready():
        return {
            "ready": False,
            "message": "Index not ready",
            "status": retriever.status(),
        }

    queries = json.loads(queries_path.read_text(encoding="utf-8"))
    if limit is not None:
        queries = queries[:limit]

    rows: list[dict[str, Any]] = []
    for row in queries:
        qid = row.get("id", "")
        query = row["query"]
        domain = (row.get("domain") or "").strip() or None
        entry: dict[str, Any] = {"id": qid, "query": query}
        for variant in variants:
            entry[variant] = _run_variant(retriever, query, domain, variant=variant)
        rows.append(entry)

    def _avg_score(variant: str) -> float | None:
        scores = [
            float(r[variant]["top_score"])
            for r in rows
            if r.get(variant, {}).get("top_score") is not None
        ]
        return round(sum(scores) / len(scores), 4) if scores else None

    errors = sum(
        1
        for r in rows
        for v in variants
        if r.get(v, {}).get("error")
    )
    summary = {
        "ready": True,
        "queries": len(rows),
        "variants": variants,
        "avg_top_score": {v: _avg_score(v) for v in variants},
        "index_percent": retriever.status().get("index_percent"),
        "variant_errors": errors,
        "note": (
            "Run eval while index build is idle to avoid Chroma lock errors."
            if errors
            else None
        ),
    }
    return {"summary": summary, "results": rows}


def main() -> int:
    parser = argparse.ArgumentParser(description="Books RAG eval on fixed queries.")
    parser.add_argument("--queries", default=str(DEFAULT_QUERIES), help="eval_queries.json")
    parser.add_argument(
        "--variants",
        default="dense,rerank,summary",
        help="Comma-separated: dense,rerank,summary",
    )
    parser.add_argument("--limit", type=int, default=None, help="Max queries to run")
    parser.add_argument(
        "--output",
        help="Write JSON report path (default: <BOOKS_RAG_DATA_DIR>/eval_report.json)",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    variants = [v.strip() for v in args.variants.split(",") if v.strip()]
    report = evaluate(Path(args.queries), variants=variants, limit=args.limit)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    out_path = Path(args.output) if args.output else load_config().data_dir / "eval_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    if args.json:
        print(text)
    else:
        print(out_path)
    return 0 if report.get("summary", {}).get("ready") else 1


if __name__ == "__main__":
    raise SystemExit(main())
