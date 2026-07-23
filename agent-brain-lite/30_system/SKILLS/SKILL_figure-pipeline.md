---
name: figure-pipeline
description: Use when multiple publication figures are needed; for a single forest plot use forest-plot directly Triggers include: figure pipeline, publication figures, all figures, visualization for paper.
version: 1.1
last_updated: 2026-03-30
domain: figures
tokens: ~850
triggers:
  - figure pipeline
  - publication figures
  - all figures
  - visualization for paper
requires_packages: []
reference_files: []
pipeline_position: [5]
---

# Skill: Figure Pipeline (Publication-Ready Figures)

## When to use

Use this skill when:
- User requests full figure workflow for a study ("all figures", "figures for study", "visualization for paper")
- Multiple figure types are needed (forest, funnel, sensitivity, baseline)
- Publication-ready figures from analysis results or data

## Prerequisites

- Analysis results or data suitable for figures (or clear list of required figure types)
- Standards: `30_system/behavior_rules/04_visualization.md`, Workflow 5 in `30_system/behavior_rules/09_workflow_optimization.md`
- Pipeline context: `30_system/behavior_rules/23_figure_visualization_pipeline.md`

## Step-by-step procedure

1. **Plan figures:**
   - Identify required figures (forest, funnel, sensitivity, flow, baseline tables as figures)
   - Map each figure to outcome(s) and data source
   - Decide layout (single panel, multi-panel) and format (PDF preferred; PNG/TIFF ≥300 DPI if required)

2. **Data preparation:**
   - Prepare data for each figure type
   - Check data quality and missing values
   - Document any transformations

3. **Create figures per standards:**
   - Follow `30_system/behavior_rules/04_visualization.md` (elements, colours, fonts, dimensions)
   - Follow Workflow 5 in `30_system/behavior_rules/09_workflow_optimization.md` (planning → data prep → creation → export)
   - For meta-analysis figures: apply SKILL_forest-plot then SKILL_publication-bias (funnel) in sequence when applicable
   - Use R/Python code templates from 04_visualization (e.g. forest, funnel, bubble, sensitivity plots)

4. **Export and verification:**
   - Export to PDF (vector) or PNG/TIFF at ≥300 DPI
   - Verify resolution and readability
   - Draft figure captions
   - Cross-check against 04_visualization checklist (required elements, colour scheme, labels)

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Trebam sve figure za rad u jednom prolazu (300 DPI, konzistentne oznake)."  
**Output:** "Popis figura i redoslijed `[EXTRACTED]` iz uputa; export postavke `[VERIFIED]` nakon provjere datoteka; figura bez podataka `[BLANK]`."

## Verification checklist

- [ ] All planned figures created
- [ ] Each figure meets 04_visualization standards (elements, colours, fonts)
- [ ] Export format and resolution correct (PDF or ≥300 DPI)
- [ ] Captions drafted
- [ ] When applicable: forest plot and publication-bias (funnel) steps completed

## Related rules

- `30_system/behavior_rules/04_visualization.md`
- `30_system/behavior_rules/09_workflow_optimization.md` (Workflow 5)
- `30_system/behavior_rules/23_figure_visualization_pipeline.md`
- SKILL_forest-plot.md, SKILL_publication-bias.md (use in sequence for meta-analysis figures)

## Learning integration

- **task_type:** visualization
- **log_fields:** figure_types, export_format, packages_used
- **post_step:** After completing procedure: output LEARNING_BLOCK (see `30_system/behavior_rules/14_learning_loop.md`) for ingestion.

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
