---
name: manuscript-writing
description: Use for writing or editing any journal manuscript end-to-end — principles, file hygiene, structure, style, stats QC, pre-output gate. Triggers include write manuscript, piši manuskript, edit manuscript, uredi manuskript, manuscript protocol, prepare submission, position paper, cohort manuscript.
version: 1.1
last_updated: 2026-06-28
domain: writing
tokens: ~1500
triggers:
  - write manuscript
  - piši manuskript
  - edit manuscript
  - uredi manuskript
  - manuscript protocol
  - prepare submission
  - priprema za submission
  - position paper
  - cohort manuscript
  - CRAB colistin
requires_packages: []
reference_files:
  - ../../behavior_rules/59_manuscript_writing_principles.md
  - ../../behavior_rules/58_manuscript_agent_protocol.md
  - reference/manuscript_statistical_reporting.md
  - reference/manuscript_pre_output_checklist.md
  - reference/paper_style_checklist.md
pipeline_position: [1, 4, 6]
---

# Skill: Manuscript Writing (Agent Protocol)

## When to use

Use this skill when:
- Drafting or revising **any** journal-bound manuscript (original research, review, position paper, case report, editorial)
- User asks to write, edit, polish, or prepare a manuscript for submission
- Enforcing principles, one-file workflow, structure assembly, style pass, or pre-output QC

**Pair with study-type skills when design is known:** `rct-manuscript`, `observational-studies`, `retrospective-cohort`, `prospective-cohort`, `case-report-series`, `literature-synthesis`, `meta-analysis`.

**Not this skill alone when:**
- Only IMRaD section checklist → `manuscript-structure`
- Only AI phrase polish → `avoid-ai-formulations`
- Blog/newsletter → `nonacademic-writer`

---

## Honesty and grounding (Principle 9)

- Direct language only when design and evidence support it `[VERIFIED]` against user's data/protocol
- Never fabricate citations, numbers, or guideline quotes
- Tag gaps as `[BLANK]` or `[TO_CONFIRM]` (target journal, author list, unverified references, MIC values, NI margin, priors)
- If a reference, MIC, or statistical choice cannot be verified: say so explicitly and mark for manual review; do not silently assume

---

## Workflow

### Step −1 — Principles gate

Load `59_manuscript_writing_principles.md` and `.cursor/rules/writing-manuscript-principles.mdc`.

Internalize before any manuscript output: single source of truth, atomic ops, QA in chat not files, fix at source, entropy test.

### Step 0 — Session start + integrity check (Principles 6, 3)

- Read the **current** `{short_name}_v{X.Y}.docx`, not an older draft
- State version and planned changes in chat
- **Never trust prior session summaries** — verify file contents

**Minimal integrity check** (stop if failed; do not deliver until resolved):

- **N** consistent: abstract, body text, all tables, supplements
- **Declarations:** each header matches its content
- **Abstract numbers** match Results exactly
- **Reference count** reasonable for article type

Report in chat, e.g. "N=59 consistent across abstract, Table 1, Results" or "STOP: Table 1 N=59 but audit says N=90 — clarify before continuing."

### Step 1 — File target (Part 1, Principles 1–2, 8, 10)

Load `.cursor/rules/writing-manuscript-files.mdc`.

- Confirm **one deliverable file** and naming `{short_name}_v{major}.{minor}.docx`
- Output folder: `03_output/` or `projects/.../outputs/`; QA artifacts stay in `.agent/task/`
- For edits: batch all changes → one version bump → changelog in chat
- If uncertain about a change: **ask user before writing**; no `_pre_` backup
- Fix errors **in the canonical file**, never a parallel "corrected copy"

### Step 2 — Pre-writing checklist (Part 2)

Load `.cursor/rules/writing-manuscript-structure.mdc`.

Confirm or mark `[TO_CONFIRM]`:

1. Target journal (format, limits, reference style)
2. Study design → reporting guideline (STROBE, CONSORT, PRISMA, CARE, …)
3. Available tables, figures, supplements
4. Author list
5. Language (bilingual abstract?)

Derivatives (translated abstract, checklist exports): generate from current source or embed in manuscript — no orphan maintenance (Principle 4).

### Step 3 — Draft or revise body

- Load study-type skill if matched
- Follow canonical section order (Title page → Abstract → IMRaD → Declarations → References → Tables → Legends → Supplement)
- **Declarations:** verify every header matches its content (no permutation)
- **Abstract:** Background → Methods → Results → Conclusions; translated abstract same order; numbers match Results exactly

### Step 4 — Style pass (Part 3, Principle 7)

Load `.cursor/rules/writing-paper-style.mdc` and `reference/paper_style_checklist.md`.

- Hedging audit (Discussion/Conclusion)
- Redundancy pass (findings once; table ≠ text)
- Discussion architecture (≥5 paragraphs for original research)
- Reference density check (Intro 5–10, Methods 3–5, Discussion 10–20, total 25–40 for original research)
- Proportionality by **content complexity**, not template defaults

### Step 5 — Statistical reporting (Part 4, Principle 9)

If applicable, load `reference/manuscript_statistical_reporting.md`:

- Bayesian: prior, posterior, threshold, sensitivity, plot — justify choices or `[TO_CONFIRM]`
- Non-inferiority: margin + threshold justification
- ICU Table 1 minimum variables for cohort/antibiotic studies

### Step 6 — Pre-output QC (Part 5, Principles 3, 10)

Load `reference/manuscript_pre_output_checklist.md`.

- Run §5.1 checklist
- Re-run integrity check if any numbers changed
- Score §5.2 dimensions; **weighted average must be ≥ 9/10** before delivery
- **Entropy test:** output folder should have constant or fewer manuscript files; final manuscript trivial to identify
- Report score and QA summary **in chat** — not as CSV/deliverable audit file
- **Output gate:** if integrity check or QA finds unresolved discrepancy → **do not deliver** file; fix at source first

### Step 7 — Polish pipeline

- `avoid-ai-formulations` (pairing allowed)
- Optional: `ai-detection`
- Mandatory for critical analyses: `swiss-cheese` per `verification.mdc`

### Step 8 — Session end (Part 6)

- Changelog with version (e.g. v1.0 → v1.1); user can explain each version with "Zato što..." (Principle 5)
- Append milestone to project `context/log.md` if multi-session project

---

## Pre-output gate (mandatory)

Do **not** deliver manuscript `.docx` until:

- [ ] Principles 1–10 satisfied (especially integrity check, no orphan derivatives)
- [ ] One file only in output folder
- [ ] Weighted QC score ≥ 9/10 reported in chat
- [ ] Declarations header-content verified
- [ ] Abstract numbers match Results
- [ ] No unresolved N or number discrepancies

---

## Examples

**Input:** "Uredi CRAB_colistin_v1.0.docx — popravi reference i Table 1"  
**Output:** Single `CRAB_colistin_v1.1.docx`; changelog in chat; no `_pre_` backup; QC score reported.

**Input:** "N=59 u tekstu, QA audit kaže N=90"  
**Output:** STOP; ask user to clarify; do not generate output until resolved.

**Input:** "Piši position paper o remimazolamu"  
**Output:** Apply Steps −1–7; assertive Discussion; pair with `literature-synthesis` if evidence grid needed.

---

## Related

- Principles: `59_manuscript_writing_principles.md`
- Protocol: `58_manuscript_agent_protocol.md`
- Structure check: `SKILL_manuscript-structure.md`
- Publishing handoff: `21_publishing_workflow.md`
- Agent role: `08_academic_writing_specialist.md`
