#!/usr/bin/env python3
"""Mark a stuck PDF as failed in progress.json so --resume skips it."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE))
sys.path.insert(0, str(WORKSPACE / "40_operations" / "scripts"))

from pdf_library_context import infer_library_context, stem_slug_for_pdf  # noqa: E402

SOURCE_PDF_RE = re.compile(r"^source_pdf:\s*(.+)$", re.MULTILINE)


def pdf_sha1(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_progress(path: Path) -> dict:
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"version": 1, "entries": {}}


def save_progress(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def source_pdf_from_md(md_path: Path) -> str | None:
    try:
        raw = md_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = SOURCE_PDF_RE.search(raw)
    return m.group(1).strip() if m else None


def find_pdfs(root: Path, only_prefix: str) -> list[Path]:
    prefixes = []
    if only_prefix.startswith("00_inbox"):
        prefixes.append(root / "00_inbox" / "raw")
    else:
        prefixes.append(root / "20_knowledge" / only_prefix)
    out: list[Path] = []
    for base in prefixes:
        if not base.is_dir():
            continue
        for p in base.rglob("*.pdf"):
            if p.is_file():
                out.append(p)
    return sorted(out)


def pick_stuck_pdf(root: Path, only_prefix: str, progress: dict) -> Path | None:
    entries = progress.get("entries", {})
    pending: list[Path] = []
    for pdf in find_pdfs(root, only_prefix):
        rel = pdf.relative_to(root).as_posix()
        ent = entries.get(rel)
        if ent and ent.get("content_note") == "paddleocr_ppstructurev3":
            continue
        if ent and ent.get("content_note") == "failed":
            continue
        pending.append(pdf)
    if not pending:
        return None
    return max(pending, key=lambda p: p.stat().st_size)


def write_failed_stub(
    root: Path,
    pdf: Path,
    rel_pdf: str,
    err: str,
) -> Path:
    domain, subgroup, books_sub = infer_library_context(rel_pdf)
    stem_slug = stem_slug_for_pdf(pdf.stem, rel_pdf)
    out_base = root / "20_knowledge" / "wiki" / "sources" / "books_md"
    subdir = out_base / books_sub
    subdir.mkdir(parents=True, exist_ok=True)
    stub = subdir / f"{stem_slug}_EXTRACTION_FAILED.md"
    ts = dt.datetime.now(dt.timezone.utc).isoformat()
    title = pdf.stem.replace('"', "'")
    stub.write_text(
        "\n".join(
            [
                "---",
                f'title: "{title}"',
                f"source_pdf: {rel_pdf}",
                f"domain: {domain}",
                f"subgroup: {subgroup}",
                "extraction_failed: true",
                f"extracted_utc: {ts[:10]}",
                f"content_note: failed",
                "skip_reason: watchdog_timeout",
                "---",
                "",
                f"# {pdf.stem}",
                "",
                f"Extraction error: `{err}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return stub


def mark_failed(root: Path, rel_pdf: str, reason: str, progress_path: Path) -> bool:
    pdf = root / rel_pdf
    if not pdf.is_file():
        print(f"PDF not found: {rel_pdf}", file=sys.stderr)
        return False
    progress = load_progress(progress_path)
    sha = pdf_sha1(pdf)
    _, _, books_sub = infer_library_context(rel_pdf)
    stem_slug = stem_slug_for_pdf(pdf.stem, rel_pdf)
    write_failed_stub(root, pdf, rel_pdf, reason)
    progress.setdefault("entries", {})[rel_pdf] = {
        "sha1": sha,
        "content_note": "failed",
        "stem_slug": stem_slug,
        "updated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "skip_reason": "watchdog_timeout",
    }
    save_progress(progress_path, progress)
    print(f"Marked failed: {rel_pdf}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Skip stuck PDF by marking failed in progress.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--only-prefix", default="")
    parser.add_argument("--from-newest-md", action="store_true", help="Use source_pdf from newest books_md")
    parser.add_argument("--reason", default="watchdog: no new .md within stale window")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    progress_path = root / "data" / "pdf_extract" / "progress.json"
    rel: str | None = None

    if args.from_newest_md:
        books = root / "20_knowledge" / "wiki" / "sources" / "books_md"
        mds = sorted(
            (p for p in books.rglob("*.md") if p.name != "INDEX.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if mds:
            rel = source_pdf_from_md(mds[0])
            if rel:
                print(f"From newest md: {mds[0].name} -> {rel}")

    if not rel and args.only_prefix:
        stuck = pick_stuck_pdf(root, args.only_prefix, load_progress(progress_path))
        if stuck:
            rel = stuck.relative_to(root).as_posix()
            print(f"Largest pending in prefix: {rel}")

    if not rel:
        print("No PDF to skip.", file=sys.stderr)
        return 1

    return 0 if mark_failed(root, rel, args.reason, progress_path) else 1


if __name__ == "__main__":
    raise SystemExit(main())
