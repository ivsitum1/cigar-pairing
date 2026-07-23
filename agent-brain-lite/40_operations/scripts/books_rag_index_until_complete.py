#!/usr/bin/env python3
"""Run books RAG index batches until all books_md files are indexed."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE))

from books_rag.config import load_config
from books_rag.index_builder import build_index


def _progress(root: Path) -> dict:
    path = load_config(root).progress_path
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Loop build_books_rag_index batches until done.")
    parser.add_argument("--root", default=".", help="Workspace root")
    parser.add_argument("--max-files", type=int, default=50, help="Files per batch")
    parser.add_argument("--sleep", type=int, default=5, help="Seconds between batches")
    parser.add_argument("--max-batches", type=int, default=0, help="Stop after N batches (0=all)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    build_script = root / "40_operations" / "scripts" / "build_books_rag_index.py"
    batches = 0

    while True:
        prog = _progress(root)
        done = int(prog.get("files_done", 0))
        total = int(prog.get("files_total", 0))
        if total > 0 and done >= total:
            print(f"Index complete: {done}/{total} files")
            return 0

        batches += 1
        if args.max_batches and batches > args.max_batches:
            print(f"Stopped after {args.max_batches} batch(es); {done}/{total} files")
            return 0

        print(f"Batch {batches}: {done}/{total or '?'} files indexed so far")
        rc = subprocess.call(
            [
                sys.executable,
                str(build_script),
                "--root",
                str(root),
                "--max-files",
                str(args.max_files),
            ],
        )
        if rc == 2:
            print("Build lock held by another process; retry later.", file=sys.stderr)
            return 2
        if rc != 0:
            print(f"Build failed with exit code {rc}", file=sys.stderr)
            return rc
        time.sleep(max(0, args.sleep))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
