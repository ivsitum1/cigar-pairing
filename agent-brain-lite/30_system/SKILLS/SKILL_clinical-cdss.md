---
name: clinical-cdss
description: >-
  Bedside clinical decision support for anesthesia and intensive care: SBAR
  assessment, differentials, guideline-based actions, ECMO/ICU guardrails. Wraps
  Clinical Decision Support subagent. NOT pharma document CDS. Use for ICU,
  anestezija, perioperative, sepsis, airway, ECMO, sedacija, klinički scenarij.
version: 1.0
last_updated: 2026-05-16
domain: clinical
tokens: ~950
triggers:
  - clinical scenario
  - bedside
  - ICU question
  - anestezija
  - anesthesiology
  - intenzivna
  - perioperative
  - airway
  - sepsis bundle
  - ECMO sedation
  - sedacija ECMO
  - klinički slučaj
  - clinical decision support
  - CDSS
requires_packages: []
reference_files:
  - ../../behavior_rules/agents/01_clinical_decision_support.md
pipeline_position: []
---

# Skill: Clinical CDSS (bedside — anesthesia & ICU)

**Role:** Procedural wrapper for the **Clinical Decision Support** subagent. Load this skill, then operate per `30_system/behavior_rules/agents/01_clinical_decision_support.md` and Tier 0 **`.cursor/rules/99_error_memory.mdc`** (Clinical section).

**Not for:** pharmaceutical cohort CDS documents, LaTeX regulatory reports, or treatment plans without user-supplied clinical facts (use K-Dense-style skills only if user explicitly asks for pharma-style CDS documents — default here is **bedside**).

## When to use

- Bedside or chart-based clinical questions (anesthesia, ICU, perioperative medicine).
- Differential diagnosis, immediate management, monitoring, escalation, guideline alignment.
- ECMO, mechanical ventilation, hemodynamics, sedation strategy **when the user provides scenario data**.

## When NOT to use

- Statistical analysis, meta-analysis, manuscript writing → statistics / writing skills.
- Contract / legal review → `legal-contract-review`.
- Generic “clinical-decision-support” from external repos that generate **pharma PDFs** — out of scope unless user requests that deliverable.

## Mandatory pre-check (before recommendations)

1. **Read** `reference_files` agent doc (Stage 3) — SBAR, frameworks, protocols.
2. **Apply** `99_error_memory.mdc` **Clinical** rows, including:
   - No universal “first-line” dexmedetomidine on adult ECMO from frequency/PK alone.
   - No proven “low-dose propofol adjunct to dex” regimen without full-text support.
   - No quetiapine + dex as evidence-based ECMO adjuvant from rescue-case literature.
   - No absolute “avoid opioids” on adult ECMO; age-context for paediatric opioid-sparing data.
   - No primary outcomes from **protocol** papers as if results exist.
   - Verify full text when PubMed has no abstract for a cited claim.
3. **User facts only:** drugs, doses, group names, and protocol details come from the user or loaded chart/protocol — never substitute example doses from the agent reference doc into the user’s case.

## Step-by-step procedure

### 1) Intake

Restate scenario. If missing: age, setting (OR/ICU/ECMO), acute problem, relevant labs/vitals, current therapies, question (diagnosis vs management vs risk).

If data insufficient, state `[BLANK]` and what to verify; do not invent vitals or labs.

### 2) Execute as Clinical Decision Support subagent

State: **Handling as Clinical Decision Support.**

Use **SBAR-style** structure (from agent doc):

- Situation / Background / Assessment / Recommendation
- Differential: common vs must-not-miss vs rare
- Evidence: guideline or study with level; say when evidence is weak or indirect
- Monitoring and escalation criteria
- Caveats and when to deviate

### 3) ECMO / sedation-specific

When ECMO or sedation is in scope:

- Frame sedatives as **strategy comparison and titration**, not rank-order “first choice” without source.
- Separate adult vs neonatal/paediatric evidence.
- Pair circuit PK papers with appropriate human cohort caveats.
- If only protocol or abstract-level sources exist, label as design-only or unverified.

### 4) Honesty tags

Use `[EXTRACTED]`, `[VERIFIED]` (user document or cited full text), `[INFERRED]`, `[ASSUMPTION]`, `[BLANK]` per `general-rules.mdc`.

**This is clinical decision support, not a substitute for attending judgment or local protocol.** State when formal consult (cardiology, ID, ethics) is needed.

### 5) After significant case discussion

Optional: suggest logging learning per `30_system/behavior_rules/14_learning_loop.md` if user corrects a clinical claim.

## Output format (minimum)

```markdown
**Handling as Clinical Decision Support.**

## Clinical scenario
[Restate]

## Assessment
[SBAR / differentials]

## Recommendations
1. Immediate
2. Diagnostics
3. Monitoring / escalation

## Evidence
[Guideline / level; limitations]

## Caveats
[Including ECMO/sedation guardrails if relevant]
```

## Verification checklist

- [ ] SBAR or equivalent structure
- [ ] Dangerous diagnoses addressed
- [ ] No fabricated patient data
- [ ] Clinical error-memory rules applied for ECMO/sedation if relevant
- [ ] No legal or statistical workflow mixed in

## Related (wiki)

- [[Clinical CDSS skill]]
- [[Clinical decision support subagent]]
- [[Skill registry]]
- [[99_error_memory]] (concept if present; else `.cursor/rules/99_error_memory.mdc`)

## Related (repo)

- Agent: `30_system/behavior_rules/agents/01_clinical_decision_support.md`
- Orchestrator: CLINICAL → `.cursor/rules/00_orchestrator_agent.mdc`
- External skill search: `SKILL_skill-discovery.md`

## Skill reference graph (auto)

- [[01_clinical_decision_support]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
