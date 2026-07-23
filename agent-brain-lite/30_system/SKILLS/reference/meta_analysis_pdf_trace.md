# Meta-analysis PDF trace workflow (OKF-4)

**Source:** okf-knowledge notebook grill | **Gate:** GO  
**MCP:** `pdf` server (`read_pdf`, `search_pdf`, `pdf_evidence`)

## When to use

- Full-text screening during SR/MA
- Extracting effect sizes from PDF tables/figures
- PRISMA flow reconciliation (included study count vs PDF set)
- AI-assisted visualization of forest/summary data **after** human-verified extraction

## Workflow

### 1. Register PDFs

Place under project `01_input/literature/` or link from screening sheet. One folder per review slug.

### 2. Twin + search

```
read_pdf(path, auto=true)     → Agent Document Twin (structured text)
search_pdf(path, query)       → Cheap literal hit list
pdf_evidence(path, region)    → Crop/OCR for tables and figures
```

**Prefer twin** for narrative Methods/Results; **prefer pdf_evidence** for numeric tables.

### 3. Extraction trace (reproducibility)

For each included study, log in `02_analysis/extraction/pdf_trace.jsonl`:

```json
{"study_id": "Smith2024", "pdf": "01_input/literature/smith2024.pdf", "pages": [4, 5], "tool": "pdf_evidence", "extractor": "human|agent", "field": "OR_95CI"}
```

Agent-proposed values stay `[INFERRED]` until human marks verified in codebook.

### 4. PRISMA linkage

| PRISMA item | PDF trace role |
|-------------|----------------|
| 6–7 Search | N/A (database exports) |
| 10 Included studies | PDF list matches `included_studies.csv` |
| 13a Study characteristics | Twin excerpts → extraction form |
| 20a Results per study | Figure/table evidence via pdf_evidence |

Use `SKILL_prisma-checklist` for full item list.

### 5. Meta-analysis handoff

Extracted numeric fields → `02_analysis/ma_dataset.csv` → Part II of `SKILL_meta-analysis.md`.

Do not pool from PDF prose without structured extraction row.

## Anti-patterns

- Pooled estimate from LLM reading of forest plot image without numeric extract
- Skipping RoB because abstract twin looked sufficient
- Using NotebookLM video claims as effect sizes (UNVERIFIED)

## Related maps

- `30_system/docs/OKF_KNOWLEDGE_MAP.md`
- `30_system/docs/RAG_ANATOMY_MAP.md` (when to use books_rag vs full PDF)
- `30_system/docs/bridges/pdf_md_map.md`
