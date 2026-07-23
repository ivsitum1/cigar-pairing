# Codebook templates (brain)

Study variable contracts — **not** [Books RAG](../../../30_system/docs/BOOKS_RAG.md). See [RAG vs study data](../../../30_system/docs/RAG_VS_STUDY_DATA.md).

Copy into study projects via `project_init.py` or `.ai/setup_project.py`.

| Template | Project path | Use when |
|----------|--------------|----------|
| `extraction_codebook.md` | `01_input/data_extraction/codebook.md` | Systematic review / meta-analysis (variables extracted from publications) |
| `dataset_codebook.md` | `01_input/codebook/dataset_codebook.md` | Own patient-level or study-level dataset (CSV in `01_input/data/00_inbox/raw/`) |

**Not the same as:**

- `01_input/data/metadata/` — file provenance (who sent what, when), not variable definitions
- `30_system/behavior_rules/02_statistics.md` — general analysis methods (brain), not study-specific variables

**IPD meta-analysis (future):** See Maxwell master codebook guidance in  
`20_knowledge/reference_library/statistics/papers/2024_2025/systematic_reviews/IPD_MA_Maxwell_Operational_Verbatim.md`.

**Migration (existing projects):** [30_system/docs/study_data/CODEBOOK_MIGRATION.md](../../../30_system/docs/study_data/CODEBOOK_MIGRATION.md)
