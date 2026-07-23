#!/usr/bin/env python3
"""Final Paddle migration report: extracted OK, failed, missing, still PyPDF2."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE))
sys.path.insert(0, str(WORKSPACE / "40_operations" / "scripts"))

from pdf_library_context import infer_library_context, stem_slug_for_pdf  # noqa: E402

SKIP_PARTS = {".git", ".claude", "node_modules", "__pycache__", ".venv", "venv"}
SOURCE_PDF_RE = re.compile(r"^source_pdf:\s*(.+)$", re.MULTILINE)
CONTENT_NOTE_RE = re.compile(r"^content_note:\s*(.+)$", re.MULTILINE)
ERROR_RE = re.compile(r"Extraction error:\s*`([^`]+)`")


def _find_pdfs(root: Path) -> list[Path]:
    prefixes = (root / "20_knowledge" / "reference_library", root / "00_inbox" / "raw")
    out: list[Path] = []
    for prefix in prefixes:
        if not prefix.is_dir():
            continue
        for p in prefix.rglob("*.pdf"):
            if p.is_file() and not any(part in SKIP_PARTS for part in p.parts):
                out.append(p)
    return sorted(out)


def _books_md_status(root: Path) -> dict[str, dict]:
    """Map source_pdf rel path -> best status from books_md."""
    books_md = root / "20_knowledge" / "wiki" / "sources" / "books_md"
    by_pdf: dict[str, dict] = {}
    if not books_md.is_dir():
        return by_pdf

    for md in books_md.rglob("*.md"):
        if md.name == "INDEX.md":
            continue
        try:
            raw = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        sp = SOURCE_PDF_RE.search(raw)
        if not sp:
            continue
        rel = sp.group(1).strip()
        if "extraction_failed: true" in raw or md.name.endswith("_EXTRACTION_FAILED.md"):
            err_m = ERROR_RE.search(raw)
            by_pdf[rel] = {
                "status": "failed",
                "error": err_m.group(1) if err_m else "(unknown)",
                "md": md.relative_to(books_md).as_posix(),
            }
            continue
        note_m = CONTENT_NOTE_RE.search(raw)
        note = note_m.group(1).strip() if note_m else "(none)"
        prev = by_pdf.get(rel)
        if prev and prev.get("status") == "paddleocr_ppstructurev3":
            continue
        if note == "paddleocr_ppstructurev3":
            by_pdf[rel] = {"status": "paddle", "md": md.relative_to(books_md).as_posix()}
        elif prev is None:
            by_pdf[rel] = {"status": "other", "content_note": note, "md": md.relative_to(books_md).as_posix()}
    return by_pdf


def _load_progress(root: Path) -> dict:
    path = root / "data" / "pdf_extract" / "progress.json"
    if not path.is_file():
        return {"entries": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def build_report(root: Path) -> dict:
    pdfs = _find_pdfs(root)
    pdf_rels = [p.relative_to(root).as_posix() for p in pdfs]
    md_by_pdf = _books_md_status(root)
    progress = _load_progress(root).get("entries", {})

    paddle_ok: list[str] = []
    failed: list[dict] = []
    pypdf_only: list[str] = []
    no_md: list[str] = []
    progress_only: list[dict] = []

    for rel in pdf_rels:
        md = md_by_pdf.get(rel)
        prog = progress.get(rel, {})
        if md and md.get("status") == "paddle":
            paddle_ok.append(rel)
        elif md and md.get("status") == "failed":
            failed.append({"pdf": rel, "error": md.get("error"), "md": md.get("md"), "progress": prog})
        elif md and md.get("status") == "other":
            note = md.get("content_note", "")
            if note == "full_text_extract_py_pdf2":
                pypdf_only.append(rel)
            else:
                pypdf_only.append(rel)
        elif prog.get("content_note") == "paddleocr_ppstructurev3":
            paddle_ok.append(rel)
        elif prog.get("content_note") == "failed":
            failed.append({"pdf": rel, "error": "(progress failed, no stub)", "md": None, "progress": prog})
        else:
            no_md.append(rel)

    for rel, prog in progress.items():
        if rel not in pdf_rels:
            progress_only.append({"pdf": rel, "progress": prog})

    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "pdf_count_local": len(pdf_rels),
        "paddle_ok_count": len(paddle_ok),
        "failed_count": len(failed),
        "pypdf_only_count": len(pypdf_only),
        "no_md_count": len(no_md),
        "paddle_ok": sorted(paddle_ok),
        "failed": sorted(failed, key=lambda x: x["pdf"]),
        "pypdf_only": sorted(pypdf_only),
        "no_md": sorted(no_md),
        "progress_orphan": progress_only,
        "progress_summary": dict(Counter(v.get("content_note") for v in progress.values())),
    }


def _write_markdown(report: dict, path: Path) -> None:
    lines = [
        "# PDF Paddle migracija — izvještaj",
        "",
        f"**Generirano:** {report['generated_utc']}",
        "",
        "## Sažetak",
        "",
        f"| Kategorija | Broj |",
        f"|------------|------|",
        f"| Lokalnih PDF-ova | {report['pdf_count_local']} |",
        f"| Paddle OCR uspjeh | {report['paddle_ok_count']} |",
        f"| Extraction failed | {report['failed_count']} |",
        f"| Još samo PyPDF2 / stari tekst | {report['pypdf_only_count']} |",
        f"| Bez books_md | {report['no_md_count']} |",
        "",
        f"**progress.json:** {report.get('progress_summary', {})}",
        "",
        "## Uspješno (Paddle OCR)",
        "",
    ]
    for p in report["paddle_ok"][:50]:
        lines.append(f"- `{p}`")
    if len(report["paddle_ok"]) > 50:
        lines.append(f"- … i još {len(report['paddle_ok']) - 50}")
    lines.extend(["", "## Nije ekstrahirano (EXTRACTION_FAILED)", ""])
    for item in report["failed"]:
        lines.append(f"- `{item['pdf']}`")
        lines.append(f"  - greška: {item.get('error', '?')}")
    lines.extend(
        [
            "",
            "## Ponoviti OCR (još PyPDF2 ili bez Paddle)",
            "",
            "Pokreni za pojedini prefix ili s `--retry-failed` nakon što su failovi označeni:",
            "",
            "```powershell",
            ".\\40_operations\\scripts\\extract_pdf_ocr.ps1 -Root . -OnlyPrefix \"<putanja>\" -ForceOcr -Resume",
            "# ili samo failovi:",
            ".\\venv-ocr\\Scripts\\python.exe 40_operations\\scripts\\extract_pdf_library_to_md.py --root . --ocr paddle --force-ocr --retry-failed",
            "```",
            "",
        ]
    )
    for p in report["pypdf_only"][:40]:
        lines.append(f"- `{p}`")
    if len(report["pypdf_only"]) > 40:
        lines.append(f"- … i još {len(report['pypdf_only']) - 40}")
    lines.extend(["", "## PDF bez ikakvog books_md", ""])
    for p in report["no_md"][:40]:
        lines.append(f"- `{p}`")
    if len(report["no_md"]) > 40:
        lines.append(f"- … i još {len(report['no_md']) - 40}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Migration extraction report.")
    parser.add_argument("--root", default=".", help="Workspace root")
    parser.add_argument(
        "--output-dir",
        default="",
        help="Directory for report JSON/MD (default: data/pdf_extract)",
    )
    args = parser.parse_args()
    root = Path(args.root).resolve()
    out_dir = Path(args.output_dir) if args.output_dir else root / "data" / "pdf_extract"
    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    json_path = out_dir / f"migration_report_{stamp}.json"
    md_path = out_dir / f"migration_report_{stamp}.md"
    latest_json = out_dir / "migration_report_latest.json"
    latest_md = out_dir / "migration_report_latest.md"

    payload = json.dumps(report, indent=2, ensure_ascii=False)
    json_path.write_text(payload, encoding="utf-8")
    latest_json.write_text(payload, encoding="utf-8")
    _write_markdown(report, md_path)
    _write_markdown(report, latest_md)

    print(payload)
    print(f"\nWrote {md_path.relative_to(root)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
