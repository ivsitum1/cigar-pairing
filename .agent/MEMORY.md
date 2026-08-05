# Project Memory

## Project name

cigar_and_rum — Cigar & Rum / knjiga bontona

## Agent profile

**agent brain lite — writing-only**

- Mozak: `agent-brain-lite/`
- Parent: `C:\Users\Admin\Documents\agent rules` (read-only)
- Fokus: pisanje (lifestyle / etiquette), **bez** pravila znanstvenog istraživanja
- Preferirani skill: `SKILL_nonacademic-writer.md`

## Milestones

- Agent brain lite instaliran u projekt (writing-only profil)
- Draft bontona: `docs/bonton/`
- 2026-07-25: Flavor enrichment — CigarWorld HTTP scrape + Famous Smoke via Cursor browser session (22 shop lines); ops learning in `agent-brain-lite/knowledge/learnings/shop-flavor-scrape.md`
- 2026-07-31: Four shops additive ingest (Famous, Neptune, C.Gars, La Couronne) — never overwrite regionLinks; baseline snapshot first; do not run regenerative `build-market-cigars.py` for this path
- 2026-08-01: House-line taxonomy — Crowned Heads / Foundation / Dunbarton children under parent; line name keeps marque; blurbs explain named lines

## Notes

- Radni izlaz: `01_work/output/`, `01_work/correspondence/`
- Knjižni draftovi ostaju u `docs/bonton/`
- Ne pokretati scholarly / PRISMA / statističke pipelinee u ovom workspaceu
- Shop scrape: CW = VariantInfo + aroma canvas (429→resume); Famous = CAPTCHA na urllib, radi in-page `fetch` u IDE browseru; Famous prose > CW radar bits; ne mapirati broadleaf→Maduro za prikaz wrappera
- **HR copy:** uvijek `.cursor/rules/hr-copy-canon.mdc` (cigara/padeži, pepeo, domaćin, dim, bez infinitivnih lanaca; Rječnik = pojmovi, Leksikon = govor, Bonton = etiketa)
