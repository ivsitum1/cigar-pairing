#!/usr/bin/env python3
"""Full Karpathy-style ingest pass from wiki PDF source notes."""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
WIKI = ROOT / "20_knowledge/wiki"
SOURCES_PDF = WIKI / "sources" / "pdf"
ENTITIES = WIKI / "entities"
CONCEPTS = WIKI / "concepts"
ANALYSIS = WIKI / "analysis"
WIKI_INDEX = WIKI / "index.md"
WIKI_LOG = WIKI / "log.md"


def slugify(value: str) -> str:
    s = value.lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "untitled"


def extract_pdf_context(text: str) -> tuple[str, str, str]:
    path = "UNKNOWN"
    domain = "general"
    subgroup = "unsorted"
    for line in text.splitlines():
        line_s = line.strip()
        if line_s.lower().startswith("- pdf path:"):
            path = line_s.split(":", 1)[1].strip().strip("`")
        elif line_s.lower().startswith("- context domain:"):
            domain = line_s.split(":", 1)[1].strip().strip("`")
        elif line_s.lower().startswith("- context subgroup:"):
            subgroup = line_s.split(":", 1)[1].strip().strip("`")
    return path, domain, subgroup


def ensure_dirs() -> None:
    ENTITIES.mkdir(parents=True, exist_ok=True)
    CONCEPTS.mkdir(parents=True, exist_ok=True)
    ANALYSIS.mkdir(parents=True, exist_ok=True)


def make_entity_note(base_slug: str, source_rel: str, pdf_path: str, domain: str) -> Path:
    path = ENTITIES / f"entity__{base_slug}.md"
    content = [
        f"# Entity: {base_slug}",
        "",
        "## Source",
        "",
        f"- Derived from: `20_knowledge/wiki/sources/pdf/{source_rel}`",
        f"- Original PDF: `{pdf_path}`",
        f"- Domain: `{domain}`",
        "",
        "## Links",
        "",
        f"- [[sources/pdf/{Path(source_rel).stem}]]",
        f"- [[concepts/concept__{base_slug}]]",
        f"- [[analysis/analysis__{base_slug}]]",
        "- [[index]]",
        "",
        "## Notes",
        "",
        "- Atomic entity node generated in full ingest pass.",
    ]
    path.write_text("\n".join(content) + "\n", encoding="utf-8")
    return path


def make_concept_note(base_slug: str, source_rel: str, pdf_path: str, domain: str, subgroup: str) -> Path:
    path = CONCEPTS / f"concept__{base_slug}.md"
    content = [
        f"# Concept: {base_slug}",
        "",
        "## Context",
        "",
        f"- Source note: `20_knowledge/wiki/sources/pdf/{source_rel}`",
        f"- PDF path: `{pdf_path}`",
        f"- Domain/Subgroup: `{domain}/{subgroup}`",
        "",
        "## Links",
        "",
        f"- [[sources/pdf/{Path(source_rel).stem}]]",
        f"- [[entities/entity__{base_slug}]]",
        f"- [[analysis/analysis__{base_slug}]]",
        "- [[index]]",
        "",
        "## Concept Summary",
        "",
        "- Placeholder concept summary; refine with extracted key claims and methods.",
    ]
    path.write_text("\n".join(content) + "\n", encoding="utf-8")
    return path


def make_analysis_note(base_slug: str, source_rel: str, pdf_path: str, domain: str, subgroup: str) -> Path:
    path = ANALYSIS / f"analysis__{base_slug}.md"
    content = [
        f"# Analysis: {base_slug}",
        "",
        "## Provenance",
        "",
        f"- Source note: `20_knowledge/wiki/sources/pdf/{source_rel}`",
        f"- PDF path: `{pdf_path}`",
        f"- Domain/Subgroup: `{domain}/{subgroup}`",
        "",
        "## Links",
        "",
        f"- [[sources/pdf/{Path(source_rel).stem}]]",
        f"- [[entities/entity__{base_slug}]]",
        f"- [[concepts/concept__{base_slug}]]",
        "- [[index]]",
        "",
        "## Analytical Notes",
        "",
        "- Placeholder analysis node for synthesis, consistency checks, and downstream writing.",
    ]
    path.write_text("\n".join(content) + "\n", encoding="utf-8")
    return path


def update_wiki_index(created_entity: int, created_concept: int, created_analysis: int) -> None:
    text = WIKI_INDEX.read_text(encoding="utf-8", errors="ignore") if WIKI_INDEX.exists() else "# LLM Wiki Index\n"
    marker = "## Key Nodes"
    block = [
        "## Karpathy Full Ingest Status",
        "",
        f"- Entity notes generated: {created_entity}",
        f"- Concept notes generated: {created_concept}",
        f"- Analysis notes generated: {created_analysis}",
        "- Sources map: `20_knowledge/wiki/sources/pdf/INDEX.md`",
        "",
    ]

    if "## Karpathy Full Ingest Status" in text:
        text = re.sub(
            r"## Karpathy Full Ingest Status[\s\S]*?(?=\n## |\Z)",
            "\n".join(block) + "\n",
            text,
            flags=re.MULTILINE,
        )
    elif marker in text:
        text = text.replace(marker, "\n".join(block) + marker)
    else:
        text = text.rstrip() + "\n\n" + "\n".join(block)
    WIKI_INDEX.write_text(text, encoding="utf-8")


def append_wiki_log(message: str) -> None:
    if not WIKI_LOG.exists():
        WIKI_LOG.write_text("# LLM Wiki Operations Log\n\n## Entries\n\n", encoding="utf-8")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = [
        f"- Date: {ts}",
        "  - Action: ingest",
        "  - Input: `20_knowledge/wiki/sources/pdf/*.md`",
        "  - Outputs:",
        "    - `20_knowledge/wiki/entities/entity__*.md`",
        "    - `20_knowledge/wiki/concepts/concept__*.md`",
        "    - `20_knowledge/wiki/analysis/analysis__*.md`",
        f"  - Notes: {message}",
        "",
    ]
    with open(WIKI_LOG, "a", encoding="utf-8") as handle:
        handle.write("\n".join(entry))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run full Karpathy ingest from PDF source notes.")
    parser.add_argument("--root", default=".", help="Workspace root")
    args = parser.parse_args()

    global ROOT, WIKI, SOURCES_PDF, ENTITIES, CONCEPTS, ANALYSIS, WIKI_INDEX, WIKI_LOG
    ROOT = Path(args.root).resolve()
    WIKI = ROOT / "20_knowledge/wiki"
    SOURCES_PDF = WIKI / "sources" / "pdf"
    ENTITIES = WIKI / "entities"
    CONCEPTS = WIKI / "concepts"
    ANALYSIS = WIKI / "analysis"
    WIKI_INDEX = WIKI / "index.md"
    WIKI_LOG = WIKI / "log.md"

    ensure_dirs()

    source_notes = sorted(
        p for p in SOURCES_PDF.glob("pdf__*.md") if p.is_file()
    )

    created_entity = 0
    created_concept = 0
    created_analysis = 0

    for source in source_notes:
        text = source.read_text(encoding="utf-8", errors="ignore")
        pdf_path, domain, subgroup = extract_pdf_context(text)
        slug = source.stem.replace("pdf__", "", 1)

        e = make_entity_note(slug, source.name, pdf_path, domain)
        c = make_concept_note(slug, source.name, pdf_path, domain, subgroup)
        a = make_analysis_note(slug, source.name, pdf_path, domain, subgroup)

        if e.exists():
            created_entity += 1
        if c.exists():
            created_concept += 1
        if a.exists():
            created_analysis += 1

    update_wiki_index(created_entity, created_concept, created_analysis)
    append_wiki_log(
        f"Full Karpathy ingest completed for {len(source_notes)} PDF source notes with linked entity/concept/analysis nodes."
    )

    print(f"source_notes={len(source_notes)}")
    print(f"entities={created_entity}")
    print(f"concepts={created_concept}")
    print(f"analysis={created_analysis}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
