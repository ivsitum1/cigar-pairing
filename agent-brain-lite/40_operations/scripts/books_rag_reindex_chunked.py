#!/usr/bin/env python3
"""Emit parent-child chunk manifest for books_rag reindex (P1)."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

from brain_assist.chunk_policy import split_markdown_sections  # noqa: E402

WORKSPACE = Path(__file__).resolve().parents[2]
BOOKS_MD = WORKSPACE / "20_knowledge" / "wiki" / "sources" / "books_md"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build chunked manifest for books_md corpus")
    parser.add_argument("--limit", type=int, default=0, help="Max files (0=all)")
    parser.add_argument(
        "--output",
        type=Path,
        default=WORKSPACE / "outputs" / "rag_chunks" / "books_chunk_manifest.jsonl",
    )
    parser.add_argument("--doc-version", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    args = parser.parse_args()

    paths = sorted(BOOKS_MD.rglob("*.md"))
    if args.limit:
        paths = paths[: args.limit]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with args.output.open("w", encoding="utf-8") as out:
        for p in paths:
            try:
                body = p.read_text(encoding="utf-8")
            except OSError:
                continue
            title = str(p.relative_to(BOOKS_MD).with_suffix("")).replace("\\", "/")
            for rec in split_markdown_sections(
                body,
                doc_title=title,
                doc_version=args.doc_version,
                source_type="book",
            ):
                out.write(json.dumps(rec.to_dict(), ensure_ascii=False) + "\n")
                count += 1

    print(json.dumps({"chunks": count, "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
