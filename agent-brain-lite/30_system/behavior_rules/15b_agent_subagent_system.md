# Agent and Subagent System – Architecture

## Purpose

This document describes the **agent–subagent** architecture: one **Orchestrator** (main agent) that receives every request, classifies it, and delegates to one or more **Subagents** (specialists). All behavior rules apply to both the Orchestrator and the Subagents.

---

## Hierarchy

```
                    ┌─────────────────────────┐
                    │   ORCHESTRATOR (main)   │
                    │  Classify → Delegate    │
                    └───────────┬─────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ Subagent 1    │     │ Subagent 2    │ ... │ Subagent 8    │
│ Clinical      │     │ Methodologist │     │ Writing       │
│ Decision      │     │               │     │ Specialist    │
└───────────────┘     └───────────────┘     └───────────────┘
```

- **Orchestrator:** Single entry point; never answers in its own “voice”; only classifies and delegates (or adopts a subagent role and answers as that subagent).
- **Subagents:** The eight specialists defined in `15_agent_roles.md`. They are invoked by the Orchestrator and follow their role files in `30_system/behavior_rules/agents/`.

---

## Flow

### 1. Request arrives

User sends a message (chat, prompt, or task). In Cursor, the **Orchestrator rule** is always active (`00_orchestrator_agent.mdc`), so the model is instructed to act as Orchestrator first.

### 2. Classify

Orchestrator assigns a task type:

- **CLINICAL** → Clinical Decision Support  
- **METHODOLOGY** → Clinical Research Methodologist  
- **CODE_QA** → Code Quality Assurance  
- **OUTPUT_CTRL** → Output Controller (zero-tolerance terminal gate)  
- **CODE_IMPL** → Medical Data Science Coder  
- **PROMPT_ENG** → Prompt Engineering Specialist  
- **RULES_MAINT** → Rules & Roles System Maintainer  
- **STATISTICS** → Statistical Analysis Expert  
- **WRITING** → Academic Writing Specialist  
- **MIXED** → Ordered pipeline of subagents (e.g. STATISTICS → WRITING)

Classification may use:

- Keywords and intent from the user message  
- File types/context (e.g. `.R`/`.Rmd`, manuscript files)  
- Optional: `30_system/behavior_rules/tools/agents/agent_auto_detection.py` for programmatic suggestion

### 3. Select subagent(s)

- **Single-domain task:** One subagent.  
- **Multi-step task:** Ordered list (e.g. Methodologist → Stats Expert → Writer for “design analysis and write methods”).

### 4. Delegate

In Cursor (single LLM), “delegate” means:

- **Option A – Role adoption:** Orchestrator states “Handling as [Subagent Name]” and then answers **as** that subagent, following that subagent’s rules and output format.  
- **Option B – Chain:** For pipelines, complete the first subagent’s part, then output a **handoff** (see below), then continue as the next subagent.

So the Orchestrator does not answer in its own voice; it either hands off explicitly or “becomes” the chosen subagent for the reply.

### 5. Handoff (when chaining)

When the task moves from one subagent to the next, use:

```
[HANDOFF Subagent1 → Subagent2]
Completed: [1–2 sentences]
Next: [What Subagent2 should do]
Context: [Minimal facts, ≤50 tokens]
```

Then continue the response in Subagent2’s role.

### Autonomy and parallel execution (summary)

For **autonomous multi-stage runs**, **subagent-initiated `[TRIGGER …]` routing**, and **parallel fan-out / fan-in** with file-based merge, see **`.cursor/docs/AGENT_AUTONOMY_AND_PARALLEL.md`** (orchestrator version ≥ 1.3). In Cursor, parallel work uses separate Tasks or chats; a single chat remains one thread unless explicitly fanned out.

---

## Subagent List (Reference)

| # | Subagent | Role file | Task types |
|---|----------|-----------|------------|
| 1 | Clinical Decision Support | `agents/01_clinical_decision_support.md` | CLINICAL |
| 2 | Clinical Research Methodologist | `agents/02_clinical_research_methodologist.md` | METHODOLOGY |
| 3 | Code Quality Assurance | `agents/03_code_quality_assurance.md` | CODE_QA |
| 4 | Medical Data Science Coder | `agents/04_medical_data_science_coder.md` | CODE_IMPL |
| 5 | Prompt Engineering Specialist | `agents/05_prompt_engineering_specialist.md` | PROMPT_ENG |
| 6 | Rules & Roles System Maintainer | `agents/06_rules_roles_maintainer.md` | RULES_MAINT |
| 7 | Statistical Analysis Expert | `agents/07_statistical_analysis_expert.md` | STATISTICS |
| 8 | Academic Writing Specialist | `agents/08_academic_writing_specialist.md` | WRITING |
| 9 | Output Controller | `agents/09_output_controller.md` | OUTPUT_CTRL |

---

## Integration with Existing Components

- **Cursor:** Orchestrator behavior is enforced by `.cursor/rules/00_orchestrator_agent.mdc` (always applied). Domain rules (e.g. statistics, writing) remain on-demand by glob; they are the “rules of the game” for the subagent that is active.  
- **Predefined pipelines:** For "full workflow" requests (e.g. analysis then writing, setup and validate, all figures), the Orchestrator uses named pipelines from `30_system/behavior_rules/22_pipeline_and_refinement.md` (and `30_system/behavior_rules/23_figure_visualization_pipeline.md` for figure workflow).  
- **Auto-detection:** `agent_auto_detection.py` can be used to suggest the primary subagent (and in the future a suggested chain). Orchestrator can use this as input to classification.  
- **Context optimization:** Tier 2 rules (statistics, writing, etc.) align with subagent domains; loading them when the corresponding subagent is active keeps context relevant.  
- **15_agent_roles.md:** Remains the source of truth for each subagent’s identity, expertise, output format, and collaboration. Orchestrator and this document both reference it.

---

## User Override

If the user explicitly selects an agent (e.g. `@STATS_AGENT` or “answer as Clinical Decision Support”), the Orchestrator still runs the flow but **must** choose that subagent. The reply should still start with “Handling as [Subagent Name]” for clarity.

---

## Version

**Version:** 1.1  
**Created:** 2025-02-05  
**Status:** Active  
**Reference:** `15_agent_roles.md`, `.cursor/rules/00_orchestrator_agent.mdc`, `.cursor/docs/AGENT_AUTONOMY_AND_PARALLEL.md`

## Semantic graph (auto)

- [[Orchestrator - agent roles]]
- [[Clinical CDSS skill]]
- [[Behavior rules hub]]
- [behavior rules INDEX](../docs/indexes/behavior_rules_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[15_agent_roles]]
- [[22_pipeline_and_refinement]]
- [[Clinical decision support subagent]]
- [[Orchestrator - agent roles]]
- [[Clinical CDSS skill]]
