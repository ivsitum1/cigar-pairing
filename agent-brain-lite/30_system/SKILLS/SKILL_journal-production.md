---
name: journal-production
description: Guide journal production from accepted manuscript through proofs, metadata, cover, and camera-ready PDF. LaTeX typesetting and publisher checklists.
version: 1.0
last_updated: 2026-05-22
domain: tools
tokens: ~600
triggers:
  - journal production
  - production checklist
  - galley proof
  - camera ready
  - copyedit latex
  - typesetting
  - prepress
  - issue metadata
  - publisher production
requires_packages: []
reference_files:
  - reference/latex/journal-production-stages.md
  - reference/latex/ieee-journal-twocolumn-guide.md
conflicts_with: []
disambiguation: Post-acceptance production workflow; for IMRaD structure use manuscript-structure; for cover art layout use journal-cover-design.
pipeline_position: [analysis-manuscript]
---

# Skill: Journal production

## When to use

- Manuscript is **accepted** or in **publisher production** (not initial drafting).
- User needs a **production checklist**, proof corrections, metadata, or camera-ready LaTeX/PDF.

## Procedure

1. Read `reference/latex/journal-production-stages.md` and identify current **stage** (1–9).
2. Confirm **publisher** and template (class file, word limit, float rules). Do not substitute another journal’s template without user approval.
3. **Stage 1–2:** Align with `manuscript-structure` if sections still move; lock structure before heavy typesetting.
4. **Stage 3–5:** Copyedit/proof pass — track changes as a numbered list; apply only approved fixes in `.tex`.
5. **Stage 4–6:** Run `latex` or `overleaf` MCP: validate, lint (`lint_file` if available), compile; fix undefined refs and overfull lines.
6. **Stage 6:** Metadata table for user to fill: title, short title, authors, affiliations, ORCID, keywords, running head, corresponding author.
7. **Stage 7:** Hand off to `journal-cover-design` if cover or graphical abstract is in scope.
8. **Stage 8–9:** Prepress checklist (bleed, PDF/X, font embedding); list supplementary files.

## Swiss Cheese

Before calling production “final,” run Swiss Cheese on **numbers** that appear in PDF (tables, effect sizes) against analysis outputs.

## MCP

- Local: `latex` server for edit/compile.
- Overleaf: `overleaf` for pull → check → fix → push when user works in cloud.

## Verification

- [ ] Stage and owner documented in reply
- [ ] Open items listed (refs, figures, metadata blanks)
- [ ] No fabricated ISSN, DOI, or volume/issue data

## Related

- `SKILL_latex-document.md`, `SKILL_journal-cover-design.md`, `SKILL_manuscript-structure.md`, `SKILL_latex-compile.md`

## Related Hubs

- [[Journal production skill]]

## Semantic graph (auto)

- [[LaTeX and journal production stack]]
- [[Journal production skill]]
- [[Skill registry]]
- [[skills-auto-detect]]
- [SKILLS INDEX](../docs/indexes/SKILLS_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[Journal production skill]]
- [[journal-production-stages]]
- [[LaTeX and journal production stack]]
- [[SKILL_journal-cover-design]]
- [[Journal cover design skill]]
