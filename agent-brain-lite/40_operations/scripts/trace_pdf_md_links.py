#!/usr/bin/env python3
"""Trace PDF to Markdown link coverage across the workspace."""

from __future__ import annotations

import argparse
import pathlib
import re
from collections import defaultdict


SKIP_PARTS = {".git", ".claude", "node_modules", "agent-transcripts", "__pycache__", ".venv", "venv"}


def normalize_stem(name: str) -> str:
    value = name.lower()
    value = re.sub(r"\s+", "_", value)
    value = value.replace("-", "_")
    value = re.sub(r"\(1\)|_1$|_copy$|copy$", "", value)
    value = re.sub(r"[^a-z0-9_]+", "", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value


def collect_files(root: pathlib.Path, suffix: str) -> list[pathlib.Path]:
    out: list[pathlib.Path] = []
    for p in root.rglob(f"*{suffix}"):
        if not p.is_file():
            continue
        if any(part in SKIP_PARTS for part in p.parts):
            continue
        out.append(p)
    return out


def contains_pdf_reference(md_path: pathlib.Path, pdf_name: str, pdf_stem: str) -> bool:
    text = md_path.read_text(encoding="utf-8", errors="ignore").lower()
    return pdf_name.lower() in text or pdf_stem.lower() in text


def parse_explicit_pdf_path(md_path: pathlib.Path) -> str | None:
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        line_s = line.strip()
        if line_s.lower().startswith("- pdf path:"):
            raw = line_s.split(":", 1)[1].strip()
            if raw.startswith("`") and raw.endswith("`"):
                return raw[1:-1]
            return raw
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Trace PDF <-> MD mapping and coverage.")
    parser.add_argument("--root", default=".", help="Workspace root path")
    parser.add_argument("--output", default="30_system/docs/bridges/pdf_md_map.md", help="Output markdown map path")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(collect_files(root, ".pdf"))
    mds = sorted(collect_files(root, ".md"))

    md_by_stem: dict[str, list[pathlib.Path]] = defaultdict(list)
    md_by_parent: dict[str, list[pathlib.Path]] = defaultdict(list)
    md_by_explicit_pdf: dict[str, list[pathlib.Path]] = defaultdict(list)
    for md in mds:
        md_by_stem[normalize_stem(md.stem)].append(md)
        md_by_parent[md.parent.relative_to(root).as_posix()].append(md)
        explicit = parse_explicit_pdf_path(md)
        if explicit:
            md_by_explicit_pdf[explicit].append(md)

    duplicate_groups: dict[str, list[pathlib.Path]] = defaultdict(list)
    for pdf in pdfs:
        duplicate_groups[normalize_stem(pdf.stem)].append(pdf)

    rows: list[tuple[str, str, str, str]] = []
    stats = {"paired_strict": 0, "paired_heuristic": 0, "missing": 0, "duplicates": 0}

    for pdf in pdfs:
        rel_pdf = pdf.relative_to(root).as_posix()
        normalized = normalize_stem(pdf.stem)

        explicit_candidates = md_by_explicit_pdf.get(rel_pdf, [])
        if explicit_candidates:
            rel_md = explicit_candidates[0].relative_to(root).as_posix()
            flags = ["explicit_pdf_path_match"]
            if len(duplicate_groups[normalized]) > 1:
                flags.append("duplicate_pdf_group")
                stats["duplicates"] += 1
            rows.append((rel_pdf, rel_md, ";".join(flags), "paired"))
            stats["paired_heuristic"] += 1
            continue

        strict_match = next((md for md in mds if md.stem == pdf.stem), None)
        if strict_match:
            rel_md = strict_match.relative_to(root).as_posix()
            rows.append((rel_pdf, rel_md, "strict_stem_match", "paired"))
            stats["paired_strict"] += 1
            continue

        candidates = md_by_stem.get(normalized, [])
        if not candidates:
            parent_key = pdf.parent.relative_to(root).as_posix()
            folder_candidates = md_by_parent.get(parent_key, [])
            candidates = [
                md for md in folder_candidates if contains_pdf_reference(md, pdf.name, pdf.stem)
            ]

        if candidates:
            rel_md = candidates[0].relative_to(root).as_posix()
            flags = ["heuristic_match"]
            if len(duplicate_groups[normalized]) > 1:
                flags.append("duplicate_pdf_group")
                stats["duplicates"] += 1
            rows.append((rel_pdf, rel_md, ";".join(flags), "paired"))
            stats["paired_heuristic"] += 1
        else:
            flag = "duplicate_pdf_group" if len(duplicate_groups[normalized]) > 1 else "missing_md"
            if flag == "duplicate_pdf_group":
                stats["duplicates"] += 1
            rows.append((rel_pdf, "MISSING_MD", flag, "unpaired"))
            stats["missing"] += 1

    lines: list[str] = [
        "# PDF to Markdown Trace Map",
        "",
        "Auto-generated traceability map for PDF source files and their markdown representations.",
        "",
        "## Related Hubs",
        "",
        "- [Folder index hub](../FOLDER_INDEX.md)",
        "- [Non-markdown bridges](non_markdown_bridges.md)",
        "- [Graph connectivity map](../GRAPH_CONNECTIVITY_MAP.md)",
        "",
        "## Summary",
        "",
        f"- Total PDFs: {len(pdfs)}",
        f"- Paired (strict stem): {stats['paired_strict']}",
        f"- Paired (heuristic): {stats['paired_heuristic']}",
        f"- Unpaired (missing md): {stats['missing']}",
        f"- Duplicate-like PDF entries: {stats['duplicates']}",
        "",
        "## Map",
        "",
        "| PDF | MD Note | Match Type | Status |",
        "|-----|---------|------------|--------|",
    ]

    for pdf_rel, md_rel, match_type, status in rows:
        pdf_cell = f"`{pdf_rel}`"
        md_cell = f"`{md_rel}`" if md_rel != "MISSING_MD" else "`MISSING_MD`"
        lines.append(f"| {pdf_cell} | {md_cell} | `{match_type}` | `{status}` |")

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated: {output.relative_to(root).as_posix()}")
    print(
        f"PDFs={len(pdfs)} strict={stats['paired_strict']} heuristic={stats['paired_heuristic']} "
        f"missing={stats['missing']} duplicates={stats['duplicates']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
