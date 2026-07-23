---
name: journal-cover-design
description: Design journal issue covers, title pages, and graphical abstracts in LaTeX with print-safe specs (bleed, CMYK notes, spine).
version: 1.0
last_updated: 2026-05-22
domain: tools
tokens: ~450
triggers:
  - journal cover
  - cover design
  - title page design
  - issue cover
  - graphical abstract layout
  - spine design
  - magazine cover latex
requires_packages: []
reference_files:
  - reference/latex/journal-cover-design-guide.md
conflicts_with: [figure-pipeline]
disambiguation: Cover/title-page layout and print specs; for in-article scientific figures use figure-pipeline.
pipeline_position: []
---

# Skill: Journal cover design

## When to use

- User needs a **cover**, **title page**, or **graphical abstract** layout, including LaTeX/TikZ drafts or a spec for a designer.

## Procedure

1. Read `reference/latex/journal-cover-design-guide.md`.
2. Collect **publisher brief**: trim, bleed, spine width, mandatory logos, color space (CMYK/RGB).
3. Draft layout structure (blocks: journal id, title, visual, footer metadata).
4. Implement in LaTeX (`titlepage`, `standalone`, or `tikz` grid) under project root; compile via `latex` MCP.
5. Present **low-res PDF/PNG preview** for approval; note CMYK handoff is user/printer responsibility unless tools confirm conversion.
6. Never invent ISSN, volume, issue, or copyright lines — user must supply.

## Pairing

May follow `journal-production` stage 7 in the same session if token budget allows (`tier3_pairing`).

## Verification

- [ ] Deliverable type identified (cover vs title page vs graphical abstract)
- [ ] Safe zone and bleed documented
- [ ] All identifiers user-supplied or marked `[BLANK]`

## Related

- `SKILL_journal-production.md`, `SKILL_latex-document.md`, `SKILL_figure-pipeline.md`

## Related Hubs

- [[Journal cover design skill]]

## Semantic graph (auto)

- [[Journal cover design skill]]
- [[LaTeX and journal production stack]]
- [[Skill registry]]
- [[skills-auto-detect]]
- [SKILLS INDEX](../docs/indexes/SKILLS_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[Journal cover design skill]]
- [[journal-cover-design-guide]]
- [[SKILL_journal-production]]
- [[LaTeX and journal production stack]]
- [[Journal production skill]]
