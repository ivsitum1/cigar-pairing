# Journal cover and title-page design

Use when the user asks for a **journal cover**, **issue cover**, **title page**, or **graphic abstract** layout in LaTeX (or print specs for a designer).

## 1. Clarify deliverable type

| Type | Typical size | Notes |
|------|----------------|-------|
| Journal issue cover | Publisher template (e.g. A4, custom trim) | CMYK, 3 mm bleed, spine width from page count |
| Article title page | Within `\maketitle` or `\begin{titlepage}` | Follow journal class; often no custom cover |
| Graphical abstract | 531×1328 px or journal spec | Single column figure, readable at thumbnail |
| Conference poster | A0/A1; see poster workflow in `latex-document` | Not the same as issue cover |

Ask: publisher name, trim size, bleed, spine (if book/issue), mandatory logos (society, OA badge), ISSN/barcode placement.

## 2. Content blocks (cover)

- Journal name + volume/issue/year
- Article title (short line count; avoid hyphenation across spine)
- Author list (or “et al.” on spine)
- Key visual (photo, illustration, or data figure)
- Footer: ISSN, barcode, copyright line, CC license icon if OA

## 3. LaTeX approaches

**Title page only (most articles):**

```latex
\begin{titlepage}
  \centering
  {\LARGE\bfseries Article Title\par}
  \vspace{1em}
  {\large Author One\inst{1} \and Author Two\inst{2}\par}
  \vfill
  {\small Journal Name, Vol. X, 2026\par}
\end{titlepage}
```

**Full cover page (standalone PDF):** `standalone` or `memoir`/`scrartcl` with exact `paperwidth`/`paperheight`; use `tikz` for layout grids.

**Spine text:** Only if page count known; rotate text on narrow spine box (designer often does in InDesign; export PDF for printer).

## 4. Design rules

- **Type hierarchy:** 1 display line (title), 1 secondary (journal), metadata 8–10 pt.
- **Contrast:** WCAG AA for any text on photography (scrims/overlays).
- **Safe zone:** Keep critical text inside inner margin (bleed + 5 mm).
- **Color:** Print → CMYK swatches; screen preview → RGB export separate.
- **Images:** 300 dpi at final size; vector preferred for logos.

## 5. Workflow with MCP

1. Draft layout in `.tex` under project root (`LATEX_SERVER_BASE_PATH`).
2. Compile with `latex` MCP `compile_latex` (or `overleaf` `compile`).
3. Export PNG preview for user approval before CMYK handoff.

## 6. Verification checklist

- [ ] Trim and bleed dimensions match publisher brief
- [ ] Spine width matches final page count (if applicable)
- [ ] ISSN / DOI / volume-issue text verified by user (never invent)
- [ ] Fonts embedded or outlined per printer spec
- [ ] No low-resolution raster upscaling

## Related

- `journal-production-stages.md` — stage 7 (cover / issue art)
- `templates/academic-paper.tex` — standard article front matter

## Semantic graph (auto)

- [[Skill registry]]
- [[Statistics skill stack]]
- [SKILLS INDEX](../../../docs/indexes/SKILLS_INDEX.md)
- [REFERENCE INDEX](../REFERENCE_INDEX.md)
- [FOLDER INDEX](../../../docs/FOLDER_INDEX.md)
