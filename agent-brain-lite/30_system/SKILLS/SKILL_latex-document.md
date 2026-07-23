---
name: latex-document
description: Create and edit LaTeX documents (articles, theses, posters, letters), compile to PDF, fix errors. Uses latex/overleaf MCP and bundled templates.
version: 1.0
last_updated: 2026-05-22
domain: tools
tokens: ~750
triggers:
  - write latex
  - create latex
  - latex document
  - latex paper
  - beamer
  - latex poster
  - ieee format
  - latex thesis
  - latex report
  - convert to latex
  - latex template
requires_packages: []
reference_files:
  - reference/latex/ieee-journal-twocolumn-guide.md
  - reference/latex/journal-production-stages.md
  - reference/latex/templates/academic-paper.tex
conflicts_with: [document-conversion]
disambiguation: Full LaTeX authoring and layout; for compile-only or log fixes use latex-compile; for Word round-trip use document-conversion.
pipeline_position: [journal-production]
---

# Skill: LaTeX document

## When to use

- User wants a **new** LaTeX document, major structural edit, poster/slides, or publisher-specific layout (IEEE, generic article).
- User asks to **convert** content into LaTeX or rebuild a manuscript in `.tex`.

**Not for:** quick “just compile this file” with no authoring → `latex-compile`.

## MCP (mandatory for compile/edit)

| Server | Use |
|--------|-----|
| `latex` | `create_latex_file`, `edit_latex_file`, `read_latex_file`, `validate_latex`, `compile_latex`, `list_latex_files` |
| `overleaf` (optional) | `olsync_pull` / `olsync_push`, `check_math`, `check_figures`, `lint_file`, `compile` when project lives on Overleaf |

Set `LATEX_SERVER_BASE_PATH` to the LaTeX project root. Prerequisite: MiKTeX or TeX Live on the machine.

## Procedure

1. **Scope:** Document type (article, IEEE journal, poster, beamer, thesis, letter). Load `reference_files` when type matches.
2. **IEEE / Transactions:** Read `reference/latex/ieee-journal-twocolumn-guide.md` before writing; prefer `IEEEtran` class.
3. **Template:** Copy from `reference/latex/templates/academic-paper.tex` or use `latex` MCP bundled templates via `create_latex_file`.
4. **Authoring:** Edit via MCP; keep paths under project root. Do not fabricate citations or author metadata.
5. **Validate:** `validate_latex` before compile.
6. **Compile:** `compile_latex` (engine from project or guide). Capture log; fix errors iteratively.
7. **Deliver:** PDF path, page count, list of unresolved refs/warnings.

## Long documents (11+ pages)

- Split drafting by chapter/section if needed; merge with consistent preamble.
- Reconcile figures/tables with analysis outputs before final compile.

## Extended vendor reference

Full upstream skill (scripts, 50+ templates): `90_archive/imports/latex_mcp_skills_2026-05/latex-document-skill-main/`. Load scripts from there only when the user needs mail-merge, latexdiff, or PDF-to-LaTeX OCR pipelines.

## Verification

- [ ] PDF builds without fatal errors
- [ ] Bibliography and cross-refs resolved or explicitly listed as open
- [ ] Publisher class/options match user-stated journal

## Related

- `SKILL_latex-compile.md`, `SKILL_journal-production.md`, `SKILL_journal-cover-design.md`, `SKILL_manuscript-structure.md`

## Related Hubs

- [[LaTeX compile skill]]
- [[LaTeX document skill]]
