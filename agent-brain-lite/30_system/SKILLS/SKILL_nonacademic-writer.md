---
name: nonacademic-writer
description: Blog posts, newsletters, tutorials, and other non-journal prose with outline-first workflow, sourced research, and section feedback. NOT for manuscripts, IMRaD, grants, or systematic reviews. Triggers include blog, newsletter, Substack, LinkedIn article, thought leadership, content draft.
version: 1.0
last_updated: 2026-05-16
domain: writing
tokens: ~950
triggers:
  - blog post
  - blog
  - newsletter
  - Substack
  - LinkedIn article
  - thought leadership
  - content draft
  - non-academic writing
  - nonacademic
  - web article
  - tutorial post
  - case study post
  - piši blog
  - blog objava
requires_packages: []
reference_files: []
pipeline_position: []
---

# Skill: Non-Academic Writer

Collaborative writing for **public-facing or semi-formal prose** that is **not** destined for peer-reviewed journals, protocols, or grant IMRaD structures.

**Provenance:** Workflow adapted from [ComposioHQ/content-research-writer](https://github.com/ComposioHQ/awesome-claude-skills/tree/master/content-research-writer) (Apache-2.0), integrated with this repo's honesty and style rules.

---

## When to use

Use when the user wants to:

- Draft or refine a **blog post**, **newsletter**, **Substack/LinkedIn article**, **tutorial**, or **thought-leadership** piece
- Build an **outline**, improve a **hook/introduction**, add **citations** to web-sourced claims, or get **section-by-section feedback**
- Research a topic for **general audiences** (not a formal literature review grid)

## When NOT to use (route elsewhere)

| Intent | Skill |
|--------|--------|
| Manuscript, IMRaD, abstract for journal, thesis chapter | `manuscript-structure` (+ design-specific writing skills) |
| Systematic review, analysis grid, consensus meter, research gaps | `literature-synthesis` or `meta-analysis` |
| Case report / cohort / RCT manuscript | `case-report-series`, cohort/RCT skills |
| Phrase-level AI cleanup on **any** draft (including blog) | `avoid-ai-formulations` (may load as **second** Tier 3 skill; see `context-optimization.mdc`) |
| AI detection score check | `ai-detection` |
| Scholarly spec / LOOP | scholarly skills (`research-grill-me`, etc.) |

If the user mixes blog tone with clinical claims, keep **epistemic honesty**: label uncertainty; never invent citations or trial results.

---

## Style contract (repo rules still apply)

- **No em dash**; use comma, colon, or two sentences
- **Vary sentence length**; avoid AI-flagged stock phrases (see `avoid-ai-formulations` / `99_error_memory`)
- **Do not embed** repo paths, `SKILL_*` names, or `.cursor` references in deliverable prose
- **Citations:** verify sources; never fabricate; prefer links/DOIs when the user supplies them; mark `[VERIFY]` when a claim needs a source
- **Voice:** preserve the user's tone; suggest options, do not overwrite with generic marketing voice unless asked

---

## Step-by-step procedure

### 1. Clarify the piece (short)

Ask only what is missing:

- Topic, audience, goal (educate / persuade / announce)
- Target length and format (blog vs newsletter vs thread)
- Existing outline or draft path
- Citation style preference (inline, numbered, footnotes)

### 2. Collaborative outline

Produce a compact outline:

```markdown
# [Working title]

## Hook
- Opening angle (story, stat, or question)

## Introduction
- Context, stakes, what the reader will get

## Sections
### [Section title]
- Key points
- Example or evidence needed
- [Research: topic if unknown]

## Conclusion
- Takeaway, optional CTA

## Research to-do
- [ ] Claims needing a source
```

Iterate once if the user adjusts structure.

### 3. Research (on request)

For factual claims:

- Search or use user-provided sources
- Return **key findings + citations** in the user's preferred format
- Separate **verified facts** from **inference**; do not present inference as data

### 4. Hook and section drafting

- Offer **2–3 hook options** with brief rationale when improving an opening
- Draft or revise **one section at a time** when the user prefers incremental feedback

### 5. Section feedback template

```markdown
# Feedback: [Section name]

## Works well
- ...

## Suggestions
- Clarity: ...
- Flow: ...
- Evidence: [claim] → needs source or example

## Optional line edit
Original: > ...
Suggested: > ...
Why: ...
```

### 6. Final pass

Before calling the draft done:

- Claims sourced or marked `[VERIFY]`
- Tone matches audience
- No journal-style IMRaD boilerplate unless user asked for it
- Offer handoff: `@avoid-ai-formulations` or `@ai-detection` if polish or AI score is next

---

## Tier 3 pairing

Allowed with **one** additional skill when combined estimated skill tokens stay within repo budget (see `registry.json` `tier3_pairing`):

- **`avoid-ai-formulations`** after substantive draft exists
- **`ai-detection`** when user requests a score check

Do **not** pair with `manuscript-structure` or `literature-synthesis` in the same turn; pick the primary task.

---

## Output layout (optional)

If the user works in a dedicated folder:

```text
writing/<slug>/
  outline.md
  research.md
  draft-v1.md
  final.md
```

Default: deliver sections in chat unless the user specifies paths under their project (not under `30_system/` unless maintaining this repo).

---

## Success criteria

- Outline matches audience and goal
- Hooks are specific, not generic
- Factual claims are sourced or explicitly flagged
- Prose is readable and human, not journal IMRaD
- User can publish or hand off to AI-cleanup skills without domain confusion

## Semantic graph (auto)

- [[Non-academic writing skill]]
- [[Skill registry]]
- [[skills-auto-detect]]
- [SKILLS INDEX](../docs/indexes/SKILLS_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)
