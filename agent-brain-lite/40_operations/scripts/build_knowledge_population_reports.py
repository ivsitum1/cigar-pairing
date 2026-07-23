from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "30_system" / "docs"
REF = ROOT / "20_knowledge" / "reference_library"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def local_counts() -> dict[str, int]:
    p = DOCS / "added_local_sources.json"
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding="utf-8"))
    return {k: len(v) for k, v in data.items()}


def online_open_count() -> int:
    d = REF / "opinions" / "guidelines_consensus" / "open_online"
    if not d.exists():
        return 0
    return len([x for x in d.glob("*") if x.is_file()])


def build_restricted_list() -> str:
    return """# Restricted Missing Sources (Manual Upload Needed)

These are high-value sources detected as likely restricted/paywalled or institutional.
Upload PDF/EPUB/DOCX manually when available, then place in the indicated target folders.

## Anesthesiology
- Miller's Anesthesia (latest edition) -> `20_knowledge/reference_library/medicine/anesthesiology/`
- Barash Clinical Anesthesia -> `20_knowledge/reference_library/medicine/anesthesiology/`
- Stoelting's Pharmacology & Physiology in Anesthetic Practice -> `20_knowledge/reference_library/medicine/anesthesiology/`

## Emergency Medicine
- Rosen's Emergency Medicine -> `20_knowledge/reference_library/medicine/emergency/`
- Tintinalli's Emergency Medicine -> `20_knowledge/reference_library/medicine/emergency/`
- Evidence-based emergency medicine editorials (journal collections) -> `20_knowledge/reference_library/opinions/editorials_commentaries/`

## Intensive Care
- Oh's Intensive Care Manual -> `20_knowledge/reference_library/medicine/intensive_care/`
- Irwin and Rippe's Intensive Care Medicine -> `20_knowledge/reference_library/medicine/intensive_care/`
- SCCM guideline statements not OA -> `20_knowledge/reference_library/opinions/guidelines_consensus/`

## Statistics
- Regression Modeling Strategies (Harrell) -> `20_knowledge/reference_library/statistics/books/local_collection/`
- Bayesian Data Analysis (Gelman et al.) -> `20_knowledge/reference_library/statistics/books/local_collection/`
- Cochrane Handbook full editions if restricted -> `20_knowledge/reference_library/statistics/books/local_collection/`

## Scientific Writing
- AMA Manual of Style (if restricted source) -> `20_knowledge/reference_library/writing/books_and_guides/`
- Medical journal editorial policy collections (publisher restricted) -> `20_knowledge/reference_library/opinions/editorials_commentaries/`
"""


def main() -> None:
    counts = local_counts()
    open_online = online_open_count()

    summary = f"""# Knowledge Population Summary

## Added Local (files copied into `20_knowledge`)
- anesthesiology: {counts.get('anesthesiology', 0)}
- emergency: {counts.get('emergency', 0)}
- intensive_care: {counts.get('intensive_care', 0)}
- statistics: {counts.get('statistics', 0)}
- scientific_writing: {counts.get('scientific_writing', 0)}

## Added Online Open
- guideline/consensus PDFs downloaded: {open_online}
- location: `20_knowledge/reference_library/opinions/guidelines_consensus/open_online/`

## Restricted Missing
- see `30_system/docs/restricted_missing_sources.md`
"""
    write_text(DOCS / "knowledge_population_summary.md", summary)
    write_text(DOCS / "restricted_missing_sources.md", build_restricted_list())

    opinions_readme = """# Opinions Library

## Guidelines and Consensus
- Open online PDFs: `open_online/`
- Additional restricted guideline sources: see `30_system/docs/restricted_missing_sources.md`

## Editorials and Commentaries
- Populate manually from journal editorials/commentaries where licensing permits.
- Track pending items in `30_system/docs/restricted_missing_sources.md`.
"""
    write_text(REF / "opinions" / "README.md", opinions_readme)
    write_text(
        REF / "opinions" / "editorials_commentaries" / "README.md",
        "# Editorials and Commentaries\n\nPlace editorial/commentary files here when licensing allows.\n",
    )
    write_text(
        REF / "opinions" / "guidelines_consensus" / "README.md",
        "# Guidelines and Consensus\n\nOpen files are in `open_online/`. Add additional guideline PDFs here.\n",
    )

    print("reports_generated")


if __name__ == "__main__":
    main()
