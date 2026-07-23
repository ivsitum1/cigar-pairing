# Journal production stages (editorial → prepress)

Use this checklist when the user asks about **journal production**, **galley proofs**, **copyedit**, **typesetting**, or **camera-ready** delivery. Pair with publisher-specific class files (IEEEtran, elsarticle, svjour3, etc.).

## Stage map

| Stage | Owner | Deliverable | Agent focus |
|-------|--------|-------------|-------------|
| 1. Author manuscript | Author | IMRaD `.tex` + figures + `.bib` | Structure (`manuscript-structure`); content not invented |
| 2. Journal template fit | Author / production | Publisher `.cls` + style files | Class options, float rules, word limits |
| 3. Copyedit | Publisher | CE queries, tracked changes | Grammar, consistency; no new science |
| 4. Typesetting | Production | Flowed PDF, line breaks | LaTeX cleanup, overfull boxes, float placement |
| 5. Author proof | Author | Proof corrections list | One-pass fixes; no scope creep |
| 6. Metadata | Production | Title, abstract, keywords, ORCID | XML/front matter fields |
| 7. Cover / issue art | Production / marketing | Cover PDF (CMYK), spine | `journal-cover-design` skill |
| 8. Prepress | Printer | PDF/X, bleed, imposition | Color profile, font embedding |
| 9. Publication bundle | Platform | HTML/PDF/XML, supplements | File manifest, licensing statement |

## LaTeX technical gates (before “camera-ready”)

1. **Engine:** `pdflatex` vs `xelatex`/`lualatex` per publisher (CJK/Unicode → XeLaTeX).
2. **Bibliography:** BibTeX/biber complete; no undefined citations.
3. **Cross-refs:** All `\ref{}` resolve; label naming stable.
4. **Floats:** Figures/tables match journal rules (single vs double column, `figure*`).
5. **Math:** Display math numbered per style; bracket balance.
6. **Files:** All `\input`/`\includegraphics` paths relative and present.
7. **Log:** No undefined references; document intentional overfull hboxes.

## MCP tools (do not embed log output in skills)

| Need | MCP server | Typical tools |
|------|------------|---------------|
| Local project edit + compile | `latex` | `create_latex_file`, `edit_latex_file`, `validate_latex`, `compile_latex` |
| Overleaf sync + lint | `overleaf` | `olsync_pull`, `olsync_push`, `check_*`, `compile`, `lint_file` |

Run `detect_capabilities` (overleaf) before promising `latexindent`/`chktex`/`latexmk`.

## Handoff to writing vs statistics

- **WRITING:** prose, abstract, cover text, author response letter.
- **STATISTICS:** numbers in tables/figures must match analysis outputs (Swiss Cheese before final PDF).
- **METHODOLOGY:** reporting checklists (CONSORT, PRISMA, STROBE) before production lock.

## Related

- `reference/latex/ieee-journal-twocolumn-guide.md` — IEEE Transactions layout
- `SKILL_journal-cover-design.md` — cover and title-page design
- `SKILL_latex-document.md` — authoring workflows

## Semantic graph (auto)

- [[LaTeX and journal production stack]]
- [[Skill registry]]
- [[Statistics skill stack]]
- [SKILLS INDEX](../../../docs/indexes/SKILLS_INDEX.md)
- [REFERENCE INDEX](../REFERENCE_INDEX.md)
- [FOLDER INDEX](../../../docs/FOLDER_INDEX.md)
