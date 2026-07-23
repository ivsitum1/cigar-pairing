# Agent Autonomy, Triggers, and Parallel Work

**Purpose:** Define how the Orchestrator runs **longer chains without unnecessary stops**, how **one subagent explicitly triggers the next**, and how **parallel work** is done without pretending multiple LLMs share one context window.

**Authority:** Operational detail for `.cursor/rules/00_orchestrator_agent.mdc`. Reference: `30_system/behavior_rules/15b_agent_subagent_system.md`. **Token budgets:** `context-optimization.mdc` (canonical table).

---

## 1. Platform reality (do not skip)

| Mechanism | What actually happens |
|-----------|------------------------|
| **Single chat (Composer / Agent)** | One model thread. "Subagents" are **role adoption** and **ordered steps** in one reply or across turns. |
| **True parallelism** | Multiple concurrent sessions: Cursor **Task** tool (subagents), extra chat tabs, or background jobs. Each needs its **own prompt** and **artifact path** so results merge safely. |
| **Persistence** | Handoffs and parallel outputs should land in **files** (`.agent/task/`, `30_system/04_documentation/context/log.md`) so the next step or merge does not rely on memory alone. |

Autonomy means **fewer permission-seeking pauses** when inputs are present; it does **not** mean bypassing safety, Swiss Cheese, or user checkpoints when data is missing.

---

## 2. Autonomous execution mode

**Triggers (user intent):** phrases like `@autonomous`, `AUTONOMOUS ON`, `run the full pipeline`, `do not stop between stages`, `continue until REFINE or missing input`.

**Orchestrator behavior when autonomous is ON**

1. **Plan briefly** (stages, files touched, gates) in 3–6 bullets unless the user asked for zero planning.
2. **Execute the pipeline serially** inside the thread: complete stage *n*, emit `[HANDOFF]` + log hook, continue as stage *n+1* in the **same turn** when feasible (token limits may force a continuation message).
3. **Gates (must stop and ask):** missing files or parameters; destructive operations; ambiguous classification after `detect_agent`; any **critical** statistical or clinical claim without sources when the user expects verification.
4. **REFINE / Swiss Cheese:** Still mandatory where `verification.mdc` and `22_pipeline_and_refinement.md` say so; autonomy does not skip REFINE.
5. **End state:** Emit `AUTONOMOUS PASS COMPLETE` or `AUTONOMOUS STOP: [reason]` so the user sees a clear boundary.

---

## 3. Agent-triggered handoff (subagent invokes the next)

Any subagent may signal that the **next specialist** must take over. This is **not** a second LLM process; it is an explicit **routing instruction** for the Orchestrator.

**Format (after completing the current subagent’s slice):**

```
[TRIGGER Orchestrator → SubagentName]
Reason: [why the next role is required]
Inputs_ready: [paths or facts the next role needs]
Blockers: [none | list]
```

Then the Orchestrator **continues the same response** as `SubagentName` (or states HANDOFF first if the contract is A→B style). **Always** log with `log_handoff` / `handoff_log.py` when moving between named subagents.

**When to use TRIGGER vs HANDOFF**

- **HANDOFF:** Linear pipeline step; usual `Completed / Next / Context`.
- **TRIGGER:** Subagent discovers scope creep, failure, or dependency (e.g. stats done but QA needed before writing); adds `Reason` and `Blockers`.

---

## 4. Parallel fan-out / fan-in

Use when workstreams are **independent** (no shared mutable state mid-step), e.g. literature chunk screening, separate figure panels, independent code reviews, parallel research notes.

### 4.1 Fan-out (Orchestrator)

1. **Partition** the task into **Track A, Track B, …** with non-overlapping outputs.
2. For each track, define: **goal**, **inputs**, **output path** (required):

   `.agent/task/parallel_<run_id>_<track>.md`

   Use a short `<run_id>` (date or slug): `parallel_20260410_stats`.

3. **Launch parallel workers** using one of:
   - **Cursor Task tool:** one Task per track with a self-contained prompt: role, rules to follow, files to read, and **exact output path**.
   - **Manual multi-chat:** give the user copy-paste prompts for Tab 2 / Tab 3 (clearly labelled Track B/C).
4. **Do not** assume parallel workers see each other’s partial messages; only **files** count.

### 4.2 Fan-in (Orchestrator)

1. Wait until **all** track files exist (or user confirms tracks done).
2. **Synthesize** as Orchestrator (or WRITING / STATISTICS as appropriate): reconcile conflicts, deduplicate, one coherent deliverable.
3. Append a line to `30_system/04_documentation/context/log.md` or `.agent/MEMORY.md`: parallel run id, tracks, outcome.

### 4.3 Safety

- No parallel destructive git/file ops without explicit user approval per track.
- **Primary analysis** or **single pooled estimate:** prefer **serial** expert review unless pre-specified sensitivity tracks are independent by design.

---

## 5. Token economics (when parallelism helps)

| Pattern | Typical context cost | Guidance |
|---------|---------------------|----------|
| Serial `@autonomous` in **one** chat | All stages + tools accumulate in **one** thread | Use for **coupled** steps; keep HANDOFF text minimal (see orchestrator). |
| **Fan-out** (Task / extra chats) | Each worker carries **only** its track prompt + tools | Prefer when **≥2 independent** streams each need bulky MCP output (e.g. many PDFs, large searches). |
| **Fan-in** | Main thread reads **track files**, not every intermediate tool blob | Require **summary-first** sections in `parallel_<run_id>_<track>.md`; avoid pasting raw dumps into the merge chat. |

**Orchestrator default:** Offer or run parallel tracks when the user asks to **save context/tokens** or when partitionability is obvious; stay serial when ordering or shared state matters. Canonical numbers: `context-optimization.mdc` § Token budget.

**Enforced caps (RAG Anatomy / workflow notebooks):**
- Max **3** parallel Task tracks per fan-out unless user overrides.
- Each track file should stay under **~8k tokens** of prose summary; link raw artifacts by path.
- Autonomous serial chains: pause and fold lemmas when estimated context exceeds **~120k tokens** (use `context_sync --fold-lemma`).

---

## 6. Loop-of-loops nested autonomy (NotebookLM batch 2026-06)

**Map:** [`30_system/docs/LOOP_OF_LOOPS_MAP.md`](../../30_system/docs/LOOP_OF_LOOPS_MAP.md) | Grill: `outputs/notebooklm/loop-of-loops_*`

Loop-of-loops is **nested serial autonomy**: an outer loop (orchestrator / project phase) contains inner loops (research, wiki ingest, skill eval) with explicit **stop conditions** and **human gates**.

| Layer | Brain repo anchor | Stop condition |
|-------|-------------------|----------------|
| Outer | `@autonomous` + orchestrator pipelines | `[AUTONOMOUS STOP]` or missing required input |
| Inner research | STORM-style multi-perspective via `research-grill-me` | Spec TBDs closed or user confirms proceed |
| Inner wiki | `wiki-synthesize`, `daily-update`, `wiki-ingest` | Lint pass or human review on structural edits |
| Inner eval | `skill_gap_optimize_gate` composite ≥ cutoff | Regression on eval seed; no auto Tier 0 rewrite |

**Handoff file (MVP):** one path per inner loop, e.g. `.agent/task/loop_<run_id>_handoff.md` with `Completed / Next / Blockers / Human_gate_needed`.

**Do not:** replace orchestrator with unbounded nested agents; duplicate Ralph loop semantics; skip REFINE on primary analysis.

**Parallel with Ralph:** Ralph = single-repo iteration to PRD/issues; loop-of-loops = cross-artifact KB + research loops. Use **serial** when shared state; **fan-out** (§4) only for independent literature tracks.

---

## 7. Quick reference

| User says | Action |
|-----------|--------|
| `@autonomous` / `AUTONOMOUS ON` | Section 2 |
| `[TRIGGER Orchestrator → X]` | Section 3; continue as X; log handoff |
| `parallel`, `fan-out`, `two tracks`, **ušteda konteksta / tokena** | Section 4–5; file naming under `.agent/task/` |
| `loop of loops`, nested agent loop | Section 6; handoff file + human gate every 3rd iteration for MVP |

---

**Version:** 1.2 | **Last updated:** 2026-06-30

## Related Hubs

- [Folder index hub](../../30_system/docs/FOLDER_INDEX.md)
- [All notes index](../../30_system/docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
