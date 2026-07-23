# Manuscript Writing Rules — AI Agent Protocol

**Version:** 1.1  
**Author:** Ivan Šitum / Claude  
**Last updated:** 2026-06-28  
**Purpose:** Prevent file proliferation, enforce clean single-output workflow, maintain scientific writing quality.

**Scope:** All manuscript types (original research, reviews, position papers, case reports, editorials). Scale reference counts and discussion length to article type; never compromise file hygiene, statistical reporting, or the one-file rule.

**Conceptual foundation:** `59_manuscript_writing_principles.md` (HR) — why these rules exist. This document is the operational how.

**Execution slices:** `.cursor/rules/writing-manuscript-principles.mdc` (principles summary), `writing-manuscript-files.mdc` (Part 1), `writing-manuscript-structure.mdc` (Part 2), `writing-paper-style.mdc` (Part 3); skill `SKILL_manuscript-writing.md` orchestrates full workflow.

### Principles → Parts (mapping)

| Principle | Part(s) |
|-----------|---------|
| 1 Single source of truth | 1, 2.3 |
| 2 Atomic operations | 1.5 |
| 3 QA is process, not artifact | 5 |
| 4 Derivatives generated | 1.3–1.4 |
| 5 Version = milestone | 1.2 |
| 6 Context verified | 6 |
| 7 Form follows content | 3.4–3.6 |
| 8 Fix at source | 1.5 |
| 9 Transparency of uncertainty | 4, skill honesty |
| 10 Resistant to accumulation | 1.3, 5.3 |

---

## PART 1: FILE MANAGEMENT — "One manuscript, one file, one truth"

### 1.1 The Golden Rule

**Every task produces exactly ONE output file per deliverable.** No backups, no intermediates, no `_pre_` snapshots. If you need to make 6 edits, make 6 edits to the same file. The version control is the conversation history, not a pile of `.docx` files.

### 1.2 File Naming Convention

```
{short_name}_v{major}.{minor}.docx
```

- `major` increments on structural changes (new section, rewritten discussion)
- `minor` increments on editorial fixes (typos, reference corrections, formatting)
- Examples: `CRAB_colistin_v1.0.docx`, `CRAB_colistin_v1.1.docx`, `CRAB_colistin_v2.0.docx`
- NEVER: `manuscript_submission_v1_pre_ref_fix.docx` or any `_pre_` suffix

### 1.3 Prohibited Patterns

- Creating backup before each micro-edit
- Separate `.md` files for abstracts, supplements, or QA notes that belong inside the manuscript or don't belong in output at all
- QA/audit artifacts in the output folder — keep in working directory only
- Intermediate files with datestamps in filename (`_2026-06-28`)
- Reference files (.ris, .bib) as separate deliverables unless explicitly requested

### 1.4 What Goes Where

| Artifact | Location | Delivery to user |
|----------|----------|-----------------|
| Final manuscript `.docx` | Project output (`03_output/`, `projects/.../outputs/`) | Yes — present to user |
| Supplementary materials | Same output folder (only if submission-ready) | Yes |
| QA logs, audit CSVs, diff reports | Working directory / `.agent/task/` only | No — summarise in chat |
| Reference `.ris`/`.bib` | Working directory; embed in manuscript or keep only if user asks | No by default |
| Translated abstracts | Inside the manuscript `.docx` | N/A — part of main file |

### 1.5 Editing Workflow

When asked to fix/edit an existing manuscript:

1. Read the file once
2. Identify ALL needed changes (not one at a time)
3. Apply all changes in a single editing session
4. Produce ONE updated file
5. Report changes as a summary in chat, not as separate QA documents

If uncertain about a change, **ask the user before writing a file** — do not create a backup "just in case" (Principle 2).

If the edit is complex (>20 changes), group them logically and report:

```
Changes applied (v1.0 → v1.1):
— Declarations section: fixed header/content permutation (6 items reordered)
— References: added 18 new citations [8-25]
— Table 1: added SOFA, APACHE II, GFR, vasopressor columns
— Romanian abstract: corrected section order
— Discussion: expanded from 3 to 6 paragraphs
```

---

## PART 2: MANUSCRIPT STRUCTURE — Assembly Before Writing

### 2.1 Pre-writing Checklist

Before generating ANY text, confirm with the user or infer from context:

1. **Target journal** — determines format, word limits, required sections, abstract structure, reference style
2. **Study design** — determines reporting guideline (STROBE, CONSORT, PRISMA, CARE, ARRIVE, STARD)
3. **Available data** — what tables, figures, supplementary materials exist
4. **Author list** — finalised or placeholder
5. **Language requirements** — bilingual abstract? Romanian/Croatian translation?

### 2.2 Canonical Section Order

Unless journal specifies otherwise:

```
Title page (title, authors, affiliations, corresponding author, word count, keywords)
Abstract (structured: Background, Methods, Results, Conclusions)
[Translated abstract if required — SAME section order as English]
Introduction
Methods
Results
Discussion
Conclusion (if separate from Discussion)
Declarations
  ├── Ethics approval and consent to participate
  ├── Consent for publication
  ├── Availability of data and materials
  ├── Competing interests
  ├── Funding
  ├── Authors' contributions
  └── Acknowledgements
References
Tables (or embedded)
Figure legends
Supplementary material (or separate files)
```

**CRITICAL: Declarations subsection HEADINGS must match their CONTENT.** Never permute. If using copy-paste, verify every header-content pair before output.

### 2.3 Abstract Discipline

- Structured abstract sections ALWAYS follow: Background → Methods → Results → Conclusions
- Translated abstracts follow IDENTICAL section order
- Numbers in abstract MUST match numbers in Results text EXACTLY
- Abstract is self-contained: a reader who reads nothing else gets the complete picture

---

## PART 3: WRITING STYLE — The Anti-Bureaucratic Academic

### 3.1 Core Principles

1. **Assertive, not defensive.** State findings and interpretations directly. Limitations go in the Limitations subsection, not sprinkled into every paragraph.
2. **Precise over diplomatic.** "Remimazolam halved desaturation (25% vs 62.5%)" beats "Remimazolam was associated with lower rates of desaturation events compared with the propofol group."
3. **Numbers over adjectives.** Never write "significantly fewer" without the number. Never write "comparable" without the comparison.
4. **Active voice for claims and recommendations.** "We found" / "The analysis showed" / "Centres should record." Passive only in Methods when describing procedures.
5. **One idea per sentence.** Target: ≤25 words/sentence average. Break complex sentences at the conjunction.

### 3.2 Hedging Rules

Hedging has a place in science. It does not have 14 places per page.

| Situation | Appropriate hedge | Inappropriate hedge |
|-----------|------------------|-------------------|
| Your own RCT result | None needed — state the finding | "Our results seem to possibly suggest..." |
| Interpreting someone else's data | "X et al. reported..." | "It has been suggested by some authors that..." |
| Extrapolating beyond your data | ONE qualifier per claim: "may", "could", or "potentially" | Stacking: "This may potentially suggest a possible..." |
| Limitations | State in Limitations section, once | Repeating the same limitation in Introduction, Results, Discussion, AND Conclusion |
| Position paper recommendation | "We recommend" / "We propose" | "It might be considered reasonable to suggest..." |

**The hedge audit:** Before submission, search the manuscript for: may, might, could, potentially, possibly, appears to, seems to, it is suggested. If total count exceeds 1 per 300 words in Discussion/Conclusion, cut.

### 3.3 Redundancy Rules

- **State each finding ONCE in the appropriate section.** Results in Results. Interpretation in Discussion. Summary in Abstract and Conclusion.
- **Tables and text are complementary, not identical.** Table = data. Text = interpretation of that data. Never narrate a table row-by-row.
- **If you catch yourself paraphrasing the same conclusion from a previous paragraph — delete one of them.**

### 3.4 Discussion Architecture

Minimum 5 paragraphs for any original research:

1. **Principal finding** — one paragraph, lead with the main result, interpret it
2. **Context** — how does this compare to existing literature? (2-3 paragraphs, each addressing a different comparison or mechanism)
3. **Clinical implications** — what should change in practice? Or why not yet?
4. **Strengths** — briefly, without false modesty
5. **Limitations** — comprehensive, honest, with assessment of direction of bias
6. **[Optional] Future directions** — only if not covered in Conclusion

### 3.5 Reference Density

| Section | Minimum references | Purpose |
|---------|-------------------|---------|
| Introduction | 5-10 | Establish the gap |
| Methods | 3-5 | Justify design choices, cite reporting guidelines |
| Discussion | 10-20 | Contextualise findings |
| Total for original research | 25-40 | Comprehensive but focused |

If the reference list looks thin, search for: the pivotal trials in the field, the most-cited reviews, the reporting guideline, and the methodological reference for your statistical approach.

### 3.6 Proportionality (all paper types)

Default text budget:

- Core argument / primary findings + recommendations: ~60%
- Background / current practice: ~20%
- Technical digressions: ~10% (+ references for interested readers)
- Limitations + future research: ~10%

Scale to article type; position papers weight Discussion/Conclusions higher; pure methods papers may weight Methods higher.

### 3.7 Self-check

- Each paragraph: can the reader understand it without the previous 3 paragraphs? If not, restructure.
- Abstract test: 80% of readers read only the abstract — does it answer what, why, and what now?

---

## PART 4: STATISTICAL REPORTING

### 4.1 Bayesian Analysis Reporting

When reporting Bayesian analysis, include:

- Prior specification and justification (why this prior? sensitivity to alternatives?)
- Posterior summary: median/mean, 95% credible interval
- Decision criterion: prespecified threshold AND justification for that threshold
- Sensitivity analysis: at minimum, with different priors; ideally also with different decision thresholds
- Visual: posterior density plot with decision boundary marked

See also `SKILL_bayesian-workflow.md`.

### 4.2 Non-inferiority Specific

- State the NI margin AND justify it (where does it come from? clinical reasoning? regulatory precedent?)
- State the decision threshold AND justify it (P>0.70 requires explicit argument; P>0.90 is conventional)
- Acknowledge that NI from observational data has inherent limitations (assay sensitivity, confounding)
- Consider reframing as "Bayesian comparative effectiveness estimation" if not randomised

### 4.3 Table 1 for ICU Studies

Minimum variables for any ICU cohort study:

```
Demographics: age, sex, BMI
Severity scores: APACHE II or III, SOFA (admission + peak)
Comorbidities: Charlson index or individual (DM, CKD, liver disease, transplant, malignancy, immunosuppression)
ICU context: reason for admission, MV at enrolment, vasopressor use, days in ICU before infection
Infection: site, MIC values, prior antibiotics, polymicrobial
Treatment: drug doses, duration, concomitant antibiotics
Renal: baseline GFR/creatinine, RRT during treatment
```

A Table 1 without severity scores and renal function in an antibiotic ICU study is incomplete and will be flagged by any competent reviewer.

---

## PART 5: QUALITY CONTROL — Self-Assessment Before Output

### 5.1 Pre-output Checklist

Before presenting ANY manuscript file to the user, verify:

- [ ] **One file only** — no intermediates, no backups in output
- [ ] **Declarations match** — each header corresponds to its content
- [ ] **Abstract numbers match Results** — cross-check every number
- [ ] **Translated abstract** — same section order, same numbers
- [ ] **References** — formatted consistently, sufficient count, DOIs present
- [ ] **Tables** — no prose-table redundancy; all referenced in text
- [ ] **Figures** — all referenced; legends are self-explanatory
- [ ] **STROBE/CONSORT/PRISMA** — checklist mentioned AND available (as supplement or appendix)
- [ ] **Word count** — within journal limit
- [ ] **Hedge count** — ≤1 per 300 words in Discussion/Conclusion

### 5.2 Self-Assessment Scoring

Before final output, score the manuscript internally:

| Dimension | Target | Weight |
|-----------|--------|--------|
| Completeness (all required sections present) | 10/10 | 20% |
| Statistical rigour (methods justified, reported correctly) | 10/10 | 20% |
| Writing clarity (assertive, non-redundant, precise) | 10/10 | 20% |
| Table/figure quality (informative, non-redundant) | 10/10 | 15% |
| Reference adequacy (sufficient, relevant, formatted) | 10/10 | 10% |
| File hygiene (one file, correct naming, no artifacts) | 10/10 | 15% |

**Minimum threshold for output: weighted average ≥ 9/10 (canonical per core-principles.mdc).** If below 9/10, iterate before presenting. Below 7/10 → re-approach entirely. Report the score to the user in chat.

**Output gate (Principle 3):** Do **not** deliver a manuscript file if the minimal integrity check fails (e.g. N mismatch across abstract, text, tables) or if QA finds an unresolved discrepancy. Communicate findings in chat; fix at source before output.

### 5.3 Common Failure Modes to Actively Prevent

1. **Header-content permutation** in Declarations — verify every pair
2. **Backup file proliferation** — catch yourself before creating `_pre_` anything
3. **QA artifacts in output** — audit logs stay in working directory
4. **Orphaned translated sections** — never as separate `.md` files
5. **Progressive degradation** — later edits introducing errors into previously correct sections
6. **Reference rot** — citing a paper without verifying it exists and says what you think it says

---

## PART 6: MULTI-SESSION CONTINUITY

### 6.1 Handoff Protocol

When a manuscript spans multiple conversations:

- Start each session by reading the CURRENT version (not the original draft)
- State what version you're working from and what changes are planned
- End each session with a changelog and the version number

### 6.2 Never Trust Prior Session Summaries

If a previous conversation summary says "references verified" or "methods synced" — verify anyway. Trust the file, not the summary. Extract text, check the numbers, confirm the structure.

### 6.3 Minimal integrity check (every session start)

Before editing or delivering, verify in the **current file**:

- **N** consistent across abstract, body text, tables, supplements
- **Declarations** headers match content
- **Abstract numbers** match Results exactly
- **Reference count** reasonable for article type

If any check fails, **stop** and resolve before generating output (Principles 3, 6).

---

## Related

- `59_manuscript_writing_principles.md` — conceptual foundation (HR)
- `.cursor/rules/writing-manuscript-principles.mdc`
- `.cursor/rules/writing-manuscript-structure.mdc`
- `.cursor/rules/writing-paper-style.mdc`
- `.cursor/rules/writing-avoid-ai.mdc`
- `30_system/SKILLS/SKILL_manuscript-writing.md`
- `30_system/SKILLS/reference/manuscript_statistical_reporting.md`
- `30_system/SKILLS/reference/manuscript_pre_output_checklist.md`
