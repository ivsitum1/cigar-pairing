#!/usr/bin/env python3
"""Build or update the books_md vector index for books RAG."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

WORKSPACE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE))

from books_rag.config import load_config
from books_rag.index_builder import build_index


def main() -> int:
    parser = argparse.ArgumentParser(description="Build books RAG index from books_md corpus.")
    parser.add_argument("--root", default=".", help="Workspace root")
    parser.add_argument("--force", action="store_true", help="Rebuild entire index from scratch")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without embedding")
    parser.add_argument("--limit", type=int, default=None, help="Process only first N MD files (smoke test)")
    parser.add_argument(
        "--max-files",
        type=int,
        default=None,
        help="Stop after indexing at most N new/changed files (batch runs)",
    )
    parser.add_argument(
        "--embed-buffer",
        type=int,
        default=None,
        help="Flush embed buffer after this many chunks (default from config, usually 12)",
    )
    parser.add_argument("--no-lock", action="store_true", help="Do not acquire build lock file")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    cfg = load_config(root)
    print(f"books_md: {cfg.books_md_dir}")
    print(f"chroma:   {cfg.chroma_path}")
    print(f"model:    {cfg.embedding_model}")
    print(f"chunk:    {cfg.chunk_size_chars} chars, buffer={args.embed_buffer or cfg.embed_buffer_size}")

    try:
        stats = build_index(
            cfg,
            force=args.force,
            dry_run=args.dry_run,
            limit_files=args.limit,
            max_files=args.max_files,
            embed_buffer_size=args.embed_buffer,
            use_lock=not args.no_lock,
        )
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 2

    print(json.dumps(stats, indent=2))
    if stats.get("error"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
