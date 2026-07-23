# LOOP-3: Self-improving knowledge base pipeline

**Notebook:** loop-of-loops | **Gate:** GO | **Maps:** `LOOP_OF_LOOPS_MAP.md`, AGENT_AUTONOMY §6

## Intent

Claude + Obsidian pattern from the notebook maps to **existing** brain skills — not a second orchestrator.

## Pipeline (minimal loop)

```mermaid
flowchart LR
  ingest[wiki-ingest / data-ingest] --> daily[daily-update]
  daily --> synth[wiki-synthesize]
  synth --> lint[wiki-lint]
  lint --> human[Human gate every 3rd cycle]
```

| Stage | Skill | Output |
|-------|-------|--------|
| Ingest new sources | `wiki-ingest`, `obsidian-wiki-ingest`, `ingest-url` | New/updated pages under vault |
| Freshness + index | `daily-update` | `index.md`, `hot.md`, stale manifest |
| Cross-concept synthesis | `wiki-synthesize` | `synthesis/*.md` pages |
| Quality | `wiki-lint` | Fix wikilinks, frontmatter |
| Brain handoff | `wiki-stage-commit` | Git commit when user approves |

## Stop conditions (loop-of-loops)

- **Stop:** lint errors > threshold, or user `[AUTONOMOUS STOP]`
- **Human gate:** every 3rd full cycle before Tier 0 rule edits or bulk rename
- **Do not:** auto-edit `.cursor/rules` from synthesis prose

## Handoff file (MVP)

Path: `.agent/task/loop_<YYYYMMDD>_handoff.md`

```markdown
Completed: [one sentence]
Next: [wiki-synthesize | daily-update | ...]
Blockers: [none | list]
Human_gate_needed: yes | no
Cycle: n/3
```

## STORM alignment

Multi-perspective research → `research-grill-me` + eval case `case_storm_multi_perspective` in `evals/research-grill-me.json`. Full STORM skill deferred (LOOP-2 seed only).

## Verification

```bash
# Dry run daily cycle (manual in agent session)
# /daily-update per daily-update SKILL

# After ingest batch
python 40_operations/scripts/obsidian_connectivity_check.py  # if configured
```

## Related

- `.cursor/docs/AGENT_AUTONOMY_AND_PARALLEL.md` §6
- `.agent/task/notebooklm_batch_2026-06_backlog.md` (LOOP-3 ✅, LOOP-4 ✅ `wiki_nested_loop.py`)
