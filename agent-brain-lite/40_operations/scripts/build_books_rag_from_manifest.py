#!/usr/bin/env python3
"""Build books RAG index from hierarchical chunk manifest (parent-child metadata)."""
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
from books_rag.manifest_index import build_from_manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Index books_chunk_manifest.jsonl into Chroma with parent-child metadata."
    )
    parser.add_argument("--root", default=".", help="Workspace root")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=WORKSPACE / "outputs" / "rag_chunks" / "books_chunk_manifest.jsonl",
        help="JSONL manifest from books_rag_reindex_chunked.py",
    )
    parser.add_argument("--force", action="store_true", help="Reset Chroma and rebuild")
    parser.add_argument("--dry-run", action="store_true", help="Count chunks only")
    parser.add_argument("--limit", type=int, default=None, help="Max manifest lines (smoke)")
    parser.add_argument("--no-resume", action="store_true", help="Start from line 0 unless --force")
    parser.add_argument("--no-lock", action="store_true", help="Skip build lock")
    parser.add_argument(
        "--embed-buffer",
        type=int,
        default=None,
        help="Flush embed buffer after N chunks (default from config)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    cfg = load_config(root)
    manifest = args.manifest if args.manifest.is_absolute() else (root / args.manifest)

    print(f"manifest: {manifest}")
    print(f"chroma:   {cfg.chroma_path}")
    print(f"model:    {cfg.embedding_model}")
    print(f"device:   {cfg.compute_device}")

    try:
        stats = build_from_manifest(
            cfg,
            manifest,
            force=args.force,
            dry_run=args.dry_run,
            limit=args.limit,
            resume=not args.no_resume,
            use_lock=not args.no_lock,
            embed_buffer_size=args.embed_buffer,
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(json.dumps(stats, indent=2, ensure_ascii=False))
    if stats.get("error"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
