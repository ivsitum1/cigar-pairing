# NotebookLM batch grill prompts — 2026-06

**Config:** [`notebooklm_batch_2026-06_questions.json`](notebooklm_batch_2026-06_questions.json)  
**Orchestrator:** `python 40_operations/scripts/notebooklm_batch_grill.py`  
**First-run:** [`.agent/task/NOTEBOOKLM_BATCH_2026-06_FIRST_RUN.md`](../../../.agent/task/NOTEBOOKLM_BATCH_2026-06_FIRST_RUN.md)

## Notebooks

| Slug | ID |
|------|-----|
| okf-knowledge | `8e1995f8-1721-4624-bbe0-92cd4f6a31ba` |
| last-mile-glm | `604aa4bf-7261-407c-9af3-e5f407f1e5f0` |
| humanize-predictability | `5b10b85d-f085-4ff3-a293-69bfe614298b` |
| loop-of-loops | `c1280bad-7406-43f1-bc45-d6bb91502114` |

## Pass 1 (14 = 8 common + 6 topic)

See JSON `common` + `topic[slug]`.

## Pass 2 (6 follow-up)

See JSON `pass2`.

## Commands

```bash
# Pass 1 — all notebooks
python 40_operations/scripts/notebooklm_batch_grill.py --pass 1

# Pass 2 — after source expansion
python 40_operations/scripts/notebooklm_batch_grill.py --pass 2

# Post-process (normalize, gate, docs)
python 40_operations/scripts/notebooklm_batch_postprocess.py --all
python 40_operations/scripts/notebooklm_batch_postprocess.py --slug okf-knowledge --pass 2
```

## Dedup anchors

- humanize-predictability → `outputs/notebooklm/humanize_ai_vs_agent_rules_delta.md`
- loop-of-loops → Harness SkillTree, Ralph, wiki skills
- okf-knowledge → RAG Anatomy, RAG Chunking, wiki manifest
