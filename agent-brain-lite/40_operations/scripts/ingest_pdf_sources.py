#!/usr/bin/env python3
"""Create contextual markdown source notes for all PDFs."""

from __future__ import annotations

import argparse
import pathlib
from collections import defaultdict

from pdf_library_context import infer_library_context, stem_slug_for_pdf


SKIP_PARTS = {".git", ".claude", "node_modules", "agent-transcripts", "__pycache__", ".venv", "venv"}


def related_hub_links(domain: str, subgroup: str) -> list[str]:
    links = [
        "- [[20_knowledge/wiki/index]]",
        "- [[20_knowledge/wiki/sources/books_md/INDEX]]",
        "- [[30_system/docs/REFERENCE_LIBRARY_AGENT_ACCESS]]",
        "- [[30_system/docs/FOLDER_INDEX]]",
        "- [[30_system/docs/bridges/pdf_md_map]]",
    ]
    if domain == "statistics":
        links.extend(
            [
                "- [Statistics reference index](../../../20_knowledge/reference_library/statistics/index.md)",
                "- [Statistics library README](../../../20_knowledge/reference_library/index.md)",
            ]
        )
        if subgroup == "books":
            links.append("- [Statistics books area](../../../20_knowledge/reference_library/statistics/books/)")
        if subgroup == "papers":
            links.append("- [Statistics papers README](../../../20_knowledge/reference_library/statistics/papers/index.md)")
    elif domain == "medicine":
        links.extend(
            [
                "- [Medicine library README](../../../20_knowledge/reference_library/medicine/index.md)",
                "- [Medicine textbooks README](../../../20_knowledge/reference_library/medicine/textbooks/index.md)",
            ]
        )
    elif domain == "writing":
        links.append("- [Writing / style library](../../../20_knowledge/reference_library/writing/)")
    elif domain == "opinions":
        links.append("- [Opinions / guidelines](../../../20_knowledge/reference_library/opinions/)")
    else:
        links.append("- [Reference library README](../../../20_knowledge/reference_library/index.md)")
    return links


def extract_md_links(root: pathlib.Path, books_sub: str, stem_slug: str) -> list[str]:
    """Find generated full-text MD files for this PDF stem (after extract_pdf_library_to_md.py)."""
    d = root / "20_knowledge" / "wiki" / "sources" / "books_md" / books_sub
    if not d.is_dir():
        return []
    matches = sorted(d.glob(f"{stem_slug}*.md"))
    if not matches:
        return []
    out: list[str] = []
    for m in matches:
        rel = m.relative_to(root).as_posix()
        no_ext = rel[:-3] if rel.endswith(".md") else rel
        out.append(f"- [[{no_ext}]]")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate contextual source notes for all PDFs.")
    parser.add_argument("--root", default=".", help="Workspace root")
    parser.add_argument("--out-dir", default="20_knowledge/wiki/sources/pdf", help="Output notes directory")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    out_dir = root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(
        p for p in root.rglob("*.pdf") if p.is_file() and not any(part in SKIP_PARTS for part in p.parts)
    )

    note_paths: list[pathlib.Path] = []
    by_group: dict[str, list[pathlib.Path]] = defaultdict(list)

    for pdf in pdfs:
        rel_pdf = pdf.relative_to(root).as_posix()
        domain, subgroup, books_sub = infer_library_context(rel_pdf)
        stem_slug = stem_slug_for_pdf(pdf.stem, rel_pdf)
        note_name = f"pdf__{stem_slug}.md"
        note_path = out_dir / note_name

        md_extract_links = extract_md_links(root, books_sub, stem_slug)
        md_section = (
            ["## Extracted text (Markdown)", ""]
            + (md_extract_links if md_extract_links else ["_No extracted MD yet. Run:_ `python 40_operations/scripts/extract_pdf_library_to_md.py`", ""])
        )

        content = [
            f"# Source Note: {pdf.stem}",
            "",
            "## File Mapping",
            "",
            f"- PDF path: `{rel_pdf}`",
            f"- Context domain: `{domain}`",
            f"- Context subgroup: `{subgroup}`",
            f"- Books MD folder: `20_knowledge/wiki/sources/books_md/{books_sub}/`",
            "",
            *md_section,
            "## Related Hubs",
            "",
            *related_hub_links(domain, subgroup),
            "",
            "## Processing Notes",
            "",
            "- Source stub links the PDF location and optional full-text extract.",
            "- For agent search inside the book, use the linked `books_md` note(s).",
            "",
        ]
        note_path.write_text("\n".join(content), encoding="utf-8")
        note_paths.append(note_path)
        by_group[f"{domain}/{subgroup}"].append(note_path)

    index_lines = [
        "# PDF Source Notes Index",
        "",
        "Auto-generated source stubs for PDFs plus links to searchable extracts in `books_md/` when present.",
        "",
        "## Related Hubs",
        "",
        "- [[20_knowledge/wiki/index]]",
        "- [[20_knowledge/wiki/sources/books_md/INDEX]]",
        "- [[30_system/docs/REFERENCE_LIBRARY_AGENT_ACCESS]]",
        "- [[30_system/docs/FOLDER_INDEX]]",
        "- [[30_system/docs/bridges/pdf_md_map]]",
        "",
        "## By Context",
        "",
    ]
    for group in sorted(by_group):
        index_lines.append(f"### {group}")
        index_lines.append("")
        for note in sorted(by_group[group]):
            rel_note = note.relative_to(root).as_posix()
            # INDEX.md and the note stubs share out_dir, so link by basename.
            # (Previously prefixed with ../../../<repo-relative-path>, which
            # from a 4-deep dir resolved to 20_knowledge/20_knowledge/... and
            # broke every one of these links.)
            index_lines.append(f"- [{rel_note}]({note.name})")
        index_lines.append("")
    (out_dir / "INDEX.md").write_text("\n".join(index_lines), encoding="utf-8")

    # Remove stale pdf__*.md stubs (replaced when PDF set or slug scheme changes).
    kept = {p.name for p in note_paths}
    for stale in out_dir.glob("pdf__*.md"):
        if stale.name not in kept:
            stale.unlink(missing_ok=True)

    source_index = root / "20_knowledge" / "wiki" / "sources" / "INDEX.md"
    source_index.write_text(
        "\n".join(
            [
                "# Sources Index",
                "",
                "## Nodes",
                "",
                "- [PDF source stubs (all PDFs)](pdf/INDEX.md)",
                "- [Extracted book text (reference library + inbox)](books_md/INDEX.md)",
                "- [[30_system/docs/bridges/pdf_md_map]]",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Generated PDF notes: {len(note_paths)}")
    print(f"Index: {(out_dir / 'INDEX.md').relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
