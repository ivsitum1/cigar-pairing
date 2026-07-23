# Awakening Ritual – Discovery Session Start

## Purpose

At the **optional** start of a full Discovery run (Pipeline 7B), the Awakening Ritual loads recent context and produces a short **state summary** so the engine can avoid re-discovering the same directions and respect prior decisions. It does not run automatically on every chat; it is triggered when the Orchestrator begins a 7B run and the pipeline specifies the optional Step 1 (Awakening).

**Reference:** Discovery Super-pipeline: `30_system/behavior_rules/26_discovery_superpipeline.md` (Step 1); capability registry: `30_system/behavior_rules/25_capability_registry.md` (AwakeningAgent).

---

## Inputs (what to read)

| Source | Path | Content |
|--------|------|---------|
| Memory | `.agent/MEMORY.md` | High-level tasks and milestones (last ~30 lines if large) |
| Handoff log | `.agent/handoff_log.jsonl` or MCP handoff | Recent agent handoffs; last Discovery run if present |
| OTA log | `30_system/04_documentation/context/log.md` | Last N entries (e.g. 10–20); focus on discovery/design entries |
| Commit / phase | `30_system/04_documentation/context/commit.md` | Current phase, completed, next (if present) |

If a vector store (e.g. ChromaDB) or knowledge-framework store exists, the ritual may optionally query recent embeddings or framework list and include a one-line summary (e.g. "K frameworks available"); this is optional and not required for the ritual to run.

---

## Output: state summary

The AwakeningAgent (WRITING subagent) produces a **short state summary** (1–3 paragraphs or bullet list) that includes:

1. **Recent domains** – Which disease/therapy/method areas were last explored (from MEMORY and log).
2. **Prior directions** – Which research directions or hypotheses were already prioritised or abandoned (from handoff and log).
3. **Open gaps** – Any unresolved gaps or follow-ups explicitly noted in MEMORY or commit.

This summary is passed into the next step (ContextLoader) so that the rest of the pipeline can avoid duplicate work and align with the user’s prior choices.

---

## When the ritual runs

- **Pipeline 7B:** Optional Step 1 in `26_discovery_superpipeline.md` (Cluster 1). If omitted (e.g. first run or no filled `30_system/04_documentation/context`), Step 2 (load `.agent/README.md` and `30_system/04_documentation/context/*`) still runs.
- **Pipeline 7A:** No awakening step; context loading in `24_discovery_pipeline.md` is sufficient.

---

## Script (optional)

For an automated state summary before or at Step 1 of Pipeline 7B, run:

```bash
python 40_operations/scripts/awakening.py
```

Options: `--lines N` (default 20), `--memory-path`, `--handoff-path`, `--log-path`, `--commit-path`. The agent in Step 1 can use this script’s stdout or read the same sources manually.

---

## Version

**Version:** 1.0  
**Status:** Optional component of Pipeline 7B. Implemented by adopting AwakeningAgent role and reading the above paths, or by running `40_operations/scripts/awakening.py`.

## Related Hubs

- [Folder index hub](../../30_system/docs/FOLDER_INDEX.md)
- [All notes index](../../30_system/docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
