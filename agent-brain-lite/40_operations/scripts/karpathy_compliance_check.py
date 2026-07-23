#!/usr/bin/env python3
"""Karpathy wiki compliance check for PDF ingest coverage."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Karpathy-style wiki compliance.")
    parser.add_argument("--root", default=".", help="Workspace root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    sources = sorted((root / "20_knowledge/wiki" / "sources" / "pdf").glob("pdf__*.md"))
    entities = sorted((root / "20_knowledge/wiki" / "entities").glob("entity__*.md"))
    concepts = sorted((root / "20_knowledge/wiki" / "concepts").glob("concept__*.md"))
    analysis = sorted((root / "20_knowledge/wiki" / "analysis").glob("analysis__*.md"))
    wiki_log = root / "20_knowledge/wiki" / "log.md"
    wiki_index = root / "20_knowledge/wiki" / "index.md"

    source_stems = {p.stem.replace("pdf__", "", 1) for p in sources}
    entity_stems = {p.stem.replace("entity__", "", 1) for p in entities}
    concept_stems = {p.stem.replace("concept__", "", 1) for p in concepts}
    analysis_stems = {p.stem.replace("analysis__", "", 1) for p in analysis}

    missing_entity = sorted(source_stems - entity_stems)
    missing_concept = sorted(source_stems - concept_stems)
    missing_analysis = sorted(source_stems - analysis_stems)

    score = 100
    if missing_entity:
        score -= 25
    if missing_concept:
        score -= 25
    if missing_analysis:
        score -= 25
    if not wiki_log.exists() or "Full Karpathy ingest completed" not in wiki_log.read_text(encoding="utf-8", errors="ignore"):
        score -= 15
    if not wiki_index.exists() or "Karpathy Full Ingest Status" not in wiki_index.read_text(encoding="utf-8", errors="ignore"):
        score -= 10
    score = max(score, 0)

    report = root / "30_system/docs" / "KARPATHY_COMPLIANCE_REPORT.md"
    lines = [
        "# Karpathy Compliance Report",
        "",
        f"- Compliance score: {score}/100",
        f"- Source notes: {len(sources)}",
        f"- Entity notes: {len(entities)}",
        f"- Concept notes: {len(concepts)}",
        f"- Analysis notes: {len(analysis)}",
        "",
        "## Coverage Gaps",
        "",
        f"- Missing entity nodes: {len(missing_entity)}",
        f"- Missing concept nodes: {len(missing_concept)}",
        f"- Missing analysis nodes: {len(missing_analysis)}",
        "",
    ]

    if missing_entity:
        lines.append("### Missing Entities")
        lines.extend([f"- `{x}`" for x in missing_entity[:50]])
        lines.append("")
    if missing_concept:
        lines.append("### Missing Concepts")
        lines.extend([f"- `{x}`" for x in missing_concept[:50]])
        lines.append("")
    if missing_analysis:
        lines.append("### Missing Analysis")
        lines.extend([f"- `{x}`" for x in missing_analysis[:50]])
        lines.append("")

    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"KARPATHY_COMPLIANCE_SCORE={score}/100")
    print(f"report={report.relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
