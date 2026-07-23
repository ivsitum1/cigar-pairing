#!/usr/bin/env python3
"""Classify PDF extraction gaps and write OCR retry strategy (data/pdf_extract/OCR_RETRY_STRATEGY.md)."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone

WORKSPACE = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE / "40_operations" / "python"))

from pdf_extraction.pymupdf_fallback import classify_local_pdf, is_pdf_header  # noqa: E402


def unique_paths(items: list) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        rel = item if isinstance(item, str) else item.get("pdf", "")
        if not rel or rel in seen:
            continue
        seen.add(rel)
        out.append(rel)
    return out


def route_for(rel: str, error: str | None) -> str:
    p = WORKSPACE / rel
    kind = classify_local_pdf(p)
    err = (error or "").lower()
    if kind in ("placeholder", "missing"):
        return "onedrive_or_replace"
    if kind == "html":
        return "replace_non_pdf"
    if kind == "empty_pdf":
        return "redownload"
    if "unable to allocate" in err or "miller" in rel.lower():
        try:
            import fitz

            n = fitz.open(p).page_count
            if n > 2000:
                return "pypdf_text_layer"
        except Exception:
            pass
        if "unable to allocate" in err:
            return "pypdf_text_layer"
    if kind == "corrupt_pdf":
        return "raster_or_redownload"
    return "paddle_raster_retry"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Workspace root")
    parser.add_argument(
        "--report",
        default="data/pdf_extract/migration_report_latest.json",
        help="Migration report JSON (relative to root)",
    )
    parser.add_argument(
        "--out",
        default="data/pdf_extract/OCR_RETRY_STRATEGY.md",
        help="Strategy markdown output",
    )
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report_path = root / args.report
    if not report_path.is_file():
        print(f"Missing report: {report_path}", file=sys.stderr)
        return 1

    report = json.loads(report_path.read_text(encoding="utf-8"))
    failed = report.get("failed", [])
    pypdf_only = report.get("pypdf_only", [])
    no_md = report.get("no_md", [])

    buckets: dict[str, list[dict[str, str]]] = {
        "onedrive_or_replace": [],
        "replace_non_pdf": [],
        "redownload": [],
        "pypdf_text_layer": [],
        "paddle_raster_retry": [],
        "paddle_standard_retry": [],
        "never_extracted": [],
        "pypdf_only_upgrade": [],
    }

    for item in failed:
        rel = item["pdf"]
        err = item.get("error", "")
        r = route_for(rel, err)
        buckets[r].append({"pdf": rel, "error": err, "class": classify_local_pdf(root / rel)})

    for rel in unique_paths(pypdf_only):
        buckets["pypdf_only_upgrade"].append(
            {"pdf": rel, "error": "legacy PyPDF2 only", "class": classify_local_pdf(root / rel)}
        )

    for rel in unique_paths(no_md):
        buckets["never_extracted"].append(
            {"pdf": rel, "error": "no books_md", "class": classify_local_pdf(root / rel)}
        )

    ts = datetime.now(timezone.utc).isoformat()
    lines = [
        "# OCR retry strategy (auto-generated)",
        "",
        f"**Generated:** {ts}",
        f"**Source:** `{args.report}`",
        "",
        "## Summary",
        "",
        "| Bucket | Count | Action |",
        "|--------|------:|--------|",
        "| OneDrive placeholder / not a PDF | "
        f"{len(buckets['onedrive_or_replace'])} | Download locally; verify `%PDF-` header |",
        "| HTML masquerading as PDF | "
        f"{len(buckets['replace_non_pdf'])} | Replace with real PDF |",
        "| Empty/corrupt stub | "
        f"{len(buckets['redownload'])} | Re-ingest from source |",
        "| Large text-layer book (Miller) | "
        f"{len(buckets['pypdf_text_layer'])} | `--ocr off` (PyPDF2), not full-doc Paddle |",
        "| Paddle + PyMuPDF raster fallback | "
        f"{len(buckets['paddle_raster_retry'])} | `--retry-failed --force-ocr` (raster auto) |",
        "| Still PyPDF2 only | "
        f"{len(buckets['pypdf_only_upgrade'])} | `--ocr auto` if scan/sparse |",
        "| Never extracted | "
        f"{len(buckets['never_extracted'])} | First-time extract |",
        "",
        "## Commands (PowerShell, repo root)",
        "",
        "### A. OneDrive — make files real PDFs first",
        "",
        "```powershell",
        "Get-ChildItem 20_knowledge\\reference_library -Recurse -Filter *.pdf |",
        "  Where-Object { $_.Attributes -match 'ReparsePoint' } |",
        "  Select-Object FullName, Length",
        "```",
        "",
        "Right-click folder → **Always keep on this device**, then re-run diagnose.",
        "",
        "### B. Retry failed (raster fallback for PDFium/OOM/page errors)",
        "",
        "```powershell",
        ".\\40_operations\\scripts\\run_ocr_retry_failed.ps1 -Root .",
        "```",
        "",
        "### C. Miller / huge text-layer PDFs (PyPDF2 only)",
        "",
        "```powershell",
        ".\\.venv-ocr\\Scripts\\python.exe 40_operations\\scripts\\extract_pdf_library_to_md.py `",
        "  --root . --ocr off --retry-failed --prune-stale `",
        "  --only-prefix medicine/anesthesiology/Miller",
        "```",
        "",
        "### D. Never extracted + PyPDF2 backlog",
        "",
        "```powershell",
        ".\\.venv-ocr\\Scripts\\python.exe 40_operations\\scripts\\extract_pdf_library_to_md.py `",
        "  --root . --ocr auto --only-prefix \"<path fragment>\"",
        "```",
        "",
        "### E. After OCR gaps closed",
        "",
        "```powershell",
        ".\\.venv-ocr\\Scripts\\python.exe 40_operations\\scripts\\build_books_rag_index.py --root . --force",
        "```",
        "",
    ]

    def section(title: str, key: str) -> None:
        items = buckets[key]
        if not items:
            return
        lines.append(f"## {title}")
        lines.append("")
        for it in items:
            lines.append(f"- `{it['pdf']}`")
            if it.get("class"):
                lines.append(f"  - class: `{it['class']}`")
            if it.get("error"):
                lines.append(f"  - last error: {it['error'][:200]}")
        lines.append("")

    section("OneDrive / not PDF", "onedrive_or_replace")
    section("Replace HTML file", "replace_non_pdf")
    section("Redownload empty PDF", "redownload")
    section("PyPDF2 text layer (do not force full Paddle)", "pypdf_text_layer")
    section("Paddle raster retry", "paddle_raster_retry")
    section("PyPDF2-only upgrade", "pypdf_only_upgrade")
    section("Never extracted", "never_extracted")

    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_path.relative_to(root)}")
    for key, items in buckets.items():
        if items:
            print(f"  {key}: {len(items)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
