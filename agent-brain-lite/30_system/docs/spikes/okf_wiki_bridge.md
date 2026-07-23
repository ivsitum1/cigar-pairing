# Spike: OKF wiki bridge

**Notebook:** okf-knowledge | **Issue:** OKF-1

## Question

Can Google Open Knowledge Format (OKF) sit above `20_knowledge/wiki/` without breaking Obsidian wikilinks?

## Proposed seam (spike only)

1. Keep `.md` + YAML frontmatter as canonical human/edit layer
2. Optional export job: `wiki` → OKF JSON for agent consumption (read-only)
3. Do not replace `books_rag` chunk index without gate

## Dependencies

- Official OKF spec URL verified in grill external ledger
- Grill gate GO for OKF-1

## Status

**H1 GO confirmed** — export script `okf_wiki_export.py` pilot (US-37). Production GO still gated on official OKF spec URL verification.
