---
name: latex-compile
description: Compile LaTeX to PDF, fix build errors, verify output. Prefer latex MCP tools; CLI fallback when MCP unavailable.
version: 1.1
last_updated: 2026-05-22
domain: tools
tokens: ~500
triggers:
  - compile latex
  - compile paper
  - latex PDF
  - fix latex error
  - arxiv build
  - latexmk
requires_packages: []
reference_files: []
conflicts_with: []
disambiguation: Compile and log-debug only; for new documents or layout use latex-document.
pipeline_position: []
---

# Skill: LaTeX compile

## When to use

- User has an existing `.tex` project and needs **PDF build** or **error resolution** only.

## Procedure

1. **MCP first:** Call `latex` server `compile_latex` on the main file (or `overleaf` `compile` if synced project).
2. Identify engine (`pdflatex`, `xelatex`, `lualatex`, `latexmk`) from project config or log.
3. On failure: `read_latex_file` + log; fix missing packages, paths, references; recompile.
4. **Fallback (no MCP):** From project root run `latexmk -pdf -interaction=nonstopmode main.tex` (or engine per project).
5. Confirm PDF path and page count; list undefined citations/refs.

## Verification

- [ ] Build log clean or only benign warnings documented
- [ ] Bibliography resolved (no undefined citations)

## Related

- `SKILL_latex-document.md`, `SKILL_document-conversion.md`

## Related Hubs

- [[LaTeX compile skill]]
