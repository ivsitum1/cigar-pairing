> **⚠️ MIGRATED** -> `.cursor/rules/visualization.mdc` (2026-05-08)

# Figure and Visualization Pipeline (PaperBanana-Style)

## Purpose

This document defines a **PaperBanana-style pipeline** (Retrieve → Plan → Render → Refine) for generating **publication-ready figures and visualizations**. It is Pipeline 5 in the overall architecture; see `30_system/behavior_rules/22_pipeline_and_refinement.md` for the general pipeline framework. Standards for figure content and export are in `30_system/behavior_rules/04_visualization.md` and Workflow 5 in `30_system/behavior_rules/09_workflow_optimization.md`.

**Version:** 1.0  
**Last updated:** 2026-04-10  
**Reference:** PaperBanana (paperbanana.org); Pipeline framework: `30_system/behavior_rules/22_pipeline_and_refinement.md`.

---

## Pipeline Stages (PaperBanana Mapping)

| PaperBanana | Figure pipeline (our system) |
|-------------|------------------------------|
| **Retrieve** | Gather context: outcomes, study type, data availability, journal/author requirements. Use protocol, `04_visualization.md`, Workflow 5. |
| **Plan** | Decide which figures are needed (forest, funnel, flow, baseline, sensitivity), for which outcomes, layout (single/multi-panel), format (PDF preferred). |
| **Render** | Generate figures: R/Python code per `04_visualization.md` and Workflow 5 (forest plots, funnel plots, sensitivity plots). Optionally, future integration with an external diagram/illustration service (e.g. PaperBanana-like) for methodology diagrams. |
| **Refine** | Check against `04_visualization.md` (elements, colours, fonts, dimensions), resolution (e.g. 300+ DPI for raster), captions; optional critic pass. |

---

## Subagents and Skills

- **Primary subagents:** STATISTICS (for analysis-derived figures: forest, funnel, sensitivity); CODE_IMPL (for code that produces figures and batch export).
- **REFINE:** Same subagent or the one most relevant (STATISTICS/CODE_IMPL) runs the checklist from `04_visualization.md` and Workflow 5 (export and verification).
- **Skill:** Use **SKILL_figure-pipeline** when the task is "figure pipeline", "all figures", "visualization for paper", or "figures for study". Within the skill, call SKILL_forest-plot, SKILL_publication-bias in sequence when applicable (e.g. meta-analysis figures).

---

## When This Pipeline Runs

The Orchestrator triggers this pipeline when the user intent matches figure/visualization workflow (e.g. "figure", "visualization", "forest plot", "methods diagram", "all figures for study"). Classification remains under STATISTICS or CODE_IMPL with pipeline flag; SKILL_figure-pipeline is loaded. See `.cursor/rules/00_orchestrator_agent.mdc` and `.cursor/rules/skills-auto-detect.mdc`.

---

## Future: External Diagram Service

For methodology diagrams (flowcharts, architecture diagrams) that are not data-driven, a future integration with an external service (e.g. PaperBanana or similar) can be added as an alternative **Render** path. This document remains the single reference for the figure pipeline; any such integration would be described here or in a dedicated integration note.

---

## References

- `30_system/behavior_rules/04_visualization.md` – forest plots, funnel plots, colours, fonts, export (PDF/PNG), resolution
- `30_system/behavior_rules/09_workflow_optimization.md` – Workflow 5: Figure Generation (planning, data prep, creation, export and verification)
- `30_system/behavior_rules/22_pipeline_and_refinement.md` – named pipelines, REFINE phase, skill sequencing
- `30_system/SKILLS/SKILL_figure-pipeline.md` – step-by-step procedure for this pipeline
- `30_system/SKILLS/SKILL_forest-plot.md`, `30_system/SKILLS/SKILL_publication-bias.md` – used in sequence when producing meta-analysis figures

---

**Status:** Active. Part of Pipeline 5 in the agent architecture.

---

## Privremeno rješenje za metodološke dijagrame

Dok eksterni servis za dijagrame ne bude integriran, za **metodološke dijagrame bez podataka** (npr. flowchart studije, dijagram arhitekture analize) koristi:

- **Mermaid** unutar R Markdown / Quarto ili Markdown dokumenata (npr. `flowchart TD ...`) za CONSORT/PRISMA/STROBE sheme.
- Ili jednostavne blok dijagrame opisane u tekstu (koraci numerirani 1–N) kada Mermaid nije dostupan.

Ove dijagrame možeš tretirati kao dio Pipeline 5 (PLAN + RENDER), ali za njih ne treba generirati kod u R/Pythonu – dovoljno je strukturirano tekstualno ili Mermaid rješenje.

## Related Hubs

- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
