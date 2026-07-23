---
name: manuscript-structure
description: Use for structural completeness check (IMRaD sections); for prose quality use avoid-ai-formulations Triggers include: manuscript structure, IMRaD, check article structure, section check, does it have all sections.
version: 1.3
last_updated: 2026-06-28
domain: writing
tokens: ~1100
triggers:
  - manuscript structure
  - IMRaD
  - check article structure
  - section check
  - does it have all sections
requires_packages: []
reference_files:
  - reference/kdense/results_reporting_snippets.md
  - reference/scientific_thinking/citation_styles.md
  - reference/medical_research/INDEX.md
  - reference/medical_research/consistency-checker-across-manuscript/hard-rules.md
  - reference/medical_research/title-and-abstract-optimizer/hard-rules.md
pipeline_position: [1, 4]
---

# Skill: Manuscript Structure Check (IMRaD)

## When to use

Use this skill when:
- Checking whether a manuscript has all required sections
- Verifying that Results/Findings are separate from Discussion
- Reviewing structure before submission
- User asks "check article structure", "does it have all sections", "is Discussion separate from Results"

## Prerequisites

- Manuscript draft (full or partial)
- Optional: `20_knowledge/reference_library/writing/manuscript_tips_checklist.md` for full checklists

## Step-by-step procedure

### 0. Pre-writing checklist

Before structure check, confirm (or flag `[TO_CONFIRM]`):

1. Target journal and author instructions  
2. Study design and reporting guideline (STROBE, CONSORT, PRISMA, CARE, …)  
3. Available tables, figures, supplements  
4. Author list  
5. Language / translated abstract requirements  

Canonical order and Declarations rules: `58_manuscript_agent_protocol.md` Part 2; `.cursor/rules/writing-manuscript-structure.mdc`.

### 1. Check section order (IMRaD + Abstract, Conclusion)

- Confirm presence and order: **Abstract** → **Introduction** (with CARS: territory → niche → occupy) → **Literature/Theory** (if separate) → **Methods** → **Results/Findings** → **Discussion** → **Conclusion** → **Acknowledgements** (if any) → **References**.
- Title and abstract are written last; working title during drafting is fine.
- Hourglass: Introduction broad → Methods narrow → Discussion broad again.
- **Systematic reviews:** Skip the separate Literature Review section — the entire manuscript IS the literature synthesis. Introduction provides only the framing context; Methods and Results contain the synthesis itself.

### 2. Section-level checklist

For each section, verify:

| Section | Check |
|---------|--------|
| **Title** | Fewest words that accurately describe content; IV/DV or relationship for empirical papers; no rare abbreviations; ≤20 words; not clever/ambiguous for empirical work. |
| **Abstract** | Research question, why it matters, 1–2 sentences method/setting, **main findings** (not hidden). 150–250 words; no jargon, no citations; written after manuscript complete. |
| **Introduction** | Focus on RQ; frame of reference; gap shown; justification. Answers: What is the problem? Solutions? Best one? Limitation of theory? What do you hope to achieve? "So what?" answered. Use the **Inverted Triangle** strategy (broad → narrow): **Para 1** broad context and importance → **Para 2** narrow to the specific field and key findings → **Para 3** identify the gap (where do studies agree/disagree?) → **Para 4** state RQ/objective. Complements CARS (territory → niche → occupy). For upstream literature synthesis, see `SKILL_literature-synthesis.md`. |
| **Hypotheses / RQ** | Linked to theory; one testable claim per hypothesis; directional; 2–4 key hypotheses/RQs; type 2 error/power considered. |
| **Methods** | Scientific standards + replicability (or generalizability); method matched to RQ; assumptions stated; CMV addressed if applicable (not only Harman). No results (e.g. response rates, coefficients) in Methods. |
| **Results / Findings** | Same order as framework/hypotheses. Facts only—no interpretation or editorializing ("interestingly" does not belong). Figures/tables self-explanatory. Descriptive + **effect size and 95% CI** with p-values (never p alone). Vancouver (or journal style) by default; see `reference/kdense/results_reporting_snippets.md` for common reporting mistakes. |
| **Discussion** | Links back to introduction and RQ; interpretation; comparison with literature; limitations and why contribution still matters; future research; practical implications. No new terms; no overclaim (e.g. causality from cross-sectional). Quantitative precision, not "low/high" or "dramatic" without numbers. |
| **Conclusions** | Global and specific conclusions; contribution; optional limitations and future work. Does not repeat abstract; does not overstate; does not undermine with "might", "probably", "maybe". |

### 2a. Declarations and abstract discipline

- **Declarations:** Verify each subsection heading matches its content (Ethics, Consent for publication, Data availability, Competing interests, Funding, Authors' contributions, Acknowledgements). Flag any permutation.
- **Abstract:** Structured order Background → Methods → Results → Conclusions; translated abstract same order.
- **Numbers:** Cross-check every number in Abstract against Results text.

### 2b. Cross-section consistency and title/abstract (when full draft available)

- Load `reference/medical_research/consistency-checker-across-manuscript/hard-rules.md`: reconcile numbers, dates, and population labels across Abstract, Methods, Results, Discussion.
- Load `reference/medical_research/title-and-abstract-optimizer/` only to improve clarity; never add findings not in Results.

### 3. Validation questions

Answer (or ensure the manuscript answers) clearly:

- **RQ:** What is the research question or purpose?
- **Gap:** What gap does the research fill, and why does it matter?
- **Framework:** What is the theoretical/conceptual frame of reference?
- **Findings vs interpretation:** Are Results/Findings free of interpretation? Is Discussion clearly separate and linked to introduction/RQ?
- **Replication:** Can another researcher replicate (or assess generalizability) from the Methods section?

If answers are unclear or inconsistent across sections, flag for revision.

### 4. Optional: "End of each page" check

For each page, ask: *"What did I do on this page to convince the reader that the manuscript is worth publishing?"* If nothing, consider tightening or moving content.

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Nedostaje li Discussionu nešto tipično za IMRaD u ovom nacrtu?"  
**Output:** "Checklist sekcija `[INFERRED]`; konkretne rupe samo iz dostavljenog teksta `[EXTRACTED]`; bez MS `[BLANK]`."

## Verification

- [ ] Section order follows IMRaD + Abstract, Conclusion
- [ ] Title and abstract meet checklist (title accurate, abstract has findings)
- [ ] Introduction has CARS and answers "so what?"
- [ ] Results/Findings are free of interpretation; Discussion is separate and linked to RQ
- [ ] Methods enable replication/generalizability; no results in Methods
- [ ] Discussion includes limitations and implications; no overclaim
- [ ] Conclusions state contribution without repeating abstract or undermining with hedging

## Learning integration

- **task_type:** writing
- **log_fields:** sections_completed, structure_used
- **post_step:** After completing procedure: output LEARNING_BLOCK (see `30_system/behavior_rules/14_learning_loop.md`) for ingestion.

## Related rules and references

- `SKILL_literature-synthesis.md` — Literature review synthesis, analysis grids, consensus meter, gap identification
- `.cursor/rules/writing-manuscript-structure.mdc` — IMRaD, CARS, do's/don'ts by section
- `SKILL_manuscript-writing.md` — Full draft/edit/QC protocol (file hygiene, style, pre-output gate)
- `30_system/behavior_rules/58_manuscript_agent_protocol.md` — Canonical Parts 1–6
- `.cursor/rules/writing-avoid-ai.mdc` — Phrases to avoid; rhetorical structure by section
- `20_knowledge/reference_library/writing/manuscript_tips_checklist.md` — Full tips and checklists from sources

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)

## Skill reference graph (auto)

- [[INDEX]]
- [[results_reporting_snippets]]
- [[citation_styles]]
- [[hard-rules]]
- [[hard-rules]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
