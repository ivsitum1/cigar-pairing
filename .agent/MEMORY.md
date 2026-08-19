# Project Memory

## Project name

cigar_and_rum — Cigar & Rum / knjiga bontona

## Agent profile

agent brain lite — writing-only

- Mozak: `agent-brain-lite/`
- Parent: `C:\Users\Admin\Documents\agent rules` (read-only)
- Fokus: pisanje (lifestyle / etiquette), **bez** pravila znanstvenog istraživanja
- Preferirani skill: `SKILL_nonacademic-writer.md`

## Milestones

- Agent brain lite instaliran u projekt (writing-only profil)
- Draft bontona: `docs/bonton/`
- 2026-07-25: Flavor enrichment — CigarWorld HTTP scrape + Famous Smoke via Cursor browser session (22 shop lines); ops learning in `agent-brain-lite/knowledge/learnings/shop-flavor-scrape.md`
- 2026-07-31: Four shops additive ingest (Famous, Neptune, C.Gars, La Couronne) — never overwrite regionLinks; baseline snapshot first; do not run regenerative `build-market-cigars.py` for this path
- 2026-08-18: House-line catalog fold — shop-title splits under parent (3313→3293); skip Cuban vs New World homonyms; product photos follow aliases
- 2026-08-18: Gift finder — polica/segment iz pitanja (rupa, vrh, omjer), budžet 100 €+, bez tuđe kolekcije
- 2026-08-17: Gift chooser `#/shopping/gift` — pet pitanja, razredi do 20 / 20–40 / 40–60 / 60–100 €, poklon cigara / boca / kombinacija, samo artikli s cijenom u odabranom tržištu
- 2026-08-01: House-line taxonomy — Crowned Heads / Foundation / Dunbarton children under parent; line name keeps marque; blurbs explain named lines
- 2026-08-19: Arhivirane varijante bonton-knjige u `docs/bonton/ARCHIVE_VARIJANTE.md` (jasan status kanon/draft/inbox)
- 2026-08-19: EN rukopis postavljen kao glavni radni manuskript; freeze/translation meta uklonjena iz `docs/bonton/HOW-TO-BE-A-GENTLEMAN-AT-THE-TABLE-DRAFT.md`
- 2026-08-19: Late journal rating: “Ocjena večeri” (journal) može se unijeti naknadno u `CollectionPage` i `JournalCalendar`, bez miješanja s “Moja ocjena” na kartici cigare/pića
- 2026-08-19: OCR pack (TypeScript warm/reset) i i18n ključevi riješeni; proširen `barcodeCatalog.json` EAN-ovima (Don Tomas Bundle Churchill/Robusto, Romeo y Julieta Churchill, Plasencia Alma Fuerte Robustus) uz `sync-cigar-barcodes.py --check` i fokalni OCR test prolaz.

## Notes

- Radni izlaz: `01_work/output/`, `01_work/correspondence/`
- Knjižni draftovi ostaju u `docs/bonton/`
- Ne pokretati scholarly / PRISMA / statističke pipelinee u ovom workspaceu
- Shop scrape: CW = VariantInfo + aroma canvas (429→resume); Famous = CAPTCHA na urllib, radi in-page `fetch` u IDE browseru; Famous prose > CW radar bits; ne mapirati broadleaf→Maduro za prikaz wrappera
- **HR copy:** uvijek `.cursor/rules/hr-copy-canon.mdc` (cigara/padeži, pepeo, domaćin, dim, bez infinitivnih lanaca; Rječnik = pojmovi, Leksikon = govor, Bonton = etiketa)
