# NotebookLM grill prompts — user notebook 91614142

**Notebook UUID:** `91614142-303b-45b8-ad5c-91ee60b66e06`  
**Library slug (proposed):** `user-notebook-91614142`  
**URL:** https://notebooklm.google.com/notebook/91614142-303b-45b8-ad5c-91ee60b66e06

## Auth prerequisite

MCP `get_health` must report `authenticated=true`. If false:

1. Close all Chrome windows using the NotebookLM MCP profile
2. `node scripts/notebooklm-setup-auth.mjs` (or MCP `setup_auth`)
3. Verify with `get_health`

## Extraction

**MCP (preferred):** `ask_question` with `notebook_url`; reuse `session_id`; `source_format: footnotes`.

**Playwright batch:**

```powershell
python 40_operations/scripts/notebooklm_user_notebook_grill.py --discovery-only
python 40_operations/scripts/notebooklm_user_notebook_grill.py
python 40_operations/scripts/notebooklm_bridge.py export-normalize `
  --input outputs/notebooklm/user_notebook_91614142_query_batch.json `
  --output outputs/notebooklm/user_notebook_91614142_normalized.json
python 40_operations/scripts/notebooklm_bridge.py gate-report `
  --input outputs/notebooklm/user_notebook_91614142_normalized.json `
  --output outputs/notebooklm/user_notebook_91614142_gate_report.json
```

## Discovery questions (Q1–Q3)

1. List every source: title, URL, type, one-line topic; total count.
2. Central thesis in 3 sentences; actionable vs background-only for harness work.
3. Define key terms and how they relate hierarchically.

## Full grill (14 questions)

Same set as [`notebooklm_harness_skilltree_grill_prompts.md`](notebooklm_harness_skilltree_grill_prompts.md) — reuse for harness/memory/skill-tree corpora; dedup against prior Harness SkillTree cycle (`86aaaf0e-…`).

## Gate

External ledger: `30_system/docs/notebooklm_user_notebook_91614142_external_verification.json`  
Gate report: `outputs/notebooklm/user_notebook_91614142_gate_report.json`

## Classification

- If sources match HORMA, Self-Harness, HIP-If, skill tree, K1 → **Harness overlap**; delta-only vs [harness backlog](.agent/task/harness_skilltree_incorporation_backlog.md)
- Otherwise → new slug; full incorporation backlog

## Related

- [[NotebookLM research gate]]
- [[Agent harness memory and skill tree]]
