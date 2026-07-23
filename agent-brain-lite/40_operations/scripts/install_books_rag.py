#!/usr/bin/env python3
"""One-shot install: pip deps + full books RAG index + verification."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("BOOKS_RAG_ENABLED", "1")
if sys.platform == "win32":
    os.environ.setdefault("BOOKS_RAG_DATA_DIR", r"C:\books_rag")


def _run(cmd: list[str], *, cwd: Path) -> None:
    print(">", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=str(cwd), check=True)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Install books RAG and build index.")
    parser.add_argument(
        "--with-ocr",
        action="store_true",
        help="Run install_paddle_ocr.py before indexing (scanned PDF support)",
    )
    args = parser.parse_args()

    root = WORKSPACE
    req = root / "requirements.txt"
    build = root / "40_operations" / "scripts" / "build_books_rag_index.py"
    from books_rag.config import load_config

    cfg = load_config(root)
    status_out = cfg.data_dir / "install_status.json"
    install_ocr = root / "40_operations" / "scripts" / "install_paddle_ocr.py"

    if args.with_ocr:
        print("=== 0/4 PaddleOCR (optional stack) ===", flush=True)
        _run([sys.executable, str(install_ocr), "--skip-bootstrap"], cwd=root)

    print("=== 1/3 pip install ===", flush=True)
    _run([sys.executable, "-m", "pip", "install", "-r", str(req)], cwd=root)

    import importlib

    for mod in ("chromadb", "sentence_transformers", "fastmcp"):
        importlib.import_module(mod)

    print("=== 2/3 build index (--force, micro-chunk pipeline) ===", flush=True)
    _run([sys.executable, str(build), "--root", str(root), "--force"], cwd=root)

    print("=== 3/3 verify ===", flush=True)
    from books_rag.retrieval import BooksRetriever

    retriever = BooksRetriever(cfg)
    status = retriever.status()
    sample = retriever.search("regional anesthesia", k=2)
    status_out.parent.mkdir(parents=True, exist_ok=True)
    status_out.write_text(
        json.dumps(
            {
                "status": status,
                "sample_hits": len(sample.get("items") or []),
                "ready": status.get("ready"),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(json.dumps(status, indent=2, ensure_ascii=False))
    if not status.get("ready"):
        print("WARNING: index not ready after build.", file=sys.stderr)
        return 1
    print(f"OK — {status.get('chunk_count')} chunks. Status: {status_out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
