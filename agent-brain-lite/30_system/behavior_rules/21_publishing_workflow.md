# Publishing Workflow

## Purpose

This document defines a step-by-step workflow from **final manuscript** to **submission**, **revision**, and **publication**. It links pre-submission checklists, journal selection, cover letter, and post-submission steps. Use it once the manuscript is ready for submission.

---

## When to Use

- Manuscript drafting and internal review are complete
- Pre-submission checks (references, AI detection, plagiarism) are done or in progress
- You are ready to choose a journal and submit

For **draft/edit/QC during writing**, use `30_system/behavior_rules/58_manuscript_agent_protocol.md` and `SKILL_manuscript-writing.md` (one-file rule, pre-output weighted score ≥9/10).

---

## Multi-session manuscript handoff

When a manuscript spans multiple conversations:

- Start each session from the **current** `{short_name}_v{X.Y}.docx`
- State version and planned changes; end with changelog and new version number
- **Trust the file, not prior summaries** — re-verify references, numbers, and Declarations

See Part 6 of `58_manuscript_agent_protocol.md`.

---

## Workflow Overview

```
FINAL MANUSCRIPT
    │
    ▼
1. PRE-SUBMISSION CHECKLIST  ──►  2. JOURNAL SELECTION
    │                                    │
    ▼                                    ▼
3. JOURNAL GUIDELINES (paste when ready) ──►  4. COVER LETTER
    │                                              │
    ▼                                              ▼
5. SUBMISSION  ──►  6. RESPONSE TO REVIEWERS  ──►  7. REVISIONS
    │                                                      │
    ▼                                                      ▼
8. PROOFS  ──►  9. PUBLICATION / POST-ACCEPTANCE
```

---

## Step 1: Pre-Submission Checklist

Complete before submission. See:

- **`30_system/behavior_rules/58_manuscript_agent_protocol.md`** — File hygiene, structure, style, pre-output QC (during drafting)
- **`30_system/behavior_rules/03_scientific_writing.md`** — Reference verification, PRISMA/GRADE, pre-submission checklist
- **`30_system/behavior_rules/10_ai_writing_plagiarism.md`** — AI detection, plagiarism check, AI usage declaration

**Minimum:**

- [ ] All references verified (existence, accuracy, relevance)
- [ ] AI writing detection checked (target &lt; 20%; see Writing Workflow 7)
- [ ] Plagiarism check completed
- [ ] AI usage declaration prepared if applicable
- [ ] Numbers consistent across text, tables, figures
- [ ] Reporting checklist (PRISMA/CONSORT/STROBE etc.) completed as required

---

## Step 2: Journal Selection

- Shortlist 2–3 target journals (scope, impact, acceptance rate, Open Access options)
- Check typical time to first decision and to publication
- Note each journal’s **instructions for authors** and **editorial policies**

### Desk Rejection Risk Factors — Check Before Submitting

Journals desk-reject manuscripts before peer review. Screen for these before submission:

1. **Scope mismatch**: verify study type appears in journal's last 3 issues
2. **Sample size below journal norm**: check median n in recently published studies
3. **Primary outcome not clinically meaningful**: endpoints must matter to patients, not just researchers
4. **Prior rejection at same journal within 12 months** without substantial revision
5. **Missing mandatory items**: word count, structured abstract, ethics statement, data sharing

**Mitigation**: if risk ≥ 2 factors, send a 3-sentence presubmission inquiry to the editor before
full submission. Template:

> "We are considering submitting a [study type] of [n] patients examining [outcome] in [population].
> Our primary finding is [1-sentence result]. Is this within the scope of [Journal]?"

---

## Step 3: Journal Guidelines

**When you reach submission, add journal-specific guidelines** so the agent can help with formatting, word limits, and structure.

### Where to Store

- **Option A:** `30_system/04_documentation/journal_guidelines/` in your project  
  - Create one file per journal, e.g. `[JournalName]_author_instructions.md`
- **Option B:** A single `journal_guidelines.md` in `30_system/04_documentation/` for the current target journal

### What to Add

When you have them, **paste or summarise**:

- Link to (or copy of) *Instructions for authors*
- Word limits (abstract, main text, references)
- Structure requirements (sections, headings)
- Figure/table format and file type
- Reference style (Vancouver, Harvard, etc.)
- Cover letter requirements
- Any other editorial requirements

**Placeholder:** Until you have the guidelines, keep a note:

```markdown
## Journal guidelines – [TARGET JOURNAL]

*Paste journal-specific guidelines here when ready.*
```

Once you copy the guidelines, replace this with the actual content (or a link + short summary). The agent will use them for formatting, cover letter, and submission checks.

---

## Step 4: Cover Letter

- Address to the Editor-in-Chief or Handling Editor
- Brief rationale for the journal and fit with scope
- Short summary of aims, main findings, and significance
- Confirm originality, no dual submission, and any conflict of interest statements
- Suggest reviewers if the journal allows (and you wish to)
- Align tone and length with **journal guidelines** (Step 3)

---

## Step 5: Submission

- Use the journal’s **submission system** (Editorial Manager, ScholarOne, etc.)
- Upload files per **journal guidelines** (title page, main manuscript, figures, tables, supplements)
- Complete all required fields (abstract, keywords, declarations, etc.)
- **Archive a submission version** in `05_version_control/versions/` (e.g. `v1.0_submitted_YYYY-MM-DD`). See `07_project_structure.md`.

---

## Step 6: Response to Reviewers

- Create a **point-by-point response** document (table or numbered list)
- For each comment: quote reviewer text → your response → optional quote of revised manuscript
- Be clear and constructive; cite line/figure/table changes where helpful
- Store in `30_system/04_documentation/correspondence/` (e.g. `response_to_reviewers_v1.md`)

---

## Step 7: Revisions

- Revise manuscript and supplementary materials according to your responses
- Re-run pre-submission checks for changed sections (references, AI detection if applicable)
- Update **journal guidelines** reference if the journal’s instructions have changed
- Archive revised version before resubmission (e.g. `v1.1_revised_YYYY-MM-DD`)

---

## Step 8: Proofs

- Proofread **galley proofs** carefully (typos, author names, affiliations, references, figures)
- Check that edits from revision are correctly implemented
- Reply to the publisher by the requested deadline

---

## Step 9: Publication / Post-Acceptance

- Confirm **copyright** and **license** (e.g. CC-BY) if applicable
- **DOI** and **citation**: update project README or citation file
- Archive **final accepted version** (e.g. `v2.0_accepted_YYYY-MM-DD`)
- Update **changelog** and project status

---

## Project Structure (Relevant Folders)

From `07_project_structure.md`:

```
30_system/04_documentation/
├── protocol/
├── sap/
├── meeting_notes/
├── correspondence/          # Cover letters, responses to reviewers, editor emails
└── journal_guidelines/      # Create this; store journal-specific guidelines here

05_version_control/
├── changelog.md
└── versions/                # Archive at submission, revision, acceptance
```

---

## References

- **Pre-submission, reporting:** `30_system/behavior_rules/03_scientific_writing.md`
- **AI detection, plagiarism, declaration:** `30_system/behavior_rules/10_ai_writing_plagiarism.md`
- **Project structure, versioning:** `30_system/behavior_rules/07_project_structure.md`
- **Writing workflow (incl. AI check):** `30_system/behavior_rules/09_workflow_optimization.md` (Workflow 7)

---

**Version:** 1.0  
**Last updated:** 2025-01-29

## Related Hubs

- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
