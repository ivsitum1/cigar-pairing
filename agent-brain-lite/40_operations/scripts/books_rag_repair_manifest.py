#!/usr/bin/env python3
"""Align C:\\books_rag\\manifest.json with live Chroma count."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE))

from books_rag.config import load_config
from books_rag.store import BooksVectorStore


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair books_rag manifest.json from Chroma.")
    parser.add_argument("--root", default=".", help="Workspace root")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    cfg = load_config(Path(args.root).resolve())
    store = BooksVectorStore(cfg.chroma_path, cfg.collection_name)
    live = store.count()

    manifest: dict = {}
    if cfg.manifest_path.exists():
        try:
            manifest = json.loads(cfg.manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            manifest = {}

    manifest["chunks_indexed"] = live
    manifest.setdefault("chunking_schema", "parent-child-v1")
    manifest["last_build_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["embedding_model"] = manifest.get("embedding_model") or cfg.embedding_model
    manifest["repaired_utc"] = datetime.now(timezone.utc).isoformat()

    cfg.manifest_path.parent.mkdir(parents=True, exist_ok=True)
    cfg.manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    out = {
        "ok": live > 0,
        "manifest_path": str(cfg.manifest_path),
        "chunks_indexed": live,
        "chunking_schema": manifest.get("chunking_schema"),
    }
    text = json.dumps(out, indent=2, ensure_ascii=False)
    print(text if args.json else f"Repaired manifest: {live} chunks -> {cfg.manifest_path}")
    return 0 if live > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
