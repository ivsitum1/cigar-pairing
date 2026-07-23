# NotebookLM grill prompts — Harness Memory v2

**Notebook ID:** `f9554fae-424f-434a-ab64-bbd873804627`  
**Library ID:** `harness-memory-v2`  
**URL:** https://notebooklm.google.com/notebook/f9554fae-424f-434a-ab64-bbd873804627

## Extraction

**MCP (preferred):** `ask_question` with `notebook_url`; reuse `session_id`; `source_format: json` for programmatic citations.

```bash
python 40_operations/scripts/notebooklm_grill_playwright.py \
  --notebook-url "https://notebooklm.google.com/notebook/f9554fae-424f-434a-ab64-bbd873804627" \
  --questions-file 30_system/docs/reference/notebooklm_harness_v2_questions.json \
  --output outputs/notebooklm/harness_v2_query_batch.json

python 40_operations/scripts/assemble_harness_v2_batch.py
python 40_operations/scripts/notebooklm_bridge.py export-normalize \
  --input outputs/notebooklm/harness_v2_query_batch_merged.json \
  --output outputs/notebooklm/harness_v2_normalized.json
python 40_operations/scripts/notebooklm_bridge.py gate-report \
  --input outputs/notebooklm/harness_v2_normalized.json \
  --output outputs/notebooklm/harness_v2_gate_report.json
```

Output batch: `outputs/notebooklm/harness_v2_query_batch_merged.json`

## Grill questions (14 pass 1 + 6 pass 2)

See [`notebooklm_harness_v2_questions.json`](notebooklm_harness_v2_questions.json).

## Gate

External ledger: `30_system/docs/notebooklm_harness_v2_external_verification.json`  
Gate report: `outputs/notebooklm/harness_v2_gate_report.json`

**Policy (inherited from v1 cycle):**
- Self-harness proposals: human gate every **3rd** iteration
- K1: clinical priority research spike before implementation
- Reward decay: implement in skill_rerank / verifier eval

## Related notebooks (dedup)

| Notebook | Dedup |
|----------|-------|
| Agent Harness SkillTree (86aaaf0e) | Prior cycle — extend, do not duplicate |
| SkillDAG | Tree = grouping; DAG = routing |
| Geometry of Intelligence | Model-native / LifeHarness L1–L4 |
| Humanize AI | No substantive overlap |

## Semantic graph (auto)

- [[Agent harness memory and skill tree]]
- [[SkillDAG]]
- [[NotebookLM research gate]]
- [FOLDER INDEX](../FOLDER_INDEX.md)
