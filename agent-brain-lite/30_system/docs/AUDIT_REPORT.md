# Audit Report – Phase 1

**Date:** 2025-03-01  
**Goal:** Identify Context Bloat, Outdated Context, Ambiguity, Hiding Failures before upgrade.

---

## 1. Context Bloat

### 1.1 alwaysApply: true (Tier 0)

| Rule | Status | Note |
|------|--------|------|
| 00_orchestrator_agent.mdc | Needed | Core – shorten classification hints |
| core-principles.mdc | OK | ~120 tok, minimal |
| context-optimization.mdc | Needed | Reduce verbose descriptions |
| 99_error_memory.mdc | OK | Critical for quality |
| skills-auto-detect.mdc | Needed | Task→Skill table – summarize |

**Goal:** Reduce Tier 0 from ~1800 to ~1200–1400 tokens. **Status (2025-03):** Implemented – classification hints, context-optimization and skills-auto-detect shortened; reference tables in 30_system/behavior_rules/reference/.

### 1.2 Overly broad globs

| Rule | Glob | Problem |
|------|------|---------|
| 50_ml_mlops_standards.mdc | `**/*.py`, `**/*.R` | Loads on all R/Python – too broad |
| visualization.mdc | `**/*.R`, `**/*.Rmd` | Overlaps with statistics |
| statistics-test-selection.mdc | `**/*.R`, `**/analysis/**` | OK for domain |
| 99_error_memory.mdc | `**/*` | Always – intentional |

### 1.3 Tier 1 conflict

- `statistics-test-selection.mdc`: `**/*.R`, `**/analysis/**`
- `writing-avoid-ai.mdc`, `writing-manuscript-structure.mdc`: `**/manuscript/**`, `**/*paper*`
- `reporting-auto-detect.mdc`: `**/protocol/**`, `**/manuscript/**`, `**/*paper*`

**Problem:** `manuscript/methods.R` matches all three. Context-optimization says "MAX 1 Tier 1" but has no mechanism for selection.

---

## 2. Outdated Context

### 2.1 Does orchestrator reference non-existent files?

| Reference | Status |
|-----------|--------|
| `30_system/behavior_rules/tools/agents/agent_auto_detection.R` | EXISTS |
| `30_system/behavior_rules/tools/agents/agent_auto_detection.py` | EXISTS |
| `30_system/behavior_rules/22_pipeline_and_refinement.md` | EXISTS |
| `30_system/behavior_rules/23_figure_visualization_pipeline.md` | EXISTS |
| `30_system/behavior_rules/05_verification.md` | EXISTS |
| `.cursor/errors/error_log.jsonl` | CREATED (was empty) |

### 2.2 Architecture vs. actual structure

EXISTING_ARCHITECTURE.md matches actual structure. 30_system/behavior_rules/tools/agents/ exists.

---

## 3. Ambiguity

| Problem | Location | Solution |
|---------|----------|----------|
| "Use existing patterns" | Various agents | Precise paths, function names |
| "When critical" (Swiss Cheese) | core-principles | Enumerated – 3 points |
| "Transfer 30_system/context" (handoff) | orchestrator | Template: [HANDOFF A→B] Done: X. Next: Y. Context: ≤30 tok |
| "MAX 1 Tier 1" without priority | context-optimization | Add: If glob matches multiple → most specific |

---

## 4. Hiding Failures

| Mechanism | Status | Action |
|-----------|--------|--------|
| error_log.jsonl | Created in .cursor/errors/ | Keep |
| surprises.log | Created in .cursor/ | Agent logs confusing situations |
| learning_loop.py | EXISTS in 30_system/behavior_rules/tools/ | Integrate with audit |

---

## 5. Summary

- **Context Bloat:** Shorten Tier 0; 50_ml glob too broad; resolve Tier 1 conflict with priorities
- **Outdated:** No obsolete references
- **Ambiguity:** Handoff template; Tier 1 priority; "critical" enumerated
- **Hiding Failures:** surprises.log created; error_log.jsonl created

## Related Hubs

- [Folder index hub](FOLDER_INDEX.md)
- [All notes index](ALL_NOTES_INDEX.md)
- [Graph connectivity map](GRAPH_CONNECTIVITY_MAP.md)
