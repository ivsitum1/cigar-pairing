#!/usr/bin/env python3
"""Extract text from PDFs under reference_library / inbox into searchable MD for Obsidian and agents."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import sys
from typing import Any

WORKSPACE = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE))
sys.path.insert(0, str(WORKSPACE / "40_operations" / "python"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from pdf_library_context import infer_library_context, stem_slug_for_pdf
from pdf_extraction import (
    CONTENT_NOTE_PADDLE,
    PADDLE_CONTENT_NOTES,
    extract_document_pages,
    get_last_content_note,
    is_paddle_available,
    needs_ocr,
)

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = Any  # type: ignore


SKIP_PARTS = {".git", ".claude", "node_modules", "agent-transcripts", "__pycache__", ".venv", "venv"}

# Keep single-file size reasonable for editors and LLM chunking; spill to _partN.md
MAX_CHARS_PER_FILE = 180_000
CONTENT_NOTE_PYPDF = "full_text_extract_py_pdf2"
PROGRESS_VERSION = 1


def pdf_sha1(path: pathlib.Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_progress(path: pathlib.Path) -> dict:
    if not path.is_file():
        return {"version": PROGRESS_VERSION, "entries": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "entries" in data:
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return {"version": PROGRESS_VERSION, "entries": {}}


def save_progress(path: pathlib.Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def prune_stale_md(out_base: pathlib.Path, books_sub: str, stem_slug: str) -> int:
    """Remove prior MD parts and failure stubs for this PDF stem."""
    subdir = out_base / books_sub
    if not subdir.is_dir():
        return 0
    removed = 0
    for pattern in (f"{stem_slug}.md", f"{stem_slug}_part*.md", f"{stem_slug}_EXTRACTION_FAILED.md"):
        for p in subdir.glob(pattern):
            try:
                p.unlink()
                removed += 1
            except OSError:
                pass
    return removed


def should_skip_resume(
    rel_pdf: str,
    sha: str,
    progress: dict,
    *,
    resume: bool,
    retry_failed: bool = False,
) -> bool:
    if not resume:
        return False
    entry = progress.get("entries", {}).get(rel_pdf)
    if not entry:
        return False
    if entry.get("sha1") != sha:
        return False
    note = entry.get("content_note")
    if note in PADDLE_CONTENT_NOTES:
        return True
    # Do not re-OCR failed PDFs for hours (OOM etc.) unless explicitly requested.
    if note == "failed" and not retry_failed:
        return True
    return False


def extract_text_pages(pdf_path: pathlib.Path) -> tuple[list[str], int, str | None]:
    """Return (page_texts, page_count, error_message)."""
    if PdfReader is Any:
        return [], 0, "PyPDF2 not installed"
    try:
        reader = PdfReader(str(pdf_path))
        if getattr(reader, "is_encrypted", False):
            try:
                reader.decrypt("")
            except Exception:
                return [], 0, "encrypted"
        n = len(reader.pages)
        texts: list[str] = []
        for i in range(n):
            try:
                t = reader.pages[i].extract_text() or ""
            except Exception as e:
                t = f"\n_[Extraction failed on page {i + 1}: {e}]_\n"
            texts.append(t)
        return texts, n, None
    except Exception as e:
        return [], 0, str(e)


def resolve_extraction(
    pdf_path: pathlib.Path,
    *,
    ocr_mode: str,
    force_ocr: bool,
) -> tuple[list[str], int, str | None, str]:
    """
    Return (page_texts, page_count, error, content_note).

    ocr_mode: auto | paddle | off
    """
    if ocr_mode == "paddle" or force_ocr:
        if not is_paddle_available():
            return (
                [],
                0,
                "PaddleOCR not installed; run: python 40_operations/scripts/install_paddle_ocr.py",
                CONTENT_NOTE_PADDLE,
            )
        texts, n, err = extract_document_pages(pdf_path)
        return texts, n, err, get_last_content_note()

    if ocr_mode == "off":
        texts, n, err = extract_text_pages(pdf_path)
        return texts, n, err, CONTENT_NOTE_PYPDF

    # auto: PyPDF2 first, Paddle when sparse or empty
    texts, n, err = extract_text_pages(pdf_path)
    if err and n == 0:
        if is_paddle_available():
            texts, n, err = extract_document_pages(pdf_path)
            return texts, n, err, get_last_content_note()
        return texts, n, err, CONTENT_NOTE_PYPDF

    if force_ocr or needs_ocr(texts):
        if not is_paddle_available():
            note = err or "sparse_text_layer"
            return texts, n, f"{note}; PaddleOCR not installed", CONTENT_NOTE_PYPDF
        p_texts, p_n, p_err = extract_document_pages(pdf_path)
        if p_texts:
            return p_texts, p_n, p_err, get_last_content_note()
        if texts and any(t.strip() for t in texts):
            return texts, n, p_err, CONTENT_NOTE_PYPDF

    return texts, n, err, CONTENT_NOTE_PYPDF


def write_md_parts(
    root: pathlib.Path,
    out_base: pathlib.Path,
    subdomain: str,
    stem_slug: str,
    title: str,
    rel_pdf: str,
    domain: str,
    subgroup: str,
    page_texts: list[str],
    page_count: int,
    err: str | None,
    *,
    content_note: str = CONTENT_NOTE_PYPDF,
) -> list[pathlib.Path]:
    """Write one or more markdown files with YAML frontmatter."""
    full_body_parts: list[str] = []
    for i, t in enumerate(page_texts):
        full_body_parts.append(f"\n## Page {i + 1}\n\n{t.strip() or '_[No text extracted; possible scan-only PDF]_'}\n")

    combined = "".join(full_body_parts)
    if len(combined) <= MAX_CHARS_PER_FILE:
        chunks = [combined]
    else:
        chunks = []
        buf: list[str] = []
        size = 0
        for part in full_body_parts:
            if size + len(part) > MAX_CHARS_PER_FILE and buf:
                chunks.append("".join(buf))
                buf = [part]
                size = len(part)
            else:
                buf.append(part)
                size += len(part)
        if buf:
            chunks.append("".join(buf))

    written: list[pathlib.Path] = []
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    subdir = out_base / subdomain
    subdir.mkdir(parents=True, exist_ok=True)

    for idx, chunk in enumerate(chunks):
        suffix = "" if len(chunks) == 1 else f"_part{idx + 1:02d}"
        fname = f"{stem_slug}{suffix}.md"
        path = subdir / fname

        frontmatter = "\n".join(
            [
                "---",
                f'title: "{title.replace(chr(34), chr(39))[:500]}"',
                f"source_pdf: {rel_pdf}",
                f"domain: {domain}",
                f"subgroup: {subgroup}",
                f"pages: {page_count}",
                f"extracted_utc: {ts}",
                f"content_note: {content_note}",
                f"extraction_engine_version: 2",
            ]
        )
        if err:
            frontmatter += f"\nextraction_note: {err[:500]!s}"
        frontmatter += "\n---\n\n"

        domain_key = subdomain.replace("/", "_") if "/" not in subdomain else subdomain
        hub = "\n".join(
            [
                "## Agent and graph hubs",
                "",
                "- [[20_knowledge/wiki/index]]",
                "- [[20_knowledge/wiki/sources/books_md/INDEX]]",
                f"- Domain shelf: [[20_knowledge/wiki/sources/books_md/INDEX#{domain_key}]]",
                "- [[30_system/docs/REFERENCE_LIBRARY_AGENT_ACCESS]]",
                f"- Original PDF: `{rel_pdf}`",
                "",
            ]
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(frontmatter + hub + f"# {title}\n\n" + chunk, encoding="utf-8")
        written.append(path)

    return written


def build_domain_index(root: pathlib.Path, out_base: pathlib.Path) -> None:
    lines = [
        "# Reference books and PDFs (extracted text)",
        "",
        "Auto-generated from PDFs under `20_knowledge/reference_library/` and `00_inbox/raw/`.",
        "Use [[20_knowledge/wiki/index]] and [[30_system/docs/REFERENCE_LIBRARY_AGENT_ACCESS]] for workflow context.",
        "",
        "## By domain",
        "",
    ]
    if not out_base.exists():
        lines.append(
            "_No extractions yet. Run `python 40_operations/scripts/extract_pdf_library_to_md.py` "
            "(install OCR: `python 40_operations/scripts/install_paddle_ocr.py`)._\n"
        )
        (out_base / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")
        return

    for subdir in sorted(out_base.iterdir()):
        if not subdir.is_dir() or subdir.name.startswith("."):
            continue
        lines.append(f"### {subdir.name}")
        lines.append("")
        for md in sorted(subdir.glob("*.md")):
            if md.name == "INDEX.md":
                continue
            rel = md.relative_to(root).as_posix()
            lines.append(f"- [[{rel.replace('.md', '')}]]")
        lines.append("")

    (out_base / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract PDF text to markdown under wiki/sources/books_md.")
    parser.add_argument("--root", default=".", help="Workspace root")
    parser.add_argument(
        "--out-dir",
        default="20_knowledge/wiki/sources/books_md",
        help="Output directory for extracted markdown",
    )
    parser.add_argument(
        "--only-prefix",
        default="",
        help="Only process PDFs whose path contains this substring (e.g. reference_library/medicine)",
    )
    parser.add_argument(
        "--ocr",
        choices=("auto", "paddle", "off"),
        default="auto",
        help="OCR engine: auto (PyPDF2 then Paddle for scans), paddle only, or off",
    )
    parser.add_argument(
        "--force-ocr",
        action="store_true",
        help="Always run PaddleOCR (requires install_paddle_ocr.py)",
    )
    parser.add_argument(
        "--prune-stale",
        action="store_true",
        help="Delete existing books_md files for each PDF stem before writing",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip PDFs already in progress.json (paddle OK, or failed unless --retry-failed)",
    )
    parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="With --resume, re-run OCR for entries marked failed (default: skip failed)",
    )
    parser.add_argument(
        "--progress-file",
        default="data/pdf_extract/progress.json",
        help="Resume/progress JSON path relative to workspace root",
    )
    parser.add_argument(
        "--report",
        default="",
        help="Write JSON summary (default: data/pdf_extract/last_extract_report.json when set to 'auto')",
    )
    args = parser.parse_args()

    if PdfReader is Any and args.ocr == "off":
        print("PyPDF2 is required (see requirements.txt).", file=sys.stderr)
        return 1

    root = pathlib.Path(args.root).resolve()
    out_base = root / args.out_dir
    out_base.mkdir(parents=True, exist_ok=True)
    progress_path = root / args.progress_file
    progress = load_progress(progress_path)

    report_path: pathlib.Path | None = None
    if args.report:
        report_path = (
            root / "data/pdf_extract/last_extract_report.json"
            if args.report == "auto"
            else pathlib.Path(args.report)
        )

    prefixes = (
        str(root / "20_knowledge" / "reference_library"),
        str(root / "00_inbox" / "raw"),
    )

    pdfs = sorted(
        p
        for p in root.rglob("*.pdf")
        if p.is_file()
        and not any(part in SKIP_PARTS for part in p.parts)
        and str(p).startswith(prefixes)
    )

    if args.only_prefix:
        needle = args.only_prefix.lower().replace("\\", "/")
        pdfs = [p for p in pdfs if needle in p.relative_to(root).as_posix().lower()]

    count_ok = 0
    count_fail = 0
    count_skipped = 0
    pruned_total = 0
    ts = dt.datetime.now(dt.timezone.utc).isoformat()
    report_items: list[dict[str, Any]] = []

    try:
        for pdf in pdfs:
            rel_pdf = pdf.relative_to(root).as_posix()
            sha = pdf_sha1(pdf)
            domain, subgroup, books_sub = infer_library_context(rel_pdf)
            stem_slug = stem_slug_for_pdf(pdf.stem, rel_pdf)

            if should_skip_resume(
                rel_pdf,
                sha,
                progress,
                resume=args.resume,
                retry_failed=args.retry_failed,
            ):
                count_skipped += 1
                reason = "resume"
                ent = progress.get("entries", {}).get(rel_pdf, {})
                if ent.get("content_note") == "failed":
                    reason = "resume_failed"
                report_items.append({"pdf": rel_pdf, "status": "skipped", "reason": reason})
                continue

            if args.prune_stale:
                pruned_total += prune_stale_md(out_base, books_sub, stem_slug)

            page_texts, page_count, err, content_note = resolve_extraction(
                pdf,
                ocr_mode=args.ocr,
                force_ocr=args.force_ocr,
            )
            if err and page_count == 0:
                count_fail += 1
                subdir = out_base / books_sub
                subdir.mkdir(parents=True, exist_ok=True)
                stub = subdir / f"{stem_slug}_EXTRACTION_FAILED.md"
                stub.write_text(
                    "\n".join(
                        [
                            "---",
                            f'title: "{pdf.stem.replace(chr(34), chr(39))}"',
                            f"source_pdf: {rel_pdf}",
                            f"domain: {domain}",
                            f"subgroup: {subgroup}",
                            "extraction_failed: true",
                            f"extracted_utc: {ts[:10]}",
                            "---",
                            "",
                            f"# {pdf.stem}",
                            "",
                            f"Extraction error: `{err}`",
                            "",
                            f"Open PDF: `{rel_pdf}`",
                            "",
                            "Install OCR: `python 40_operations/scripts/install_paddle_ocr.py`",
                            "",
                            "- [[20_knowledge/wiki/index]]",
                            "- [[30_system/docs/REFERENCE_LIBRARY_AGENT_ACCESS]]",
                            "",
                        ]
                    ),
                    encoding="utf-8",
                )
                progress.setdefault("entries", {})[rel_pdf] = {
                    "sha1": sha,
                    "content_note": "failed",
                    "stem_slug": stem_slug,
                    "updated_utc": ts,
                }
                report_items.append({"pdf": rel_pdf, "status": "failed", "error": err})
                save_progress(progress_path, progress)
                continue

            write_md_parts(
                root,
                out_base,
                books_sub,
                stem_slug,
                pdf.stem,
                rel_pdf,
                domain,
                subgroup,
                page_texts,
                page_count,
                err,
                content_note=content_note,
            )
            count_ok += 1
            progress.setdefault("entries", {})[rel_pdf] = {
                "sha1": sha,
                "content_note": content_note,
                "stem_slug": stem_slug,
                "updated_utc": ts,
            }
            report_items.append(
                {"pdf": rel_pdf, "status": "ok", "content_note": content_note, "pages": page_count}
            )
            save_progress(progress_path, progress)
    finally:
        build_domain_index(root, out_base)

    summary = {
        "extracted_utc": ts,
        "ocr": args.ocr,
        "force_ocr": args.force_ocr,
        "only_prefix": args.only_prefix or None,
        "ok": count_ok,
        "failed": count_fail,
        "skipped": count_skipped,
        "pruned_files": pruned_total,
        "pdf_total": len(pdfs),
        "items": report_items,
    }
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(
        f"Extracted OK: {count_ok}, failed/stub: {count_fail}, skipped: {count_skipped}, "
        f"pruned: {pruned_total}, ocr={args.ocr}, output: {(out_base / 'INDEX.md').relative_to(root).as_posix()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
