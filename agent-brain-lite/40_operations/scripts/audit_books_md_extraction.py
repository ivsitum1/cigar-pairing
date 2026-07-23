#!/usr/bin/env python3
"""Inventory PDFs vs books_md extraction quality (content_note, missing sources, failures)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE))
sys.path.insert(0, str(WORKSPACE / "40_operations" / "scripts"))

from pdf_library_context import infer_library_context, stem_slug_for_pdf  # noqa: E402

SKIP_PARTS = {".git", ".claude", "node_modules", "agent-transcripts", "__pycache__", ".venv", "venv"}
SOURCE_PDF_RE = re.compile(r"^source_pdf:\s*(.+)$", re.MULTILINE)
CONTENT_NOTE_RE = re.compile(r"^content_note:\s*(.+)$", re.MULTILINE)


def _find_pdfs(root: Path) -> list[Path]:
    prefixes = (
        root / "20_knowledge" / "reference_library",
        root / "00_inbox" / "raw",
    )
    out: list[Path] = []
    for prefix in prefixes:
        if not prefix.is_dir():
            continue
        for p in prefix.rglob("*.pdf"):
            if p.is_file() and not any(part in SKIP_PARTS for part in p.parts):
                out.append(p)
    return sorted(out)


def _scan_books_md(books_md: Path) -> dict:
    content_notes: Counter[str] = Counter()
    failed: list[str] = []
    source_pdfs: set[str] = set()
    md_without_pdf: list[str] = []

    for md in books_md.rglob("*.md"):
        if md.name == "INDEX.md":
            continue
        try:
            raw = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "extraction_failed: true" in raw or md.name.endswith("_EXTRACTION_FAILED.md"):
            failed.append(md.relative_to(books_md).as_posix())
            continue
        m = CONTENT_NOTE_RE.search(raw)
        note = m.group(1).strip() if m else "(none)"
        content_notes[note] += 1
        sp = SOURCE_PDF_RE.search(raw)
        if sp:
            source_pdfs.add(sp.group(1).strip())

    return {
        "content_notes": dict(content_notes),
        "extraction_failed_count": len(failed),
        "extraction_failed_samples": failed[:20],
        "unique_source_pdfs_in_md": len(source_pdfs),
        "source_pdfs": source_pdfs,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit books_md vs local PDFs.")
    parser.add_argument("--root", default=".", help="Workspace root")
    parser.add_argument(
        "--output",
        default="",
        help="Write JSON report (default: data/pdf_extract/inventory.json)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    books_md = root / "20_knowledge" / "wiki" / "sources" / "books_md"
    out_path = Path(args.output) if args.output else root / "data" / "pdf_extract" / "inventory.json"

    pdfs = _find_pdfs(root)
    pdf_rels = {p.relative_to(root).as_posix() for p in pdfs}

    md_scan = _scan_books_md(books_md) if books_md.is_dir() else {}
    source_pdfs = md_scan.get("source_pdfs") or set()
    missing_pdf = sorted(sp for sp in source_pdfs if not (root / sp).is_file())
    pdfs_without_md: list[str] = []
    for p in pdfs:
        rel = p.relative_to(root).as_posix()
        slug = stem_slug_for_pdf(p.stem, rel)
        _, _, books_sub = infer_library_context(rel)
        subdir = books_md / books_sub
        if not subdir.is_dir() or not list(subdir.glob(f"{slug}*.md")):
            pdfs_without_md.append(rel)

    report = {
        "pdf_count_local": len(pdfs),
        "books_md_files": sum(1 for _ in books_md.rglob("*.md") if _.name != "INDEX.md")
        if books_md.is_dir()
        else 0,
        "content_notes": md_scan.get("content_notes", {}),
        "extraction_failed_count": md_scan.get("extraction_failed_count", 0),
        "extraction_failed_samples": md_scan.get("extraction_failed_samples", []),
        "unique_source_pdfs_in_md": md_scan.get("unique_source_pdfs_in_md", 0),
        "source_pdf_missing_on_disk_count": len(missing_pdf),
        "source_pdf_missing_on_disk_samples": missing_pdf[:30],
        "local_pdf_without_books_md_count": len(pdfs_without_md),
        "local_pdf_without_books_md_samples": pdfs_without_md[:30],
        "local_pdf_paths_sample": [p.relative_to(root).as_posix() for p in pdfs[:15]],
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nWrote {out_path.relative_to(root).as_posix()}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
