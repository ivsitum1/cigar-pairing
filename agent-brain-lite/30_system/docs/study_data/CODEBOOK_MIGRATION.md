# Codebook migration guide

> **Scope:** Study projects only. Not related to [Books RAG](../BOOKS_RAG.md) or `BOOKS_RAG_DATA_DIR` (`C:\books_rag`).

## Meta-analysis project (external study folder)

Use a **study workspace root** (not agent-rules). Example layout: `…/publikacije/<study_slug>/` with legacy `Data_Extraction_Codebook.docx` if you have one.

### Steps

1. Open the study folder as the **workspace root** in Cursor (not agent-rules).
2. Seed templates from brain (if folders missing):

   ```powershell
   python agent-rules/40_operations/scripts/codebook_seed.py --root .
   ```

   Or from agent-rules repo against an explicit root:

   ```powershell
   python 40_operations/scripts/codebook_seed.py --root "C:\path\to\your-study-folder"
   ```

3. Copy variable definitions from your legacy extraction doc into `01_input/data_extraction/codebook.md` (one row per variable; `variable_name` = sheet column headers).
4. Ensure `30_system/04_documentation/context/main.md` includes the **Data contracts** section:

   - `extraction_codebook: 01_input/data_extraction/codebook.md`

5. Tag a frozen version when fields are locked (git tag or changelog entry `codebook v1.0`).

### Prepare script

`prepare_study_codebook.py` seeds codebooks and patches `main.md` if the Data contracts block is absent:

```powershell
python agent-rules/40_operations/scripts/prepare_study_codebook.py --root "C:\path\to\your-study-folder"
```

See [examples/METAANALIZA_CODEBOOK_MIGRATION.md](examples/METAANALIZA_CODEBOOK_MIGRATION.md) for a sample checklist.

---

## Patient-level study (later)

1. Run `project_init` or `setup_project` so `01_input/codebook/dataset_codebook.md` exists.
2. Fill every analysis column **before** first EDA (`SKILL_eda-flexplot`).
3. Link SAP outcomes via `sap_id` column; do not duplicate full definitions in SAP prose.

Template: `40_operations/templates/codebooks/dataset_codebook.md`.
