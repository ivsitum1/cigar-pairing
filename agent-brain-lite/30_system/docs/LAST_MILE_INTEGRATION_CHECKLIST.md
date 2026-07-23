# Last-mile integration checklist (MILE-3)

**Source:** last-mile-glm notebook | **Machine:** US-36 | **Map:** `LAST_MILE_GLM_MAP.md`

## Rent vs build (strategic engineering)

Before adding a dependency, MCP server, or parallel orchestrator:

1. **Existing seam:** Can an existing skill, script, or `.mdc` rule cover 80% of the need?
2. **Ownership:** Who maintains it across PCs (OneDrive, junction health, MCP governance)?
3. **Evidence:** Is the claim VERIFIED (repo, doc, test) or UNVERIFIED (video, benchmark tweet)?
4. **Rollback:** Can we disable with one env flag or delete one spike doc without breaking Tier 0?
5. **Clinical risk:** Does it touch PHI, dosing, or manuscript numbers? → Primary stop-the-line applies.

## project_init last-mile steps

After `python 40_operations/scripts/project_init.py <name>`:

| Step | Action |
|------|--------|
| 1 | Confirm `30_system/04_documentation/context/main.md` has PICO/deliverables |
| 2 | Link brain: `.cursor` junction + `write_project_scope_file` |
| 3 | Seed `01_input/literature/` and extraction codebook |
| 4 | Run `brain_health.py` from brain root (optional `--strict`) |
| 5 | For SR/MA: load `SKILL_meta-analysis` + `meta_analysis_pdf_trace.md` before PDF extraction |

## Integration vs new stack (grill-me prompts)

Use when NotebookLM or digest proposes LangGraph, Zapier MCP, or second wiki index:

- *Which existing orchestrator path already handles this handoff?*
- *What breaks if we add a parallel `knowledge-index.md` or `global-orchestrator.md`?*
- *Is the integration one script behind a deep module interface, or a new product?*

## omo / harness patterns (US-31)

From oh-my-openagent spike — adopt in brain repo:

1. **Failure log → contract:** Repeated tool failures → `harness_failure_analyze.py` suggests deterministic rule snippet (no auto-apply).
2. **Prescreen before retry:** MCP/tool schema check before blind retry loop (`harness_tdd.mdc` phase 1).

## Reject (human gates confirmed)

- GLM 5.2 cost benchmarks without primary source
- JEPA / world-model training inside brain repo
- Einstein world-module MCP without solver libraries

## Verification

```bash
python 40_operations/scripts/project_init.py --help
python 40_operations/scripts/harness_failure_analyze.py --json
```
