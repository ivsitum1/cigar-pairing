# Example: meta-analysis codebook migration checklist

**Scope:** External study project workspace (not agent-rules). **Not** Books RAG.

**Status:** Brain templates ready. Study content must be filled in the study project root.

## Prerequisites

- Workspace root = folder containing your legacy extraction codebook (e.g. `Data_Extraction_Codebook.docx`)
- `agent-rules/` cloned inside project or reachable path to brain scripts

## Checklist

- [ ] Run `python agent-rules/40_operations/scripts/prepare_study_codebook.py --root .`
- [ ] Confirm `01_input/data_extraction/codebook.md` exists
- [ ] Copy all variables from legacy docx into codebook tables (`variable_name` = Excel column headers)
- [ ] Confirm `30_system/04_documentation/context/main.md` lists extraction codebook path
- [ ] Align extraction spreadsheet headers with codebook
- [ ] Record `codebook v1.0` in changelog or git tag when fields are frozen

## Reference

- [CODEBOOK_MIGRATION.md](../CODEBOOK_MIGRATION.md)
- Template: `40_operations/templates/codebooks/extraction_codebook.md`
- [RAG vs study data](../../RAG_VS_STUDY_DATA.md)
