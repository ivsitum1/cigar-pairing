# Discovery Pipeline – Autonomous Discovery Engine

## Purpose

This document defines the **Discovery Pipeline** that turns the conceptual Autonomous Discovery Engine into a concrete, operable workflow on top of the existing agent-rules brain.

The pipeline is designed for tasks where the primary goal is **systematic discovery and gap-finding**, not only execution of a predefined protocol. Typical intents:

- Explore **research directions** in a disease / method / therapy area
- Identify **knowledge gaps** and opportunities for new studies
- Draft **high‑level experimental or trial concepts** before formal protocols

The Discovery Pipeline follows a five‑stage structure adapted from the PaperBanana Retrieve → Plan → Render → Refine model:

- **RETRIEVE** – gather project context and initial knowledge
- **DISCOVER** – search external sources and map gaps
- **PLAN** – organise candidate hypotheses / research directions
- **EXECUTE** – sketch one or more priority paths at high level
- **REFINE** – critique, consolidate, and log learnings

It complements, not replaces, existing Pipelines 1–6 in `30_system/behavior_rules/22_pipeline_and_refinement.md`.

---

## Discovery Pipeline – Stage Table

### Overview

| Stage     | Primary subagent | Optional skills / tools                         | Output artefact                                  |
|----------|------------------|--------------------------------------------------|--------------------------------------------------|
| RETRIEVE | WRITING or METHODOLOGY | Context loading (project docs, protocol stubs) | Short context brief + clarified discovery goal   |
| DISCOVER | WRITING          | `SKILL_literature-synthesis` (when appropriate) | Literature grid, preliminary gap statements      |
| PLAN     | METHODOLOGY      | (future) discovery‑specific skills              | Ranked list of hypotheses / research directions  |
| EXECUTE  | METHODOLOGY (+ STATISTICS when needed) | Existing design/analysis skills as references | High‑level design sketches for 1–2 top directions |
| REFINE   | WRITING + RULES_MAINT (optional) | Learning Loop integration, Swiss‑Cheese principles | Consolidated discovery note + LEARNING_BLOCK     |

Notes:

- Subagents are re‑used from the existing system (no new agent type is required).
- The Discovery Pipeline focuses on **what to explore and why**; detailed protocol and analysis work then proceeds via Pipelines 1–6.

---

## Stage Definitions

### Stage 1 – RETRIEVE (Context Collection)

**Goal:** Build a compact understanding of the current project/state before exploring new directions.

- **Subagent:** WRITING (for narrative project context) or METHODOLOGY (for protocol-centric project context), depending on the task.
- **Typical inputs:**
  - `.agent/README.md` (if present)
  - `30_system/04_documentation/context/main.md`, `commit.md`, `log.md` (latest entries)
  - Any user‑supplied description of domain, constraints, or goals
- **Output:** 1–3 paragraph context brief that answers:
  - What is already known / in scope?
  - What is the user trying to discover (directions, gaps, designs, etc.)?

This stage may be implicit when the user gives a very clear, self‑contained description; otherwise, it should be run explicitly.

---

### Stage 2 – DISCOVER (External Knowledge and Gaps)

**Goal:** Use external data sources to understand the state of the art and locate **gaps** worth exploring.

- **Subagent:** WRITING
- **Skills / tools:**
  - `SKILL_literature-synthesis` when the task resembles a mini‑review or structured literature pass.
  - MCP tools (see “MCP Integration” below) for PubMed and repository inspection.
- **Activities (conceptual):**
  - Run 1–3 **structured literature searches** via PubMed MCP using:
    - Core disease/therapy/method keywords
    - Filters by study type when relevant (RCTs, cohort, etc.)
  - Extract key themes:
    - Common outcome measures
    - Frequently used designs
    - Known limitations or open questions
  - Draft preliminary **gap statements**, each in the form:
    - “Despite X, there is limited evidence on Y in population Z / context W.”
- **Output:**
  - Compact **literature grid** (topics × study types or outcomes)
  - 2–5 draft **gap statements**.

DISCOVER should remain **breadth‑oriented**: map the space and identify promising voids without yet committing to a single design.

---

### Stage 3 – PLAN (Candidate Directions and Prioritisation)

**Goal:** Turn gaps into concrete, structured **research directions**.

- **Subagent:** METHODOLOGY
- **Inputs:**
  - Context brief from RETRIEVE
  - Literature grid and gap statements from DISCOVER
- **Activities:**
  - For each gap statement, propose one or more:
    - **Research questions** (RQ)
    - **Study archetypes** (e.g. RCT, prospective cohort, diagnostic accuracy study, mechanistic lab study)
  - Score or at least **qualitatively rank** directions using criteria such as:
    - Feasibility (data availability, sample size, logistics)
    - Potential impact (clinical or scientific)
    - Alignment with user constraints (resources, timelines)
- **Output:**
  - Short, ranked list (e.g. 2–4) of **candidate directions**, each with:
    - RQ, proposed design type, high‑level rationale.

This list forms the menu from which EXECUTE will choose 1–2 directions for deeper sketching.

---

### Stage 4 – EXECUTE (High‑Level Design Sketches)

**Goal:** For one or two priority directions, produce high‑level **design sketches** that can later be formalised by existing pipelines.

- **Subagent:** METHODOLOGY (primary) ± STATISTICS (for early analysis considerations).
- **Inputs:**
  - Prioritised directions from PLAN.
- **Activities:**
  - For each selected direction:
    - Outline **PICO** (or equivalent abstract structure).
    - Suggest **primary and key secondary outcomes** (without over‑specifying).
    - Propose a **basic design**:
      - RCT / observational / diagnostic / mechanistic etc.
      - Rough sample size scale (small pilot vs large study) without numeric power calculations.
    - Map which existing **pipelines/skills** would follow:
      - e.g. “For this direction, use Pipeline 4 (Manuscript from scratch) with CONSORT/PRISMA/STROBE variant.”
- **Output:**
  - 1–3 design sketches, each no more than a page equivalent, suitable as a starting point for full protocol work via Pipelines 1–6.

EXECUTE **must not** jump ahead to full SAPs, sample size calculations, or manuscript drafting; those belong to downstream pipelines.

---

### Stage 5 – REFINE (Critique and Learning)

**Goal:** Critically review the proposals, record trade‑offs, and update the learning system.

- **Subagent:** WRITING, with optional RULES_MAINT for rule‑level changes.
- **Inputs:**
  - Design sketches from EXECUTE.
- **Activities:**
  - Apply a light‑weight **Swiss Cheese** mindset:
    - Identify obvious feasibility risks, bias sources, or ethical red flags.
    - Flag where more formal verification (full SKILL_swiss-cheese) is required later.
  - Compare directions:
    - Note **dominant direction(s)** vs backup options.
    - Record reasons (pros/cons) so they are visible in future sessions.
  - Generate a **LEARNING_BLOCK** per **`30_system/behavior_rules/14_learning_loop.md`** (format and ingestion: same file; do not duplicate here).
- **Output:**
  - Short **Discovery Note** summarising:
    - Context, key gaps, top directions, chosen sketch(es), and main caveats.
  - A structured **LEARNING_BLOCK** object ready for `learning_loop.py` (schema: `14_learning_loop.md`).

---

## MCP Integration in RETRIEVE and DISCOVER

The Discovery Pipeline relies on MCP exclusively for external data access, following `.cursor/docs/MCP_AND_SKILLS_LAYERS.md`.

### MCP Sources

Current relevant MCP servers (as configured in `.cursor/mcp.json`):

- **PubMed MCP** – literature search and retrieval.
- **Filesystem / Git MCP** – inspection of local project structure, history, and documentation.
- **PDF MCP** – reading existing PDFs when needed.

Future sources (e.g. ChEMBL, UniProt, docking tools) can be added as new servers and invoked from the same stages without changing the Discovery logic.

### RETRIEVE Stage – MCP Usage

- Primary focus is on **local context**:
  - Read `.agent/README.md` and, if present, `30_system/04_documentation/context/{main,commit,log}.md` using filesystem MCP or standard file tools.
  - Optionally inspect recent git history for relevant changes in analysis/manuscript files.
- PubMed is **not mandatory** here; RETRIEVE can be entirely local if the user already provides rich context.

### DISCOVER Stage – MCP Usage

- PubMed MCP is the **main external source**:
  - Perform a small number of focused searches rather than broad scrapes.
  - Use query templates such as:
    - `[disease] AND [intervention] AND [outcome]`
    - `[method] AND validation` etc.
  - Retrieve only **metadata and abstracts** necessary to infer patterns; do not replicate full articles.
- Filesystem/Git MCP may be used to:
  - Check for prior analyses or manuscripts in the same domain within the current repository.

### No Hard‑coded Data

- Discovery skills and this pipeline **must not** embed PubMed results or other external data verbatim in rule files.
- All concrete data retrieval occurs at runtime through MCP, keeping this document as **pure process logic**.

---

## Learning Loop Hook – LEARNING_BLOCK for Discovery

The Discovery Pipeline integrates with the Learning Loop in **`30_system/behavior_rules/14_learning_loop.md`**.

**LEARNING_BLOCK format (including optional fields and Pipeline 7B extensions):** defined only in `14_learning_loop.md` — do not duplicate here. For ingestion, use `30_system/behavior_rules/tools/ingest_learning_block.py` as documented in `14_learning_loop.md`.

Patterns derived from Discovery sessions can justify updates to this pipeline or to specific skills.

---

## MVP Discovery Workflow (First Operational Version)

This section defines a minimal, yet useful, **first version** of the Autonomous Discovery Engine.

### Inputs

- User provides:
  - Domain (disease, therapy, method, or topic),
  - Goal (e.g. “novel research questions”, “trial design options”, “is meta-analysis feasible”),
  - Any hard constraints (data availability, population, setting, resources).

### Steps (MVP)

1. **RETRIEVE**
   - Summarise project context (local docs + user prompt).
   - Clarify the discovery question in one paragraph.
2. **DISCOVER**
   - Run 1–2 structured PubMed searches using MCP.
   - Extract 3–7 key points (themes, consistent findings, obvious limitations).
   - Draft 2–4 preliminary gap statements.
3. **PLAN**
   - For each gap statement, propose at least one research question and candidate design type.
   - Rank 2–4 directions qualitatively.
4. **EXECUTE**
   - For 1–2 top directions:
     - Sketch PICO,
     - Name candidate outcomes and design archetype,
     - Indicate which existing pipeline(s) and skills would be used next.
5. **REFINE**
   - Briefly check internal consistency and feasibility.
   - Choose one “primary” direction and optionally note 1–2 backups.
   - Emit a LEARNING_BLOCK for the session.

### Outputs (MVP)

At the end of an MVP Discovery run, the user should have:

- A concise **Discovery Summary**,
- A ranked list of **research directions** with rationale,
- At least one **design sketch** ready to be elaborated by Pipelines 1–6.

---

## Awakening Ritual – Discovery Variant (Optional)

The general Awakening Ritual concept is outlined in `.cursor/docs/DISCOVERY_ENGINE.md`. For Discovery, an optional light‑weight variant can be:

### Inputs for Awakening

- `.agent/MEMORY.md` – past high‑level tasks and milestones.
- `.agent/handoff_log.jsonl` – recent agent handoffs, including previous Discovery runs if logged.
- `30_system/04_documentation/context/log.md` – last N entries, especially those tagged as discovery or design changes.

### Awakening Summary

When starting a new Discovery session, the engine can:

- Read these sources,
- Produce a **short state summary** such as:
  - Which domains have been recently explored,
  - Which directions were previously prioritised or abandoned,
  - Any unresolved gaps flagged in earlier Discovery notes.

This summary does not change the pipeline stages but helps avoid **re‑discovering** identical directions without acknowledging prior decisions.

Implementation of a full `AWAKENING_RITUAL.md` can extend this section; for now it is treated as an optional add‑on.

---

## QA, Metrics, and Iteration

To ensure the Discovery Pipeline improves over time, connect it to the evaluation metrics defined in `30_system/behavior_rules/14_learning_loop.md`.

### Suggested Metrics for Discovery

- **Discovery usefulness (subjective):**
  - Proportion of sessions where the user adopts at least one suggested direction or design sketch.
  - Qualitative user feedback on clarity and novelty.
- **Directional efficiency:**
  - Frequency of “dead ends” where directions are later abandoned as infeasible or irrelevant.
  - Time from Discovery output to first concrete downstream action (e.g. protocol drafting, data extraction).
- **Process stability:**
  - Consistency of stage completion (avoid skipping DISCOVER or REFINE in complex tasks).
  - Self‑assessment scores for Discovery tasks over time.

### Review and Adaptation Cycle

- **Monthly (or similar cadence):**
  - Use Learning Loop analysis tools (`learning_loop.py analyze` / `recommend`) focusing on `task_type == "discovery"`.
  - Identify:
    - Recurring successful strategies (e.g. certain query templates, framing styles),
    - Failure patterns (e.g. overly broad questions, missing constraints).
  - Propose adaptations:
    - Adjust recommended number of PubMed searches,
    - Tighten or relax criteria for prioritising directions,
    - Add micro‑rules (e.g. always frame gaps in PICO terms before PLAN).
- **Documentation:**
  - When a change is adopted, briefly document:
    - What changed in this `24_discovery_pipeline.md`,
    - Why the change was made (link to Learning Loop evidence if available).

Over time, this process turns the Discovery Pipeline into a genuinely **adaptive Autonomous Discovery Engine**, grounded in real usage patterns rather than fixed heuristics.

---

**Version:** 1.1  
**Last updated:** 2026-04-10

## Related Hubs

- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
