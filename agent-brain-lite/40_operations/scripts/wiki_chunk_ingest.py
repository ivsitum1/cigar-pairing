#!/usr/bin/env python3
"""Layout-aware wiki chunk ingest using chunk_policy (heading splits + parent-child)."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

from brain_assist.chunk_policy import orphan_chunks, split_markdown_sections  # noqa: E402

WORKSPACE = Path(__file__).resolve().parents[2]
WIKI_ROOT = WORKSPACE / "20_knowledge" / "wiki"
OUT_DIR = WORKSPACE / "outputs" / "rag_chunks"


def ingest_file(
    path: Path,
    *,
    doc_version: str,
    source_type: str = "wiki",
) -> list[dict]:
    rel = path.relative_to(WIKI_ROOT)
    doc_title = str(rel.with_suffix("")).replace("\\", "/")
    body = path.read_text(encoding="utf-8")
    records = split_markdown_sections(
        body,
        doc_title=doc_title,
        doc_version=doc_version,
        source_type=source_type,
    )
    return [r.to_dict() for r in records]


def main() -> int:
    parser = argparse.ArgumentParser(description="Wiki heading-based chunk ingest")
    parser.add_argument("--path", type=Path, help="Single .md file under wiki/")
    parser.add_argument("--all", action="store_true", help="Process all wiki .md files")
    parser.add_argument("--doc-version", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    parser.add_argument("--output", type=Path, default=OUT_DIR / "wiki_chunks.jsonl")
    args = parser.parse_args()

    paths: list[Path] = []
    if args.path:
        paths = [args.path.resolve()]
    elif args.all:
        paths = sorted(WIKI_ROOT.rglob("*.md"))
    else:
        parser.error("Specify --path or --all")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    orphans = 0
    with args.output.open("w", encoding="utf-8") as out:
        for p in paths:
            if not p.is_file():
                continue
            try:
                chunks = ingest_file(p, doc_version=args.doc_version)
            except (OSError, ValueError) as exc:
                print(f"skip {p}: {exc}", file=sys.stderr)
                continue
            from brain_assist.chunk_policy import split_markdown_sections as _sms

            rec_objs = _sms(
                p.read_text(encoding="utf-8"),
                doc_title=str(p.relative_to(WIKI_ROOT).with_suffix("")).replace("\\", "/"),
                doc_version=args.doc_version,
                source_type="wiki",
            )
            orphans += len(orphan_chunks(rec_objs))
            for c in chunks:
                out.write(json.dumps(c, ensure_ascii=False) + "\n")
                total += 1

    print(json.dumps({"chunks_written": total, "orphan_children": orphans, "output": str(args.output)}))
    return 0 if orphans == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
